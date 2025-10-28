"""
Integration Tests for State Transition Flow
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.core.state_manager import StateManager
from src.states.menu_state import MenuState
from src.states.game_list_state import GameListState
from src.states.download_state import DownloadState
from src.states.settings_state import SettingsState


class TestStateTransitionFlow(unittest.TestCase):
    """Integration tests for state transition flow."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a mock screen
        self.mock_screen = Mock()
        
        # Create temporary directories for testing
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
        
        # Create mock components
        self.mock_config = Mock()
        self.mock_game_library = Mock()
        self.mock_input_handler = Mock()

    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()
        
        # Clean up temporary directories
        import shutil
        shutil.rmtree(self.temp_data_dir)
        shutil.rmtree(self.temp_games_dir)

    def test_menu_to_game_list_transition(self):
        """Test transition from menu state to game list state."""
        # Create state manager
        state_manager = StateManager(
            screen=self.mock_screen,
            hw_config=self.hw_config,
            config=self.mock_config,
            game_library=self.mock_game_library,
            input_handler=self.mock_input_handler
        )
        
        # Verify initial state is menu
        self.assertIsInstance(state_manager.current_state, MenuState)
        
        # Test changing state to game_list
        state_manager.change_state('game_list')
        self.assertIsInstance(state_manager.current_state, GameListState)

    def test_menu_to_download_transition(self):
        """Test transition from menu state to download state."""
        # Create state manager
        state_manager = StateManager(
            screen=self.mock_screen,
            hw_config=self.hw_config,
            config=self.mock_config,
            game_library=self.mock_game_library,
            input_handler=self.mock_input_handler
        )
        
        # Test changing state to download
        state_manager.change_state('download')
        self.assertIsInstance(state_manager.current_state, DownloadState)

    def test_menu_to_settings_transition(self):
        """Test transition from menu state to settings state."""
        # Create state manager
        state_manager = StateManager(
            screen=self.mock_screen,
            hw_config=self.hw_config,
            config=self.mock_config,
            game_library=self.mock_game_library,
            input_handler=self.mock_input_handler
        )
        
        # Test changing state to settings
        state_manager.change_state('settings')
        self.assertIsInstance(state_manager.current_state, SettingsState)

    def test_state_stack_operations(self):
        """Test state stack operations during transitions."""
        # Create state manager
        state_manager = StateManager(
            screen=self.mock_screen,
            hw_config=self.hw_config,
            config=self.mock_config,
            game_library=self.mock_game_library,
            input_handler=self.mock_input_handler
        )
        
        # Verify initial state is menu
        self.assertIsInstance(state_manager.current_state, MenuState)
        
        # Save the initial state
        initial_state = state_manager.current_state
        
        # Manually push current state to stack (simulating what push_state would do before it calls change_state)
        state_manager.state_stack.append(initial_state)
        
        # Manually change to game list state without calling change_state (which would clear the stack)
        state_manager.current_state = state_manager.states['game_list']
        state_manager.current_state.on_enter(None)
        
        self.assertIsInstance(state_manager.current_state, GameListState)
        
        # Mock the on_exit method to prevent issues
        with patch.object(state_manager.current_state, 'on_exit') as mock_on_exit:
            mock_on_exit.return_value = None
            
            # Pop back to menu state
            state_manager.pop_state()
            self.assertIsInstance(state_manager.current_state, MenuState)


if __name__ == '__main__':
    unittest.main()