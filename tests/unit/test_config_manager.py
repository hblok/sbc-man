"""
Unit Tests for ConfigManager Model

Tests for ConfigManager class.
"""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import shutil
import tempfile
import unittest
from src.hardware.paths import AppPaths

from src.models.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.hw_config = {
            "paths": {
                "data": self.temp_dir,
            },
            "display": {
                "resolution": [1280, 720],
                "fps_target": 60,
            },
        }

        self.app_paths = AppPaths()
        self.config = ConfigManager(self.hw_config, self.app_paths)

    def tearDown(self):
        
        shutil.rmtree(self.temp_dir)

    def test_config_manager_initialization(self):
        self.assertIsNotNone(self.config.hw_config)

    def test_get_config_value(self):
        resolution = self.config.get("display.resolution")
        
        self.assertEqual(resolution, [1280, 720])

    def test_get_with_default(self):
        value = self.config.get("nonexistent.key", "default_value")
        
        self.assertEqual(value, "default_value")

    def test_set_config_value(self):
        self.config.set("display.fps_target", 120)
        
        self.assertEqual(self.config.get("display.fps_target"), 120)

    def test_save_and_load_config(self):
        self.config.set("custom.setting", "test_value")
        self.config.save()
        
        config2 = ConfigManager(self.hw_config, self.app_paths)
        
        self.assertEqual(config2.get("custom.setting"), "test_value")

    def test_nested_config_access(self):
        self.config.set("level1.level2.level3", "deep_value")
        
        value = self.config.get("level1.level2.level3")
        
        self.assertEqual(value, "deep_value")