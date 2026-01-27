# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Game Library Module
Manages the collection of games with CRUD operations and persistence.
"""

import json
import logging
import pathlib
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any

from google.protobuf import json_format

from sbcman.proto import game_pb2
from .game_utils import game_to_dict, game_from_dict
from .game_list_entry import GameListEntry, GameStatus
from sbcman.path.paths import AppPaths
from sbcman.services import network


logger = logging.getLogger(__name__)


class GameLibrary:
    """
    Game library manager.
    
    Manages the collection of games, providing CRUD operations
    and persistence to JSON file.
    """

    def __init__(self, hw_config: Dict[str, Any], app_paths: AppPaths):
        self.hw_config = hw_config
        self.app_paths = app_paths
        self.games: List[game_pb2.Game] = []
        
        self.local_games_file = app_paths.local_games_file
        self.games_file = self.local_games_file  # For test compatibility
        
        self.local_games = self.load_games(self.local_games_file)
        self.games = self.local_games.copy()  # For test compatibility

        if self.local_games:
            logger.info(f"GameLibrary initialized with {len(self.local_games)} games")

    def load_games(self, games_file: pathlib.Path) -> list[game_pb2.Game]:
        """
        Load games from JSON file.

        Args:
            games_file: Path to the games JSON file.

        Returns:
            List of Game objects loaded from the file, or
            an empty games file if it doesn't exist.
        """
        if not games_file.exists():
            logger.info("Games file not found, creating empty library")
            return []

        try:
            with open(games_file, "r") as f:
                data = json.load(f)

            games = [game_from_dict(game_data) for game_data in data]
            logger.info(f"Loaded {len(games)} games from {games_file}")
            return games

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in games file: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load games: {e}")
            return []

    def _save_games_to_file(self, games: list[game_pb2.Game], games_file: pathlib.Path) -> None:
        """ Save games to JSON file.

        Args:
            games: List of Game objects to save.
            games_file: Path to the games JSON file.
        """
        try:
            logger.info(f"Save list of games to {games_file}")
            games_file.parent.mkdir(parents=True, exist_ok=True)

            # TODO: Use protobuf json serialization here
            data = [game_to_dict(game) for game in games]

            with open(games_file, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(games)} games to {games_file}")

        except Exception as e:
            logger.error(f"Failed to save games: {e}")
    
    def save_games(self) -> None:
        """Save current games to the default games file."""
        self._save_games_to_file(self.local_games, self.local_games_file)
        
    def add_game(self, game: game_pb2.Game) -> None:
        """
        Add a game to the library.
        
        Args:
            game: Game instance to add
        """
        # Check if game already exists
        existing = self.get_game(game.id)
        if existing:
            logger.warning(f"Game {game.id} already exists, updating")
            self.remove_game(game.id)
        
        self.local_games.append(game)
        self.games = self.local_games.copy()  # Keep games in sync
        logger.info(f"Added game: {game.name}")

    def remove_game(self, game_id: str) -> bool:
        """
        Remove a game from the library.
        
        Args:
            game_id: ID of game to remove
            
        Returns:
            bool: True if game was removed, False if not found
        """
        for i, game in enumerate(self.local_games):
            if game.id == game_id:
                removed = self.local_games.pop(i)
                self.games = self.local_games.copy()  # Keep games in sync
                logger.info(f"Removed game: {removed.name}")
                return True
        
        logger.warning(f"Game {game_id} not found for removal")
        return False

    def get_game(self, game_id: str) -> Optional[game_pb2.Game]:
        """
        Get a game by ID.
        
        Args:
            game_id: ID of game to retrieve
            
        Returns:
            Game: Game instance if found, None otherwise
        """
        for game in self.local_games:
            if game.id == game_id:
                return game
        return None

    def get_all_games(self) -> List[game_pb2.Game]:
        """
        Get all games in the library.
        
        Returns:
            list: List of all Game instances
        """
        return self.local_games.copy()

    def get_installed_games(self) -> List[game_pb2.Game]:
        """
        Get all installed games.
        
        Returns:
            list: List of installed Game instances
        """
        return [game for game in self.local_games if game.installed]

    def get_available_games(self) -> List[game_pb2.Game]:
        """ Get all available (not installed) games. """

        # TODO: Change to Max Games 
        # https://hblok.github.io/sbc-man/games.json

        net = network.NetworkService()
        url = "https://hblok.github.io/sbc-man/games.json"
        tmp_games_json = pathlib.Path(tempfile.mkdtemp()) / "games.json"

        if net.check_url(url):
            net.download_file(url, tmp_games_json)

            with open(tmp_games_json) as f:
                list_obj = json.load(f)
                return [json_format.ParseDict(g, game_pb2.Game()) for g in list_obj]

        # TODO: Keep or remove?
        return [game for game in self.local_games if not game.installed]

    def update_game(self, game: game_pb2.Game) -> bool:
        """
        Update an existing game in the library.
        
        Args:
            game: Game instance with updated data
            
        Returns:
            bool: True if game was updated, False if not found
        """
        for i, existing_game in enumerate(self.local_games):
            if existing_game.id == game.id:
                self.local_games[i] = game
                logger.info(f"Updated game: {game.name}")
                return True
        
        logger.warning(f"Game {game.id} not found for update")
        return False

    def get_game_status(self, game: game_pb2.Game) -> GameStatus:
        """Check installation status of a game.
        
        Args:
            game: Game object to check
            
        Returns:
            GameStatus: Installation status of the game
        """
        installed_game = self.get_game(game.id)
        
        if not installed_game or not installed_game.installed:
            return GameStatus.NOT_INSTALLED
        
        # Check if remote version is newer than local version
        if self._is_newer_version(installed_game.version, game.version):
            return GameStatus.UPDATE_AVAILABLE
        
        return GameStatus.INSTALLED
    
    def _is_newer_version(self, local_version: str, remote_version: str) -> bool:
        """Compare two version strings to determine if remote is newer.
        
        Args:
            local_version: Local installed version string
            remote_version: Remote available version string
            
        Returns:
            bool: True if remote version is newer
        """
        try:
            local_parts = [int(x) for x in local_version.split('.')]
            remote_parts = [int(x) for x in remote_version.split('.')]
            
            for i in range(max(len(local_parts), len(remote_parts))):
                local_val = local_parts[i] if i < len(local_parts) else 0
                remote_val = remote_parts[i] if i < len(remote_parts) else 0
                
                if remote_val > local_val:
                    return True
                elif remote_val < local_val:
                    return False
            
            return False
        except (ValueError, AttributeError):
            logger.warning(f"Failed to compare versions: {local_version} vs {remote_version}")
            return False
    
    def get_game_icon_path(self, game: game_pb2.Game) -> Optional[pathlib.Path]:
        """Get local path to game icon.
        
        Args:
            game: Game object
            
        Returns:
            Path: Local path to icon file, or None if not found
        """
        if not game.icon:
            return None
        
        icon_path = self.app_paths.games_dir / game.id / game.icon
        
        if icon_path.exists():
            return icon_path
        
        return None
    
    def get_game_icon_url(self, game: game_pb2.Game) -> str:
        """Get URL to download game icon.
        
        Args:
            game: Game object
            
        Returns:
            str: URL to icon file or None
        """
        if not game.icon:
            return None
        
        # Construct icon URL based on download_url base
        if game.download_url:
            base_url = game.download_url.rsplit('/', 1)[0]
            return f"{base_url}/{game.icon}"
        
        return None
    
    def get_enhanced_game_list(self) -> list[GameListEntry]:
        """Get list of games with enhanced information.
        
        Returns:
            List of GameListEntry objects with status and icon information
        """
        available_games = self.get_available_games()
        enhanced_list = []
        
        for game in available_games:
            status = self.get_game_status(game)
            icon_path = self.get_game_icon_path(game)
            icon_url = self.get_game_icon_url(game)
            
            local_version = None
            installed_game = self.get_game(game.id)
            if installed_game:
                local_version = installed_game.version
            
            entry = GameListEntry(
                game=game,
                status=status,
                icon_path=icon_path,
                icon_url=icon_url,
                local_version=local_version
            )
            enhanced_list.append(entry)
        
        return enhanced_list
