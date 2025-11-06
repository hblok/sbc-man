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

from ..services.network import NetworkService
from .game import Game

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

    def __init__(self, hw_config: dict):
        """
        Args:
            hw_config: Hardware configuration dictionary
        """
        self.hw_config = hw_config
        self.network = NetworkService()
        
        # Download state
        self.current_download: Optional[threading.Thread] = None
        self.is_downloading = False
        self.download_progress = 0.0
        
        # Determine download directory
        paths = hw_config.get("paths", {})
        # FIXME
        games_dir = Path(paths.get("games", "~/games")).expanduser()
        self.downloads_dir = games_dir / "downloads"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("DownloadManager initialized")

    def download_game(self, game: Game, observer: Optional[DownloadObserver] = None) -> None:
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

    def _download_thread(self, game: Game, observer: Optional[DownloadObserver]) -> None:
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
            game.install_path = install_path
            
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

    def _extract_archive(self, archive_path: Path, game: Game) -> Path:
        """
        Extract downloaded archive to installation directory.
        
        Args:
            archive_path: Path to downloaded archive
            game: Game being installed
            
        Returns:
            Path: Installation directory path
            
        Raises:
            Exception: If extraction fails
        """
        # Determine installation directory
        paths = self.hw_config.get("paths", {})
        # FIXME
        games_dir = Path(paths.get("games", "~/games")).expanduser()
        install_dir = games_dir / game.id
        install_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract based on file type
        # FIXME
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(install_dir)
        elif archive_path.suffix in [".tar", ".gz", ".bz2", ".xz"]:
            with tarfile.open(archive_path, "r:*") as tar_ref:
                tar_ref.extractall(install_dir)
        else:
            raise Exception(f"Unsupported archive format: {archive_path.suffix}")
        
        logger.info(f"Extracted to {install_dir}")
        
        # Set executable permissions on entry point
        entry_point = install_dir / game.entry_point
        if entry_point.exists():
            entry_point.chmod(0o755)
        
        return install_dir

    def cancel_download(self) -> None:
        if self.is_downloading:
            logger.info("Download cancellation requested")
            self.is_downloading = False
            # Note: Thread will check is_downloading flag and exit

    def get_progress(self) -> float:
        """ Return the current download progress as a value between 0.0 and 1.0. """
        return self.download_progress
