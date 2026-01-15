# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for State Manager

Tests for the state machine pattern implementation including state transitions,
lifecycle management, and state stack operations for overlays.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame

from sbcman.core.state_manager import StateManager


class TestStateManager(unittest.TestCase):
    """Test cases for StateManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.screen = Mock()
        self.hw_config = {'detected_device': 'test', 'detected_os': 'test'}
        self.config = Mock()
        self.game_library = Mock()
        self.input_handler = Mock()
        self.app_paths = Mock()

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def disable_test_initialization(self, mock_update_state, mock_playing_state, 
                          mock_settings_state, mock_download_state,
                          mock_game_list_state, mock_menu_state):
        """Test state manager initialization."""
        # Setup mock state instances
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        mock_game_list_instance = Mock()
        mock_game_list_state.return_value = mock_game_list_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Verify attributes
        self.assertEqual(state_manager.screen, self.screen)
        self.assertEqual(state_manager.hw_config, self.hw_config)
        self.assertEqual(state_manager.config, self.config)
        self.assertEqual(state_manager.game_library, self.game_library)
        self.assertEqual(state_manager.input_handler, self.input_handler)
        self.assertEqual(state_manager.app_paths, self.app_paths)

        # Verify all states were created
        self.assertEqual(len(state_manager.states), 6)
        self.assertIn('menu', state_manager.states)
        self.assertIn('game_list', state_manager.states)
        self.assertIn('download', state_manager.states)
        self.assertIn('settings', state_manager.states)
        self.assertIn('playing', state_manager.states)
        self.assertIn('update', state_manager.states)

        # Verify initial state is menu
        self.assertEqual(state_manager.current_state, mock_menu_instance)

        # Verify initial state's on_enter was called
        mock_menu_instance.on_enter.assert_called_once_with(None)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def disable_test_change_state(self, mock_update_state, mock_playing_state,
                         mock_settings_state, mock_download_state,
                         mock_game_list_state, mock_menu_state):
        """Test state transitions."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        mock_game_list_instance = Mock()
        mock_game_list_state.return_value = mock_game_list_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Change to game_list state
        state_manager.change_state('game_list')

        # Verify current state changed
        self.assertEqual(state_manager.current_state, mock_game_list_instance)

        # Verify previous state's on_exit was called
        mock_menu_instance.on_exit.assert_called_once()

        # Verify new state's on_enter was called with previous state
        mock_game_list_instance.on_enter.assert_called_once_with(mock_menu_instance)

        # Verify state stack was cleared
        self.assertEqual(len(state_manager.state_stack), 0)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def disable_test_change_state_invalid(self, mock_update_state, mock_playing_state,
                                  mock_settings_state, mock_download_state,
                                  mock_game_list_state, mock_menu_state):
        """Test changing to invalid state raises error."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Try to change to invalid state
        with self.assertRaises(KeyError):
            state_manager.change_state('invalid_state')

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def disable_test_push_state(self, mock_update_state, mock_playing_state,
                       mock_settings_state, mock_download_state,
                       mock_game_list_state, mock_menu_state):
        """Test pushing state onto stack."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        mock_settings_instance = Mock()
        mock_settings_state.return_value = mock_settings_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Push settings state
        state_manager.push_state('settings')

        # Verify current state changed
        self.assertEqual(state_manager.current_state, mock_settings_instance)

        # Verify previous state was pushed to stack
        self.assertEqual(len(state_manager.state_stack), 1)
        self.assertEqual(state_manager.state_stack[0], mock_menu_instance)

        # Verify new state's on_enter was called
        mock_settings_instance.on_enter.assert_called_once_with(mock_menu_instance)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def disable_test_pop_state(self, mock_update_state, mock_playing_state,
                     mock_settings_state, mock_download_state,
                     mock_game_list_state, mock_menu_state):
        """Test popping state from stack."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        mock_settings_instance = Mock()
        mock_settings_state.return_value = mock_settings_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Push settings state
        state_manager.push_state('settings')

        # Pop state
        state_manager.pop_state()

        # Verify current state restored to menu
        self.assertEqual(state_manager.current_state, mock_menu_instance)

        # Verify state stack is empty
        self.assertEqual(len(state_manager.state_stack), 0)

        # Verify settings state's on_exit was called
        mock_settings_instance.on_exit.assert_called_once()

        # Verify menu state's on_enter was called
        mock_menu_instance.on_enter.assert_called_once_with(None)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def diable_test_pop_empty_stack(self, mock_update_state, mock_playing_state,
                           mock_settings_state, mock_download_state,
                           mock_game_list_state, mock_menu_state):
        """Test popping from empty stack doesn't cause errors."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Pop from empty stack (should not error)
        state_manager.pop_state()

        # Verify current state unchanged
        self.assertEqual(state_manager.current_state, mock_menu_instance)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def diable_test_update(self, mock_update_state, mock_playing_state,
                   mock_settings_state, mock_download_state,
                   mock_game_list_state, mock_menu_state):
        """Test update calls current state's update."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Call update
        state_manager.update(0.016)

        # Verify current state's update was called with delta time
        mock_menu_instance.update.assert_called_once_with(0.016)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def diable_test_handle_events(self, mock_update_state, mock_playing_state,
                         mock_settings_state, mock_download_state,
                         mock_game_list_state, mock_menu_state):
        """Test handle_events passes events to current state."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Create mock events
        events = [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})]

        # Handle events
        state_manager.handle_events(events)

        # Verify current state's handle_events was called
        mock_menu_instance.handle_events.assert_called_once_with(events)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def diable_test_render(self, mock_update_state, mock_playing_state,
                   mock_settings_state, mock_download_state,
                   mock_game_list_state, mock_menu_state):
        """Test render renders current state and stacked states."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        mock_settings_instance = Mock()
        mock_settings_state.return_value = mock_settings_instance
        
        mock_surface = Mock()
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Push settings state
        state_manager.push_state('settings')

        # Render
        state_manager.render(mock_surface)

        # Verify stacked state was rendered (for overlay effect)
        mock_menu_instance.render.assert_called_once_with(mock_surface)

        # Verify current state was rendered
        mock_settings_instance.render.assert_called_once_with(mock_surface)

    @patch('sbcman.core.state_manager.MenuState')
    @patch('sbcman.core.state_manager.GameListState')
    @patch('sbcman.core.state_manager.DownloadState')
    @patch('sbcman.core.state_manager.SettingsState')
    @patch('sbcman.core.state_manager.PlayingState')
    @patch('sbcman.core.state_manager.UpdateState')
    def diable_test_selected_game(self, mock_update_state, mock_playing_state,
                         mock_settings_state, mock_download_state,
                         mock_game_list_state, mock_menu_state):
        """Test selected_game attribute can be set and retrieved."""
        # Setup mocks
        mock_menu_instance = Mock()
        mock_menu_state.return_value = mock_menu_instance
        
        # Create state manager
        state_manager = StateManager(
            self.screen, self.hw_config, self.config,
            self.game_library, self.input_handler, self.app_paths
        )

        # Initially should be None
        self.assertIsNone(state_manager.selected_game)

        # Set selected game
        mock_game = Mock()
        state_manager.selected_game = mock_game

        # Verify it was set
        self.assertEqual(state_manager.selected_game, mock_game)


if __name__ == '__main__':
    unittest.main()
