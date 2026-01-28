# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Manages game downloads with observer pattern for progress tracking.
Uses threading to keep UI responsive during downloads.
"""

import logging
import threading
from pathlib import Path
from typing import Optional, Callable

from sbcman.services import network
from sbcman.services import install_game
from sbcman.path import paths
from sbcman.proto import game_pb2

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float], None]


class DownloadObserver:
    """ Observer interface for download progress. """

    def on_progress(self, downloaded: int, total: int) -> None:
        """Called when download progress updates."""
        pass

    def on_complete(self, success: bool, message: str) -> None:
        """Called when download completes."""
        pass

    def on_error(self, error_message: str) -> None:
        """Called when an error occurs."""
        pass


class DownloadManager:
    """
    Download manager with observer pattern.

    Manages game downloads in a separate thread, providing progress
    updates via observer callbacks.
    """

    def __init__(self, hw_config: dict, app_paths: paths.AppPaths, game_library, config):
        """
        Args:
            hw_config: Hardware configuration dictionary
            app_paths: Application paths instance
            game_library: Optional GameLibrary instance for persisting installed games
            config: Optional ConfigManager instance for accessing install settings
        """
        self.hw_config = hw_config
        self.app_paths = app_paths
        self.game_library = game_library
        self.config = config
        self.network = network.NetworkService()
        self.game_installer = install_game.GameInstaller(config, app_paths)

        # Download state
        self.current_download: Optional[threading.Thread] = None
        self.is_downloading = False
        self.download_progress = 0.0

        # Use AppPaths for download directory
        self.downloads_dir = self.app_paths.downloads_dir
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

        logger.info("DownloadManager initialized")

    def download_game(self, game: game_pb2.Game, observer: Optional[DownloadObserver] = None) -> None:
        """Start downloading a game in a separate thread."""
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
        """Worker thread for downloading and extracting game."""
        try:
            dest_file = self._download_file(game, observer)
            install_path = self._install_game(dest_file, game, observer)

            game.installed = True
            game.install_path = str(install_path)

            self._persist_if_available(game)
            dest_file.unlink()

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

    def _download_file(self, game: game_pb2.Game, observer: Optional[DownloadObserver]) -> Path:
        """Download the game file and return the destination path."""
        filename = Path(game.download_url).name

        dest_file = self.downloads_dir / filename
        logger.info(f"Downloading {game.download_url} to {dest_file}")

        def progress_callback(downloaded: int, total: int) -> None:
            # Scale download progress to 0-60% range
            download_fraction = min(downloaded / total if total > 0 else 0, 1.0)
            self.download_progress = download_fraction * 0.6
            if observer:
                observer.on_progress(downloaded, total)

        success = self.network.download_file(
            game.download_url,
            dest_file,
            progress_callback,
        )

        if not success:
            raise Exception("Download failed")

        return dest_file

    def _install_game(self, archive_path: Path, game: game_pb2.Game, 
                     observer: Optional[DownloadObserver]) -> Path:
        """Install the game from the downloaded archive."""
        # Create progress callback for installer (60-100% range)
        def install_progress_callback(progress: float) -> None:
            # progress is 0.0-1.0, scale to 60-100%
            self.download_progress = 0.6 + (progress * 0.4)
            if observer:
                # Convert to downloaded/total format for backward compatibility
                total = 100
                downloaded = int(self.download_progress * total)
                observer.on_progress(downloaded, total)
        
        return self.game_installer.install_game(archive_path, game, install_progress_callback)

    def _persist_if_available(self, game: game_pb2.Game) -> None:
        """Persist game to library if available."""
        if self.game_library:
            try:
                self._persist_installed_game(game)
                logger.info(f"Game {game.name} added to local games library")
            except Exception as e:
                logger.error(f"Failed to persist game to library: {e}")
        else:
            logger.warning("No game_library provided - installed game will not be persisted")

    
    def _persist_installed_game(self, game: game_pb2.Game) -> None:
        """Persist the installed game to local_games.json."""
        if not self.game_library:
            logger.warning("Cannot persist game - no game_library available")
            return

        existing_game = self.game_library.get_game(game.id)

        if existing_game:
            logger.info(f"Updating existing game in library: {game.name}")
            self.game_library.update_game(game)
        else:
            logger.info(f"Adding new game to library: {game.name}")
            self.game_library.add_game(game)

        self.game_library.save_games()
        logger.info(f"Successfully persisted game {game.name} to local_games.json")

    def cancel_download(self) -> None:
        if self.is_downloading:
            logger.info("Download cancellation requested")
            self.is_downloading = False
            # Note: Thread will check is_downloading flag and exit

    def get_progress(self) -> float:
        """ Return the current download progress as a value between 0.0 and 1.0. """
        return self.download_progress