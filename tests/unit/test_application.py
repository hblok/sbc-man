# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Application

Tests for the main application class initialization and lifecycle management.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from sbcman.core.application import Application
from sbcman.hardware.paths import AppPaths


class TestApplication(unittest.TestCase):
    """Test cases for Application."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.app_paths = AppPaths(self.temp_dir, self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('sbcman.core.application.pygame.init')
    @patch('sbcman.core.application.StateManager')
    def test_application_initialization(self, mock_state_manager_class, mock_pygame_init):
        """Test application initialization."""
        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager_class.return_value = mock_state_manager
        
        # Create application
        app = Application(self.app_paths)
        
        # Verify pygame was initialized
        mock_pygame_init.assert_called_once()
        
        # Verify state manager was created
        mock_state_manager_class.assert_called_once()
        
        # Verify attributes
        self.assertEqual(app.app_paths, self.app_paths)
        self.assertEqual(app.state_manager, mock_state_manager)
        self.assertFalse(app.running)

    @patch('sbcman.core.application.pygame.init')
    @patch('sbcman.core.application.pygame.quit')
    def test_application_cleanup(self, mock_pygame_quit, mock_pygame_init):
        """Test application cleanup."""
        app = Application(self.app_paths)
        
        # Call cleanup
        app.cleanup()
        
        # Verify pygame.quit was called
        mock_pygame_quit.assert_called_once()
        
        # Verify running flag is False
        self.assertFalse(app.running)

    @patch('sbcman.core.application.pygame.init')
    @patch('sbcman.core.application.time.Clock')
    def test_application_run_basic(self, mock_clock_class, mock_pygame_init):
        """Test basic application run functionality."""
        # Setup mocks
        mock_clock = Mock()
        mock_clock_class.return_value = mock_clock
        mock_clock.tick.return_value = 16  # Mock 60 FPS
        
        app = Application(self.app_paths)
        
        # Mock the state manager to stop after one iteration
        app.state_manager = Mock()
        app.state_manager.current_state = Mock()
        
        # Set running to False immediately to exit loop
        def stop_running():
            app.running = False
        
        # Mock update to stop the loop
        app.state_manager.update.side_effect = stop_running
        
        # Run the application
        app.run()
        
        # Verify the loop was entered
        mock_clock.tick.assert_called()
        
        # Verify state manager methods were called
        app.state_manager.handle_events.assert_called()
        app.state_manager.update.assert_called()
        app.state_manager.render.assert_called()


if __name__ == '__main__':
    unittest.main()