# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Wheel Installation Module

Provides reusable functionality for installing Python wheel (.whl) files
using pip or manual extraction as fallback.
"""

import logging
import subprocess
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Callable

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float], None]


class WheelInstaller:
    """Handles installation of Python wheel (.whl) files."""

    def __init__(self):
        logger.info("WheelInstaller initialized")

    def install_wheel(self, wheel_path: Path, 
                      progress_callback: Optional[ProgressCallback] = None) -> Tuple[bool, str]:
        """Install a wheel file using pip or manual extraction."""
        if not wheel_path.exists():
            return False, f"Wheel file not found: {wheel_path}"
        
        if not wheel_path.suffix.lower() == '.whl':
            return False, f"Not a wheel file: {wheel_path}"
        
        logger.info(f"Installing wheel: {wheel_path}")
        
        if progress_callback:
            progress_callback(0.1)
        
        success, message = self._install_with_pip(wheel_path, progress_callback)
        if success:
            if progress_callback:
                progress_callback(1.0)
            return True, "Update installed successfully using pip"
        
        logger.info("Pip installation failed, trying manual extraction")
        if progress_callback:
            progress_callback(0.5)
        
        success, message = self._install_with_extraction(wheel_path, progress_callback)
        if success:
            if progress_callback:
                progress_callback(1.0)
            return True, "Update installed successfully using manual extraction"
        
        return False, f"Installation failed: {message}"

    def _install_with_pip(self, wheel_path: Path,
                          progress_callback: Optional[ProgressCallback] = None) -> Tuple[bool, str]:
        """Install wheel using pip."""
        try:
            pip_command = self._find_pip_command()
            if not pip_command:
                return False, "pip not found"
            
            if progress_callback:
                progress_callback(0.2)
            
            supports_break_system_packages = self._check_pip_break_system_packages_support(pip_command)
            
            cmd = [
                pip_command, 
                "install",
                "-v",
                "--force-reinstall"
            ]
            
            if supports_break_system_packages:
                cmd.append("--break-system-packages")
            
            cmd.append(str(wheel_path))
            
            logger.info(f"Installing with pip: {' '.join(cmd)}")
            
            if progress_callback:
                progress_callback(0.3)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if progress_callback:
                progress_callback(0.9)
            
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
        """Check if pip supports the --break-system-packages option."""
        try:
            result = subprocess.run(
                [pip_command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"Could not determine pip version for {pip_command}")
                return False
            
            version_output = result.stdout.strip()
            if "pip " not in version_output:
                logger.warning(f"Unexpected pip version output: {version_output}")
                return False
            
            version_str = version_output.split("pip ")[1].split(" ")[0]
            version_parts = version_str.split(".")
            if len(version_parts) < 2:
                logger.warning(f"Could not parse pip version: {version_str}")
                return False
            
            try:
                major = int(version_parts[0])
                minor = int(version_parts[1])
                
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

    def _install_with_extraction(self, wheel_path: Path,
                                  progress_callback: Optional[ProgressCallback] = None) -> Tuple[bool, str]:
        """Install wheel using manual extraction (fallback method)."""
        try:
            extract_path = Path("/mnt/SDCARD/System/lib/python3.11/site-packages")
            
            if not extract_path.exists():
                python_site_packages = self._get_site_packages_path()
                if python_site_packages:
                    extract_path = python_site_packages
                else:
                    return False, "Cannot determine site-packages directory"
            
            logger.info(f"Extracting wheel to: {extract_path}")
            
            if progress_callback:
                progress_callback(0.6)
            
            with zipfile.ZipFile(wheel_path, 'r') as zip_file:
                zip_file.extractall(extract_path)
            
            if progress_callback:
                progress_callback(0.9)
            
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
        """Find available pip command."""
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
        """Get the Python site-packages directory."""
        try:
            import site
            site_packages = site.getsitepackages()[0]
            return Path(site_packages)
        except Exception:
            return None