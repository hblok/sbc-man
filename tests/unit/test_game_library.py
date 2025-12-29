# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for GameLibrary Model

Tests for GameLibrary class.
"""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import shutil
import tempfile
import unittest
from sbcman.hardware.paths import AppPaths

from sbcman.models.game_library import GameLibrary
from sbcman.models.game import Game


class TestGameLibrary(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hw_config = {
            "paths": {
                "data": self.temp_dir,
            }
        }

        self.library = GameLibrary(self.hw_config, AppPaths())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_library_initialization(self):
        self.library.games = []  # Ensure clean state
        self.assertEqual(len(self.library.games), 0)

    def test_add_game(self):
        game = Game(game_id="test-game", name="Test Game")
        
        self.library.add_game(game)
        
        self.assertEqual(len(self.library.games), 1)
        self.assertEqual(self.library.games[0].id, "test-game")

    def test_get_game(self):
        game = Game(game_id="test-game", name="Test Game")
        self.library.add_game(game)
        
        retrieved = self.library.get_game("test-game")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "test-game")

    def test_remove_game(self):
        game = Game(game_id="test-game", name="Test Game")
        self.library.add_game(game)
        
        result = self.library.remove_game("test-game")
        
        self.assertTrue(result)
        self.assertEqual(len(self.library.games), 0)

    def test_get_installed_games(self):
        self.library.games = []  # Ensure clean state
        game1 = Game(game_id="game1", name="Game 1", installed=True)
        game2 = Game(game_id="game2", name="Game 2", installed=False)
        self.library.add_game(game1)
        self.library.add_game(game2)
        
        installed = self.library.get_installed_games()
        
        self.assertEqual(len(installed), 1)
        self.assertEqual(installed[0].id, "game1")

    def test_save_and_load_games(self):
        game = Game(game_id="test-game", name="Test Game", installed=True)
        self.library.add_game(game)
        self.library.save_games()
        
        library2 = GameLibrary(self.hw_config, AppPaths())
        library2.games = library2.load_games(library2.games_file)
        
        self.assertEqual(len(library2.games), 1)
        self.assertEqual(library2.games[0].id, "test-game")
        self.assertTrue(library2.games[0].installed)