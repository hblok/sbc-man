# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Self-Update Service Module

Handles application self-updating functionality including version checking,
downloading updates, and installation using pip or manual extraction.

Based on requirements for adding self-update feature to the game manager.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Callable
import urllib.request
import urllib.error
import traceback

from ..services.config_manager import ConfigManager
from ..services.wheel_installer import WheelInstaller
from sbcman.path.paths import AppPaths
from sbcman import version

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float], None]


class UpdaterService:
    """
    Service for handling application self-updates.
    
    Provides functionality to check for updates, download wheel files,
    and install them using pip or manual extraction as fallback.
    """

    def __init__(self, config_manager: ConfigManager, app_paths: AppPaths):
        """
        Initialize the updater service.
        
        Args:
            config_manager: Configuration manager instance
            app_paths: Application paths instance
        """
        self.config_manager = config_manager
        self.app_paths = app_paths
        self.current_version = version.VERSION
        
        # Get update repository URL from config (default to sbc-man GitHub)
        self.update_repo_url = config_manager.get("update.repository_url")

        # Threading support
        self.is_updating = False
        self.update_progress = 0.0
        self.update_message = ""
        self.current_update_thread: Optional[threading.Thread] = None
        self._update_lock = threading.Lock()
        
        logger.info(f"UpdaterService initialized with repo: {self.update_repo_url}")

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if a newer version is available.
        
        Returns:
            Tuple of (update_available, latest_version, download_url)
        """
        try:
            # Use GitHub API to get latest release information
            # Convert GitHub URL to API format
            if "github.com" in self.update_repo_url:
                # Extract owner/repo from GitHub URL
                # Example: https://github.com/hblok/sbc-man -> hblok/sbc-man
                github_parts = self.update_repo_url.replace("https://github.com/", "").strip("/")
                api_url = f"https://api.github.com/repos/{github_parts}/releases/latest"
            else:
                # Fallback to original format (may not work for non-GitHub repos)
                api_url = f"{self.update_repo_url}/releases/latest"
            
            logger.info(f"Checking for updates at: {api_url}")
            
            # Get latest release info from GitHub API
            with urllib.request.urlopen(api_url) as response:  # nosec : Config is http only
                release_data = json.loads(response.read().decode('utf-8'))
            
            latest_version = release_data.get("tag_name", "").lstrip("v")
            
            if not latest_version:
                logger.warning("No version tag found in release")
                return False, None, None
            
            # Find wheel download URL
            download_url = None
            for asset in release_data.get("assets", []):
                if asset.get("name", "").endswith(".whl"):
                    download_url = asset.get("browser_download_url")
                    break
            
            if not download_url:
                logger.warning("No wheel file found in release assets")
                return False, None, None
            
            # Compare versions
            update_available = self._compare_versions(self.current_version, latest_version)
            
            logger.info(f"Current: {self.current_version}, Latest: {latest_version}, Update: {update_available}")
            
            return update_available, latest_version, download_url
            
        except urllib.error.URLError as e:
            print(traceback.format_exc())
            logger.error(f"Network error checking for updates: {e}")
            return False, None, None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response checking updates: {e}")
            return False, None, None
        except Exception as e:
            logger.error(f"Unexpected error checking for updates: {e}")
            return False, None, None

    def start_update(self, download_url: str) -> None:
        """Start the update process in a background thread.
        
        Args:
            download_url: URL to download the update from
        """
        if self.is_updating:
            logger.warning("Update already in progress")
            return
        
        self.is_updating = True
        self.update_progress = 0.0
        self.update_message = "Preparing update..."
        
        self.current_update_thread = threading.Thread(
            target=self._update_thread,
            args=(download_url,),
            daemon=True,
        )
        self.current_update_thread.start()
        logger.info("Started update thread")

    def _update_thread(self, download_url: str) -> None:
        """Worker thread for downloading and installing updates."""
        try:
            # Download phase
            with self._update_lock:
                self.update_message = "Downloading update..."
            
            wheel_path = self._download_file(download_url)
            
            if not wheel_path:
                with self._update_lock:
                    self.update_message = "Failed to download update"
                return
            
            # Install phase
            with self._update_lock:
                self.update_message = "Installing update..."
                self.update_progress = 0.6
            
            success, message = self._install_wheel(wheel_path)
            
            # Update final status
            with self._update_lock:
                self.update_progress = 1.0
                if success:
                    self.update_message = f"Update complete: {message}"
                else:
                    self.update_message = f"Installation failed: {message}"
            
            logger.info("Update completed successfully" if success else "Update failed")
            
        except Exception as e:
            logger.error(f"Error during update: {e}")
            with self._update_lock:
                self.update_message = f"Update error: {str(e)}"
                self.update_progress = 1.0
        finally:
            self.is_updating = False

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

    def _download_file(self, download_url: str) -> Optional[Path]:
        """
        Download the update wheel file (internal method).
        
        Args:
            download_url: URL to download the wheel file from
        
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Create temporary directory for download
            temp_dir = self.app_paths.temp_dir / "updates"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract filename from URL
            filename = download_url.split("/")[-1]
            wheel_path = temp_dir / filename
            
            logger.info(f"Downloading update from: {download_url}")
            logger.info(f"Saving to: {wheel_path}")
            
            # Download the file with progress indication
            if "http" not in download_url:
                raise ValueError(f"Must be http/s, was: {download_url}")
            
            # Track download progress
            with self._update_lock:
                self.update_progress = 0.0
            
            # Use urlretrieve with custom reporthook for progress tracking
            def reporthook(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    # Scale to 0-60% range
                    download_fraction = min(downloaded / total_size, 1.0)
                    with self._update_lock:
                        self.update_progress = download_fraction * 0.6
            
            urllib.request.urlretrieve(download_url, wheel_path, reporthook)  # nosec : handled above
            
            # Verify file exists and has content
            if wheel_path.exists() and wheel_path.stat().st_size > 0:
                logger.info(f"Successfully downloaded update: {wheel_path}")
                with self._update_lock:
                    self.update_progress = 0.6  # Download complete at 60%
                return wheel_path
            else:
                logger.error("Downloaded file is empty or missing")
                return None
                
        except urllib.error.URLError as e:
            logger.error(f"Network error downloading update: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading update: {e}")
            return None

    def _install_wheel(self, wheel_path: Path) -> Tuple[bool, str]:
        """
        Install the update using pip or manual extraction (internal method).
        
        Args:
            wheel_path: Path to the wheel file to install
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Use the WheelInstaller module for installation
            installer = WheelInstaller()
            success, message = installer.install_wheel(wheel_path)
            
            return success, message
        except Exception as e:
            logger.error(f"Error during installation: {e}")
            return False, str(e)

    
    def download_update(self, download_url: str) -> Optional[Path]:
        """Download the update wheel file (synchronous wrapper).
        
        Args:
            download_url: URL to download the wheel file from
        
        Returns:
            Path to downloaded file or None if failed
        """
        return self._download_file(download_url)

    def install_update(self, wheel_path: Path) -> Tuple[bool, str]:
        """Install the update (synchronous wrapper).
        
        Args:
            wheel_path: Path to the wheel file to install
        
        Returns:
            Tuple of (success, message)
        """
        return self._install_wheel(wheel_path)

    def _compare_versions(self, current: str, latest: str) -> bool:
        """
        Compare two version strings.
        
        Args:
            current: Current version string
            latest: Latest version string
        
        Returns:
            True if latest version is newer
        """
        try:
            # Simple version comparison - split by dots and compare numerically
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            for cur, lat in zip(current_parts, latest_parts):
                if lat > cur:
                    return True
                elif lat < cur:
                    return False
            
            return False  # Versions are equal
            
        except ValueError:
            # If version parsing fails, assume update is available
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