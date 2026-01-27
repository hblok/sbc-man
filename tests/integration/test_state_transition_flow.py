# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Integration Tests for State Transition Flow
"""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import os
import shutil
import tempfile
import unittest

import pygame

from sbcman.core.state_manager import StateManager
from sbcman.path.paths import AppPaths
from sbcman.states.download_state import DownloadState
from sbcman.states.game_list_state import GameListState
from sbcman.states.menu_state import MenuState
from sbcman.states.settings_state import SettingsState


class TestStateTransitionFlow(unittest.TestCase):
    """Integration tests for state transition flow."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a mock screen
        self.mock_screen = Mock()
        
        # Create temporary directories for testing
        self.temp_data_dir = Path(tempfile.mkdtemp())
        self.temp_games_dir = Path(tempfile.mkdtemp())

        self.app_paths = AppPaths(self.temp_data_dir, self.temp_data_dir)
        
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

        self.state_manager = StateManager(
            screen=self.mock_screen,
            hw_config=self.hw_config,
            config=self.mock_config,
            game_library=self.mock_game_library,
            input_handler=self.mock_input_handler,
            app_paths=self.app_paths
        )

    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()
        
        shutil.rmtree(self.temp_data_dir)
        shutil.rmtree(self.temp_games_dir)

    # FIXME: Mock issue        
    def disabled_test_menu_to_game_list_transition(self):
        # Verify initial state is menu
        self.assertIsInstance(self.state_manager.current_state, MenuState)
        
        # Configure mock game library to return an empty list
        self.mock_game_library.get_available_games.return_value = []
        self.mock_game_library.games = []
        
        # Test changing state to game_list
        self.state_manager.change_state('game_list')
        self.assertIsInstance(self.state_manager.current_state, GameListState)

    def test_menu_to_download_transition(self):
        # Configure mock game library to return an empty list
        self.mock_game_library.get_available_games.return_value = []
        self.mock_game_library.get_enhanced_game_list.return_value = []
        
        # Test changing state to download
        self.state_manager.change_state('download')
        self.assertIsInstance(self.state_manager.current_state, DownloadState)

    def test_menu_to_settings_transition(self):
        # Test changing state to settings
        self.state_manager.change_state('settings')
        self.assertIsInstance(self.state_manager.current_state, SettingsState)

    # FIXME: Mock issue
    def disabled_test_state_stack_operations(self):
        # Verify initial state is menu
        self.assertIsInstance(self.state_manager.current_state, MenuState)
        
        # Configure mock game library to return an empty list
        self.mock_game_library.get_available_games.return_value = []
        self.mock_game_library.games = []
        
        # Save the initial state
        initial_state = self.state_manager.current_state
        
        # Manually push current state to stack (simulating what push_state would do before it calls change_state)
        self.state_manager.state_stack.append(initial_state)
        
        # Manually change to game list state without calling change_state (which would clear the stack)
        self.state_manager.current_state = self.state_manager.states['game_list']
        self.state_manager.current_state.on_enter(None)
        
        self.assertIsInstance(self.state_manager.current_state, GameListState)
        
        # Mock the on_exit method to prevent issues
        with patch.object(self.state_manager.current_state, 'on_exit') as mock_on_exit:
            mock_on_exit.return_value = None
            
            # Pop back to menu state
            self.state_manager.pop_state()
            self.assertIsInstance(self.state_manager.current_state, MenuState)


if __name__ == '__main__':
    unittest.main()
