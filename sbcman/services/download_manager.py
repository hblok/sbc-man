# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Manages game downloads with observer pattern for progress tracking.
Uses threading to keep UI responsive during downloads.
"""

import logging
import threading
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Callable, Any
import os
import zipfile

from sbcman.services.network import NetworkService
from sbcman.services.wheel_installer import WheelInstaller
from sbcman.path.paths import AppPaths
from sbcman.proto import game_pb2

logger = logging.getLogger(__name__)


class DownloadObserver:
    """ Observer interface for download progress. """

    def on_progress(self, downloaded: int, total: int) -> None:
        """
        Called when download progress updates.
        
        Args:
            downloaded: Bytes downloaded so far
            total: Total bytes to download
        """
        pass

    def on_complete(self, success: bool, message: str) -> None:
        """
        Called when download completes.
        
        Args:
            success: True if download succeeded
            message: Success or error message
        """
        pass

    def on_error(self, error_message: str) -> None:
        """
        Called when an error occurs.
        
        Args:
            error_message: Description of the error
        """
        pass


class DownloadManager:
    """
    Download manager with observer pattern.
    
    Manages game downloads in a separate thread, providing progress
    updates via observer callbacks.
    """

    def __init__(self, hw_config: dict, app_paths: AppPaths, game_library=None):
        """
        Args:
            hw_config: Hardware configuration dictionary
            app_paths: Application paths instance
            game_library: Optional GameLibrary instance for persisting installed games
        """
        self.hw_config = hw_config
        self.app_paths = app_paths
        self.game_library = game_library
        self.network = NetworkService()
        
        # Download state
        self.current_download: Optional[threading.Thread] = None
        self.is_downloading = False
        self.download_progress = 0.0
        
        # Use AppPaths for download directory
        self.downloads_dir = self.app_paths.downloads_dir
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("DownloadManager initialized")

    def download_game(self, game: game_pb2.Game, observer: Optional[DownloadObserver] = None) -> None:
        """
        Start downloading a game in a separate thread.
        
        Args:
            game: Game to download
            observer: Observer to receive progress updates
        """
        if self.is_downloading:
            logger.warning("Download already in progress")
            if observer:
                observer.on_error("Download already in progress")
            return
        
        if not game.download_url:
            logger.error(f"No download URL for game: {game.name}")
            if observer:
                observer.on_error("No download URL available")
            return
        
        # Start download thread
        self.is_downloading = True
        self.current_download = threading.Thread(
            target=self._download_thread,
            args=(game, observer),
            daemon=True,
        )
        self.current_download.start()
        logger.info(f"Started download for game: {game.name}")

    def _download_thread(self, game: game_pb2.Game, observer: Optional[DownloadObserver]) -> None:
        """
        Worker thread for downloading and extracting game.
        
        Args:
            game: Game to download
            observer: Observer to receive updates
        """
        try:
            # Download file
            # FIXME
            filename = Path(game.download_url).name
            if not filename:
                filename = f"{game.id}.zip"
            
            dest_file = self.downloads_dir / filename
            
            logger.info(f"Downloading {game.download_url} to {dest_file}")
            
            # Progress callback
            def progress_callback(downloaded: int, total: int) -> None:
                self.download_progress = downloaded / total if total > 0 else 0
                if observer:
                    observer.on_progress(downloaded, total)
            
            # Download the file
            success = self.network.download_file(
                game.download_url,
                dest_file,
                progress_callback,
            )
            
            if not success:
                raise Exception("Download failed")
            
            # Extract archive
            logger.info(f"Extracting {dest_file}")
            install_path = self._extract_archive(dest_file, game)
            
            # Update game
            game.installed = True
            game.install_path = str(install_path)
            
            # Persist game to local_games.json if game_library is available
            if self.game_library:
                try:
                    self._persist_installed_game(game)
                    logger.info(f"Game {game.name} added to local games library")
                except Exception as e:
                    logger.error(f"Failed to persist game to library: {e}")
                    # Don't fail the entire installation if persistence fails
            else:
                logger.warning("No game_library provided - installed game will not be persisted")
            
            # Cleanup download file
            dest_file.unlink()
            
            # Notify success
            if observer:
                observer.on_complete(True, f"Successfully installed {game.name}")
            
            logger.info(f"Download and installation complete: {game.name}")
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            if observer:
                observer.on_error(str(e))
                observer.on_complete(False, str(e))
        
        finally:
            self.is_downloading = False
            self.download_progress = 0.0

    def _persist_installed_game(self, game: game_pb2.Game) -> None:
        """
        Persist the installed game to local_games.json.
        
        This method adds the newly installed game to the game library and saves it
        to the local_games.json file, ensuring it appears in the "Browse games" menu.
        
        Args:
            game: The game that was just installed
            
        Raises:
            Exception: If game persistence fails
        """
        if not self.game_library:
            logger.warning("Cannot persist game - no game_library available")
            return
        
        try:
            # Check if game already exists in library
            existing_game = self.game_library.get_game(game.id)
            
            if existing_game:
                # Update existing game
                logger.info(f"Updating existing game in library: {game.name}")
                self.game_library.update_game(game)
            else:
                # Add new game
                logger.info(f"Adding new game to library: {game.name}")
                self.game_library.add_game(game)
            
            # Save to file
            self.game_library.save_games()
            logger.info(f"Successfully persisted game {game.name} to local_games.json")
            
        except Exception as e:
            logger.error(f"Failed to persist game {game.name}: {e}")
            raise

    def _extract_archive(self, archive_path: Path, game: game_pb2.Game) -> Path:
        """
        Extract downloaded archive to installation directory.
        
        Supports multiple archive formats:
        - .whl files: Installed using pip or manual extraction
        - .zip files: Extracted using zipfile module
        - .tar files: Extracted using tarfile module (including .tar.gz, .tar.bz2, .tar.xz)
        
        Args:
            archive_path: Path to downloaded archive
            game: Game being installed
            
        Returns:
            Path: Installation directory path
            
        Raises:
            Exception: If extraction fails or format is unsupported
        """
        # Determine file type by extension
        suffix = archive_path.suffix.lower()
        
        # Handle .whl files using WheelInstaller
        if suffix == '.whl':
            logger.info(f"Detected wheel file: {archive_path}")
            installer = WheelInstaller()
            success, message = installer.install_wheel(archive_path)
            
            if not success:
                raise Exception(f"Wheel installation failed: {message}")
            
            logger.info(f"Wheel installed successfully: {message}")
            
            # For wheel files, return the site-packages directory as install path
            # This is a special case since wheels install to Python's site-packages
            # rather than a game-specific directory
            install_dir = self.app_paths.games_dir / game.id
            install_dir.mkdir(parents=True, exist_ok=True)
            return install_dir
        
        # Use AppPaths for installation directory
        install_dir = self.app_paths.games_dir / game.id
        install_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle .zip files
        if suffix == ".zip":
            logger.info(f"Extracting zip file: {archive_path}")
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                safe_members = self.get_secure_zip_members(zip_ref)
                zip_ref.extractall(install_dir, members=safe_members)  # nosec : handled in get_secure_zip_members
        
        # Handle .tar files (including .tar.gz, .tar.bz2, .tar.xz)
        elif suffix in [".tar", ".gz", ".bz2", ".xz"] or archive_path.name.endswith(('.tar.gz', '.tar.bz2', '.tar.xz')):
            logger.info(f"Extracting tar file: {archive_path}")
            with tarfile.open(archive_path, "r:*") as tar_ref:
                safe_members = self.get_secure_tar_members(tar_ref)
                tar_ref.extractall(install_dir, members=safe_members)  # nosec : handled in get_secure_tar_members
        
        # Unsupported format
        else:
            raise Exception(f"Unsupported archive format: {suffix}. Supported formats: .whl, .zip, .tar, .tar.gz, .tar.bz2, .tar.xz")
        
        logger.info(f"Extracted to {install_dir}")
        
        # Set executable permissions on entry point
        entry_point = install_dir / game.entry_point
        if entry_point.exists():
            entry_point.chmod(0o755)
        
        return install_dir
    
    def _validate_path(self, member_name: str) -> bool:
        """Validate member path for security issues."""
        # Check for absolute paths
        if member_name.startswith('/'):
            print(f"Absolute path: {member_name}")
            return False
        
        # Check for path traversal
        if '..' in member_name.split(os.sep):
            print(f"Path traversal: {member_name}")
            return False
        
        # Normalize and check again
        normalized = os.path.normpath(member_name)
        if normalized.startswith('..'):
            print(f"Normalized path traversal: {member_name}")
            return False
        
        # Check for null bytes (null injection)
        if '\x00' in member_name:
            print(f"Null byte in path: {member_name}")
            return False
        
        return True
    
    def get_secure_zip_members(self, zip_file: zipfile.ZipFile):
        """
        Get list of safe members from zip archive.
        
        Returns:
            List of validated member names
        """
        safe_members = []
        total_size = 0


        rejected_count = 0
        accepted_count = 0
        
        for member_info in zip_file.infolist():
            member_name = member_info.filename
            
            # Run all validation checks
            if not self._validate_path(member_name):
                rejected_count += 1
                continue
            
            if not self._validate_compression(member_info):
                rejected_count += 1
                continue
            
            if not self._validate_size(member_info, total_size):
                rejected_count += 1
                continue
            
            # All checks passed
            if not member_name.endswith('/'):
                print(f"✓ {member_name} ({member_info.file_size} bytes)")
                total_size += member_info.file_size
                accepted_count += 1
            
            safe_members.append(member_name)
        
        return safe_members

    def _validate_size(self, member_info: zipfile.ZipInfo, 
                      current_total: int) -> bool:
        """Validate member size."""

        max_total_size: int = 1024*1024*1024         # 1GB
        max_file_size: int = 100*1024*1024           # 100MB
        
        if member_info.file_size > max_file_size:
            print(f"File too large ({member_info.file_size} bytes): {member_info.filename}")
            return False
        
        if current_total + member_info.file_size > max_total_size:
            print(f"Total size would exceed limit: {member_info.filename}")
            return False
        
        return True
    
    def _validate_compression(self, member_info: zipfile.ZipInfo) -> bool:
        """Detect compression bombs."""
        max_compression_ratio: float = 100  # Zip bomb detection
        
        if member_info.compress_size > 0:
            ratio = member_info.file_size / member_info.compress_size
            if ratio > max_compression_ratio:
                print(f"Suspicious compression ratio ({ratio:.1f}x): {member_info.filename}")
                return False
        
        return True
    
    def get_secure_tar_members(self, tar, targetpath="."):
        """
        Filter tar members to prevent security vulnerabilities.
        Returns a list of safe members to extract.
        """
        safe_members = []

        for member in tar.getmembers():
            # Prevent absolute paths
            if member.name.startswith('/'):
                print(f"Skipping absolute path: {member.name}")
                continue

            # Prevent path traversal (../)
            if '..' in member.name.split(os.sep):
                print(f"Skipping path traversal: {member.name}")
                continue

            # Prevent symlinks
            if member.issym() or member.islnk():
                print(f"Skipping symlink: {member.name}")
                continue

            # Prevent device files
            if member.isdev() or member.ischr() or member.isblk():
                print(f"Skipping device file: {member.name}")
                continue

            safe_members.append(member)

        return safe_members
    
    # Python 3.12
    def secure_filter(self, tarinfo, targetpath):
        """
        Secure filter to prevent path traversal and dangerous extractions.
        """
        # Prevent absolute paths
        if tarinfo.name.startswith('/'):
            raise tarfile.ExtractError(f"Absolute path not allowed: {tarinfo.name}")

        # Prevent path traversal (../)
        if '..' in tarinfo.name.split(os.sep):
            raise tarfile.ExtractError(f"Path traversal not allowed: {tarinfo.name}")

        # Prevent symlinks
        if tarinfo.issym() or tarinfo.islnk():
            raise tarfile.ExtractError(f"Symlinks not allowed: {tarinfo.name}")

        # Prevent device files
        if tarinfo.isdev():
            raise tarfile.ExtractError(f"Device files not allowed: {tarinfo.name}")

        # Prevent character/block devices
        if tarinfo.ischr() or tarinfo.isblk():
            raise tarfile.ExtractError(f"Device files not allowed: {tarinfo.name}")

        return tarinfo


    def cancel_download(self) -> None:
        if self.is_downloading:
            logger.info("Download cancellation requested")
            self.is_downloading = False
            # Note: Thread will check is_downloading flag and exit

    def get_progress(self) -> float:
        """ Return the current download progress as a value between 0.0 and 1.0. """
        return self.download_progress