# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Hardware Prober

Tests for HardwareProber class.
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from sbcman.hardware.prober import HardwareProber


class TestHardwareProber(unittest.TestCase):

    def test_probe_display(self):
        
        mock_info = Mock()
        mock_info.current_w = 1920
        mock_info.current_h = 1080
        mock_info.hw = True
        mock_info.bitsize = 32
        mock_info.video_mem = 256
        
        with patch.object(pygame.display, 'Info', return_value=mock_info):
            with patch.object(pygame.display, 'list_modes', return_value=[]):
                display_info = HardwareProber.probe_display()
        
        self.assertEqual(display_info["current_resolution"], [1920, 1080])
        self.assertTrue(display_info["hardware_accelerated"])
        self.assertEqual(display_info["bit_depth"], 32)

    @patch("pygame.joystick.get_count")
    @patch("pygame.joystick.Joystick")
    def test_probe_input(self, mock_joystick_class, mock_get_count):
        mock_get_count.return_value = 1
        
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
        mock_exists.return_value = True
        mock_access.return_value = True
        
        mock_usage = Mock()
        mock_usage.total = 1000000000
        mock_usage.used = 500000000
        mock_usage.free = 500000000
        mock_disk_usage.return_value = mock_usage
        
        storage_info = HardwareProber.probe_storage()
        
        self.assertGreater(len(storage_info), 0)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_probe_cpu(self, mock_read_text, mock_exists):
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