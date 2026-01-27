# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Scrollable List Widget Module

Provides a reusable scrolling component for lists that adapts to available screen space.
Only shows scroll indicators when content exceeds available vertical space.
"""

import pygame
from typing import List, Callable, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ScrollableList:
    """
    An adaptive scrollable list widget that only scrolls when necessary.
    
    Automatically detects if content fits within available space and hides
    scroll indicators when not needed. Adapts to different screen sizes.
    Supports optional icons and status indicators for each item.
    """
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int,
                 item_height: int = 40,
                 font_size: int = 32,
                 padding: int = 10,
                 show_icons: bool = False,
                 icon_size: int = 32):
        """
        Initialize the adaptive scrollable list.
        
        Args:
            x: X position of the list
            y: Y position of the list
            width: Width of the list
            height: Height of the list (maximum available area)
            item_height: Height of each list item
            font_size: Font size for text rendering
            padding: Internal padding
            show_icons: Whether to display icons for items
            icon_size: Size of icons in pixels
        """
        self.x = x
        self.y = y
        self.init_y = y
        
        self.width = width
        self.height = height
        self.item_height = item_height
        self.font_size = font_size
        self.padding = padding
        self.show_icons = show_icons
        self.icon_size = icon_size
        
        # Scrolling state
        self.items: List[str] = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_items_count = (height - 2 * padding) // item_height
        
        # Adaptive layout state
        self.needs_scrolling = False
        self.actual_height = height  # Will be reduced if no scrolling needed
        
        # Visual settings
        self.bg_color = (20, 20, 30)
        self.selected_bg_color = (50, 50, 80)
        self.text_color = (255, 255, 255)
        self.selected_text_color = (255, 255, 0)
        self.disabled_text_color = (150, 150, 150)
        self.border_color = (100, 100, 100)
        
        # Fonts
        self.font = pygame.font.Font(None, font_size)
        self.status_font = pygame.font.Font(None, font_size - 4)
        
        # Scroll indicators (only shown when needed)
        self.show_scroll_indicators = False
        self.scroll_indicator_color = (100, 100, 100)
        
        # Icon and status support
        self.icons: Optional[List[pygame.Surface]] = None
        self.status_indicators: Optional[List[str]] = None
        
    def set_items(self, 
                 items: List[str], 
                 item_states: Optional[List[bool]] = None,
                 icons: Optional[List[pygame.Surface]] = None,
                 status_indicators: Optional[List[str]] = None) -> None:
        """
        Set the list items and determine if scrolling is needed.
        
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
        self.icons = icons if self.show_icons else None
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
        
    def _calculate_layout_requirements(self) -> None:
        """
        Calculate if scrolling is needed and adjust layout accordingly.
        """
        if not self.items:
            self.needs_scrolling = False
            self.show_scroll_indicators = False
            self.actual_height = self.height
            return
            
        # Calculate how much space the items need
        total_item_height = len(self.items) * self.item_height
        available_space = self.height - 2 * self.padding
        
        # Determine if scrolling is needed
        self.needs_scrolling = total_item_height > available_space
        
        if self.needs_scrolling:
            # Use full height and show scroll indicators
            self.actual_height = self.height
            self.visible_items_count = available_space // self.item_height
            self.show_scroll_indicators = True
        else:
            # Reduce height to fit content exactly and hide scroll indicators
            self.actual_height = total_item_height + 2 * self.padding
            self.visible_items_count = len(self.items)
            self.show_scroll_indicators = False
            
            # Center the content vertically if it doesn't fill the available space
            #print(self.actual_height, self.height)
            if self.actual_height < self.height:
                vertical_offset = (self.height - self.actual_height) // 2
                self.y = self.init_y + vertical_offset
                #print(self.y)
        
        logger.debug(f"Layout: {len(self.items)} items, needs_scrolling={self.needs_scrolling}, "
                    f"actual_height={self.actual_height}, visible_items={self.visible_items_count}")
        
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
        if not self.needs_scrolling:
            return  # No scrolling needed, everything is visible
            
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_items_count:
            self.scroll_offset = self.selected_index - self.visible_items_count + 1

        self._validate_scroll_offset()
        
    def _validate_scroll_offset(self) -> None:
        """Ensure scroll offset is within valid bounds."""
        if not self.needs_scrolling:
            self.scroll_offset = 0
            return
            
        max_offset = max(0, len(self.items) - self.visible_items_count)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
        
    def render(self, surface: pygame.Surface) -> None:
        """
        Render the adaptive scrollable list to the surface.
        
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
            remaining_width = self.width - text_x - 2 * self.padding
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
        if self.show_scroll_indicators and self.needs_scrolling:
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
        bar_height = self.actual_height - 20
        bar_y = self.y + 10
        
        # Background bar
        pygame.draw.rect(surface, self.scroll_indicator_color, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Scroll thumb
        if len(self.items) > 0:
            thumb_height = max(20, int(bar_height * self.visible_items_count / len(self.items)))
            thumb_y = bar_y + int((self.actual_height - 20 - thumb_height) * self.scroll_offset / 
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
                if self.needs_scrolling:
                    self.selected_index = max(0, self.selected_index - self.visible_items_count)
                    self._ensure_selection_visible()
                return True
            elif event.key == pygame.K_PAGEDOWN:
                # Page down - move by visible items count
                if self.needs_scrolling:
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
