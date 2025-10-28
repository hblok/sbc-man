"""
Unit Tests for Model Classes

Tests for Game, GameLibrary, ConfigManager, and DownloadManager.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.models.game import Game
from src.models.game_library import GameLibrary
from src.models.config_manager import ConfigManager


class TestGame(unittest.TestCase):
    """Test cases for Game model."""

    def test_game_initialization(self):
        """Test game initialization with required parameters."""
        game = Game(game_id="test-game", name="Test Game")
        
        self.assertEqual(game.id, "test-game")
        self.assertEqual(game.name, "Test Game")
        self.assertEqual(game.version, "1.0.0")
        self.assertEqual(game.description, "")
        self.assertFalse(game.installed)

    def test_game_to_dict(self):
        """Test game serialization to dictionary."""
        game = Game(
            game_id="test-game",
            name="Test Game",
            version="2.0.0",
            description="A test game",
            installed=True,
        )
        
        data = game.to_dict()
        
        self.assertEqual(data["id"], "test-game")
        self.assertEqual(data["name"], "Test Game")
        self.assertEqual(data["version"], "2.0.0")
        self.assertEqual(data["description"], "A test game")
        self.assertTrue(data["installed"])

    def test_game_from_dict(self):
        """Test game deserialization from dictionary."""
        data = {
            "id": "test-game",
            "name": "Test Game",
            "version": "3.0.0",
            "description": "A test game",
            "author": "Test Author",
            "installed": True,
        }
        
        game = Game.from_dict(data)
        
        self.assertEqual(game.id, "test-game")
        self.assertEqual(game.name, "Test Game")
        self.assertEqual(game.version, "3.0.0")
        self.assertEqual(game.author, "Test Author")
        self.assertTrue(game.installed)

    def test_game_custom_settings(self):
        """Test game with custom resolution and FPS."""
        game = Game(
            game_id="test-game",
            name="Test Game",
            custom_resolution=(1920, 1080),
            custom_fps=120,
        )
        
        self.assertEqual(game.custom_resolution, (1920, 1080))
        self.assertEqual(game.custom_fps, 120)


class TestGameLibrary(unittest.TestCase):
    """Test cases for GameLibrary."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.hw_config = {
            "paths": {
                "data": self.temp_dir,
            }
        }

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_library_initialization(self):
        """Test library initialization creates empty library."""
        library = GameLibrary(self.hw_config)
        
        self.assertEqual(len(library.games), 0)
        self.assertTrue(library.games_file.exists())

    def test_add_game(self):
        """Test adding a game to library."""
        library = GameLibrary(self.hw_config)
        game = Game(game_id="test-game", name="Test Game")
        
        library.add_game(game)
        
        self.assertEqual(len(library.games), 1)
        self.assertEqual(library.games[0].id, "test-game")

    def test_get_game(self):
        """Test retrieving a game by ID."""
        library = GameLibrary(self.hw_config)
        game = Game(game_id="test-game", name="Test Game")
        library.add_game(game)
        
        retrieved = library.get_game("test-game")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "test-game")

    def test_remove_game(self):
        """Test removing a game from library."""
        library = GameLibrary(self.hw_config)
        game = Game(game_id="test-game", name="Test Game")
        library.add_game(game)
        
        result = library.remove_game("test-game")
        
        self.assertTrue(result)
        self.assertEqual(len(library.games), 0)

    def test_get_installed_games(self):
        """Test filtering installed games."""
        library = GameLibrary(self.hw_config)
        game1 = Game(game_id="game1", name="Game 1", installed=True)
        game2 = Game(game_id="game2", name="Game 2", installed=False)
        library.add_game(game1)
        library.add_game(game2)
        
        installed = library.get_installed_games()
        
        self.assertEqual(len(installed), 1)
        self.assertEqual(installed[0].id, "game1")

    def test_save_and_load_games(self):
        """Test saving and loading games from file."""
        library = GameLibrary(self.hw_config)
        game = Game(game_id="test-game", name="Test Game", installed=True)
        library.add_game(game)
        library.save_games()
        
        # Create new library instance
        library2 = GameLibrary(self.hw_config)
        
        self.assertEqual(len(library2.games), 1)
        self.assertEqual(library2.games[0].id, "test-game")
        self.assertTrue(library2.games[0].installed)


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.hw_config = {
            "paths": {
                "data": self.temp_dir,
            },
            "display": {
                "resolution": [1280, 720],
                "fps_target": 60,
            },
        }

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_config_manager_initialization(self):
        """Test config manager initialization."""
        config = ConfigManager(self.hw_config)
        
        self.assertIsNotNone(config.hw_config)
        self.assertTrue(config.config_file.exists())

    def test_get_config_value(self):
        """Test getting configuration values."""
        config = ConfigManager(self.hw_config)
        
        resolution = config.get("display.resolution")
        
        self.assertEqual(resolution, [1280, 720])

    def test_get_with_default(self):
        """Test getting non-existent value with default."""
        config = ConfigManager(self.hw_config)
        
        value = config.get("nonexistent.key", "default_value")
        
        self.assertEqual(value, "default_value")

    def test_set_config_value(self):
        """Test setting configuration values."""
        config = ConfigManager(self.hw_config)
        
        config.set("display.fps_target", 120)
        
        self.assertEqual(config.get("display.fps_target"), 120)

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        config = ConfigManager(self.hw_config)
        config.set("custom.setting", "test_value")
        config.save()
        
        # Create new config manager instance
        config2 = ConfigManager(self.hw_config)
        
        self.assertEqual(config2.get("custom.setting"), "test_value")

    def test_nested_config_access(self):
        """Test accessing nested configuration values."""
        config = ConfigManager(self.hw_config)
        config.set("level1.level2.level3", "deep_value")
        
        value = config.get("level1.level2.level3")
        
        self.assertEqual(value, "deep_value")


if __name__ == "__main__":
    unittest.main()