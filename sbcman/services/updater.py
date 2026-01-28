# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Self-Update Service Module

Handles application self-updating functionality including version checking,
downloading updates, and installation using pip or manual extraction.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Optional, Tuple
import traceback

from sbcman.services import config_manager
from sbcman.services import wheel_installer
from sbcman.services import network
from sbcman.path import paths
from sbcman import version

logger = logging.getLogger(__name__)


class UpdateObserver:
    """Observer interface for update progress."""

    def on_progress(self, progress: float, message: str) -> None:
        """Called when update progress changes.
        
        Args:
            progress: Progress value from 0.0 to 1.0
            message: Current status message
        """
        pass

    def on_complete(self, success: bool, message: str) -> None:
        """Called when update completes."""
        pass

    def on_error(self, error_message: str) -> None:
        """Called when an error occurs."""
        pass


class UpdaterService:
    """Service for handling application self-updates."""

    def __init__(self, config: config_manager.ConfigManager, app_paths: paths.AppPaths):
        self.config_manager = config
        self.app_paths = app_paths
        self.current_version = version.VERSION
        
        self.update_repo_url = config.get("update.repository_url")
        self.network = network.NetworkService()

        self.is_updating = False
        self.update_progress = 0.0
        self.update_message = ""
        self.current_update_thread: Optional[threading.Thread] = None
        self._update_lock = threading.Lock()
        
        logger.info(f"UpdaterService initialized with repo: {self.update_repo_url}")

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Check if a newer version is available."""
        try:
            api_url = self._build_api_url()
            logger.info(f"Checking for updates at: {api_url}")
            
            response = self.network.get(api_url)
            if response is None:
                logger.error("Failed to get release data from API")
                return False, None, None
            
            release_data = response.json()
            
            latest_version = release_data.get("tag_name", "").lstrip("v")
            if not latest_version:
                logger.warning("No version tag found in release")
                return False, None, None
            
            download_url = self._find_wheel_url(release_data)
            if not download_url:
                logger.warning("No wheel file found in release assets")
                return False, None, None
            
            update_available = self._compare_versions(self.current_version, latest_version)
            logger.info(f"Current: {self.current_version}, Latest: {latest_version}, "
                       f"Update: {update_available}")
            
            return update_available, latest_version, download_url
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response checking updates: {e}")
            return False, None, None
        except Exception as e:
            logger.error(f"Unexpected error checking for updates: {e}")
            return False, None, None

    def _build_api_url(self) -> str:
        """Build the GitHub API URL from the repository URL."""
        if "github.com" in self.update_repo_url:
            github_parts = self.update_repo_url.replace("https://github.com/", "").strip("/")
            return f"https://api.github.com/repos/{github_parts}/releases/latest"
        return f"{self.update_repo_url}/releases/latest"

    def _find_wheel_url(self, release_data: dict) -> Optional[str]:
        """Find the wheel download URL from release assets."""
        for asset in release_data.get("assets", []):
            if asset.get("name", "").endswith(".whl"):
                return asset.get("browser_download_url")
        return None

    def start_update(self, download_url: str, 
                     observer: Optional[UpdateObserver] = None) -> None:
        """Start the update process in a background thread."""
        if self.is_updating:
            logger.warning("Update already in progress")
            if observer:
                observer.on_error("Update already in progress")
            return
        
        self.is_updating = True
        self.update_progress = 0.0
        self.update_message = "Preparing update..."
        
        self.current_update_thread = threading.Thread(
            target=self._update_thread,
            args=(download_url, observer),
            daemon=True,
        )
        self.current_update_thread.start()
        logger.info("Started update thread")

    def _update_thread(self, download_url: str, 
                       observer: Optional[UpdateObserver]) -> None:
        """Worker thread for downloading and installing updates."""
        try:
            self._set_progress(0.0, "Downloading update...")
            self._notify_observer(observer)
            
            wheel_path = self._download_file(download_url, observer)
            
            if not wheel_path:
                self._set_progress(1.0, "Failed to download update")
                self._notify_observer(observer)
                if observer:
                    observer.on_complete(False, "Failed to download update")
                return
            
            self._set_progress(0.6, "Installing update...")
            self._notify_observer(observer)
            
            success, message = self._install_wheel(wheel_path, observer)
            
            self._set_progress(1.0, message if success else f"Installation failed: {message}")
            self._notify_observer(observer)
            
            if observer:
                if success:
                    observer.on_complete(True, message)
                else:
                    observer.on_complete(False, message)
            
            logger.info("Update completed successfully" if success else "Update failed")
            
        except Exception as e:
            logger.error(f"Error during update: {e}")
            error_msg = f"Update error: {str(e)}"
            self._set_progress(1.0, error_msg)
            self._notify_observer(observer)
            if observer:
                observer.on_error(error_msg)
                observer.on_complete(False, error_msg)
        finally:
            self.is_updating = False

    def _set_progress(self, progress: float, message: str) -> None:
        """Thread-safe progress update."""
        with self._update_lock:
            self.update_progress = progress
            self.update_message = message

    def _notify_observer(self, observer: Optional[UpdateObserver]) -> None:
        """Notify observer of current progress."""
        if observer:
            with self._update_lock:
                observer.on_progress(self.update_progress, self.update_message)

    def get_progress(self) -> float:
        """Return the current update progress as a value between 0.0 and 1.0."""
        with self._update_lock:
            return self.update_progress

    def get_message(self) -> str:
        """Return the current update message."""
        with self._update_lock:
            return self.update_message

    def cancel_update(self) -> None:
        """Cancel the current update operation."""
        if self.is_updating:
            self.is_updating = False
            logger.info("Update cancelled")

    def _download_file(self, download_url: str, 
                       observer: Optional[UpdateObserver]) -> Optional[Path]:
        """Download the update wheel file."""
        try:
            temp_dir = self.app_paths.temp_dir / "updates"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            filename = download_url.split("/")[-1]
            wheel_path = temp_dir / filename
            
            logger.info(f"Downloading update from: {download_url}")
            logger.info(f"Saving to: {wheel_path}")
            
            if "http" not in download_url:
                raise ValueError(f"Must be http/s, was: {download_url}")
            
            def progress_callback(downloaded: int, total_size: int):
                if total_size > 0:
                    download_fraction = min(downloaded / total_size, 1.0)
                    progress = download_fraction * 0.6
                    self._set_progress(progress, "Downloading update...")
                    self._notify_observer(observer)
            
            success = self.network.download_file(
                download_url, 
                wheel_path, 
                progress_callback=progress_callback
            )
            
            if success and wheel_path.exists() and wheel_path.stat().st_size > 0:
                logger.info(f"Successfully downloaded update: {wheel_path}")
                self._set_progress(0.6, "Download complete")
                self._notify_observer(observer)
                return wheel_path
            else:
                logger.error("Downloaded file is empty or missing")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error downloading update: {e}")
            return None

    def _install_wheel(self, wheel_path: Path, 
                       observer: Optional[UpdateObserver]) -> Tuple[bool, str]:
        """Install the update using WheelInstaller with progress tracking."""
        try:
            installer = wheel_installer.WheelInstaller()
            
            def install_progress_callback(progress: float) -> None:
                # Scale installation progress from 60% to 100%
                scaled_progress = 0.6 + (progress * 0.4)
                self._set_progress(scaled_progress, "Installing update...")
                self._notify_observer(observer)
            
            success, message = installer.install_wheel(
                wheel_path, 
                progress_callback=install_progress_callback
            )
            
            return success, message
        except Exception as e:
            logger.error(f"Error during installation: {e}")
            return False, str(e)

    def download_update(self, download_url: str) -> Optional[Path]:
        """Download the update wheel file (synchronous wrapper for tests)."""
        return self._download_file(download_url, observer=None)

    def install_update(self, wheel_path: Path) -> Tuple[bool, str]:
        """Install the update (synchronous wrapper for tests)."""
        return self._install_wheel(wheel_path, observer=None)

    def _compare_versions(self, current: str, latest: str) -> bool:
        """Compare two version strings."""
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            for cur, lat in zip(current_parts, latest_parts):
                if lat > cur:
                    return True
                elif lat < cur:
                    return False
            
            return False
            
        except ValueError:
            logger.warning("Version parsing failed, assuming update available")
            return True

    def cleanup_temp_files(self) -> None:
        """Clean up temporary update files."""
        try:
            temp_dir = self.app_paths.temp_dir / "updates"
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                logger.info("Cleaned up temporary update files")
        except Exception as e:
            logger.warning(f"Failed to clean up temp files: {e}")