"""
Unit Tests for Hardware Detection

Tests for HardwareDetector and HardwareProber.
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.hardware.detector import HardwareDetector
from src.hardware.prober import HardwareProber


class TestHardwareDetector(unittest.TestCase):
    """Test cases for HardwareDetector."""

    def test_detect_device_from_environment(self):
        """Test device detection from environment variable."""
        with patch.dict(os.environ, {"DEVICE_TYPE": "anbernic"}):
            device_type = HardwareDetector._detect_device()
            
            self.assertEqual(device_type, "anbernic")

    def test_detect_device_fallback_to_desktop(self):
        """Test device detection falls back to desktop."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                device_type = HardwareDetector._detect_device()
                
                self.assertEqual(device_type, "desktop")

    def test_detect_os_from_environment(self):
        """Test OS detection from environment variable."""
        with patch.dict(os.environ, {"OS_TYPE": "arkos"}):
            os_type = HardwareDetector._detect_os()
            
            self.assertEqual(os_type, "arkos")

    def test_detect_os_fallback_to_standard_linux(self):
        """Test OS detection falls back to standard_linux."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                os_type = HardwareDetector._detect_os()
                
                self.assertEqual(os_type, "standard_linux")

    def test_expand_paths(self):
        """Test path expansion with environment variables."""
        config = {
            "paths": {
                "home": "~/test",
                "data": "$HOME/data",
            }
        }
        
        HardwareDetector._expand_paths(config)
        
        # Paths should be expanded
        self.assertNotIn("~", config["paths"]["home"])
        self.assertNotIn("$HOME", config["paths"]["data"])

    def test_get_config(self):
        """Test complete config retrieval."""
        from src.hardware.prober import HardwareProber
        from src.hardware.config_loader import ConfigLoader
        
        # Mock probe results
        mock_probe_result = {
            "display": {"current_resolution": [1280, 720]},
            "input": {"joystick_count": 0},
            "storage": {},
            "cpu": {"core_count": 4},
        }
        
        # Mock config
        mock_config = {
            "display": {"resolution": [1280, 720]},
            "paths": {"data": "~/.local/share/sbc-man"},
        }
        
        with patch.object(HardwareProber, 'probe_all', return_value=mock_probe_result):
            with patch.object(ConfigLoader, 'load_config', return_value=mock_config):
                with patch.dict(os.environ, {"DEVICE_TYPE": "desktop", "OS_TYPE": "standard_linux"}):
                    config = HardwareDetector.get_config()
        
        self.assertIn("detected_device", config)
        self.assertIn("detected_os", config)
        self.assertEqual(config["detected_device"], "desktop")


class TestHardwareProber(unittest.TestCase):
    """Test cases for HardwareProber."""

    def test_probe_display(self):
        """Test display probing."""
        import pygame
        
        # Mock display info
        mock_info = Mock()
        mock_info.current_w = 1920
        mock_info.current_h = 1080
        mock_info.hw = True
        mock_info.bitsize = 32
        mock_info.video_mem = 256  # Set to an integer value
        
        with patch.object(pygame.display, 'Info', return_value=mock_info):
            with patch.object(pygame.display, 'list_modes', return_value=[]):
                display_info = HardwareProber.probe_display()
        
        self.assertEqual(display_info["current_resolution"], [1920, 1080])
        self.assertTrue(display_info["hardware_accelerated"])
        self.assertEqual(display_info["bit_depth"], 32)

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.Joystick")
    def test_probe_input(self, mock_joystick_class, mock_get_count):
        """Test input device probing."""
        mock_get_count.return_value = 1
        
        # Mock joystick
        mock_joystick = Mock()
        mock_joystick.get_name.return_value = "Test Controller"
        mock_joystick.get_numaxes.return_value = 4
        mock_joystick.get_numbuttons.return_value = 12
        mock_joystick.get_numhats.return_value = 1
        mock_joystick_class.return_value = mock_joystick
        
        input_info = HardwareProber.probe_input()
        
        self.assertTrue(input_info["has_keyboard"])
        self.assertEqual(input_info["joystick_count"], 1)
        self.assertEqual(len(input_info["joysticks"]), 1)

    @patch("os.access")
    @patch("shutil.disk_usage")
    @patch("pathlib.Path.exists")
    def test_probe_storage(self, mock_exists, mock_disk_usage, mock_access):
        """Test storage probing."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        # Mock disk usage
        mock_usage = Mock()
        mock_usage.total = 1000000000
        mock_usage.used = 500000000
        mock_usage.free = 500000000
        mock_disk_usage.return_value = mock_usage
        
        storage_info = HardwareProber.probe_storage()
        
        # Should have at least one storage location
        self.assertGreater(len(storage_info), 0)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_probe_cpu(self, mock_read_text, mock_exists):
        """Test CPU probing."""
        mock_exists.return_value = True
        mock_read_text.return_value = """
processor       : 0
processor       : 1
processor       : 2
processor       : 3
model name      : Intel(R) Core(TM) i5
"""
        
        cpu_info = HardwareProber.probe_cpu()
        
        self.assertEqual(cpu_info["core_count"], 4)
        self.assertEqual(cpu_info["architecture"], "x86")


if __name__ == "__main__":
    unittest.main()