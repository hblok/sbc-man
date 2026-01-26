# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Update State

Tests for the self-update state including update checking, downloading,
installing, and UI management with adaptive layout.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame

from sbcman.states.update_state import UpdateState


class TestUpdateState(unittest.TestCase):
    """Test cases for UpdateState."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock state manager
        self.state_manager = Mock()
        self.state_manager.screen = pygame.Surface((640, 480))
        self.state_manager.hw_config = {}
        self.state_manager.config = Mock()
        self.state_manager.game_library = Mock()
        self.state_manager.input_handler = Mock()
        self.state_manager.app_paths = Mock()

        # Patch ScrollableList to avoid pygame dependencies
        with patch('sbcman.views.widgets.ScrollableList') as mock_scrollable:
            mock_list_instance = Mock()
            mock_scrollable.return_value = mock_list_instance
            self.state = UpdateState(self.state_manager)

    def test_initialization(self):
        """Test update state initialization."""
        self.assertIsNotNone(self.state)
        self.assertEqual(self.state.stage, "checking")
        self.assertFalse(self.state.update_available)
        self.assertIsNone(self.state.latest_version)
        self.assertIsNone(self.state.download_url)
        self.assertEqual(self.state.message, "Checking for updates...")

    @patch('sbcman.services.updater.UpdaterService')
    def test_on_enter_initializes_scrollable_list(self, mock_updater_service):
        """Test on_enter sets up adaptive scrollable list."""
        # Create new state to test on_enter
        with patch('sbcman.views.widgets.ScrollableList') as mock_scrollable:
            mock_list_instance = Mock()
            mock_scrollable.return_value = mock_list_instance
            state = UpdateState(self.state_manager)
            
            # Call on_enter
            state.on_enter(None)
            
            # Verify scrollable list was set up
            self.assertTrue(hasattr(state, 'options_list'))

    @patch('sbcman.services.updater.UpdaterService')
    def test_on_enter_starts_update_check(self, mock_updater_service):
        """Test on_enter starts update check."""
        # Create new state to test on_enter
        with patch('sbcman.views.widgets.ScrollableList') as mock_scrollable:
            mock_list_instance = Mock()
            mock_scrollable.return_value = mock_list_instance
            state = UpdateState(self.state_manager)
            
            # Call on_enter
            state.on_enter(None)
            
            # Verify update check was started
            # TODO
            #self.assertEqual(state.stage, "checking")

    def test_on_exit(self):
        """Test on_exit cleans up temporary files."""
        # Mock updater cleanup
        self.state.updater = Mock()
        self.state.updater.cleanup_temp_files = Mock()
        
        # Call on_exit
        self.state.on_exit()
        
        # Verify cleanup was called
        self.state.updater.cleanup_temp_files.assert_called_once()

    def test_update_does_nothing(self):
        """Test update method does nothing (updates are async)."""
        # Should not raise any errors
        self.state.update(0.016)

    def test_handle_events_exit(self):
        """Test handle_events exits on back input."""
        # Mock exit input
        self.state._handle_exit_input = Mock(return_value=True)
        
        # Handle events
        events = []
        self.state.handle_events(events)
        
        # Verify state change to menu
        self.state_manager.change_state.assert_called_with("menu")

    def test_handle_available_stage_events_navigation(self):
        """Test handling navigation events in available stage."""
        # Set stage to available
        self.state.stage = "available"
        self.state.options = ["Download and Install", "Cancel"]
        
        # Mock input handler
        self.state.input_handler.is_action_pressed = Mock(return_value=False)
        
        # Create mock options list
        self.state.options_list = Mock()
        self.state.options_list.scroll_up = Mock()
        self.state.options_list.scroll_down = Mock()
        self.state.options_list.get_selected_item = Mock(return_value="Download and Install")
        
        # Handle events
        events = []
        self.state.handle_events(events)

    def test_handle_available_stage_events_confirm_download(self):
        """Test handling confirm event in available stage starts download."""
        # Set stage to available
        self.state.stage = "available"
        self.state.options = ["Download and Install", "Cancel"]
        
        # Mock input handler - confirm pressed
        def is_action_pressed(action, events):
            return action == "confirm"
        
        self.state.input_handler.is_action_pressed = is_action_pressed
        
        # Mock options list
        self.state.options_list = Mock()
        self.state.options_list.get_selected_item = Mock(return_value="Download and Install")
        
        # Mock _start_download
        self.state._start_download = Mock()
        
        # Handle events
        events = []
        self.state.handle_events(events)
        
        # Verify download started
        self.state._start_download.assert_called_once()

    def test_handle_available_stage_events_cancel(self):
        """Test handling cancel event in available stage."""
        # Set stage to available
        self.state.stage = "available"
        self.state.options = ["Download and Install", "Cancel"]
        
        # Mock input handler - confirm pressed but cancel selected
        def is_action_pressed(action, events):
            return action == "confirm"
        
        self.state.input_handler.is_action_pressed = is_action_pressed
        
        # Mock options list
        self.state.options_list = Mock()
        self.state.options_list.get_selected_item = Mock(return_value="Cancel")
        
        # Handle events
        events = []
        self.state.handle_events(events)
        
        # Verify state changed to menu
        self.state_manager.change_state.assert_called_with("menu")

    def test_handle_completion_stage_events(self):
        """Test handling events in completion stage."""
        # Set stage to complete
        self.state.stage = "complete"
        self.state.message = "Update complete"
        
        # Mock input handler - confirm pressed
        def is_action_pressed(action, events):
            return action == "confirm"
        
        self.state.input_handler.is_action_pressed = is_action_pressed
        
        # Handle events
        events = []
        self.state.handle_events(events)
        
        # Verify state changed to menu
        self.state_manager.change_state.assert_called_with("menu")

    def test_wrap_message_basic(self):
        """Test basic message wrapping."""
        message = "This is a long message that should be wrapped"
        result = self.state._wrap_message(message, max_width=20)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 1)

    def test_wrap_message_empty(self):
        """Test wrapping empty message."""
        result = self.state._wrap_message("", max_width=50)
        
        self.assertEqual(result, [])

    def test_wrap_message_single_word(self):
        """Test wrapping single word message."""
        result = self.state._wrap_message("short", max_width=50)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "short")

    def test_calculate_adaptive_message_lines_large_screen(self):
        """Test calculating max visible lines for large screen."""
        result = self.state._calculate_adaptive_message_lines(1024)
        
        self.assertEqual(result, 12)

    def test_calculate_adaptive_message_lines_medium_screen(self):
        """Test calculating max visible lines for medium screen."""
        result = self.state._calculate_adaptive_message_lines(800)
        
        self.assertEqual(result, 8)

    def test_calculate_adaptive_message_lines_small_screen(self):
        """Test calculating max visible lines for small screen."""
        result = self.state._calculate_adaptive_message_lines(640)
        
        self.assertEqual(result, 6)

    def test_get_message_color_error(self):
        """Test getting message color for error stage."""
        self.state.stage = "error"
        color = self.state._get_message_color()
        
        self.assertEqual(color, (255, 100, 100))

    def test_get_message_color_complete(self):
        """Test getting message color for complete stage."""
        self.state.stage = "complete"
        color = self.state._get_message_color()
        
        self.assertEqual(color, (100, 255, 100))

    def test_get_message_color_normal(self):
        """Test getting message color for normal stage."""
        self.state.stage = "checking"
        color = self.state._get_message_color()
        
        self.assertEqual(color, (255, 255, 255))

    def test_update_message_display(self):
        """Test updating message display wraps message."""
        self.state.message = "This is a test message"
        self.state._update_message_display()
        
        self.assertGreater(len(self.state.message_lines), 0)
        self.assertEqual(self.state.message_scroll_offset, 0)

    def test_update_options_list(self):
        """Test updating options list."""
        self.state.options = ["Option 1", "Option 2"]
        
        # Mock options list
        self.state.options_list = Mock()
        self.state.options_list.set_items = Mock()
        
        self.state._update_options_list()
        
        # Verify set_items was called
        self.state.options_list.set_items.assert_called_once()

    def test_update_options_list_without_list(self):
        """Test updating options list when list doesn't exist."""
        self.state.options = ["Option 1", "Option 2"]
        
        # Should not raise error
        self.state._update_options_list()

    @patch('sbcman.views.widgets.ScrollableList')
    def test_setup_adaptive_scrollable_list(self, mock_scrollable):
        """Test setting up adaptive scrollable list."""
        mock_list_instance = Mock()
        mock_scrollable.return_value = mock_list_instance
        
        state = UpdateState(self.state_manager)
        state._setup_adaptive_scrollable_list()
        
        # Verify options list was created
        self.assertTrue(hasattr(state, 'options_list'))
        mock_scrollable.assert_called_once()


if __name__ == '__main__':
    unittest.main()
