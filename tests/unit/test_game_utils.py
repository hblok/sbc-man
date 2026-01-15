# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Game Utilities

Tests for protobuf game compatibility functions including creating,
converting, and manipulating game objects.
"""

import unittest
from unittest.mock import Mock

from sbcman.proto import game_pb2
from sbcman.services.game_utils import (
    create_game,
    game_to_dict,
    game_from_dict,
    get_custom_resolution,
    get_custom_fps,
)


class TestGameUtils(unittest.TestCase):
    """Test cases for game utility functions."""

    def test_create_game_basic(self):
        """Test creating a basic game."""
        game = create_game(
            game_id="test1",
            name="Test Game"
        )

        self.assertEqual(game.id, "test1")
        self.assertEqual(game.name, "Test Game")
        self.assertFalse(game.installed)
        self.assertEqual(game.entry_point, "main.py")

    def test_create_game_with_all_fields(self):
        """Test creating a game with all optional fields."""
        game = create_game(
            game_id="test2",
            name="Test Game 2",
            version="1.0.0",
            description="A test game",
            author="Test Author",
            install_path="/path/to/game",
            entry_point="game.py",
            installed=True,
            download_url="http://example.com/game.zip",
            custom_input_mappings={"key1": "value1", "key2": "value2"},
            custom_resolution=(1920, 1080),
            custom_fps=60
        )

        self.assertEqual(game.id, "test2")
        self.assertEqual(game.name, "Test Game 2")
        self.assertEqual(game.version, "1.0.0")
        self.assertEqual(game.description, "A test game")
        self.assertEqual(game.author, "Test Author")
        self.assertEqual(game.install_path, "/path/to/game")
        self.assertEqual(game.entry_point, "game.py")
        self.assertTrue(game.installed)
        self.assertEqual(game.download_url, "http://example.com/game.zip")
        
        # Check custom_input_mappings
        self.assertEqual(len(game.custom_input_mappings), 2)
        self.assertEqual(game.custom_input_mappings[0].key, "key1")
        self.assertEqual(game.custom_input_mappings[0].value, "value1")
        
        # Check custom_resolution
        self.assertEqual(game.custom_resolution.width, 1920)
        self.assertEqual(game.custom_resolution.height, 1080)
        
        # Check custom_fps
        self.assertEqual(game.custom_fps, 60)

    def test_create_game_empty_fields(self):
        """Test creating a game with empty optional fields."""
        game = create_game(
            game_id="test3",
            name="Test Game 3",
            version="",
            description="",
            author="",
            install_path="",
            download_url=""
        )

        self.assertEqual(game.id, "test3")
        self.assertEqual(game.name, "Test Game 3")
        self.assertEqual(game.version, "")
        self.assertEqual(game.description, "")
        self.assertEqual(game.author, "")
        self.assertEqual(game.install_path, "")
        self.assertEqual(game.download_url, "")

    def test_game_to_dict_basic(self):
        """Test converting game to dictionary."""
        game = create_game(
            game_id="test4",
            name="Test Game 4",
            version="1.0"
        )

        result = game_to_dict(game)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "test4")
        self.assertEqual(result["name"], "Test Game 4")
        self.assertEqual(result["version"], "1.0")
        self.assertEqual(result["installed"], False)

    def test_game_to_dict_with_mappings(self):
        """Test converting game with input mappings to dictionary."""
        game = create_game(
            game_id="test5",
            name="Test Game 5",
            custom_input_mappings={"up": "w", "down": "s"}
        )

        result = game_to_dict(game)

        self.assertEqual(result["custom_input_mappings"], {"up": "w", "down": "s"})

    def test_game_to_dict_with_resolution(self):
        """Test converting game with custom resolution to dictionary."""
        game = create_game(
            game_id="test6",
            name="Test Game 6",
            custom_resolution=(800, 600)
        )

        result = game_to_dict(game)

        self.assertEqual(result["custom_resolution"], (800, 600))

    def test_game_to_dict_without_resolution(self):
        """Test converting game without custom resolution to dictionary."""
        game = create_game(
            game_id="test7",
            name="Test Game 7"
        )

        result = game_to_dict(game)

        self.assertIsNone(result["custom_resolution"])

    def test_game_to_dict_with_fps(self):
        """Test converting game with custom FPS to dictionary."""
        game = create_game(
            game_id="test8",
            name="Test Game 8",
            custom_fps=30
        )

        result = game_to_dict(game)

        self.assertEqual(result["custom_fps"], 30)

    def test_game_to_dict_without_fps(self):
        """Test converting game without custom FPS to dictionary."""
        game = create_game(
            game_id="test9",
            name="Test Game 9"
        )

        result = game_to_dict(game)

        self.assertIsNone(result["custom_fps"])

    def test_game_from_dict_basic(self):
        """Test creating game from dictionary."""
        data = {
            "id": "test10",
            "name": "Test Game 10",
            "version": "2.0",
            "description": "Test",
            "author": "Tester",
            "install_path": "/path",
            "entry_point": "main.py",
            "installed": True,
            "download_url": "http://test.com"
        }

        game = game_from_dict(data)

        self.assertEqual(game.id, "test10")
        self.assertEqual(game.name, "Test Game 10")
        self.assertEqual(game.version, "2.0")
        self.assertEqual(game.description, "Test")
        self.assertEqual(game.author, "Tester")
        self.assertEqual(game.install_path, "/path")
        self.assertEqual(game.entry_point, "main.py")
        self.assertTrue(game.installed)
        self.assertEqual(game.download_url, "http://test.com")

    def test_game_from_dict_with_optional_fields(self):
        """Test creating game from dictionary with optional fields."""
        data = {
            "id": "test11",
            "name": "Test Game 11",
            "custom_input_mappings": {"key": "value"},
            "custom_resolution": [1280, 720],
            "custom_fps": 60
        }

        game = game_from_dict(data)

        self.assertEqual(game.id, "test11")
        self.assertEqual(len(game.custom_input_mappings), 1)
        self.assertEqual(game.custom_resolution.width, 1280)
        self.assertEqual(game.custom_resolution.height, 720)
        self.assertEqual(game.custom_fps, 60)

    def test_game_from_dict_with_resolution_tuple(self):
        """Test creating game from dictionary with resolution as tuple."""
        data = {
            "id": "test12",
            "name": "Test Game 12",
            "custom_resolution": (1280, 720)
        }

        game = game_from_dict(data)

        self.assertEqual(game.custom_resolution.width, 1280)
        self.assertEqual(game.custom_resolution.height, 720)

    def test_game_from_dict_defaults(self):
        """Test creating game from dictionary with default values."""
        data = {
            "id": "test13",
            "name": "Test Game 13"
        }

        game = game_from_dict(data)

        self.assertEqual(game.version, "")
        self.assertEqual(game.description, "")
        self.assertEqual(game.author, "")
        self.assertEqual(game.install_path, "")
        self.assertEqual(game.entry_point, "main.py")
        self.assertFalse(game.installed)
        self.assertEqual(game.download_url, "")

    def test_get_custom_resolution_with_resolution(self):
        """Test getting custom resolution when it exists."""
        game = create_game(
            game_id="test14",
            name="Test Game 14",
            custom_resolution=(1920, 1080)
        )

        result = get_custom_resolution(game)

        self.assertEqual(result, (1920, 1080))

    def test_get_custom_resolution_without_resolution(self):
        """Test getting custom resolution when it doesn't exist."""
        game = create_game(
            game_id="test15",
            name="Test Game 15"
        )

        result = get_custom_resolution(game)

        self.assertIsNone(result)

    def test_get_custom_fps_with_fps(self):
        """Test getting custom FPS when it exists."""
        game = create_game(
            game_id="test16",
            name="Test Game 16",
            custom_fps=45
        )

        result = get_custom_fps(game)

        self.assertEqual(result, 45)

    def test_get_custom_fps_without_fps(self):
        """Test getting custom FPS when it doesn't exist."""
        game = create_game(
            game_id="test17",
            name="Test Game 17"
        )

        result = get_custom_fps(game)

        self.assertIsNone(result)

    def test_get_custom_fps_zero_value(self):
        """Test getting custom FPS when it's zero (default)."""
        game = create_game(
            game_id="test18",
            name="Test Game 18",
            custom_fps=0
        )

        result = get_custom_fps(game)

        self.assertIsNone(result)

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion from dict to game and back."""
        original_data = {
            "id": "test19",
            "name": "Test Game 19",
            "version": "3.0",
            "description": "Roundtrip test",
            "author": "Roundtrip Author",
            "install_path": "/roundtrip/path",
            "entry_point": "roundtrip.py",
            "installed": True,
            "download_url": "http://roundtrip.com",
            "custom_input_mappings": {"action": "space"},
            "custom_resolution": (1600, 900),
            "custom_fps": 75
        }

        # Convert to game
        game = game_from_dict(original_data)

        # Convert back to dict
        result_data = game_to_dict(game)

        # Verify all fields match
        self.assertEqual(result_data["id"], original_data["id"])
        self.assertEqual(result_data["name"], original_data["name"])
        self.assertEqual(result_data["version"], original_data["version"])
        self.assertEqual(result_data["description"], original_data["description"])
        self.assertEqual(result_data["author"], original_data["author"])
        self.assertEqual(result_data["install_path"], original_data["install_path"])
        self.assertEqual(result_data["entry_point"], original_data["entry_point"])
        self.assertEqual(result_data["installed"], original_data["installed"])
        self.assertEqual(result_data["download_url"], original_data["download_url"])
        self.assertEqual(result_data["custom_input_mappings"], original_data["custom_input_mappings"])
        self.assertEqual(result_data["custom_resolution"], original_data["custom_resolution"])
        self.assertEqual(result_data["custom_fps"], original_data["custom_fps"])


if __name__ == '__main__':
    unittest.main()