# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for ScrollableIconList

Tests for scrollable list with icon and status indicator support.
"""

import unittest
from unittest.mock import patch, MagicMock
import pygame

from sbcman.views.widgets.scrollable_icon_list import ScrollableIconList


class TestScrollableIconList(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.list_widget = ScrollableIconList(
            x=10, y=20, width=300, height=200,
            item_height=60, font_size=24, padding=10, icon_size=40
        )

    def tearDown(self):
        pygame.quit()

    def test_initialization(self):
        widget = ScrollableIconList(
            x=10, y=20, width=300, height=200,
            item_height=60, font_size=24, padding=10, icon_size=40
        )
        self.assertEqual(widget.x, 10)
        self.assertEqual(widget.y, 20)
        self.assertEqual(widget.width, 300)
        self.assertEqual(widget.height, 200)
        self.assertEqual(widget.item_height, 60)
        self.assertEqual(widget.font_size, 24)
        self.assertEqual(widget.padding, 10)
        self.assertEqual(widget.icon_size, 40)
        self.assertTrue(widget.show_icons)

    def test_set_items_with_icons(self):
        items = ["Item 1", "Item 2"]
        icons = [MagicMock(), MagicMock()]
        
        self.list_widget.set_items(items, icons=icons)
        
        self.assertEqual(len(self.list_widget.items), 2)
        self.assertIsNotNone(self.list_widget.icons)

    def test_set_items_with_status_indicators(self):
        items = ["Item 1", "Item 2"]
        status = ["[Installed]", "[Update]"]
        
        self.list_widget.set_items(items, status_indicators=status)
        
        self.assertEqual(len(self.list_widget.items), 2)
        self.assertIsNotNone(self.list_widget.status_indicators)

    def test_set_items_invalid_icons_length(self):
        items = ["Item 1", "Item 2"]
        icons = [MagicMock()]
        
        with patch('sbcman.views.widgets.scrollable_icon_list.logger') as mock_logger:
            self.list_widget.set_items(items, icons=icons)
            self.assertIsNone(self.list_widget.icons)
            mock_logger.warning.assert_called()

    def test_set_items_invalid_status_length(self):
        items = ["Item 1", "Item 2"]
        status = ["[Installed]"]
        
        with patch('sbcman.views.widgets.scrollable_icon_list.logger') as mock_logger:
            self.list_widget.set_items(items, status_indicators=status)
            self.assertIsNone(self.list_widget.status_indicators)
            mock_logger.warning.assert_called()

    def test_set_items_empty(self):
        self.list_widget.set_items([])
        
        self.assertEqual(len(self.list_widget.items), 0)
        self.assertEqual(self.list_widget.selected_index, 0)

    def test_set_items_with_states(self):
        items = ["Item 1", "Item 2", "Item 3"]
        states = [True, False, True]
        
        self.list_widget.set_items(items, item_states=states)
        
        self.assertEqual(self.list_widget.item_states, states)

    def test_set_items_default_states(self):
        items = ["Item 1", "Item 2"]
        
        self.list_widget.set_items(items)
        
        self.assertEqual(self.list_widget.item_states, [True, True])

    def test_render_empty_list(self):
        surface = pygame.Surface((300, 200))
        
        self.list_widget.set_items([])
        
        self.list_widget.render(surface)

    def test_render_with_items(self):
        surface = pygame.Surface((300, 200))
        
        self.list_widget.set_items(["Item 1", "Item 2"])
        
        self.list_widget.render(surface)

    def test_render_with_icons(self):
        surface = pygame.Surface((300, 200))
        
        icons = [pygame.Surface((40, 40)), pygame.Surface((40, 40))]
        self.list_widget.set_items(["Item 1", "Item 2"], icons=icons)
        
        self.list_widget.render(surface)

    def test_render_with_status_indicators(self):
        surface = pygame.Surface((300, 200))
        
        status = ["[Installed]", "[Update]"]
        self.list_widget.set_items(["Item 1", "Item 2"], status_indicators=status)
        
        self.list_widget.render(surface)

    def test_render_respects_icon_visibility(self):
        surface = pygame.Surface((300, 200))
        
        self.list_widget.show_icons = False
        icons = [MagicMock(), MagicMock()]
        self.list_widget.set_items(["Item 1", "Item 2"], icons=icons)
        
        self.list_widget.render(surface)

    def test_selected_index_adjusts_on_set_items(self):
        self.list_widget.selected_index = 5
        self.list_widget.set_items(["Item 1", "Item 2"])
        
        self.assertEqual(self.list_widget.selected_index, 1)

    def test_scroll_offset_resets_on_set_items(self):
        self.list_widget.scroll_offset = 10
        self.list_widget.set_items(["Item 1", "Item 2", "Item 3"])
        
        self.assertEqual(self.list_widget.scroll_offset, 0)

    def test_icon_size_property(self):
        widget = ScrollableIconList(
            x=10, y=20, width=300, height=200,
            icon_size=50
        )
        self.assertEqual(widget.icon_size, 50)

    def test_show_icons_property(self):
        widget = ScrollableIconList(
            x=10, y=20, width=300, height=200
        )
        self.assertTrue(widget.show_icons)

    def test_set_items_with_all_parameters(self):
        items = ["Item 1", "Item 2"]
        states = [True, False]
        icons = [MagicMock(), MagicMock()]
        status = ["[OK]", "[Pending]"]
        
        self.list_widget.set_items(
            items,
            item_states=states,
            icons=icons,
            status_indicators=status
        )
        
        self.assertEqual(len(self.list_widget.items), 2)
        self.assertEqual(self.list_widget.item_states, states)
        self.assertEqual(self.list_widget.icons, icons)
        self.assertEqual(self.list_widget.status_indicators, status)

    def test_status_font_creation(self):
        self.assertIsNotNone(self.list_widget.status_font)

    def test_inherits_from_scrollable_list(self):
        from sbcman.views.widgets.scrollable_list import ScrollableList
        self.assertIsInstance(self.list_widget, ScrollableList)