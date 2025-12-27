"""
Integration Tests for Game Launch Flow
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from sbcman.states.game_list_state import GameListState
from sbcman.states.playing_state import PlayingState
from sbcman.models.game import Game


class TestGameLaunchFlow(unittest.TestCase):
    """Integration tests for game launch flow."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a mock state manager
        self.mock_state_manager = Mock()
        
        # Create temporary directories
        self.temp_data_dir = tempfile.mkdtemp()
        self.temp_games_dir = tempfile.mkdtemp()
        
        # Create a mock hardware config
        self.hw_config = {
            "paths": {
                "data": self.temp_data_dir,
                "games": self.temp_games_dir,
            },
            "display": {
                "resolution": [1280, 720],
                "fps_target": 60,
            }
        }
        
        # Create a mock game library
        self.mock_game_library = Mock()
        
        # Create a mock input handler
        self.mock_input_handler = Mock()

    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()
        
        # Clean up temporary directories
        import shutil
        shutil.rmtree(self.temp_data_dir)
        shutil.rmtree(self.temp_games_dir)

    def test_game_list_state_initialization(self):
        """Test game list state initialization and game loading."""
        # Create test games
        test_games = [
            Game(
                game_id="test-game-1",
                name="Test Game 1",
                installed=True,
                install_path="/tmp/games/test-game-1",
                entry_point="main.py"
            ),
            Game(
                game_id="test-game-2",
                name="Test Game 2",
                installed=False,
                install_path="/tmp/games/test-game-2",
                entry_point="game.py",
                download_url="https://example.com/test-game-2.zip"
            ),
        ]
        
        # Configure mock game library to return test games
        self.mock_game_library.get_all_games.return_value = test_games
        
        # Create game list state
        game_list_state = GameListState(self.mock_state_manager)
        game_list_state.hw_config = self.hw_config
        game_list_state.game_library = self.mock_game_library
        game_list_state.input_handler = self.mock_input_handler
        
        # Enter the game list state
        game_list_state.on_enter(None)
        
        # Verify games were loaded
        self.assertEqual(len(game_list_state.games), 2)
        self.assertEqual(game_list_state.selected_index, 0)

    def test_game_selection_navigation(self):
        """Test game selection navigation in game list state."""
        # Create test games
        test_games = [
            Game(
                game_id="test-game-1",
                name="Test Game 1",
                installed=True,
                install_path="/tmp/games/test-game-1",
                entry_point="main.py"
            ),
            Game(
                game_id="test-game-2",
                name="Test Game 2",
                installed=True,
                install_path="/tmp/games/test-game-2",
                entry_point="game.py"
            ),
        ]
        
        # Configure mock game library to return test games
        self.mock_game_library.get_all_games.return_value = test_games
        
        # Create game list state
        game_list_state = GameListState(self.mock_state_manager)
        game_list_state.hw_config = self.hw_config
        game_list_state.game_library = self.mock_game_library
        game_list_state.input_handler = self.mock_input_handler
        
        # Enter the game list state
        game_list_state.on_enter(None)
        
        # Verify initial selection
        self.assertEqual(game_list_state.selected_index, 0)
        
        # Mock input handler to simulate down navigation
        with patch.object(self.mock_input_handler, 'is_action_pressed') as mock_action:
            mock_action.side_effect = lambda action, events: action == "down"
            
            mock_events = [Mock()]
            game_list_state.handle_events(mock_events)
            
            # Verify selection moved
            self.assertEqual(game_list_state.selected_index, 1)

    def test_playing_state_initialization(self):
        """Test playing state initialization."""
        # Create playing state
        playing_state = PlayingState(self.mock_state_manager)
        playing_state.hw_config = self.hw_config
        playing_state.game_library = self.mock_game_library
        playing_state.input_handler = self.mock_input_handler
        
        # Enter the playing state
        playing_state.on_enter(None)
        
        # Verify state was initialized
        self.assertTrue(playing_state.game_running)
        self.assertEqual(playing_state.message, "Game would be launched here")


if __name__ == '__main__':
    unittest.main()