"""
Game Library Module

Manages the collection of games with CRUD operations and persistence.

Based on: docs/code/class_models_game_library.txt
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .game import Game

logger = logging.getLogger(__name__)


class GameLibrary:
    """
    Game library manager.
    
    Manages the collection of games, providing CRUD operations
    and persistence to JSON file.
    """

    def __init__(self, hw_config: Dict[str, Any]):
        """
        Initialize game library.
        
        Args:
            hw_config: Hardware configuration dictionary
        """
        self.hw_config = hw_config
        self.games: List[Game] = []
        
        # Determine games file path
        paths = hw_config.get("paths", {})
        data_dir = Path(paths.get("data", "~/.local/share/sbc-man")).expanduser()
        self.games_file = data_dir / "games.json"
        
        # Load games from file
        self.load_games()
        
        logger.info(f"GameLibrary initialized with {len(self.games)} games")

    def load_games(self) -> None:
        """
        Load games from JSON file.
        
        Creates an empty games file if it doesn't exist.
        """
        if not self.games_file.exists():
            logger.info("Games file not found, creating empty library")
            self.games = []
            self.save_games()
            return
        
        try:
            with open(self.games_file, "r") as f:
                data = json.load(f)
            
            self.games = [Game.from_dict(game_data) for game_data in data]
            logger.info(f"Loaded {len(self.games)} games from {self.games_file}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in games file: {e}")
            self.games = []
        except Exception as e:
            logger.error(f"Failed to load games: {e}")
            self.games = []

    def save_games(self) -> None:
        """
        Save games to JSON file.
        
        Persists the current game library to disk.
        """
        try:
            # Ensure directory exists
            self.games_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize games
            data = [game.to_dict() for game in self.games]
            
            # Write to file
            with open(self.games_file, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.games)} games to {self.games_file}")
            
        except Exception as e:
            logger.error(f"Failed to save games: {e}")

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
        
        self.games.append(game)
        logger.info(f"Added game: {game.name}")

    def remove_game(self, game_id: str) -> bool:
        """
        Remove a game from the library.
        
        Args:
            game_id: ID of game to remove
            
        Returns:
            bool: True if game was removed, False if not found
        """
        for i, game in enumerate(self.games):
            if game.id == game_id:
                removed = self.games.pop(i)
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
        for game in self.games:
            if game.id == game_id:
                return game
        return None

    def get_all_games(self) -> List[Game]:
        """
        Get all games in the library.
        
        Returns:
            list: List of all Game instances
        """
        return self.games.copy()

    def get_installed_games(self) -> List[Game]:
        """
        Get all installed games.
        
        Returns:
            list: List of installed Game instances
        """
        return [game for game in self.games if game.installed]

    def get_available_games(self) -> List[Game]:
        """
        Get all available (not installed) games.
        
        Returns:
            list: List of available Game instances
        """
        return [game for game in self.games if not game.installed]

    def update_game(self, game: Game) -> bool:
        """
        Update an existing game in the library.
        
        Args:
            game: Game instance with updated data
            
        Returns:
            bool: True if game was updated, False if not found
        """
        for i, existing_game in enumerate(self.games):
            if existing_game.id == game.id:
                self.games[i] = game
                logger.info(f"Updated game: {game.name}")
                return True
        
        logger.warning(f"Game {game.id} not found for update")
        return False