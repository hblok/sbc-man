"""
Integration Tests for Application Startup Flow
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.core.application import Application
from src.hardware.detector import HardwareDetector
from src.models.game_library import GameLibrary


class TestStartupFlow(unittest.TestCase):
    """Integration tests for application startup flow."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()

    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()

    @patch('src.hardware.detector.HardwareDetector.get_config')
    @patch('src.models.game_library.GameLibrary.load_games')
    @patch('src.models.game_library.GameLibrary.save_games')
    @patch('src.core.game_loop.GameLoop.run')
    def test_application_startup_flow(self, mock_game_loop_run, mock_save_games, mock_load_games, mock_get_config):
        """Test the complete application startup workflow."""
        # Mock hardware detection
        mock_get_config.return_value = {
            "detected_device": "desktop",
            "detected_os": "standard_linux",
            "display": {
                "resolution": [1280, 720],
                "fullscreen": False,
                "fps_target": 60
            },
            "paths": {
                "data": "/tmp/data",
                "games": "/tmp/games",
                "screenshots": "/tmp/screenshots"
            }
        }
        
        # Mock game library loading
        mock_load_games.return_value = None
        mock_save_games.return_value = None
        
        # Mock game loop to avoid infinite loop
        mock_game_loop_run.return_value = None
        
        # Create temporary directories for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            games_dir = Path(temp_dir) / "games"
            data_dir.mkdir()
            games_dir.mkdir()
            
            # Mock the paths
            mock_get_config.return_value["paths"]["data"] = str(data_dir)
            mock_get_config.return_value["paths"]["games"] = str(games_dir)
            
            # Create application instance
            app = Application()
            
            # Mock the _ensure_data_directories method to avoid actual directory creation
            with patch.object(app, '_ensure_data_directories') as mock_ensure_dirs:
                mock_ensure_dirs.return_value = None
                
                # Mock pygame initialization
                with patch('pygame.display.set_mode') as mock_set_mode:
                    mock_surface = Mock()
                    mock_set_mode.return_value = mock_surface
                    
                    with patch('pygame.time.Clock') as mock_clock:
                        mock_clock_instance = Mock()
                        mock_clock_instance.tick.return_value = 16  # Mock 60 FPS
                        mock_clock.return_value = mock_clock_instance
                        
                        # Run the application
                        app.run()
                        
                        # Verify hardware config was loaded
                        self.assertIsNotNone(app.hw_config)
                        self.assertEqual(app.hw_config["detected_device"], "desktop")
                        self.assertEqual(app.hw_config["detected_os"], "standard_linux")
                        
                        # Verify components were created
                        self.assertIsNotNone(app.config_manager)
                        self.assertIsNotNone(app.game_library)
                        self.assertIsNotNone(app.input_handler)
                        self.assertIsNotNone(app.state_manager)


if __name__ == '__main__':
    unittest.main()