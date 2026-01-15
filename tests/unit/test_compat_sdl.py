# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for SDL Compatibility Layer

Tests for SDL/pygame initialization with driver fallback support,
display setup, and environment variable handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os

from sbcman.hardware.compat_sdl import init_display, _try_init_pygame_display


class TestCompatSDL(unittest.TestCase):
    """Test cases for SDL compatibility layer."""

    def setUp(self):
        """Set up test fixtures."""
        # Save original environment variables
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Restore original environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    @patch('sbcman.hardware.compat_sdl.pygame.display.set_mode')
    @patch('sbcman.hardware.compat_sdl.pygame.display.Info')
    @patch('sbcman.hardware.compat_sdl.pygame.event.pump')
    @patch('sbcman.hardware.compat_sdl.pygame.display.get_driver')
    @patch('sbcman.hardware.compat_sdl.pygame._sdl2')
    def test_init_display_success(self, mock_sdl2, mock_get_driver, mock_pump,
                                 mock_display_info, mock_set_mode, mock_display_init):
        """Test successful display initialization."""
        # Setup mocks
        mock_screen = Mock()
        mock_screen.get_size.return_value = (1280, 720)
        mock_set_mode.return_value = mock_screen
        
        mock_info = Mock()
        mock_info.current_w = 1920
        mock_info.current_h = 1080
        mock_display_info.return_value = mock_info
        
        mock_get_driver.return_value = 'x11'
        
        # Mock SDL2 introspection to raise exception (fallback case)
        mock_sdl2.video = None
        
        # Call init_display
        screen, info = init_display(fullscreen=True, vsync=True, size=(1280, 720))
        
        # Verify screen was returned
        self.assertEqual(screen, mock_screen)
        
        # Verify info dictionary contains expected keys
        self.assertIn('driver', info)
        self.assertIn('renderer', info)
        self.assertIn('size', info)
        
        # Verify size
        self.assertEqual(info['size'], (1280, 720))

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    @patch('sbcman.hardware.compat_sdl.pygame.display.set_mode')
    @patch('sbcman.hardware.compat_sdl.pygame.display.Info')
    @patch('sbcman.hardware.compat_sdl.pygame.event.pump')
    @patch('sbcman.hardware.compat_sdl.pygame.display.get_driver')
    def test_init_display_windowed(self, mock_get_driver, mock_pump,
                                   mock_display_info, mock_set_mode, mock_display_init):
        """Test display initialization in windowed mode."""
        # Setup mocks
        mock_screen = Mock()
        mock_screen.get_size.return_value = (640, 480)
        mock_set_mode.return_value = mock_screen
        
        mock_get_driver.return_value = 'x11'
        
        # Call init_display without fullscreen
        screen, info = init_display(fullscreen=False, vsync=False, size=(640, 480))
        
        # Verify vsync environment variable was set to 0
        self.assertEqual(os.environ.get('SDL_RENDER_VSYNC'), '0')
        
        # Verify screen was returned
        self.assertEqual(screen, mock_screen)

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    @patch('sbcman.hardware.compat_sdl.pygame.display.set_mode')
    @patch('sbcman.hardware.compat_sdl.pygame.event.pump')
    @patch('sbcman.hardware.compat_sdl.pygame.display.quit')
    def test_try_init_pygame_display_success(self, mock_display_quit, mock_pump,
                                           mock_set_mode, mock_display_init):
        """Test _try_init_pygame_display success."""
        # Setup mocks
        mock_screen = Mock()
        mock_set_mode.return_value = mock_screen
        
        # Call _try_init_pygame_display
        screen, error = _try_init_pygame_display(
            (1280, 720), fullscreen=True, allow_software=False
        )
        
        # Verify screen was returned and no error
        self.assertEqual(screen, mock_screen)
        self.assertIsNone(error)
        
        # Verify pygame.init was called
        mock_display_init.assert_called_once()
        
        # Verify set_mode was called with fullscreen flag
        mock_set_mode.assert_called_once()
        call_args = mock_set_mode.call_args[0]
        self.assertEqual(call_args[0], (1280, 720))
        self.assertEqual(call_args[1], pygame.FULLSCREEN)

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    def test_try_init_pygame_display_init_failure(self, mock_display_init):
        """Test _try_init_pygame_display when init fails."""
        # Setup mock to raise exception
        mock_display_init.side_effect = Exception("Display init failed")
        
        # Call _try_init_pygame_display
        screen, error = _try_init_pygame_display(
            (1280, 720), fullscreen=True, allow_software=False
        )
        
        # Verify error was returned
        self.assertIsNone(screen)
        self.assertIsNotNone(error)
        self.assertIn("Display init failed", error)

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    @patch('sbcman.hardware.compat_sdl.pygame.display.set_mode')
    @patch('sbcman.hardware.compat_sdl.pygame.event.pump')
    def test_try_init_pygame_display_set_mode_failure(self, mock_pump,
                                                     mock_set_mode, mock_display_init):
        """Test _try_init_pygame_display when set_mode fails."""
        # Setup mock to raise exception
        mock_set_mode.side_effect = Exception("Set mode failed")
        
        # Call _try_init_pygame_display
        screen, error = _try_init_pygame_display(
            (1280, 720), fullscreen=True, allow_software=False
        )
        
        # Verify error was returned
        self.assertIsNone(screen)
        self.assertIsNotNone(error)
        self.assertIn("Set mode failed", error)

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    @patch('sbcman.hardware.compat_sdl.pygame.display.set_mode')
    @patch('sbcman.hardware.compat_sdl.pygame.display.quit')
    def test_try_init_pygame_display_cleanup_on_failure(self, mock_display_quit,
                                                       mock_set_mode, mock_display_init):
        """Test _try_init_pygame_display cleans up on failure."""
        # Setup mock to raise exception
        mock_set_mode.side_effect = Exception("Set mode failed")
        
        # Call _try_init_pygame_display
        screen, error = _try_init_pygame_display(
            (1280, 720), fullscreen=True, allow_software=False
        )
        
        # Verify quit was called to clean up
        mock_display_quit.assert_called()

    def test_try_init_pygame_display_software_mode(self):
        """Test _try_init_pygame_display with software renderer."""
        with patch('sbcman.hardware.compat_sdl.pygame.display.init') as mock_init, \
             patch('sbcman.hardware.compat_sdl.pygame.display.set_mode') as mock_set_mode, \
             patch('sbcman.hardware.compat_sdl.pygame.event.pump') as mock_pump:
            
            # Setup mocks
            mock_screen = Mock()
            mock_set_mode.return_value = mock_screen
            
            # Call with software mode
            screen, error = _try_init_pygame_display(
                (640, 480), fullscreen=False, allow_software=True
            )
            
            # Verify SDL_RENDER_DRIVER was set to software
            self.assertEqual(os.environ.get('SDL_RENDER_DRIVER'), 'software')
            
            # Verify screen was returned
            self.assertEqual(screen, mock_screen)
            self.assertIsNone(error)

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    @patch('sbcman.hardware.compat_sdl.pygame.display.set_mode')
    @patch('sbcman.hardware.compat_sdl.pygame.display.Info')
    @patch('sbcman.hardware.compat_sdl.pygame.event.pump')
    @patch('sbcman.hardware.compat_sdl.pygame.display.get_driver')
    def test_init_display_fullscreen_desktop_size(self, mock_get_driver, mock_pump,
                                                  mock_display_info, mock_set_mode,
                                                  mock_display_init):
        """Test fullscreen uses desktop size when size not specified."""
        # Setup mocks
        mock_screen = Mock()
        mock_screen.get_size.return_value = (1920, 1080)
        mock_set_mode.return_value = mock_screen
        
        mock_info = Mock()
        mock_info.current_w = 1920
        mock_info.current_h = 1080
        mock_display_info.return_value = mock_info
        
        mock_get_driver.return_value = 'x11'
        
        # Mock SDL2 introspection to raise exception
        with patch('sbcman.hardware.compat_sdl.pygame._sdl2', side_effect=ImportError):
            # Call init_display with fullscreen and small size
            screen, info = init_display(fullscreen=True, vsync=True, size=(640, 480))
            
            # Verify desktop size was used
            mock_set_mode.assert_called()
            call_args = mock_set_mode.call_args[0]
            self.assertEqual(call_args[0], (1920, 1080))

    @patch('sbcman.hardware.compat_sdl.pygame.display.init')
    @patch('sbcman.hardware.compat_sdl.pygame.display.set_mode')
    @patch('sbcman.hardware.compat_sdl.pygame.event.pump')
    @patch('sbcman.hardware.compat_sdl.pygame.display.get_driver')
    @patch('sbcman.hardware.compat_sdl.pygame._sdl2')
    def test_init_display_renderer_info(self, mock_sdl2, mock_get_driver, mock_pump,
                                       mock_set_mode, mock_display_init):
        """Test renderer info is extracted when SDL2 is available."""
        # Setup mocks
        mock_screen = Mock()
        mock_screen.get_size.return_value = (1280, 720)
        mock_set_mode.return_value = mock_screen
        
        mock_get_driver.return_value = 'x11'
        
        # Mock SDL2 introspection
        mock_window = Mock()
        mock_renderer = Mock()
        mock_renderer.name = 'opengl'
        mock_renderer.destroy.return_value = None
        mock_sdl2.video.Window.from_display_module.return_value = mock_window
        mock_sdl2.video.Renderer.from_window.return_value = mock_renderer
        
        # Call init_display
        screen, info = init_display(fullscreen=True, vsync=True, size=(1280, 720))
        
        # Verify renderer info was extracted
        self.assertEqual(info['renderer'], 'opengl')


if __name__ == '__main__':
    unittest.main()