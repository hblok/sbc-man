"""
Unit Tests for Game List State Module

Tests for GameListState class.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.states.game_list_state import GameListState
from src.models.game import Game


class TestGameListState(unittest.TestCase):
    
    def setUp(self):
        pygame.init()
        self.mock_state_manager = Mock()
        self.game_list_state = GameListState(self.mock_state_manager)
        self.hw_config = {
            "display": {
                "resolution": [1280, 720],
            }
        }
        self.game_list_state.hw_config = self.hw_config
        self.mock_input_handler = Mock()
        self.game_list_state.input_handler = self.mock_input_handler
        self.mock_game_library = Mock()
        self.game_list_state.game_library = self.mock_game_library
    
    def tearDown(self):
        pygame.quit()
    
    def test_game_list_state_initialization(self):
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=True),
        ]
        
        self.mock_game_library.get_all_games.return_value = test_games
        
        self.game_list_state.on_enter(None)
        
        self.assertEqual(self.game_list_state.selected_index, 0)
        self.assertEqual(self.game_list_state.scroll_offset, 0)
    
    def test_game_list_state_on_enter(self):
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=True),
        ]
        
        self.mock_game_library.get_all_games.return_value = test_games
        
        self.game_list_state.on_enter(None)
        
        self.assertEqual(self.game_list_state.games, test_games)
    
    def test_game_list_state_on_exit(self):
        self.game_list_state.on_exit()
    
    def test_game_list_state_update(self):
        self.game_list_state.update(0.016)
    
    def test_game_list_state_handle_events_navigate(self):
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=True),
            Game(game_id="game3", name="Game 3", installed=True),
        ]
        
        self.game_list_state.games = test_games
        self.game_list_state.selected_index = 0
        self.game_list_state.scroll_offset = 0
        
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,
            False,
            True,
            False,
            False,
        ]
        
        mock_events = [Mock()]
        
        with patch.object(self.game_list_state, '_handle_exit_input', return_value=False):
            self.game_list_state.handle_events(mock_events)
            
            self.assertEqual(self.game_list_state.selected_index, 1)
    
    def test_game_list_state_handle_events_confirm_launch(self):
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
        ]
        
        self.game_list_state.games = test_games
        self.game_list_state.selected_index = 0
        
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,
            False,
            False,
            True,
            False,
        ]
        
        mock_events = [Mock()]
        
        with patch.object(self.game_list_state, '_handle_exit_input', return_value=False):
            self.game_list_state.handle_events(mock_events)
            
            self.mock_state_manager.change_state.assert_called_once_with("playing")
    
    def test_game_list_state_render(self):
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=False),
        ]
        
        self.game_list_state.games = test_games
        self.game_list_state.selected_index = 0
        
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        
        with patch('pygame.font.Font', return_value=mock_font):
            with patch('pygame.draw.rect') as mock_draw_rect:
                self.game_list_state.render(mock_surface)
                
                mock_surface.fill.assert_called_once_with((20, 20, 30))
                self.assertTrue(mock_font.render.called)