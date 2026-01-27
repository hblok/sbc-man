# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Scrollable Icon List Widget Module

Provides a scrolling component that displays items with icons and status indicators.
Subclass of ScrollableList that adds support for visual enhancements.
"""

import pygame
from typing import List, Optional
import logging

from .scrollable_list import ScrollableList

logger = logging.getLogger(__name__)


class ScrollableIconList(ScrollableList):
    """Scrollable list with icon and status indicator support.
    
    Extends ScrollableList to display icons alongside text and show
    status indicators for each item.
    """
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int,
                 item_height: int = 60,
                 font_size: int = 24,
                 padding: int = 10,
                 icon_size: int = 40):
        """Initialize the scrollable icon list.
        
        Args:
            x: X position of the list
            y: Y position of the list
            width: Width of the list
            height: Height of the list (maximum available area)
            item_height: Height of each list item
            font_size: Font size for text rendering
            padding: Internal padding
            icon_size: Size of icons in pixels
        """
        super().__init__(x, y, width, height, item_height, font_size, padding)
        
        self.show_icons = True
        self.icon_size = icon_size
        
        # Additional font for status indicators
        self.status_font = pygame.font.Font(None, font_size - 4)
        
        # Icon and status support
        self.icons: Optional[List[pygame.Surface]] = None
        self.status_indicators: Optional[List[str]] = None
    
    def set_items(self, 
                 items: List[str], 
                 item_states: Optional[List[bool]] = None,
                 icons: Optional[List[pygame.Surface]] = None,
                 status_indicators: Optional[List[str]] = None) -> None:
        """Set the list items with optional icons and status indicators.
        
        Args:
            items: List of item strings to display
            item_states: Optional list of booleans indicating if items are enabled/disabled
            icons: Optional list of icon surfaces for each item
            status_indicators: Optional list of status indicator strings (e.g., "[Installed]", "[Update]")
        """
        self.items = items
        self.selected_index = min(self.selected_index, len(items) - 1) if items else 0
        self.scroll_offset = 0
        self.item_states = item_states or [True] * len(items)
        self.icons = icons
        self.status_indicators = status_indicators
        
        # Validate input lists have same length
        if icons and len(icons) != len(items):
            logger.warning(f"Icons list length ({len(icons)}) doesn't match items length ({len(items)})")
            self.icons = None
        
        if status_indicators and len(status_indicators) != len(items):
            logger.warning(f"Status indicators list length ({len(status_indicators)}) doesn't match items length ({len(items)})")
            self.status_indicators = None
        
        # Determine if scrolling is needed
        self._calculate_layout_requirements()
        
        # Ensure scroll offset is valid
        self._validate_scroll_offset()
    
    def _render_visible_items(self, surface: pygame.Surface, start_idx: int, end_idx: int) -> None:
        """Render visible items with icons and status indicators.
        
        Args:
            surface: Pygame surface to render on
            start_idx: Starting index of visible items
            end_idx: Ending index of visible items
        """
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
            
            # Calculate text position (account for icons)
            text_x = self.x + 2 * self.padding
            if self.show_icons and self.icons and i < len(self.icons):
                icon = self.icons[i]
                if icon:
                    # Draw icon
                    icon_y = current_y + (self.item_height - self.icon_size) // 2
                    surface.blit(icon, (text_x, icon_y))
                text_x += self.icon_size + self.padding
            
            # Render text (truncate if too long)
            # Calculate remaining space for text (account for status indicator if present)
            text_size = self.font.render(item_text, True, self.text_color)
            text_width = text_size.get_width()            
            remaining_width = self.width - text_width - 2 * self.padding
            
            if self.status_indicators and i < len(self.status_indicators):
                status_text = self.status_indicators[i]
                if status_text:
                    status_surface = self.status_font.render(status_text, True, text_color)
                    remaining_width -= status_surface.get_width() + self.padding
            
            max_text_width = max(remaining_width, 10)  # Ensure at least 10 pixels
            rendered_text = self._truncate_text(item_text, max_text_width)
            text_surface = self.font.render(rendered_text, True, text_color)
            surface.blit(text_surface, (text_x, current_y + 5))
            
            # Render status indicator if present
            if self.status_indicators and i < len(self.status_indicators):
                status_text = self.status_indicators[i]
                if status_text:
                    status_surface = self.status_font.render(status_text, True, text_color)
                    status_x = self.width - 2 * self.padding - status_surface.get_width()
                    surface.blit(status_surface, (status_x, current_y + 8))
            
            current_y += self.item_height
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the scrollable icon list to the surface.
        
        Args:
            surface: Pygame surface to render on
        """
        # Draw background with adaptive height
        pygame.draw.rect(surface, self.bg_color, (self.x, self.y, self.width, self.actual_height))
        
        # Draw border with adaptive height
        pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.width, self.actual_height), 2)
        
        if not self.items:
            # Draw empty state
            empty_text = self.font.render("No items available", True, self.disabled_text_color)
            text_rect = empty_text.get_rect(center=(self.x + self.width // 2, self.y + self.actual_height // 2))
            surface.blit(empty_text, text_rect)
            return
        
        # Calculate visible range
        if self.needs_scrolling:
            start_idx = self.scroll_offset
            end_idx = min(start_idx + self.visible_items_count, len(self.items))
        else:
            start_idx = 0
            end_idx = len(self.items)
        
        # Render visible items with custom rendering
        self._render_visible_items(surface, start_idx, end_idx)
        
        # Draw scroll indicators only if needed
        if self.show_scroll_indicators and self.needs_scrolling:
            self._render_scroll_indicators(surface)
