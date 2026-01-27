# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for GameListEntry module."""

import unittest
from pathlib import Path

from sbcman.proto import game_pb2
from sbcman.services.game_list_entry import GameListEntry, GameStatus


class GameListEntryTestCase(unittest.TestCase):
    """Test cases for GameListEntry class."""

    def test_entry_creation(self):
        """Test creating a game list entry."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.version = "1.0.0"
        
        entry = GameListEntry(game)
        
        self.assertEqual(entry.id, "test-game")
        self.assertEqual(entry.name, "Test Game")
        self.assertEqual(entry.version, "1.0.0")
        self.assertEqual(entry.status, GameStatus.NOT_INSTALLED)

    def test_installed_status(self):
        """Test entry with installed status."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.version = "1.0.0"
        
        entry = GameListEntry(game, status=GameStatus.INSTALLED)
        
        self.assertTrue(entry.is_installed)
        self.assertFalse(entry.has_update)

    def test_update_available_status(self):
        """Test entry with update available status."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.version = "2.0.0"
        
        entry = GameListEntry(
            game, 
            status=GameStatus.UPDATE_AVAILABLE,
            local_version="1.0.0"
        )
        
        self.assertTrue(entry.is_installed)
        self.assertTrue(entry.has_update)

    def test_display_name_not_installed(self):
        """Test display name for not installed game."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.version = "1.0.0"
        
        entry = GameListEntry(game)
        
        self.assertEqual(entry.display_name, "Test Game (v1.0.0)")

    def test_display_name_installed(self):
        """Test display name for installed game."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.version = "1.0.0"
        
        entry = GameListEntry(
            game, 
            status=GameStatus.INSTALLED,
            local_version="1.0.0"
        )
        
        self.assertEqual(entry.display_name, "Test Game (v1.0.0)")

    def test_display_name_with_update(self):
        """Test display name for game with update available."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.version = "2.0.0"
        
        entry = GameListEntry(
            game, 
            status=GameStatus.UPDATE_AVAILABLE,
            local_version="1.0.0"
        )
        
        self.assertEqual(entry.display_name, "Test Game (v1.0.0) [Update to v2.0.0]")