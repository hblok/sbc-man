"""
Unit Tests for Playing State Module

Tests for PlayingState class.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.states.playing_state import PlayingState


class TestPlayingState(unittest.TestCase):
    
    def setUp(self):
        pygame.init()
        self.mock_state_manager = Mock()
        self.playing_state = PlayingState(self.mock_state_manager)
        self.hw_config = {
            "paths": {
                "data": "/tmp",
            },
            "display": {
                "resolution": [1280, 720],
                "fps_target": 60,
            }
        }
        self.playing_state.hw_config = self.hw_config
        self.mock_input_handler = Mock()
        self.playing_state.input_handler = self.mock_input_handler
    
    def tearDown(self):
        pygame.quit()
    
    def test_playing_state_initialization(self):
        self.playing_state.on_enter(None)
        self.assertTrue(self.playing_state.game_running)
        self.assertIsNotNone(self.playing_state.launcher)
    
    def test_playing_state_on_enter(self):
        self.playing_state.on_enter(None)
        
        self.assertTrue(self.playing_state.game_running)
        self.assertIsNotNone(self.playing_state.launcher)
        self.assertEqual(self.playing_state.message, "Game would be launched here")
    
    def test_playing_state_on_exit(self):
        self.playing_state.on_enter(None)
        
        self.playing_state.on_exit()
        
        self.assertFalse(self.playing_state.game_running)
    
    def test_playing_state_update(self):
        self.playing_state.on_enter(None)
        
        self.playing_state.update(0.016)
    
    def test_playing_state_handle_events_cancel(self):
        self.playing_state.on_enter(None)
        
        self.mock_input_handler.is_action_pressed.side_effect = [
            True,
            False,
        ]
        
        mock_events = [Mock()]
        
        with patch.object(self.playing_state, '_handle_exit_input', return_value=False):
            self.playing_state.handle_events(mock_events)
            
            self.mock_state_manager.change_state.assert_called_once_with("game_list")
    
    def test_playing_state_render(self):
        self.playing_state.on_enter(None)
        
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        mock_font.render.return_value.get_rect.return_value = Mock(center=(640, 360))
        
        with patch('pygame.font.Font', return_value=mock_font):
            self.playing_state.render(mock_surface)
            
            mock_surface.fill.assert_called_once_with((20, 20, 30))
            self.assertTrue(mock_font.render.called)