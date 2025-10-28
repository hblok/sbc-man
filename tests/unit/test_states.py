"""
Unit Tests for State Modules

Tests for base state functionality and other state modules.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.states.base_state import BaseState
from src.states.menu_state import MenuState
from src.states.game_list_state import GameListState
from src.states.playing_state import PlayingState
from src.states.settings_state import SettingsState
from src.models.game import Game


class TestBaseState(unittest.TestCase):
    """Test cases for BaseState abstract base class."""
    
    def test_base_state_cannot_be_instantiated(self):
        """Test that BaseState cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            base_state = BaseState(Mock())


class TestMenuState(unittest.TestCase):
    """Test cases for MenuState."""
    
    def setUp(self):
        """Set up test fixtures."""
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
        """Clean up test fixtures."""
        pygame.quit()
    
    def test_menu_state_initialization(self):
        """Test menu state initialization."""
        self.menu_state.on_enter(None)
        self.assertEqual(self.menu_state.selected_option, 0)
        self.assertEqual(len(self.menu_state.menu_options), 4)
    
    def test_menu_state_on_enter(self):
        """Test entering menu state."""
        self.menu_state.on_enter(None)
        # No specific assertions as on_enter mainly logs, but verify it doesn't raise an exception
    
    def test_menu_state_on_exit(self):
        """Test exiting menu state."""
        self.menu_state.on_exit()
        # No specific assertions as on_exit mainly logs, but verify it doesn't raise an exception
    
    def test_menu_state_update(self):
        """Test updating menu state."""
        self.menu_state.update(0.016)  # ~60 FPS
        # No specific assertions as update does nothing, but verify it doesn't raise an exception
    
    def test_menu_state_handle_events_navigate_down(self):
        """Test handling navigation down events."""
        self.menu_state.on_enter(None)
        self.menu_state.selected_option = 0
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.menu_state, '_handle_exit_input', return_value=False):
            # Set up mock input handler - need to call it multiple times in the right order
            self.mock_input_handler.is_action_pressed.side_effect = lambda action, events: {
                "up": False,
                "down": True,
                "confirm": False,
            }.get(action, False)
            
            self.menu_state.handle_events(mock_events)
            
            # Verify selected option was incremented
            self.assertEqual(self.menu_state.selected_option, 1)
    
    def test_menu_state_handle_events_navigate_up(self):
        """Test handling navigation up events."""
        self.menu_state.on_enter(None)
        self.menu_state.selected_option = 1
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.menu_state, '_handle_exit_input', return_value=False):
            # Set up mock input handler - need to call it multiple times in the right order
            self.mock_input_handler.is_action_pressed.side_effect = lambda action, events: {
                "up": True,
                "down": False,
                "confirm": False,
            }.get(action, False)
            
            self.menu_state.handle_events(mock_events)
            
            # Verify selected option was decremented
            self.assertEqual(self.menu_state.selected_option, 0)
    
    def test_menu_state_handle_events_confirm_selection(self):
        """Test handling confirm action events."""
        self.menu_state.on_enter(None)
        
        test_cases = [
            (0, "game_list"),    # Browse Games
            (1, "download"),     # Download Games
            (2, "settings"),     # Settings
        ]
        
        for selected_option, expected_state in test_cases:
            with self.subTest(selected_option=selected_option):
                # Reset mocks
                self.mock_state_manager.reset_mock()
                self.mock_input_handler.reset_mock()
                
                # Set up menu state
                self.menu_state.selected_option = selected_option
                
                # Create a mock event list
                mock_events = [Mock()]
                
                # Handle events
                with patch.object(self.menu_state, '_handle_exit_input', return_value=False):
                    # Set up mock input handler - need to call it multiple times in the right order
                    self.mock_input_handler.is_action_pressed.side_effect = lambda action, events: {
                        "up": False,
                        "down": False,
                        "confirm": True,
                    }.get(action, False)
                    
                    self.menu_state.handle_events(mock_events)
                    
                    # Verify the correct method was called
                    self.mock_state_manager.change_state.assert_called_once_with(expected_state)
    
    def test_menu_state_render(self):
        """Test rendering menu state."""
        self.menu_state.on_enter(None)
        
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        mock_font.render.return_value.get_rect.return_value = Mock(center=(640, 100))
        
        # Render the state
        with patch('pygame.font.Font', return_value=mock_font):
            with patch('pygame.draw.rect') as mock_draw_rect:
                self.menu_state.render(mock_surface)
                
                # Verify surface operations
                mock_surface.fill.assert_called_once_with((20, 20, 30))
                self.assertTrue(mock_font.render.called)


