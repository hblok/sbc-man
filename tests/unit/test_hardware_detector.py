"""
Unit Tests for Hardware Detection

Tests for HardwareDetector class.
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.hardware.detector import HardwareDetector
from src.hardware.prober import HardwareProber
from src.hardware.config_loader import ConfigLoader


class TestHardwareDetector(unittest.TestCase):

    def test_detect_device_from_environment(self):
        with patch.dict(os.environ, {"DEVICE_TYPE": "anbernic"}):
            device_type = HardwareDetector().detect_device()
            
            self.assertEqual(device_type, "anbernic")

    def test_detect_device_fallback_to_desktop(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                device_type = HardwareDetector().detect_device()
                
                self.assertEqual(device_type, "desktop")

    def test_detect_os_from_environment(self):
        with patch.dict(os.environ, {"OS_TYPE": "arkos"}):

            os_type = HardwareDetector().detect_os()
            
            self.assertEqual(os_type, "arkos")

    def test_detect_os_fallback_to_standard_linux(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                os_type = HardwareDetector().detect_os()
                
                self.assertEqual(os_type, "standard_linux")

    def test_expand_paths(self):
        config = {
            "paths": {
                "home": "~/test",
                "data": "$HOME/data",
            }
        }
        
        HardwareDetector().expand_paths(config)
        
        self.assertNotIn("~", config["paths"]["home"])

    def test_get_config(self):
        
        mock_probe_result = {
            "display": {"current_resolution": [1280, 720]},
            "input": {"joystick_count": 0},
            "storage": {},
            "cpu": {"core_count": 4},
        }
        
        mock_config = {
            "display": {"resolution": [1280, 720]},
            "paths": {"data": "~/.local/share/sbc-man"},
        }
        
        with patch.object(HardwareProber, 'probe_all', return_value=mock_probe_result):
            with patch.object(ConfigLoader, 'load_config', return_value=mock_config):
                with patch.dict(os.environ, {"DEVICE_TYPE": "desktop", "OS_TYPE": "standard_linux"}):
                    config = HardwareDetector().get_config()
        
        self.assertIn("detected_device", config)
        self.assertIn("detected_os", config)
        self.assertEqual(config["detected_device"], "desktop")