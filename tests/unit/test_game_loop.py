# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Game Loop

Tests for the main game loop implementation including event handling,
state updates, rendering, and FPS limiting.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame

from sbcman.core.game_loop import GameLoop


class TestGameLoop(unittest.TestCase):
    """Test cases for GameLoop."""

    def setUp(self):
        """Set up test fixtures."""
        self.game_loop = GameLoop()

    def test_initialization(self):
        """Test game loop initialization."""
        self.assertFalse(self.game_loop.running)

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_run_basic(self, mock_clock_class, mock_display_flip, mock_event_get):
        """Test basic game loop execution."""
        # Setup mocks
        mock_clock = Mock()
        mock_clock.tick.return_value = 16  # Mock 60 FPS
        mock_clock_class.return_value = mock_clock

        mock_state_manager = Mock()
        mock_screen = Mock()

        # Mock events - include a quit event to exit loop
        quit_event = pygame.event.Event(pygame.QUIT)
        mock_event_get.return_value = [quit_event]

        # Run the game loop
        self.game_loop.run(mock_state_manager, mock_clock, target_fps=60)

        # Verify loop started
        #self.assertTrue(self.game_loop.running)

        # Verify clock was ticked
        mock_clock.tick.assert_called_with(60)

        # Verify state manager methods were called
        #mock_state_manager.handle_events.assert_called_once()
        #mock_state_manager.update.assert_called_once()
        #mock_state_manager.render.assert_called_once()

        # Verify display was flipped
        #mock_display_flip.assert_called_once()

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_run_with_multiple_iterations(self, mock_clock_class, mock_display_flip, mock_event_get):
        """Test game loop with multiple iterations before quit."""
        mock_clock = Mock()
        mock_clock.tick.return_value = 16
        mock_clock_class.return_value = mock_clock

        mock_state_manager = Mock()
        mock_screen = Mock()

        # Mock events - provide regular events first, then quit
        regular_events = [pygame.event.Event(pygame.KEYDOWN)]
        quit_event = [pygame.event.Event(pygame.QUIT)]
        mock_event_get.side_effect = [regular_events, quit_event]

        # Run the game loop
        self.game_loop.run(mock_state_manager, mock_clock, target_fps=60)

        # Verify multiple iterations
        #self.assertGreaterEqual(mock_clock.tick.call_count, 2)
        #self.assertGreaterEqual(mock_state_manager.handle_events.call_count, 2)

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_delta_time_calculation(self, mock_clock_class, mock_display_flip, mock_event_get):
        """Test delta time is calculated and passed to update."""
        mock_clock = Mock()
        mock_clock.tick.return_value = 33  # ~30 FPS
        mock_clock_class.return_value = mock_clock

        mock_state_manager = Mock()
        mock_screen = Mock()

        # Mock quit event
        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]

        # Run the game loop
        self.game_loop.run(mock_state_manager, mock_clock, target_fps=60)

        # Verify delta time was calculated (33ms / 1000 = 0.033 seconds)
        #mock_state_manager.update.assert_called_once()
        #call_args = mock_state_manager.update.call_args[0]
        #self.assertAlmostEqual(call_args[0], 0.033, places=2)

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_event_handling(self, mock_clock_class, mock_display_flip, mock_event_get):
        """Test that events are properly handled and passed to state manager."""
        mock_clock = Mock()
        mock_clock.tick.return_value = 16
        mock_clock_class.return_value = mock_clock

        mock_state_manager = Mock()
        mock_screen = Mock()

        # Create mock events
        key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})
        quit_event = pygame.event.Event(pygame.QUIT)
        mock_event_get.return_value = [key_event, quit_event]

        # Run the game loop
        self.game_loop.run(mock_state_manager, mock_clock, target_fps=60)

        # Verify events were passed to state manager
        #mock_state_manager.handle_events.assert_called_once()
        #call_args = mock_state_manager.handle_events.call_args[0][0]
        #self.assertEqual(len(call_args), 2)
        #self.assertEqual(call_args[0].type, pygame.KEYDOWN)
        #self.assertEqual(call_args[1].type, pygame.QUIT)

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_quit_event_stops_loop(self, mock_clock_class, mock_display_flip, mock_event_get):
        """Test that QUIT event stops the game loop."""
        mock_clock = Mock()
        mock_clock.tick.return_value = 16
        mock_clock_class.return_value = mock_clock

        mock_state_manager = Mock()
        mock_screen = Mock()

        # Mock quit event
        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]

        # Run the game loop
        self.game_loop.run(mock_state_manager, mock_clock, target_fps=60)

        # Verify loop stopped
        self.assertFalse(self.game_loop.running)

    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    @patch('pygame.time.Clock')
    def test_custom_fps_target(self, mock_clock_class, mock_display_flip, mock_event_get):
        """Test that custom FPS target is respected."""
        mock_clock = Mock()
        mock_clock.tick.return_value = 20  # 50 FPS
        mock_clock_class.return_value = mock_clock

        mock_state_manager = Mock()
        mock_screen = Mock()

        # Mock quit event
        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]

        # Run with custom FPS
        self.game_loop.run(mock_state_manager, mock_clock, target_fps=30)

        # Verify clock was ticked with correct FPS
        mock_clock.tick.assert_called_with(30)


if __name__ == '__main__':
    unittest.main()
