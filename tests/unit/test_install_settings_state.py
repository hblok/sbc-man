# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit Tests for Install Settings State Module

Tests for InstallSettingsState class.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import pygame

from sbcman.states.install_settings_state import InstallSettingsState


class TestInstallSettingsState(unittest.TestCase):
    
    def setUp(self):
        pygame.init()
        self.mock_state_manager = Mock()
        self.install_settings_state = InstallSettingsState(self.mock_state_manager)
        self.hw_config = {
            "display": {
                "resolution": [1280, 720],
                "fps_target": 60,
            }
        }
        self.install_settings_state.hw_config = self.hw_config
        self.mock_input_handler = Mock()
        self.install_settings_state.input_handler = self.mock_input_handler
        self.mock_config_manager = Mock()
        self.mock_config_manager.get.side_effect = [
            False,
            False,
            str(Path.home() / "portmaster"),
            str(Path.home() / "portmaster" / "images")
        ]
        self.install_settings_state.config = self.mock_config_manager
    
    def tearDown(self):
        pygame.quit()
    
    def test_install_settings_state_initialization(self):
        self.install_settings_state.on_enter(None)
        self.assertIsNotNone(getattr(self.install_settings_state, 'settings_list', None))
    
    def test_install_settings_state_on_enter(self):
        self.install_settings_state.on_enter(None)
    
    def test_install_settings_state_on_exit(self):
        self.install_settings_state.config = Mock()
        
        self.install_settings_state.on_exit()
        
        self.install_settings_state.config.save.assert_called_once()
    
    def test_install_settings_state_update(self):
        self.install_settings_state.update(0.016)
    
    def test_install_settings_state_load_settings(self):
        self.mock_config_manager.get.side_effect = [
            True,
            False,
            str(Path.home() / "test"),
            str(Path.home() / "test" / "images")
        ]
        
        self.install_settings_state.on_enter(None)
        
        self.assertTrue(self.install_settings_state.install_as_pip)
        self.assertFalse(self.install_settings_state.add_portmaster_entry)
    
    def test_install_settings_state_handle_events_navigation(self):
        self.install_settings_state.on_enter(None)
        
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,
            True,
            False,
        ]
        
        mock_events = [Mock()]
        
        with patch.object(self.install_settings_state, '_handle_exit_input', return_value=False):
            self.install_settings_state.handle_events(mock_events)
            
            self.assertIsNotNone(self.install_settings_state.settings_list.get_selected_index())
    
    def test_install_settings_state_toggle_pip_setting(self):
        self.install_settings_state.on_enter(None)
        initial_value = self.install_settings_state.install_as_pip
        
        self.install_settings_state._select_option()
        
        self.assertNotEqual(self.install_settings_state.install_as_pip, initial_value)
    
    def test_install_settings_state_render(self):
        self.install_settings_state.on_enter(None)
        
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        
        with patch('pygame.font.Font', return_value=mock_font):
            with patch('pygame.draw.rect') as mock_draw_rect:
                self.install_settings_state.render(mock_surface)
                
                mock_surface.fill.assert_called_once_with((20, 20, 30))
                self.assertTrue(mock_font.render.called)