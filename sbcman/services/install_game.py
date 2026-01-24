# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Handles game installation from downloaded archives.

Provides functionality to install games from various archive formats,
including wheel files and compressed archives.
"""

import logging
import site
from pathlib import Path
from typing import Optional

from sbcman.services import archive_extractor
from sbcman.services import wheel_installer
from sbcman.proto import game_pb2

logger = logging.getLogger(__name__)


class GameInstaller:
    """Handles game installation from downloaded archives."""

    def __init__(self, config=None, app_paths=None):
        """
        Args:
            config: Optional ConfigManager instance for accessing install settings
            app_paths: Optional AppPaths instance for determining install directories
        """
        self.config = config
        self.app_paths = app_paths
        self.archive_extractor = archive_extractor.ArchiveExtractor()
        logger.info("GameInstaller initialized")

    def install_game(self, archive_path: Path, game: game_pb2.Game) -> Path:
        """Install the game from the downloaded archive.

        Args:
            archive_path: Path to the downloaded game archive
            game: Game protobuf object containing game metadata

        Returns:
            Path: The installation directory path

        Raises:
            Exception: If installation fails
        """
        logger.info(f"Extracting {archive_path}")
        suffix = archive_path.suffix.lower()

        # Install as wheel if enabled by config option "install.install_as_pip"
        install_as_pip = self._get_install_as_pip()
        if suffix == ".whl" and install_as_pip:
            return self._install_wheel(archive_path, game)

        return self._extract_archive(archive_path, game)

    def _install_wheel(self, wheel_path: Path, game: game_pb2.Game) -> Path:
        """Install a wheel file and return the install path.

        Args:
            wheel_path: Path to the wheel file
            game: Game protobuf object

        Returns:
            Path: The site-packages directory where the wheel was installed

        Raises:
            Exception: If wheel installation fails
        """
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

        return Path(site.getusersitepackages())

    def _extract_archive(self, archive_path: Path, game: game_pb2.Game) -> Path:
        """Extract archive and set up the game directory.

        Args:
            archive_path: Path to the archive file
            game: Game protobuf object

        Returns:
            Path: The installation directory path
        """
        base_dir = self._get_install_base_dir()
        install_dir = base_dir / game.id
        self.archive_extractor.extract(archive_path, install_dir)

        entry_point = install_dir / game.entry_point
        if entry_point.exists():
            entry_point.chmod(0o755)

        return install_dir

    def _get_install_as_pip(self) -> bool:
        """Get install_as_pip setting from config.

        Returns:
            bool: True if wheels should be installed as pip packages
        """
        if self.config:
            return self.config.get("install.install_as_pip", False)
        return False

    def _get_install_base_dir(self) -> Path:
        """Get the base directory for game installation from config.

        Returns:
            Path: The base directory for game installation
        """
        if self.config:
            add_portmaster_entry = self.config.get("install.add_portmaster_entry", False)
            if add_portmaster_entry:
                portmaster_base_dir = self.config.get("install.portmaster_base_dir")
                if portmaster_base_dir:
                    return Path(portmaster_base_dir)
        
        if self.app_paths:
            return self.app_paths.games_dir
        
        # Fallback to current directory if no paths are available
        return Path.cwd()