class TestGameListState(unittest.TestCase):
    """Test cases for GameListState."""
    
    def setUp(self):
        """Set up test fixtures."""
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
        """Clean up test fixtures."""
        pygame.quit()
    
    def test_game_list_state_initialization(self):
        """Test game list state initialization."""
        # Create test games
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=True),
        ]
        
        # Configure mock game library
        self.mock_game_library.get_all_games.return_value = test_games
        
        # Enter the state
        self.game_list_state.on_enter(None)
        
        self.assertEqual(self.game_list_state.selected_index, 0)
        self.assertEqual(self.game_list_state.scroll_offset, 0)
    
    def test_game_list_state_on_enter(self):
        """Test entering game list state."""
        # Create test games
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=True),
        ]
        
        # Configure mock game library
        self.mock_game_library.get_all_games.return_value = test_games
        
        # Enter the state
        self.game_list_state.on_enter(None)
        
        # Verify games were loaded
        self.assertEqual(self.game_list_state.games, test_games)
    
    def test_game_list_state_on_exit(self):
        """Test exiting game list state."""
        self.game_list_state.on_exit()
        # No specific assertions as on_exit mainly logs, but verify it doesn't raise an exception
    
    def test_game_list_state_update(self):
        """Test updating game list state."""
        self.game_list_state.update(0.016)  # ~60 FPS
        # No specific assertions as update does nothing, but verify it doesn't raise an exception
    
    def test_game_list_state_handle_events_navigate(self):
        """Test handling navigation events."""
        # Create test games
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=True),
            Game(game_id="game3", name="Game 3", installed=True),
        ]
        
        # Set up the state
        self.game_list_state.games = test_games
        self.game_list_state.selected_index = 0
        self.game_list_state.scroll_offset = 0
        
        # Test navigating down
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,  # cancel
            False,  # up
            True,   # down
            False,  # confirm
            False,  # exit input
        ]
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.game_list_state, '_handle_exit_input', return_value=False):
            self.game_list_state.handle_events(mock_events)
            
            # Verify selected index was incremented
            self.assertEqual(self.game_list_state.selected_index, 1)
    
    def test_game_list_state_handle_events_confirm_launch(self):
        """Test handling confirm action to launch a game."""
        # Create test games
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
        ]
        
        # Set up the state
        self.game_list_state.games = test_games
        self.game_list_state.selected_index = 0
        
        # Set up mock input handler
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,  # cancel
            False,  # up
            False,  # down
            True,   # confirm
            False,  # exit input
        ]
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.game_list_state, '_handle_exit_input', return_value=False):
            self.game_list_state.handle_events(mock_events)
            
            # Verify state transition was requested
            self.mock_state_manager.change_state.assert_called_once_with("playing")
    
    def test_game_list_state_render(self):
        """Test rendering game list state."""
        # Create test games
        test_games = [
            Game(game_id="game1", name="Game 1", installed=True),
            Game(game_id="game2", name="Game 2", installed=False),
        ]
        
        # Set up the state
        self.game_list_state.games = test_games
        self.game_list_state.selected_index = 0
        
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        
        # Render the state
        with patch('pygame.font.Font', return_value=mock_font):
            with patch('pygame.draw.rect') as mock_draw_rect:
                self.game_list_state.render(mock_surface)
                
                # Verify surface operations
                mock_surface.fill.assert_called_once_with((20, 20, 30))
                self.assertTrue(mock_font.render.called)


