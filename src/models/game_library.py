"""
Game Library Module
Manages the collection of games with CRUD operations and persistence.
"""

import json
import logging
import pathlib
from pathlib import Path
from typing import List, Optional, Dict, Any

from .game import Game
from ..hardware.paths import AppPaths


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
        self.games: List[Game] = []
        
        self.local_games_file = app_paths.local_games_file
        self.all_games_file = app_paths.all_games_file
        
        self.local_games = self.load_games(self.local_games_file)
        self.all_games = self.load_games(self.all_games_file)

        if self.local_games:
            logger.info(f"GameLibrary initialized with {len(self.local_games)} games")

    def load_games(self, games_file: pathlib.Path) -> list[Game]:
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

            games = [Game.from_dict(game_data) for game_data in data]
            logger.info(f"Loaded {len(games)} games from {games_file}")
            return games

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in games file: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load games: {e}")
            return []

    def _save_games_to_file(self, games: list[Game], games_file: pathlib.Path) -> None:
        """ Save games to JSON file.

        Args:
            games: List of Game objects to save.
            games_file: Path to the games JSON file.
        """
        try:
            games_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [game.to_dict() for game in games]

            with open(games_file, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(games)} games to {games_file}")

        except Exception as e:
            logger.error(f"Failed to save games: {e}")
    
    def save_games(self) -> None:
        """Save current games to the default games file."""
        self._save_games_to_file(self.local_games, self.local_games_file)
        
    def add_game(self, game: Game) -> None:
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
                logger.info(f"Removed game: {removed.name}")
                return True
        
        logger.warning(f"Game {game_id} not found for removal")
        return False

    def get_game(self, game_id: str) -> Optional[Game]:
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

    def get_all_games(self) -> List[Game]:
        """
        Get all games in the library.
        
        Returns:
            list: List of all Game instances
        """
        return self.local_games.copy()

    def get_installed_games(self) -> List[Game]:
        """
        Get all installed games.
        
        Returns:
            list: List of installed Game instances
        """
        return [game for game in self.local_games if game.installed]

    def get_available_games(self) -> List[Game]:
        """ Get all available (not installed) games. """
        # TODO: Lazy-download list of games
        # https://github.com/hblok/max_blocks/blob/main/LICENSE
        # TODO: Setup access token
        return [game for game in self.local_games if not game.installed]

    def update_game(self, game: Game) -> bool:
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
