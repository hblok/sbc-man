"""
Unit Tests for InputHandler

Tests for layered input mapping system.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import shutil

from src.services.input_handler import InputHandler
from src.hardware.paths import AppPaths
import pathlib


class TestInputHandler(unittest.TestCase):
    """Test cases for InputHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create config directory structure
        config_dir = Path(self.temp_dir) / "config" / "input_mappings"
        config_dir.mkdir(parents=True)
        
        # Create data directory structure
        data_dir = Path(self.temp_dir) / "data" / "input_overrides"
        data_dir.mkdir(parents=True)
        (data_dir / "games").mkdir()
        
        # Create default input mapping
        default_mapping = {
            "confirm": ["BUTTON_A", "RETURN"],
            "cancel": ["BUTTON_B", "ESCAPE"],
            "up": ["DPAD_UP", "UP"],
            "down": ["DPAD_DOWN", "DOWN"]
        }
        
        with open(config_dir / "default.json", "w") as f:
            json.dump(default_mapping, f)
        
        # Create device-specific mapping
        device_mapping = {
            "confirm": ["BUTTON_SOUTH"],
            "menu": ["BUTTON_START"]
        }
        
        with open(config_dir / "anbernic.json", "w") as f:
            json.dump(device_mapping, f)
        
        self.hw_config = {
            "detected_device": "anbernic",
            "paths": {
                "data": str(data_dir.parent)
            }
        }

        # Create a custom AppPaths for testing
        class TestAppPaths(AppPaths):
            def __init__(self, temp_dir):
                self._temp_dir = pathlib.Path(temp_dir)
                self._base_dir = pathlib.Path(temp_dir) / "data"
                self._temp_dir_name = temp_dir
            
            @property
            def config_dir(self):
                return pathlib.Path(self._temp_dir_name) / "config"
            
            @property
            def config_input_mappings(self):
                return pathlib.Path(self._temp_dir_name) / "config" / "input_mappings"
            
            @property
            def input_mappings(self):
                return pathlib.Path(self._temp_dir_name) / "config" / "input_mappings"
            
            @property
            def input_overrides(self):
                return pathlib.Path(self._temp_dir_name) / "data" / "input_overrides"
        
        app_paths = TestAppPaths(self.temp_dir)
        
        self.handler = InputHandler(self.hw_config, app_paths)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.init")
    def test_input_handler_initialization(self, mock_joystick_init, mock_get_count):
        """Test input handler initialization."""
        mock_get_count.return_value = 0
        
        # Load mapping hierarchy (already configured in setUp)
        self.handler._load_mapping_hierarchy()
        
        self.assertIsNotNone(self.handler.mappings)
        self.assertIn("confirm", self.handler.mappings)

    def test_get_button_names(self):
        # Test button 0 (A button)
        names = self.handler._get_button_names(0)
        self.assertIn("BUTTON_A", names)
        self.assertIn("BUTTON_SOUTH", names)
        self.assertIn("BUTTON_0", names)
        
        # Test button 7 (Start button)
        names = self.handler._get_button_names(7)
        self.assertIn("BUTTON_START", names)

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.init")
    def test_set_game_context(self, mock_joystick_init, mock_get_count):
        """Test setting game context for per-game mappings."""
        mock_get_count.return_value = 0
        
        # Set game context
        self.handler.set_game_context("test-game")
        
        self.assertEqual(self.handler.current_game_id, "test-game")

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.init")
    def test_clear_game_context(self, mock_joystick_init, mock_get_count):
        """Test clearing game context."""
        mock_get_count.return_value = 0
        
        self.handler.set_game_context("test-game")
        
        # Clear context
        self.handler.clear_game_context()
        
        self.assertIsNone(self.handler.current_game_id)

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.init")
    def test_is_action_pressed_keyboard(self, mock_joystick_init, mock_get_count):
        """Test action detection with keyboard events."""
        import pygame
        
        mock_get_count.return_value = 0

        # Load mapping hierarchy (already configured in setUp)
        self.handler._load_mapping_hierarchy()
        
        # Test with "cancel" action which has ESCAPE in default mapping
        # and is not overridden by device mapping
        self.assertIn("cancel", self.handler.mappings)
        
        # Mock keyboard event for ESCAPE key
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE
        
        result = self.handler.is_action_pressed("cancel", [event])
        
        # Should match because K_ESCAPE is checked explicitly in the code
        self.assertTrue(result)

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.init")
    def test_is_action_pressed_joystick(self, mock_joystick_init, mock_get_count):
        """Test action detection with joystick button events."""
        import pygame
        
        mock_get_count.return_value = 0

        # Load mapping hierarchy (already configured in setUp)
        self.handler._load_mapping_hierarchy()
        
        # Mock joystick button event (button 0 = A button)
        event = Mock()
        event.type = pygame.JOYBUTTONDOWN
        event.button = 0
        
        result = self.handler.is_action_pressed("confirm", [event])
        
        # Should match because button 0 maps to BUTTON_A
        self.assertTrue(result)

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.init")
    def test_save_mapping(self, mock_joystick_init, mock_get_count):
        """Test saving custom input mapping."""
        mock_get_count.return_value = 0
        
        # Save a custom mapping
        self.handler.save_mapping("confirm", ["BUTTON_X", "SPACE"], scope="device")
        
        # Check that file was created
        device_mapping_file = self.handler.app_paths.input_overrides / "device.json"
        self.assertTrue(device_mapping_file.exists())
        
        # Check content
        with open(device_mapping_file, "r") as f:
            saved_mapping = json.load(f)
        
        self.assertEqual(saved_mapping["confirm"], ["BUTTON_X", "SPACE"])