class TestPlayingState(unittest.TestCase):
    """Test cases for PlayingState."""
    
    def setUp(self):
        """Set up test fixtures."""
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
        """Clean up test fixtures."""
        pygame.quit()
    
    def test_playing_state_initialization(self):
        """Test playing state initialization."""
        self.playing_state.on_enter(None)
        self.assertTrue(self.playing_state.game_running)
        self.assertIsNotNone(self.playing_state.launcher)
    
    def test_playing_state_on_enter(self):
        """Test entering playing state."""
        # Enter the state
        self.playing_state.on_enter(None)
        
        # Verify state was initialized
        self.assertTrue(self.playing_state.game_running)
        self.assertIsNotNone(self.playing_state.launcher)
        self.assertEqual(self.playing_state.message, "Game would be launched here")
    
    def test_playing_state_on_exit(self):
        """Test exiting playing state."""
        # Enter the state first
        self.playing_state.on_enter(None)
        
        # Exit the state
        self.playing_state.on_exit()
        
        # Verify game_running was set to False
        self.assertFalse(self.playing_state.game_running)
    
    def test_playing_state_update(self):
        """Test updating playing state."""
        # Enter the state first
        self.playing_state.on_enter(None)
        
        # Update the state
        self.playing_state.update(0.016)  # ~60 FPS
        # No specific assertions as update does nothing, but verify it doesn't raise an exception
    
    def test_playing_state_handle_events_cancel(self):
        """Test handling cancel events."""
        # Enter the state first
        self.playing_state.on_enter(None)
        
        # Set up mock input handler
        self.mock_input_handler.is_action_pressed.side_effect = [
            True,   # cancel
            False,  # exit input
        ]
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.playing_state, '_handle_exit_input', return_value=False):
            self.playing_state.handle_events(mock_events)
            
            # Verify state transition was requested
            self.mock_state_manager.change_state.assert_called_once_with("game_list")
    
    def test_playing_state_render(self):
        """Test rendering playing state."""
        # Enter the state first
        self.playing_state.on_enter(None)
        
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        mock_font.render.return_value.get_rect.return_value = Mock(center=(640, 360))
        
        # Render the state
        with patch('pygame.font.Font', return_value=mock_font):
            self.playing_state.render(mock_surface)
            
            # Verify surface operations
            mock_surface.fill.assert_called_once_with((20, 20, 30))
            self.assertTrue(mock_font.render.called)


class TestSettingsState(unittest.TestCase):
    """Test cases for SettingsState."""
    
    def setUp(self):
        """Set up test fixtures."""
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
        """Clean up test fixtures."""
        pygame.quit()
    
    def test_settings_state_initialization(self):
        """Test settings state initialization."""
        self.settings_state.on_enter(None)
        self.assertEqual(self.settings_state.selected_option, 0)
        self.assertEqual(len(self.settings_state.settings_options), 4)
    
    def test_settings_state_on_enter(self):
        """Test entering settings state."""
        self.settings_state.on_enter(None)
        # No specific assertions as on_enter mainly logs, but verify it doesn't raise an exception
    
    def test_settings_state_on_exit(self):
        """Test exiting settings state."""
        # Set up mock config manager
        self.settings_state.config = Mock()
        
        # Exit the state
        self.settings_state.on_exit()
        
        # Verify config was saved
        self.settings_state.config.save.assert_called_once()
    
    def test_settings_state_update(self):
        """Test updating settings state."""
        self.settings_state.update(0.016)  # ~60 FPS
        # No specific assertions as update does nothing, but verify it doesn't raise an exception
    
    def test_settings_state_handle_events_navigation(self):
        """Test handling navigation events."""
        self.settings_state.on_enter(None)
        
        # Set up mock input handler for navigating down
        self.mock_input_handler.is_action_pressed.side_effect = [
            False,  # cancel
            False,  # up
            True,   # down
            False,  # confirm
            False,  # exit input
        ]
        
        # Create a mock event list
        mock_events = [Mock()]
        
        # Handle events
        with patch.object(self.settings_state, '_handle_exit_input', return_value=False):
            self.settings_state.handle_events(mock_events)
            
            # Verify selected option was incremented
            self.assertEqual(self.settings_state.selected_option, 1)
    
    def test_settings_state_render(self):
        """Test rendering settings state."""
        self.settings_state.on_enter(None)
        
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1280
        mock_surface.get_height.return_value = 720
        mock_surface.fill.return_value = None
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        
        # Render the state
        with patch('pygame.font.Font', return_value=mock_font):
            with patch('pygame.draw.rect') as mock_draw_rect:
                self.settings_state.render(mock_surface)
                
                # Verify surface operations
                mock_surface.fill.assert_called_once_with((20, 20, 30))
                self.assertTrue(mock_font.render.called)


if __name__ == "__main__":
    unittest.main()