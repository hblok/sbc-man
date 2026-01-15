# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Scrollable List Widget

Tests for the adaptive scrollable list component that only scrolls
when content exceeds available space.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame

from sbcman.views.widgets.scrollable_list import ScrollableList


class TestScrollableList(unittest.TestCase):
    """Test cases for ScrollableList."""

    def setUp(self):
        """Set up test fixtures."""
        self.list_widget = ScrollableList(
            x=10,
            y=10,
            width=200,
            height=150,
            item_height=30,
            font_size=24,
            padding=10
        )

    def test_initialization(self):
        """Test scrollable list initialization."""
        self.assertEqual(self.list_widget.x, 10)
        self.assertEqual(self.list_widget.y, 10)
        self.assertEqual(self.list_widget.width, 200)
        self.assertEqual(self.list_widget.height, 150)
        self.assertEqual(self.list_widget.item_height, 30)
        self.assertEqual(self.list_widget.font_size, 24)
        self.assertEqual(self.list_widget.padding, 10)
        self.assertEqual(self.list_widget.selected_index, 0)
        self.assertEqual(self.list_widget.scroll_offset, 0)
        self.assertFalse(self.list_widget.needs_scrolling)
        self.assertFalse(self.list_widget.show_scroll_indicators)

    def test_set_items_empty(self):
        """Test setting empty items list."""
        self.list_widget.set_items([])
        
        self.assertEqual(len(self.list_widget.items), 0)
        self.assertFalse(self.list_widget.needs_scrolling)
        self.assertFalse(self.list_widget.show_scroll_indicators)

    def test_set_items_fits_in_space(self):
        """Test setting items that fit in available space."""
        # 3 items at 30px each = 90px, fits in 150px height with padding
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        
        self.assertEqual(len(self.list_widget.items), 3)
        self.assertFalse(self.list_widget.needs_scrolling)
        self.assertFalse(self.list_widget.show_scroll_indicators)
        self.assertEqual(self.list_widget.actual_height, 110)  # 90 + 20 padding

    def test_set_items_exceeds_space(self):
        """Test setting items that exceed available space."""
        # 10 items at 30px each = 300px, exceeds 150px height
        items = [f"Item {i}" for i in range(10)]
        self.list_widget.set_items(items)
        
        self.assertEqual(len(self.list_widget.items), 10)
        self.assertTrue(self.list_widget.needs_scrolling)
        self.assertTrue(self.list_widget.show_scroll_indicators)
        self.assertEqual(self.list_widget.actual_height, 150)  # Uses full height

    def test_set_items_with_states(self):
        """Test setting items with enabled/disabled states."""
        items = ["Item 1", "Item 2", "Item 3"]
        states = [True, False, True]
        self.list_widget.set_items(items, states)
        
        self.assertEqual(len(self.list_widget.items), 3)
        self.assertEqual(len(self.list_widget.item_states), 3)
        self.assertFalse(self.list_widget.item_states[1])

    def test_scroll_up_success(self):
        """Test successful scroll up."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 2
        
        result = self.list_widget.scroll_up()
        
        self.assertTrue(result)
        self.assertEqual(self.list_widget.selected_index, 1)

    def test_scroll_up_at_top(self):
        """Test scroll up when already at top."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 0
        
        result = self.list_widget.scroll_up()
        
        self.assertFalse(result)
        self.assertEqual(self.list_widget.selected_index, 0)

    def test_scroll_up_empty_list(self):
        """Test scroll up with empty list."""
        self.list_widget.set_items([])
        
        result = self.list_widget.scroll_up()
        
        self.assertFalse(result)

    def test_scroll_down_success(self):
        """Test successful scroll down."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 0
        
        result = self.list_widget.scroll_down()
        
        self.assertTrue(result)
        self.assertEqual(self.list_widget.selected_index, 1)

    def test_scroll_down_at_bottom(self):
        """Test scroll down when already at bottom."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 2
        
        result = self.list_widget.scroll_down()
        
        self.assertFalse(result)
        self.assertEqual(self.list_widget.selected_index, 2)

    def test_scroll_down_empty_list(self):
        """Test scroll down with empty list."""
        self.list_widget.set_items([])
        
        result = self.list_widget.scroll_down()
        
        self.assertFalse(result)

    def test_get_selected_item(self):
        """Test getting selected item."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 1
        
        result = self.list_widget.get_selected_item()
        
        self.assertEqual(result, "Item 2")

    def test_get_selected_item_empty(self):
        """Test getting selected item from empty list."""
        self.list_widget.set_items([])
        
        result = self.list_widget.get_selected_item()
        
        self.assertIsNone(result)

    def test_get_selected_item_invalid_index(self):
        """Test getting selected item with invalid index."""
        items = ["Item 1", "Item 2"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 5
        
        result = self.list_widget.get_selected_item()
        
        self.assertIsNone(result)

    def test_get_selected_index(self):
        """Test getting selected index."""
        self.list_widget.selected_index = 3
        
        result = self.list_widget.get_selected_index()
        
        self.assertEqual(result, 3)

    def test_ensure_selection_visible_no_scrolling_needed(self):
        """Test ensure_selection_visible when no scrolling needed."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)  # Fits in space
        self.list_widget.selected_index = 1
        
        self.list_widget._ensure_selection_visible()
        
        self.assertEqual(self.list_widget.scroll_offset, 0)

    def test_ensure_selection_visible scrolls_into_view(self):
        """Test ensure_selection_visible scrolls selection into view."""
        # Create list that needs scrolling
        items = [f"Item {i}" for i in range(10)]
        self.list_widget.set_items(items)
        
        # Select item beyond visible range
        self.list_widget.selected_index = 8
        
        self.list_widget._ensure_selection_visible()
        
        # Scroll offset should adjust to make selection visible
        self.assertGreater(self.list_widget.scroll_offset, 0)

    def test_ensure_selection_visible_above_view(self):
        """Test ensure_selection_visible when selection is above view."""
        # Create list that needs scrolling
        items = [f"Item {i}" for i in range(10)]
        self.list_widget.set_items(items)
        self.list_widget.scroll_offset = 5
        self.list_widget.selected_index = 3
        
        self.list_widget._ensure_selection_visible()
        
        # Scroll offset should adjust to show selection
        self.assertLessEqual(self.list_widget.scroll_offset, self.list_widget.selected_index)

    def test_validate_scroll_offset_bounds(self):
        """Test scroll offset is validated to valid bounds."""
        items = [f"Item {i}" for i in range(10)]
        self.list_widget.set_items(items)
        
        # Set offset beyond max
        self.list_widget.scroll_offset = 20
        self.list_widget._validate_scroll_offset()
        
        # Should be clamped to max
        max_offset = max(0, len(items) - self.list_widget.visible_items_count)
        self.assertEqual(self.list_widget.scroll_offset, max_offset)

    def test_validate_scroll_offset_negative(self):
        """Test scroll offset is validated when negative."""
        items = [f"Item {i}" for i in range(5)]
        self.list_widget.set_items(items)
        
        # Set negative offset
        self.list_widget.scroll_offset = -5
        self.list_widget._validate_scroll_offset()
        
        # Should be clamped to 0
        self.assertEqual(self.list_widget.scroll_offset, 0)

    def test_truncate_text_fits(self):
        """Test text truncation when text fits."""
        text = "Short text"
        result = self.list_widget._truncate_text(text, max_width=200)
        
        self.assertEqual(result, text)

    def test_truncate_text_too_long(self):
        """Test text truncation when text is too long."""
        text = "This is a very long text that should be truncated"
        result = self.list_widget._truncate_text(text, max_width=50)
        
        self.assertNotEqual(result, text)
        self.assertTrue(result.endswith("..."))
        self.assertLess(len(result), len(text))

    def test_truncate_text_empty(self):
        """Test truncating empty text."""
        result = self.list_widget._truncate_text("", max_width=100)
        
        self.assertEqual(result, "")

    def test_handle_event_key_down(self):
        """Test handling KEYDOWN events."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        
        # Create KEYDOWN event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})
        
        result = self.list_widget.handle_event(event)
        
        self.assertTrue(result)
        self.assertEqual(self.list_widget.selected_index, 1)

    def test_handle_event_page_up(self):
        """Test handling PAGEUP event."""
        items = [f"Item {i}" for i in range(10)]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 5
        
        # Create PAGEUP event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_PAGEUP})
        
        result = self.list_widget.handle_event(event)
        
        self.assertTrue(result)
        self.assertEqual(self.list_widget.selected_index, 0)

    def test_handle_event_page_down(self):
        """Test handling PAGEDOWN event."""
        items = [f"Item {i}" for i in range(10)]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 0
        
        # Create PAGEDOWN event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_PAGEDOWN})
        
        result = self.list_widget.handle_event(event)
        
        self.assertTrue(result)
        # Should jump by visible_items_count
        expected = min(len(items) - 1, self.list_widget.visible_items_count)
        self.assertEqual(self.list_widget.selected_index, expected)

    def test_handle_event_home(self):
        """Test handling HOME event."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 2
        
        # Create HOME event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_HOME})
        
        result = self.list_widget.handle_event(event)
        
        self.assertTrue(result)
        self.assertEqual(self.list_widget.selected_index, 0)
        self.assertEqual(self.list_widget.scroll_offset, 0)

    def test_handle_event_end(self):
        """Test handling END event."""
        items = ["Item 1", "Item 2", "Item 3"]
        self.list_widget.set_items(items)
        self.list_widget.selected_index = 0
        
        # Create END event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_END})
        
        result = self.list_widget.handle_event(event)
        
        self.assertTrue(result)
        self.assertEqual(self.list_widget.selected_index, len(items) - 1)

    def test_handle_event_unhandled(self):
        """Test handling unhandled event."""
        # Create non-keyboard event
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN)
        
        result = self.list_widget.handle_event(event)
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()