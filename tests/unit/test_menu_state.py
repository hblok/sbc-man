"""
Unit Tests for Menu State Module

Tests for MenuState class.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.states.menu_state import MenuState


class TestMenuState(unittest.TestCase):
    
    def setUp(self):
        pygame.init()
        self.mock_state_manager = Mock()
        self.menu_state = MenuState(self.mock_state_manager)
        self.hw_config = {
            "display": {
                "resolution": [1280, 720],
            }
        }
        self.menu_state.hw_config = self.hw_config
        self.mock_input_handler = Mock()
        self.menu_state.input_handler = self.mock_input_handler
    
    def tearDown(self):
        pygame.quit()
    
    def test_menu_state_initialization(self):
        self.menu_state.on_enter(None)
        self.assertEqual(self.menu_state.selected_option, 0)
        self.assertEqual(len(self.menu_state.menu_options), 4)
    
    def test_menu_state_on_enter(self):
        self.menu_state.on_enter(None)
    
    def test_menu_state_on_exit(self):
        self.menu_state.on_exit()
    
    def test_menu_state_update(self):
        self.menu_state.update(0.016)
    
    def test_menu_state_handle_events_navigate_down(self):
        self.menu_state.on_enter(None)
        self.menu_state.selected_option = 0
        
        mock_events = [Mock()]
        
        with patch.object(self.menu_state, '_handle_exit_input', return_value=False):
            self.mock_input_handler.is_action_pressed.side_effect = lambda action, events: {
                "up": False,
                "down": True,
                "confirm": False,
            }.get(action, False)
            
            self.menu_state.handle_events(mock_events)
            
            self.assertEqual(self.menu_state.selected_option, 1)
    
    def test_menu_state_handle_events_navigate_up(self):
        self.menu_state.on_enter(None)
        self.menu_state.selected_option = 1
        
        mock_events = [Mock()]
        
        with patch.object(self.menu_state, '_handle_exit_input', return_value=False):
            self.mock_input_handler.is_action_pressed.side_effect = lambda action, events: {
                "up": True,
                "down": False,
                "confirm": False,
            }.get(action, False)
            
            self.menu_state.handle_events(mock_events)
            
            self.assertEqual(self.menu_state.selected_option, 0)
    
    def test_menu_state_handle_events_confirm_selection(self):
        self.menu_state.on_enter(None)
        
        test_cases = [
            (0, "game_list"),
            (1, "download"),
            (2, "settings"),
        ]
        
        for selected_option, expected_state in test_cases:
            with self.subTest(selected_option=selected_option):
                self.mock_state_manager.reset_mock()
                self.mock_input_handler.reset_mock()
                
                self.menu_state.selected_option = selected_option
                
                mock_events = [Mock()]
                
                with patch.object(self.menu_state, '_handle_exit_input', return_value=False):
                    self.mock_input_handler.is_action_pressed.side_effect = lambda action, events: {
                        "up": False,
                        "down": False,
                        "confirm": True,
                    }.get(action, False)
                    
                    self.menu_state.handle_events(mock_events)
                    
                    self.mock_state_manager.change_state.assert_called_once_with(expected_state)
    
    def test_menu_state_render(self):
        self.menu_state.on_enter(None)
        
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        mock_font.render.return_value.get_rect.return_value = Mock(center=(640, 100))
        
        with patch('pygame.font.Font', return_value=mock_font):
            with patch('pygame.draw.rect') as mock_draw_rect:
                self.menu_state.render(mock_surface)
                
                mock_surface.fill.assert_called_once_with((20, 20, 30))
                self.assertTrue(mock_font.render.called)