# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for ProgressBar

Tests for progress bar widget rendering and functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
import pygame

from sbcman.views.widgets.progress_bar import ProgressBar


class TestProgressBar(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.progress_bar = ProgressBar(x=100, y=100, width=400, height=30)

    def tearDown(self):
        pygame.quit()

    def test_initialization_default(self):
        progress_bar = ProgressBar(x=50, y=50, width=200)
        self.assertEqual(progress_bar.x, 50)
        self.assertEqual(progress_bar.y, 50)
        self.assertEqual(progress_bar.width, 200)
        self.assertEqual(progress_bar.height, 30)
        self.assertEqual(progress_bar.font_size, 24)
        self.assertEqual(progress_bar.background_color, (100, 100, 100))
        self.assertEqual(progress_bar.progress_color, (0, 200, 0))
        self.assertEqual(progress_bar.text_color, (255, 255, 255))
        self.assertIsNone(progress_bar._font)

    def test_initialization_custom(self):
        progress_bar = ProgressBar(
            x=10, y=20, width=300, height=40,
            font_size=32,
            background_color=(50, 50, 50),
            progress_color=(0, 255, 0),
            text_color=(200, 200, 200)
        )
        self.assertEqual(progress_bar.height, 40)
        self.assertEqual(progress_bar.font_size, 32)
        self.assertEqual(progress_bar.background_color, (50, 50, 50))
        self.assertEqual(progress_bar.progress_color, (0, 255, 0))
        self.assertEqual(progress_bar.text_color, (200, 200, 200))

    def test_get_font_creates_font(self):
        font = self.progress_bar._get_font()
        self.assertIsNotNone(font)
        self.assertIsNotNone(self.progress_bar._font)

    def test_get_font_caches_font(self):
        font1 = self.progress_bar._get_font()
        font2 = self.progress_bar._get_font()
        self.assertIs(font1, font2)

    def test_render_with_zero_progress(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, 0.0)

        self.assertIsNotNone(surface)

    def test_render_with_half_progress(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, 0.5)

        self.assertIsNotNone(surface)

    def test_render_with_full_progress(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, 1.0)

        self.assertIsNotNone(surface)

    def test_render_clamps_negative_progress(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, -0.5)

        self.assertIsNotNone(surface)

    def test_render_clamps_excess_progress(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, 1.5)

        self.assertIsNotNone(surface)

    def test_render_with_message(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, 0.75, "Downloading...")

        self.assertIsNotNone(surface)

    def test_render_without_message(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, 0.75)

        self.assertIsNotNone(surface)

    def test_render_uses_custom_colors(self):
        progress_bar = ProgressBar(
            x=100, y=100, width=400,
            background_color=(50, 50, 50),
            progress_color=(255, 0, 0)
        )
        surface = pygame.Surface((800, 600))

        progress_bar.render(surface, 0.5)

        self.assertIsNotNone(surface)

    def test_render_percentage_text(self):
        surface = pygame.Surface((800, 600))

        self.progress_bar.render(surface, 0.42)

        self.assertIsNotNone(surface)