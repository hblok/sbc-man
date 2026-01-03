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
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import urllib.request
import urllib.error
import traceback

from ..services.config_manager import ConfigManager
from sbcman.path.paths import AppPaths

logger = logging.getLogger(__name__)


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
        self.current_version = ""
        
        # Get update repository URL from config (default to sbc-man GitHub)
        self.update_repo_url = config_manager.get("update.repository_url")
        
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

    def download_update(self, download_url: str) -> Optional[Path]:
        """
        Download the update wheel file.
        
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
            
            urllib.request.urlretrieve(download_url, wheel_path)  # nosec : handled above
            
            # Verify file exists and has content
            if wheel_path.exists() and wheel_path.stat().st_size > 0:
                logger.info(f"Successfully downloaded update: {wheel_path}")
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

    def install_update(self, wheel_path: Path) -> Tuple[bool, str]:
        """
        Install the update using pip or manual extraction.
        
        Args:
            wheel_path: Path to the wheel file to install
            
        Returns:
            Tuple of (success, message)
        """
        # Try Method A: pip installation
        success, message = self._install_with_pip(wheel_path)
        if success:
            return True, "Update installed successfully using pip"
        
        # Try Method B: manual extraction (fallback)
        logger.info("Pip installation failed, trying manual extraction")
        success, message = self._install_with_extraction(wheel_path)
        if success:
            return True, "Update installed successfully using manual extraction"
        
        return False, f"Installation failed: {message}"

    def _install_with_pip(self, wheel_path: Path) -> Tuple[bool, str]:
        """
        Install update using pip.
        
        Args:
            wheel_path: Path to wheel file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if pip is available
            pip_command = self._find_pip_command()
            if not pip_command:
                return False, "pip not found"
            
            # Check if pip supports --break-system-packages (introduced in pip 23.0)
            supports_break_system_packages = self._check_pip_break_system_packages_support(pip_command)
            
            # Build pip install command with conditional --break-system-packages option
            cmd = [
                pip_command, 
                "install",
                "-v",
                "--force-reinstall"
            ]
            
            # Add --break-system-packages only if supported
            if supports_break_system_packages:
                cmd.append("--break-system-packages")
            
            cmd.append(str(wheel_path))
            
            logger.info(f"Installing with pip: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Pip installation successful")
                logger.debug("\\n\\n" + str(result.stdout))
                logger.debug("\\n\\n" + str(result.stderr))
                return True, "Pip installation successful"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"Pip installation failed: {error_msg}")
                return False, f"Pip failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Pip installation timed out"
        except FileNotFoundError:
            return False, "pip command not found"
        except Exception as e:
            logger.error(f"Unexpected error with pip installation: {e}")
            return False, f"Pip error: {e}"

    def _check_pip_break_system_packages_support(self, pip_command: str) -> bool:
        """
        Check if pip supports the --break-system-packages option.
        
        The --break-system-packages option was introduced in pip 23.0.
        This method checks the pip version to determine support.
        
        Args:
            pip_command: The pip command to check (e.g., 'pip', 'pip3')
            
        Returns:
            True if --break-system-packages is supported, False otherwise
        """
        try:
            # Get pip version
            result = subprocess.run(
                [pip_command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"Could not determine pip version for {pip_command}")
                return False
            
            # Parse version from output like "pip X.Y.Z from ..."
            version_output = result.stdout.strip()
            if "pip " not in version_output:
                logger.warning(f"Unexpected pip version output: {version_output}")
                return False
            
            # Extract version number
            version_str = version_output.split("pip ")[1].split(" ")[0]
            
            # Parse version components
            version_parts = version_str.split(".")
            if len(version_parts) < 2:
                logger.warning(f"Could not parse pip version: {version_str}")
                return False
            
            try:
                major = int(version_parts[0])
                minor = int(version_parts[1])
                
                # --break-system-packages was introduced in pip 23.0
                if major > 23 or (major == 23 and minor >= 0):
                    logger.info(f"pip {version_str} supports --break-system-packages")
                    return True
                else:
                    logger.info(f"pip {version_str} does not support --break-system-packages")
                    return False
                    
            except ValueError:
                logger.warning(f"Invalid pip version format: {version_str}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning("Timeout checking pip version")
            return False
        except Exception as e:
            logger.error(f"Error checking pip version support: {e}")
            return False

    def _install_with_extraction(self, wheel_path: Path) -> Tuple[bool, str]:
        """
        Install update using manual extraction (fallback method).
        
        Args:
            wheel_path: Path to wheel file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Default extraction path for Python packages
            extract_path = Path("/mnt/SDCARD/System/lib/python3.11/site-packages")
            
            # If path doesn't exist, try alternative paths
            if not extract_path.exists():
                # Try getting Python site-packages path dynamically
                python_site_packages = self._get_site_packages_path()
                if python_site_packages:
                    extract_path = python_site_packages
                else:
                    return False, "Cannot determine site-packages directory"
            
            logger.info(f"Extracting wheel to: {extract_path}")
            
            # Treat wheel as zip file and extract
            with zipfile.ZipFile(wheel_path, 'r') as zip_file:
                zip_file.extractall(extract_path)
            
            logger.info("Manual extraction successful")
            return True, "Manual extraction successful"
            
        except zipfile.BadZipFile:
            return False, "Wheel file is not a valid zip archive"
        except PermissionError:
            return False, "Permission denied extracting to site-packages"
        except Exception as e:
            logger.error(f"Unexpected error with manual extraction: {e}")
            return False, f"Extraction error: {e}"

    def _find_pip_command(self) -> Optional[str]:
        """
        Find available pip command.
        
        Returns:
            pip command string or None if not found
        """
        pip_commands = ["pip", "pip3"]
        
        for cmd in pip_commands:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.info(f"Found pip command: {cmd}")
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None

    def _get_site_packages_path(self) -> Optional[Path]:
        """
        Get the Python site-packages directory.
        
        Returns:
            Path to site-packages or None if not found
        """
        try:
            import site
            site_packages = site.getsitepackages()[0]
            return Path(site_packages)
        except Exception:
            return None

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
