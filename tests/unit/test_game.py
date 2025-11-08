"""
Unit Tests for Game Model

Tests for Game class.
"""

from unittest.mock import Mock, patch, MagicMock
import unittest

from src.models.game import Game


class TestGame(unittest.TestCase):

    def test_game_initialization(self):
        game = Game(game_id="test-game", name="Test Game")
        
        self.assertEqual(game.id, "test-game")
        self.assertEqual(game.name, "Test Game")
        self.assertEqual(game.version, "1.0.0")
        self.assertEqual(game.description, "")
        self.assertFalse(game.installed)

    def test_game_to_dict(self):
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
        game = Game(
            game_id="test-game",
            name="Test Game",
            custom_resolution=(1920, 1080),
            custom_fps=120,
        )
        
        self.assertEqual(game.custom_resolution, (1920, 1080))
        self.assertEqual(game.custom_fps, 120)
