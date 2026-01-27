# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for enhanced GameLibrary functionality."""

import unittest
import pathlib
import tempfile

from sbcman.proto import game_pb2
from sbcman.services.game_library import GameLibrary
from sbcman.services.game_list_entry import GameStatus
from sbcman.path.paths import AppPaths


class GameLibraryEnhancedTestCase(unittest.TestCase):
    """Test cases for enhanced GameLibrary methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        base_dir = pathlib.Path(self.temp_dir)
        
        self.app_paths = AppPaths(base_dir=base_dir)
        
        self.hw_config = {
            "screen_width": 800,
            "screen_height": 600
        }
        
        self.game_library = GameLibrary(self.hw_config, self.app_paths)
        
        # Add a local game
        local_game = game_pb2.Game()
        local_game.id = "game1"
        local_game.name = "Local Game"
        local_game.version = "1.0.0"
        local_game.installed = True
        local_game.icon = "icon.png"
        
        self.game_library.add_game(local_game)
        self.game_library.save_games()

    def test_get_game_status_installed(self):
        """Test getting status for installed game."""
        remote_game = game_pb2.Game()
        remote_game.id = "game1"
        remote_game.name = "Local Game"
        remote_game.version = "1.0.0"
        
        status = self.game_library.get_game_status(remote_game)
        
        self.assertEqual(status, GameStatus.INSTALLED)

    def test_get_game_status_not_installed(self):
        """Test getting status for not installed game."""
        remote_game = game_pb2.Game()
        remote_game.id = "game2"
        remote_game.name = "Remote Game"
        remote_game.version = "1.0.0"
        
        status = self.game_library.get_game_status(remote_game)
        
        self.assertEqual(status, GameStatus.NOT_INSTALLED)

    def test_get_game_status_update_available(self):
        """Test getting status for game with update available."""
        remote_game = game_pb2.Game()
        remote_game.id = "game1"
        remote_game.name = "Local Game"
        remote_game.version = "2.0.0"
        
        status = self.game_library.get_game_status(remote_game)
        
        self.assertEqual(status, GameStatus.UPDATE_AVAILABLE)

    def test_is_newer_version(self):
        """Test version comparison logic."""
        self.assertTrue(self.game_library._is_newer_version("1.0.0", "2.0.0"))
        self.assertTrue(self.game_library._is_newer_version("1.0.0", "1.1.0"))
        self.assertTrue(self.game_library._is_newer_version("1.0.0", "1.0.1"))
        self.assertFalse(self.game_library._is_newer_version("2.0.0", "1.0.0"))
        self.assertFalse(self.game_library._is_newer_version("1.0.0", "1.0.0"))

    def test_get_game_icon_path(self):
        """Test getting local icon path."""
        # Create icon file
        games_dir = self.app_paths.games_dir / "game1"
        games_dir.mkdir(parents=True, exist_ok=True)
        icon_file = games_dir / "icon.png"
        icon_file.write_text("fake icon")
        
        game = game_pb2.Game()
        game.id = "game1"
        game.icon = "icon.png"
        
        icon_path = self.game_library.get_game_icon_path(game)
        
        self.assertEqual(icon_path, icon_file)

    def test_get_game_icon_path_missing(self):
        """Test getting icon path when icon doesn't exist."""
        game = game_pb2.Game()
        game.id = "game2"
        game.icon = "icon.png"
        
        icon_path = self.game_library.get_game_icon_path(game)
        
        self.assertIsNone(icon_path)