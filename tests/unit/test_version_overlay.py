# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for VersionOverlay

Tests for version overlay widget rendering.
"""

import unittest
from unittest.mock import patch, MagicMock
import pygame

from sbcman.views.widgets.version_overlay import VersionOverlay


class TestVersionOverlay(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.overlay = VersionOverlay()

    def tearDown(self):
        pygame.quit()

    def test_initialization_default(self):
        overlay = VersionOverlay()
        self.assertEqual(overlay.font_size, 16)
        self.assertEqual(overlay.padding, 8)
        self.assertEqual(overlay.text_color, (120, 120, 120))
        self.assertIsNone(overlay._font)

    def test_initialization_custom(self):
        overlay = VersionOverlay(font_size=20, padding=10)
        self.assertEqual(overlay.font_size, 20)
        self.assertEqual(overlay.padding, 10)

    def test_get_font_creates_font(self):
        font = self.overlay._get_font()
        self.assertIsNotNone(font)
        self.assertIsNotNone(self.overlay._font)

    def test_get_font_caches_font(self):
        font1 = self.overlay._get_font()
        font2 = self.overlay._get_font()
        self.assertIs(font1, font2)

    def test_render_creates_surface(self):
        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600
        
        self.overlay.render(surface)
        
        surface.blit.assert_called_once()

    def test_render_position_bottom_right(self):
        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600
        
        self.overlay.render(surface)
        
        args, kwargs = surface.blit.call_args
        x, y = args[1]
        
        self.assertGreater(x, 700)
        self.assertGreaterEqual(y, 580)

    def test_render_uses_version_constant(self):
        with patch('sbcman.views.widgets.version_overlay.version') as mock_version:
            mock_version.VERSION = "1.0.0"
            
            surface = MagicMock()
            surface.get_width.return_value = 800
            surface.get_height.return_value = 600
            
            overlay = VersionOverlay()
            overlay.render(surface)
            
            surface.blit.assert_called_once()

    def test_render_respects_custom_font_size(self):
        overlay = VersionOverlay(font_size=24)
        
        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600
        
        overlay.render(surface)
        
        surface.blit.assert_called_once()

    def test_render_respects_custom_padding(self):
        overlay = VersionOverlay(padding=20)
        
        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600
        
        overlay.render(surface)
        
        args, kwargs = surface.blit.call_args
        x, y = args[1]
        
        self.assertLess(x, 800 - 20)

    def test_render_text_color(self):
        overlay = VersionOverlay()
        
        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600
        
        overlay.render(surface)
        
        surface.blit.assert_called_once()

    def test_multiple_renders(self):
        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600
        
        self.overlay.render(surface)
        self.overlay.render(surface)
        
        self.assertEqual(surface.blit.call_count, 2)

    def test_render_small_surface(self):
        surface = MagicMock()
        surface.get_width.return_value = 100
        surface.get_height.return_value = 50
        
        self.overlay.render(surface)
        
        args, kwargs = surface.blit.call_args
        x, y = args[1]
        
        self.assertGreaterEqual(x, 0)
        self.assertGreaterEqual(y, 0)

    def test_render_large_surface(self):
        surface = MagicMock()
        surface.get_width.return_value = 1920
        surface.get_height.return_value = 1080
        
        self.overlay.render(surface)
        
        args, kwargs = surface.blit.call_args
        x, y = args[1]
        
        self.assertLess(x, 1920)
        self.assertLess(y, 1080)

    def test_font_size_property(self):
        overlay = VersionOverlay(font_size=32)
        self.assertEqual(overlay.font_size, 32)

    def test_padding_property(self):
        overlay = VersionOverlay(padding=15)
        self.assertEqual(overlay.padding, 15)

    def test_text_color_property(self):
        overlay = VersionOverlay()
        self.assertEqual(overlay.text_color, (120, 120, 120))