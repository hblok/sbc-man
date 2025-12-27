"""
Unit Tests for Settings State Module

Tests for SettingsState class.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from sbcman.states.settings_state import SettingsState


class TestSettingsState(unittest.TestCase):
    
    def setUp(self):
        pygame.init()
        self.mock_state_manager = Mock()
        self.settings_state = SettingsState(self.mock_state_manager)
        self.hw_config = {
            "display": {
                "resolution": [1280, 720],
                "fps_target": 60,
            }
        }
        self.settings_state.hw_config = self.hw_config
        self.mock_input_handler = Mock()
        self.settings_state.input_handler = self.mock_input_handler
        self.mock_config_manager = Mock()
        self.settings_state.config = self.mock_config_manager
    
    def tearDown(self):
        pygame.quit()
    
    def test_settings_state_initialization(self):
        self.settings_state.on_enter(None)
        self.assertEqual(self.settings_state.selected_option, 0)
        self.assertEqual(len(self.settings_state.settings_options), 4)
    
    def test_settings_state_on_enter(self):
        self.settings_state.on_enter(None)
    
    def test_settings_state_on_exit(self):
        self.settings_state.config = Mock()
        
        self.settings_state.on_exit()
        
        self.settings_state.config.save.assert_called_once()
    
    def test_settings_state_update(self):
        self.settings_state.update(0.016)
    
    def test_settings_state_handle_events_navigation(self):
        self.settings_state.on_enter(None)
        
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,
            False,
            True,
            False,
            False,
        ]
        
        mock_events = [Mock()]
        
        with patch.object(self.settings_state, '_handle_exit_input', return_value=False):
            self.settings_state.handle_events(mock_events)
            
            self.assertEqual(self.settings_state.selected_option, 1)
    
    def test_settings_state_render(self):
        self.settings_state.on_enter(None)
        
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        
        with patch('pygame.font.Font', return_value=mock_font):
            with patch('pygame.draw.rect') as mock_draw_rect:
                self.settings_state.render(mock_surface)
                
                mock_surface.fill.assert_called_once_with((20, 20, 30))
                self.assertTrue(mock_font.render.called)