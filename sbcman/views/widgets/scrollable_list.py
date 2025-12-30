# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Scrollable List Widget Module

Provides a reusable scrolling component for lists that need to fit
within constrained screen dimensions (640x480).
"""

import pygame
from typing import List, Callable, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ScrollableList:
    """
    A scrollable list widget for displaying items within constrained screen space.
    
    Designed specifically for 640x480 resolution devices where content may
    exceed available vertical space and requires scrolling functionality.
    """
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int,
                 item_height: int = 40,
                 font_size: int = 32,
                 padding: int = 10):
        """
        Initialize the scrollable list.
        
        Args:
            x: X position of the list
            y: Y position of the list
            width: Width of the list
            height: Height of the list (visible area)
            item_height: Height of each list item
            font_size: Font size for text rendering
            padding: Internal padding
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.item_height = item_height
        self.font_size = font_size
        self.padding = padding
        
        # Scrolling state
        self.items: List[str] = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_items_count = (height - 2 * padding) // item_height
        
        # Visual settings
        self.bg_color = (20, 20, 30)
        self.selected_bg_color = (50, 50, 80)
        self.text_color = (255, 255, 255)
        self.selected_text_color = (255, 255, 0)
        self.disabled_text_color = (150, 150, 150)
        self.border_color = (100, 100, 100)
        
        # Fonts
        self.font = pygame.font.Font(None, font_size)
        
        # Scroll indicators
        self.show_scroll_indicators = True
        self.scroll_indicator_color = (100, 100, 100)
        
    def set_items(self, items: List[str], item_states: Optional[List[bool]] = None) -> None:
        """
        Set the list items.
        
        Args:
            items: List of item strings to display
            item_states: Optional list of booleans indicating if items are enabled/disabled
        """
        self.items = items
        self.selected_index = min(self.selected_index, len(items) - 1) if items else 0
        self.scroll_offset = 0
        self.item_states = item_states or [True] * len(items)
        
        # Ensure scroll offset is valid
        self._validate_scroll_offset()
        
    def scroll_up(self) -> bool:
        """
        Scroll the selection up.
        
        Returns:
            True if selection changed, False otherwise
        """
        if not self.items or self.selected_index <= 0:
            return False
            
        self.selected_index -= 1
        self._ensure_selection_visible()
        return True
        
    def scroll_down(self) -> bool:
        """
        Scroll the selection down.
        
        Returns:
            True if selection changed, False otherwise
        """
        if not self.items or self.selected_index >= len(self.items) - 1:
            return False
            
        self.selected_index += 1
        self._ensure_selection_visible()
        return True
        
    def get_selected_item(self) -> Optional[str]:
        """
        Get the currently selected item.
        
        Returns:
            Selected item string or None if no items
        """
        if not self.items or self.selected_index >= len(self.items):
            return None
        return self.items[self.selected_index]
        
    def get_selected_index(self) -> int:
        """Get the current selected index."""
        return self.selected_index
        
    def _ensure_selection_visible(self) -> None:
        """Ensure the selected item is visible in the viewport."""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_items_count:
            self.scroll_offset = self.selected_index - self.visible_items_count + 1
            
        self._validate_scroll_offset()
        
    def _validate_scroll_offset(self) -> None:
        """Ensure scroll offset is within valid bounds."""
        max_offset = max(0, len(self.items) - self.visible_items_count)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
        
    def render(self, surface: pygame.Surface) -> None:
        """
        Render the scrollable list to the surface.
        
        Args:
            surface: Pygame surface to render on
        """
        # Draw background
        pygame.draw.rect(surface, self.bg_color, (self.x, self.y, self.width, self.height))
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.width, self.height), 2)
        
        if not self.items:
            # Draw empty state
            empty_text = self.font.render("No items available", True, self.disabled_text_color)
            text_rect = empty_text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            surface.blit(empty_text, text_rect)
            return
            
        # Calculate visible range
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_items_count, len(self.items))
        
        # Render visible items
        current_y = self.y + self.padding
        
        for i in range(start_idx, end_idx):
            item_text = self.items[i]
            is_selected = (i == self.selected_index)
            is_enabled = self.item_states[i] if i < len(self.item_states) else True
            
            # Draw selection background
            if is_selected:
                pygame.draw.rect(surface, self.selected_bg_color, 
                               (self.x + self.padding, current_y - 2, 
                                self.width - 2 * self.padding, self.item_height))
            
            # Choose text color based on state
            text_color = self.selected_text_color if is_selected else \
                        (self.text_color if is_enabled else self.disabled_text_color)
            
            # Render text (truncate if too long)
            max_text_width = self.width - 4 * self.padding
            rendered_text = self._truncate_text(item_text, max_text_width)
            text_surface = self.font.render(rendered_text, True, text_color)
            surface.blit(text_surface, (self.x + 2 * self.padding, current_y + 5))
            
            current_y += self.item_height
            
        # Draw scroll indicators if needed
        if self.show_scroll_indicators and len(self.items) > self.visible_items_count:
            self._render_scroll_indicators(surface)
            
    def _truncate_text(self, text: str, max_width: int) -> str:
        """
        Truncate text to fit within maximum width.
        
        Args:
            text: Text to truncate
            max_width: Maximum width in pixels
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if not text:
            return text
            
        # Check if text fits
        text_surface = self.font.render(text, True, self.text_color)
        if text_surface.get_width() <= max_width:
            return text
            
        # Binary search for optimal truncation
        ellipsis = "..."
        ellipsis_width = self.font.render(ellipsis, True, self.text_color).get_width()
        available_width = max_width - ellipsis_width
        
        if available_width <= 0:
            return ellipsis
            
        low, high = 0, len(text)
        best_text = text
        
        while low <= high:
            mid = (low + high) // 2
            test_text = text[:mid]
            test_surface = self.font.render(test_text, True, self.text_color)
            
            if test_surface.get_width() <= available_width:
                best_text = test_text
                low = mid + 1
            else:
                high = mid - 1
                
        return best_text + ellipsis
        
    def _render_scroll_indicators(self, surface: pygame.Surface) -> None:
        """
        Render scroll position indicators.
        
        Args:
            surface: Pygame surface to render on
        """
        # Draw scroll bar on the right side
        bar_x = self.x + self.width - 15
        bar_width = 8
        bar_height = self.height - 20
        bar_y = self.y + 10
        
        # Background bar
        pygame.draw.rect(surface, self.scroll_indicator_color, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Scroll thumb
        if len(self.items) > 0:
            thumb_height = max(20, int(bar_height * self.visible_items_count / len(self.items)))
            thumb_y = bar_y + int((self.height - 20 - thumb_height) * self.scroll_offset / 
                                (len(self.items) - self.visible_items_count))
            
            pygame.draw.rect(surface, (200, 200, 200), 
                           (bar_x, thumb_y, bar_width, thumb_height))
                           
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for scrolling.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            True if event was handled, False otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return self.scroll_up()
            elif event.key == pygame.K_DOWN:
                return self.scroll_down()
            elif event.key == pygame.K_PAGEUP:
                # Page up - move by visible items count
                self.selected_index = max(0, self.selected_index - self.visible_items_count)
                self._ensure_selection_visible()
                return True
            elif event.key == pygame.K_PAGEDOWN:
                # Page down - move by visible items count
                self.selected_index = min(len(self.items) - 1, 
                                        self.selected_index + self.visible_items_count)
                self._ensure_selection_visible()
                return True
            elif event.key == pygame.K_HOME:
                # Home - go to first item
                self.selected_index = 0
                self.scroll_offset = 0
                return True
            elif event.key == pygame.K_END:
                # End - go to last item
                self.selected_index = len(self.items) - 1
                self._ensure_selection_visible()
                return True
                
        return False