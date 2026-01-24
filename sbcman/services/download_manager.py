# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Manages game downloads with observer pattern for progress tracking.
Uses threading to keep UI responsive during downloads.
"""

import logging
import site
import threading
from pathlib import Path
from typing import Optional

from sbcman.services import archive_extractor
from sbcman.services import network
from sbcman.services import wheel_installer
from sbcman.path import paths
from sbcman.proto import game_pb2

logger = logging.getLogger(__name__)


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

    def __init__(self, hw_config: dict, app_paths: paths.AppPaths, game_library=None, config=None):
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
        self.archive_extractor = archive_extractor.ArchiveExtractor()

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
            install_path = self._install_game(dest_file, game)

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
            self.download_progress = min(downloaded / total if total > 0 else 0, 1.0)
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

    def _install_game(self, archive_path: Path, game: game_pb2.Game) -> Path:
        """Install the game from the downloaded archive."""
        logger.info(f"Extracting {archive_path}")
        suffix = archive_path.suffix.lower()

        # Install as wheel if enabled by config option "install.install_as_pip"
        install_as_pip = self._get_install_as_pip()
        if suffix == ".whl" and install_as_pip:
            return self._install_wheel(archive_path, game)

        return self._extract_archive(archive_path, game)

    def _install_wheel(self, wheel_path: Path, game: game_pb2.Game) -> Path:
        """Install a wheel file and return the install path."""
        logger.info(f"Detected wheel file: {wheel_path}")
        installer = wheel_installer.WheelInstaller()
        success, message = installer.install_wheel(wheel_path)

        if not success:
            raise Exception(f"Wheel installation failed: {message}")

        logger.info(f"Wheel installed successfully: {message}")

        for s in site.getsitepackages():
            p = Path(s) / game.entry_point
            if p.exists():
                logger.info(f"Found {p}")
                return Path(s)

        # RESOLVE: what do do here??
        return Path(site.getusersitepackages())

    def _extract_archive(self, archive_path: Path, game: game_pb2.Game) -> Path:
        """Extract archive and set up the game directory."""
        
        # Use portmaster_base_dir if install.add_portmaster_entry is true
        base_dir = self._get_install_base_dir()
        install_dir = base_dir / game.id
        self.archive_extractor.extract(archive_path, install_dir)

        entry_point = install_dir / game.entry_point
        if entry_point.exists():
            entry_point.chmod(0o755)

        return install_dir

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

    def _get_install_as_pip(self) -> bool:
        """Get install_as_pip setting from config."""
        if self.config:
            return self.config.get("install.install_as_pip", False)
        return False

    def _get_install_base_dir(self) -> Path:
        """Get the base directory for game installation from config."""
        if self.config:
            add_portmaster_entry = self.config.get("install.add_portmaster_entry", False)
            if add_portmaster_entry:
                portmaster_base_dir = self.config.get("install.portmaster_base_dir")
                if portmaster_base_dir:
                    return Path(portmaster_base_dir)
        return self.app_paths.games_dir

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
