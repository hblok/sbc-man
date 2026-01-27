# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for DownloadState

Tests for download state functionality, UI rendering, and event handling.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from sbcman.states.download_state import DownloadState
from sbcman.proto import game_pb2


class TestDownloadState(unittest.TestCase):
    """Test cases for DownloadState."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a mock state manager
        self.mock_state_manager = Mock()
        
        # Create a mock hardware config
        self.hw_config = {
            "paths": {
                "data": tempfile.mkdtemp(),
                "games": tempfile.mkdtemp(),
            },
            "display": {
                "resolution": [1280, 720],
                "fps_target": 60,
            }
        }
        
        # Create a mock game library
        self.mock_game_library = Mock()
        # Mock get_enhanced_game_list to return empty list
        self.mock_game_library.get_enhanced_game_list.return_value = []
        
        # Create a mock input handler
        self.mock_input_handler = Mock()
        
        # Create the download state
        self.download_state = DownloadState(self.mock_state_manager)
        self.download_state.hw_config = self.hw_config
        self.download_state.game_library = self.mock_game_library
        self.download_state.input_handler = self.mock_input_handler
    
    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()
        
        # Clean up temporary directories
        import shutil
        shutil.rmtree(self.hw_config["paths"]["data"])
        shutil.rmtree(self.hw_config["paths"]["games"])
    
    def test_download_state_initialization(self):
        """Test download state initialization."""
        # Call on_enter to initialize the state
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        self.assertIsNotNone(self.download_state.download_manager)
        self.assertEqual(self.download_state.game_list.selected_index, 0)
        self.assertFalse(self.download_state.downloading)
        self.assertEqual(self.download_state.download_progress, 0.0)
        self.assertEqual(self.download_state.download_message, "")
    
    def test_on_enter_with_available_games(self):
        """Test entering download state with available games."""
        # Create test games
        game1 = game_pb2.Game()
        game1.id = "game1"
        game1.name = "Game 1"

        game2 = game_pb2.Game()
        game2.id = "game2"
        game2.name = "Game 2"

        test_games = [game1, game2]
        
        # Configure mock game library to return test games
        self.mock_game_library.get_available_games.return_value = test_games
        
        # Enter the state
        self.download_state.on_enter(None)
        
        # Verify the download manager was created
        self.assertIsNotNone(self.download_state.download_manager)
        
        # Verify available games were loaded
        self.assertEqual(self.download_state.available_games, test_games)
        self.assertEqual(self.download_state.game_list.selected_index, 0)
        self.assertFalse(self.download_state.downloading)
    
    def test_on_enter_without_available_games(self):
        """Test entering download state without available games."""
        # Configure mock game library to return empty list
        self.mock_game_library.get_available_games.return_value = []
        
        # Enter the state
        self.download_state.on_enter(None)
        
        # Verify the download manager was created
        self.assertIsNotNone(self.download_state.download_manager)
        
        # Verify available games list is empty
        self.assertEqual(self.download_state.available_games, [])
        self.assertEqual(self.download_state.game_list.selected_index, 0)
        self.assertFalse(self.download_state.downloading)
    
    def test_on_exit(self):
        """Test exiting download state."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Exit the state
        self.download_state.on_exit()
        
        # There's no specific assertion here as on_exit mainly logs,
        # but we verify it doesn't raise an exception
    
    def test_update_when_downloading(self):
        """Test updating download state when downloading."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up downloading state
        self.download_state.downloading = True
        self.download_state.download_manager = Mock()
        self.download_state.download_manager.get_progress.return_value = 0.75
        
        # Update the state
        self.download_state.update(0.016)  # ~60 FPS
        
        # Verify progress was updated
        self.assertEqual(self.download_state.download_progress, 0.75)
        self.download_state.download_manager.get_progress.assert_called_once()
    
    def test_update_when_not_downloading(self):
        """Test updating download state when not downloading."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up non-downloading state
        self.download_state.downloading = False
        self.download_state.download_manager = Mock()
        
        # Update the state
        self.download_state.update(0.016)  # ~60 FPS
        
        # Verify progress was not updated
        self.download_state.download_manager.get_progress.assert_not_called()
    
    def test_handle_events_cancel_action(self):
        """Test handling cancel action events."""
        game1 = game_pb2.Game()
        game1.id = "game1"
        game1.name = "Game 1"

        game2 = game_pb2.Game()
        game2.id = "game2"
        game2.name = "Game 2"

        test_games = [game1, game2]
        
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = [
            game1, game2
        ]
        self.download_state.on_enter(None)
        
        # Set up mock input handler to return True for cancel action
        self.mock_input_handler.is_action_pressed.return_value = True
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        self.download_state.handle_events(mock_events)
        
        # Verify state transition was requested
        self.mock_state_manager.change_state.assert_called_once_with("menu")
        
        # Verify input handler was checked for cancel action
        self.mock_input_handler.is_action_pressed.assert_called_with("cancel", mock_events)
    
    def test_handle_events_back_input(self):
        """Test handling back/exit input events."""
        game1 = game_pb2.Game()
        game1.id = "game1"
        game1.name = "Game 1"

        game2 = game_pb2.Game()
        game2.id = "game2"
        game2.name = "Game 2"

        
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = [
            game1, game2
        ]
        self.download_state.on_enter(None)
        
        # Set up mock input handler to return False for cancel action
        self.mock_input_handler.is_action_pressed.return_value = False
        
        # Create a mock event that simulates ESC key press
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_ESCAPE
        mock_events = [mock_event]
        
        # Handle events
        with patch.object(self.download_state, '_handle_exit_input', return_value=True):
            self.download_state.handle_events(mock_events)
            
            # Verify state transition was requested
            self.mock_state_manager.change_state.assert_called_once_with("menu")
    
    def test_handle_events_navigation(self):
        """Test handling navigation events."""

        game1 = game_pb2.Game()
        game1.id = "game1"
        game1.name = "Game 1"

        game2 = game_pb2.Game()
        game2.id = "game2"
        game2.name = "Game 2"

        game3 = game_pb2.Game()
        game3.id = "game3"
        game3.name = "Game 3"        
        
        # Create test games
        test_games = [game1, game2, game3]
        
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = test_games
        self.download_state.on_enter(None)
        
        # Set up mock input handler to return False for cancel action
        self.mock_input_handler.is_action_pressed.return_value = False
        
        # Test navigating down
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,  # cancel
            True,   # up
            False,  # down
            False,  # confirm
        ]
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        self.download_state.handle_events(mock_events)
        
        # Verify selected index was not decremented (can't go below 0)
        self.assertEqual(self.download_state.game_list.selected_index, 0)
        
        # Test navigating down
        self.download_state.game_list.selected_index = 2
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,  # cancel
            True,   # up
            False,  # down
            False,  # confirm
        ]
        
        # Handle events again
        self.download_state.handle_events(mock_events)
        
        # Verify selected index was incremented (from 0 to 1 due to scroll_down)
        self.assertEqual(self.download_state.game_list.selected_index, 1)
    
    def test_handle_events_confirm_download(self):
        """Test handling confirm action to start download."""

        game1 = game_pb2.Game()
        game1.id = "game1"
        game1.name = "Game 1"
        
        # Create test games
        test_games = [game1]        
        
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = test_games
        self.download_state.on_enter(None)
        
        # Set up mock input handler
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,  # cancel
            False,  # up
            False,  # down
            True,   # confirm
        ]
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.download_state.download_manager, 'download_game') as mock_download:
            self.download_state.handle_events(mock_events)
            
            # Verify download was started
            mock_download.assert_called_once()
            
            # Verify downloading flag was set
            self.assertTrue(self.download_state.downloading)
    
    def test_handle_events_confirm_no_games(self):
        """Test handling confirm action when no games are available."""
        # Enter the state with no available games
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up mock input handler
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,  # cancel
            False,  # up
            False,  # down
            True,   # confirm
        ]
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.download_state.download_manager, 'download_game') as mock_download:
            self.download_state.handle_events(mock_events)
            
            # Verify download was not started
            mock_download.assert_not_called()
            
            # Verify downloading flag was not set
            self.assertFalse(self.download_state.downloading)
    
    def test_render_when_downloading(self):
        """Test rendering download state when downloading."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up downloading state
        self.download_state.downloading = True
        self.download_state.download_message = "Downloading game..."
        self.download_state.download_progress = 0.75
        
        # Create a mock surface
        real_surface = pygame.Surface((1280, 720))
        
        # Render the state
        self.download_state.render(real_surface)
        
    def test_render_when_not_downloading_with_games(self):
        """Test rendering download state when not downloading but games are available."""

        game1 = game_pb2.Game()
        game1.id = "game1"
        game1.name = "Game 1"

        game2 = game_pb2.Game()
        game2.id = "game2"
        game2.name = "Game 2"
        
        # Create test games
        test_games = [game1, game2]
        
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = test_games
        self.download_state.on_enter(None)
        
        # Set up non-downloading state
        self.download_state.downloading = False
        
        # Create a mock surface
        real_surface = pygame.Surface((1280, 720))
        
        # Render the state
        self.download_state.render(real_surface)
                
        # Verify games list was rendered
        # FIXME
        #self.assertEqual(mock_font.render.call_count, 3)  # title + 2 games
    
    def test_render_when_not_downloading_no_games(self):
        """Test rendering download state when not downloading and no games are available."""
        # Enter the state with no available games
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up non-downloading state
        self.download_state.downloading = False
        
        # Create a mock surface
        real_surface = pygame.Surface((1280, 720))
        
        # Render the state
        self.download_state.render(real_surface)
            
        # Verify no games message was rendered#
        # FIXME
        #mock_font.render.assert_any_call("No games available for download", True, (150, 150, 150))
    
    def test_on_progress(self):
        """Test download progress callback."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Call on_progress
        self.download_state.on_progress(750, 1000)
        
        # Verify download progress was updated
        self.assertEqual(self.download_state.download_progress, 0.75)
        # Note: The actual implementation doesn't update the download_message in on_progress
    
    def test_on_complete_success(self):
        """Test download complete callback with success."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up downloading state
        self.download_state.downloading = True
        
        # Reconfigure the mock game library to return empty list for get_enhanced_game_list
        self.mock_game_library.get_enhanced_game_list.return_value = []
        
        # Call on_complete with success
        self.download_state.on_complete(True, "Download completed successfully")
        
        # Verify state was updated correctly
        self.assertFalse(self.download_state.downloading)
        self.assertEqual(self.download_state.download_message, "Download completed successfully")
        
        # Verify game library save was called
        self.mock_game_library.save_games.assert_called_once()
    
    def test_on_complete_failure(self):
        """Test download complete callback with failure."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up downloading state
        self.download_state.downloading = True
        
        # Call on_complete with failure
        self.download_state.on_complete(False, "Download failed")
        
        # Verify state was updated correctly
        self.assertFalse(self.download_state.downloading)
        self.assertEqual(self.download_state.download_message, "Download failed")
    
    def test_on_error(self):
        """Test download error callback."""
        # Enter the state first to initialize it
        self.mock_game_library.get_available_games.return_value = []
        self.download_state.on_enter(None)
        
        # Set up downloading state
        self.download_state.downloading = True
        
        # Call on_error
        self.download_state.on_error("Network connection failed")
        
        # Verify state was updated correctly
        self.assertEqual(self.download_state.download_message, "Error: Network connection failed")


if __name__ == "__main__":
    unittest.main()
