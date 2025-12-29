# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for ConfigLoader

Tests for configuration hierarchy loading and merging.
"""

from pathlib import Path
from unittest.mock import Mock, patch
import json
import shutil
import tempfile
import unittest

from sbcman.hardware.config_loader import ConfigLoader
from sbcman.hardware.paths import AppPaths


class TestConfigLoader(unittest.TestCase):
    """Test cases for ConfigLoader."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        
        # Create directory structure
        (self.config_dir / "devices").mkdir(parents=True)
        (self.config_dir / "os_types").mkdir(parents=True)
        
        # Create test AppPaths
        class TestAppPaths(AppPaths):
            def __init__(self, temp_dir):
                self._temp_dir = temp_dir
                self._base_dir = Path(temp_dir) / "data"
                self._temp_dir_name = temp_dir
            
            @property
            def src_config_dir(self):
                return Path(self._temp_dir_name) / "config"
        
        self.app_paths = TestAppPaths(self.temp_dir)
        
        # Create default config
        default_config = {
            "device_type": "default",
            "display": {
                "resolution": "auto",
                "fullscreen": False,
                "fps_target": 60
            },
            "paths": {
                "games": "~/games",
                "data": "~/.local/share/sbc-man"
            }
        }
        
        with open(self.config_dir / "devices" / "default.json", "w") as f:
            json.dump(default_config, f)
        
        # Create device-specific config
        device_config = {
            "device_type": "anbernic",
            "display": {
                "fullscreen": True,
                "hide_cursor": True
            },
            "paths": {
                "games": "/roms/ports"
            }
        }
        
        with open(self.config_dir / "devices" / "anbernic.json", "w") as f:
            json.dump(device_config, f)
        
        # Create OS-specific config
        os_config = {
            "os_type": "arkos",
            "display": {
                "fps_target": 30
            }
        }
        
        with open(self.config_dir / "os_types" / "arkos.json", "w") as f:
            json.dump(os_config, f)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_default_config(self):
        """Test loading default configuration."""
        loader = ConfigLoader("desktop", "standard_linux", {}, self.app_paths)
        loader.config_dir = self.config_dir
        
        # Mock user config path to return None
        with patch.object(loader, '_get_user_config_path', return_value=None):
            config = loader.load_config()
        
        self.assertEqual(config["device_type"], "default")
        # Resolution is "auto" in config, but gets replaced with default [1280, 720]
        # when no probed resolution is available
        self.assertEqual(config["display"]["resolution"], [1280, 720])

    def test_deep_merge(self):
        """Test deep merge of configurations."""
        loader = ConfigLoader("desktop", "standard_linux", {}, self.app_paths)
        
        base = {
            "display": {
                "resolution": [1280, 720],
                "fullscreen": False
            },
            "paths": {
                "games": "~/games"
            }
        }
        
        override = {
            "display": {
                "fullscreen": True,
                "fps_target": 60
            },
            "paths": {
                "data": "~/.local/share"
            }
        }
        
        result = loader._deep_merge(base, override)
        
        # Check that nested values are merged
        self.assertEqual(result["display"]["resolution"], [1280, 720])
        self.assertTrue(result["display"]["fullscreen"])
        self.assertEqual(result["display"]["fps_target"], 60)
        self.assertEqual(result["paths"]["games"], "~/games")
        self.assertEqual(result["paths"]["data"], "~/.local/share")

    def test_load_json_nonexistent(self):
        """Test loading non-existent JSON file."""
        loader = ConfigLoader("desktop", "standard_linux", {}, self.app_paths)
        
        result = loader._load_json(Path("/nonexistent/file.json"))
        
        self.assertIsNone(result)

    def test_load_json_invalid(self):
        """Test loading invalid JSON file."""
        loader = ConfigLoader("desktop", "standard_linux", {}, self.app_paths)
        
        # Create invalid JSON file
        invalid_file = Path(self.temp_dir) / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{ invalid json }")
        
        result = loader._load_json(invalid_file)
        
        self.assertIsNone(result)

    def test_apply_probed_hardware(self):
        """Test applying probed hardware to configuration."""
        probed_hardware = {
            "display": {
                "current_resolution": [1920, 1080]
            }
        }
        
        loader = ConfigLoader("desktop", "standard_linux", probed_hardware, self.app_paths)
        
        config = {
            "display": {
                "resolution": "auto",
                "fps_target": 60
            }
        }
        
        loader._apply_probed_hardware(config)
        
        # Resolution should be replaced with probed value
        self.assertEqual(config["display"]["resolution"], [1920, 1080])
        # Probed hardware should be stored
        self.assertIn("probed_hardware", config)

    def test_hierarchy_merge_order(self):
        """Test that configuration hierarchy is applied in correct order."""
        # Use empty probed hardware to avoid auto-resolution
        loader = ConfigLoader("anbernic", "arkos", {"display": {}}, self.app_paths)
        loader.config_dir = self.config_dir
        
        # Mock user config path to return None (no user config)
        with patch.object(loader, '_get_user_config_path', return_value=None):
            config = loader.load_config()
        
        # Check that values are merged correctly
        # Default: resolution=auto, fullscreen=False, fps_target=60
        # Device (anbernic): fullscreen=True, hide_cursor=True
        # OS (arkos): fps_target=30
        # Note: resolution "auto" gets replaced with default [1280, 720] when no probed resolution
        
        self.assertEqual(config["display"]["resolution"], [1280, 720])  # From default (auto -> [1280, 720])
        self.assertTrue(config["display"]["fullscreen"])  # From device
        self.assertEqual(config["display"]["fps_target"], 30)  # From OS (overrides default)
        self.assertTrue(config["display"]["hide_cursor"])  # From device
