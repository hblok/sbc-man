# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Test Configuration and Fixtures

Provides common fixtures and setup for all tests.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set SDL to dummy mode for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Mock protobuf modules that may not be compiled
sys.modules['sbcman.proto.game_pb2'] = MagicMock()
sys.modules['sbcman.proto.device_config_pb2'] = MagicMock()
sys.modules['sbcman.proto.os_config_pb2'] = MagicMock()
sys.modules['sbcman.proto.input_mappings_pb2'] = MagicMock()


def mock_hw_config():
    """Create a minimal hardware configuration for testing."""
    return {
        "detected_device": "desktop",
        "detected_os": "standard_linux",
        "display": {
            "resolution": [1280, 720],
            "fullscreen": False,
            "fps_target": 60,
            "hide_cursor": False,
        },
        "input": {
            "joystick_enabled": True,
            "keyboard_enabled": True,
        },
        "paths": {
            "games": str(Path.home() / "games"),
            "data": str(Path.home() / ".local/share/sbc-man"),
            "config": str(Path.home() / ".config/sbc-man"),
        },
        "probed_hardware": {
            "display": {
                "current_resolution": [1280, 720],
                "available_modes": [],
                "hardware_accelerated": False,
                "bit_depth": 32,
            },
            "input": {
                "has_keyboard": True,
                "joystick_count": 0,
                "joysticks": [],
            },
            "storage": {},
            "cpu": {
                "core_count": 4,
                "architecture": "x86",
            },
        },
    }


def mock_game_data():
    """Create sample game data for testing."""
    return [
        {
            "id": "test-game-1",
            "name": "Test Game 1",
            "version": "1.0.0",
            "description": "A test game",
            "author": "Test Author",
            "install_path": "/tmp/games/test-game-1",
            "entry_point": "main.py",
            "installed": True,
            "download_url": "https://example.com/game1.zip",
            "custom_input_mappings": {},
            "custom_resolution": None,
            "custom_fps": None,
        },
        {
            "id": "test-game-2",
            "name": "Test Game 2",
            "version": "2.0.0",
            "description": "Another test game",
            "author": "Test Author",
            "install_path": "/tmp/games/test-game-2",
            "entry_point": "main.py",
            "installed": False,
            "download_url": "https://example.com/game2.zip",
            "custom_input_mappings": {},
            "custom_resolution": None,
            "custom_fps": None,
        },
    ]


class TempConfigDir:
    """Context manager for temporary config directory."""
    
    def __init__(self):
        self.temp_dir = None
        self.devices_dir = None
        self.os_types_dir = None
        self.input_mappings_dir = None
    
    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.devices_dir = Path(self.temp_dir) / "devices"
        self.os_types_dir = Path(self.temp_dir) / "os_types"
        self.input_mappings_dir = Path(self.temp_dir) / "input_mappings"
        
        # Create directories
        self.devices_dir.mkdir(parents=True)
        self.os_types_dir.mkdir(parents=True)
        self.input_mappings_dir.mkdir(parents=True)
        
        # Create default config files
        default_device = {
            "device_type": "default",
            "display": {"resolution": "auto", "fullscreen": False, "fps_target": 60},
            "paths": {"games": "~/games", "data": "~/.local/share/sbc-man"},
        }
        
        with open(self.devices_dir / "default.json", "w") as f:
            json.dump(default_device, f)
        
        default_input = {
            "confirm": ["BUTTON_A", "RETURN"],
            "cancel": ["BUTTON_B", "ESCAPE"],
            "up": ["DPAD_UP", "UP"],
            "down": ["DPAD_DOWN", "DOWN"],
        }
        
        with open(self.input_mappings_dir / "default.json", "w") as f:
            json.dump(default_input, f)
        
        return self
    
    def __exit__(self, *args):
        import shutil
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)


class TempDataDir:
    """Context manager for temporary data directory."""
    
    def __init__(self):
        self.temp_dir = None
        self.games_file = None
        self.config_file = None
    
    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.games_file = Path(self.temp_dir) / "games.json"
        self.config_file = Path(self.temp_dir) / "config.json"
        
        # Create empty files
        with open(self.games_file, "w") as f:
            json.dump([], f)
        
        with open(self.config_file, "w") as f:
            json.dump({}, f)
        
        return self
    
    def __exit__(self, *args):
        import shutil
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)
