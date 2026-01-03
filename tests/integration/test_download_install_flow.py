# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Integration Tests for Download and Install Flow

Tests the complete download and installation workflow.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from sbcman.states.download_state import DownloadState
from sbcman.proto import game_pb2


class TestDownloadInstallFlow(unittest.TestCase):
    """Integration tests for download and install flow."""
    
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
        shutil.rmtree(self.temp_data_dir)
        shutil.rmtree(self.temp_games_dir)
    
    @patch('pathlib.Path.unlink')
    @patch.object(DownloadState, '_start_download')
    def test_download_and_install_flow(self, mock_start_download, mock_unlink):
        """Test the complete download and install workflow."""
        # Mock the unlink method to prevent errors
        mock_unlink.return_value = None
        
        # Create test games
        game1 = game_pb2.Game()
        game1.id = "game1"
        game1.name = "Game 1"
        game1.installed = True
        game1.install_path="/tmp/games/test-game-1"
        game1.entry_point="main.py"        

        game2 = game_pb2.Game()
        game2.id = "game2"
        game2.name = "Game 2"
        game2.installed = False
        game2.install_path="/tmp/games/test-game-2"
        game2.entry_point="game.py"
        game2.download_url="https://example.com/test-game-2.zip"        

        test_games = [game1, game2]        
        
        # Configure mock game library to return test games
        self.mock_game_library.get_available_games.return_value = test_games
        
        # Enter the download state
        self.download_state.on_enter(None)
        
        # Verify initial state
        self.assertFalse(self.download_state.downloading)
        self.assertEqual(len(self.download_state.available_games), 2)
        
        # Create a mock observer to simulate the download process
        mock_observer = Mock()
        
        # Mock the _start_download method to simulate a successful download
        mock_start_download.side_effect = lambda: setattr(self.download_state, 'downloading', True) or \
            setattr(self.download_state, 'download_message', f"Downloading {self.download_state.available_games[0].name}...")
        
        # Simulate user confirming download of first game
        with patch.object(self.mock_input_handler, 'is_action_pressed') as mock_action:
            mock_action.side_effect = lambda action, events: action == "confirm"
            
            mock_events = [Mock()]
            self.download_state.handle_events(mock_events)
            
            # Verify that downloading started
            self.assertTrue(self.download_state.downloading)
            self.assertIn("Downloading Test Game 1", self.download_state.download_message)
        
        # Simulate successful download completion
        self.download_state.on_complete(True, "Successfully installed Test Game 1")
        
        # Verify download completed successfully
        self.assertFalse(self.download_state.downloading)
        self.assertIn("Successfully installed Test Game 1", self.download_state.download_message)
