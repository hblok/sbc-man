# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Settings State Module

State for configuring application settings with adaptive layout support.

Based on: docs/code/class_states_settings_state.txt
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..views.widgets import ScrollableList

logger = logging.getLogger(__name__)


class SettingsState(BaseState):
    """
    Settings configuration state with adaptive layout.
    
    Allows users to configure application settings and input mappings.
    Automatically adapts to screen size and only shows scroll indicators
    when content exceeds available vertical space.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize settings state."""
        logger.info("Entered settings state")
        
        # Initialize adaptive scrollable list
        self._setup_adaptive_scrollable_list()
        self._update_settings_options()

    def on_exit(self) -> None:
        """Cleanup settings state."""
        logger.info("Exited settings state")
        # Save any pending configuration changes
        self.config.save()

    def update(self, dt: float) -> None:
        """Update settings logic."""
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle settings input."""
        # Check for back/exit
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            self.state_manager.change_state("menu")
            return

        # Handle scrolling through settings options
        if hasattr(self, 'settings_list'):
            if self.input_handler.is_action_pressed("up", events):
                self.settings_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.settings_list.scroll_down()

            # Select option
            if self.input_handler.is_action_pressed("confirm", events):
                self._select_option()

    def _setup_adaptive_scrollable_list(self) -> None:
        """
        Setup the adaptive scrollable list that responds to screen size.
        
        This method creates a list that will automatically detect if scrolling is needed
        based on the available screen space and content length.
        """
        # Get screen dimensions from the surface (will be called in render)
        # For now, use defaults that work for both 640x480 and larger screens
        screen_width = 640  # Default, will be updated in render
        screen_height = 480  # Default, will be updated in render
        
        # Calculate adaptive dimensions
        title_height = 90  # Space for title
        bottom_padding = 70  # Space for instructions
        available_height = screen_height - title_height - bottom_padding
        
        # Calculate adaptive width (responsive to screen size)
        max_width = min(560, screen_width - 40)  # Max 560px or screen width minus margins
        list_width = max(400, max_width)  # Min 400px for usability
        
        # Position the list
        list_x = (screen_width - list_width) // 2
        list_y = title_height
        
        # Create adaptive scrollable list
        self.settings_list = ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,  # Maximum available space
            item_height=50,
            font_size=30,
            padding=10
        )
        
        # Store dimensions for potential updates
        self._last_screen_width = screen_width
        self._last_screen_height = screen_height

    def _update_scrollable_list_dimensions(self, surface_width: int, surface_height: int) -> None:
        """
        Update scrollable list dimensions if screen size changed.
        
        Args:
            surface_width: Current surface width
            surface_height: Current surface height
        """
        # Only update if dimensions actually changed
        if (surface_width != self._last_screen_width or 
            surface_height != self._last_screen_height):
            
            # Recalculate adaptive dimensions
            title_height = 90
            bottom_padding = 70
            available_height = surface_height - title_height - bottom_padding
            
            max_width = min(560, surface_width - 40)
            list_width = max(400, max_width)
            list_x = (surface_width - list_width) // 2
            list_y = title_height
            
            # Update scrollable list properties
            self.settings_list.x = list_x
            self.settings_list.y = list_y
            self.settings_list.width = list_width
            self.settings_list.height = available_height
            
            # Recalculate layout requirements
            self.settings_list._calculate_layout_requirements()
            
            # Store new dimensions
            self._last_screen_width = surface_width
            self._last_screen_height = surface_height
            
            logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _update_settings_options(self) -> None:
        """Update the adaptive scrollable list with settings options."""
        if not hasattr(self, 'settings_list'):
            return

        # Current settings options (can be expanded in the future)
        settings_options = [
            "Display Settings",
            "Input Mappings", 
            "Audio Settings",
            "Network Settings",
            "Storage Management",
            "System Information",
            "About SBC-Man",
            "Back to Menu"
        ]
        
        # All settings options are selectable
        settings_states = [True] * len(settings_options)

        self.settings_list.set_items(settings_options, settings_states)

    def _select_option(self) -> None:
        """Handle settings option selection."""
        if not hasattr(self, 'settings_list'):
            return

        selected_item = self.settings_list.get_selected_item()
        
        if selected_item == "Back to Menu":
            self.state_manager.change_state("menu")
        else:
            logger.info(f"Settings option selected: {selected_item}")
            # TODO: Implement settings sub-menus for each option
            # For now, we can show placeholder messages or expand functionality

    def render(self, surface: pygame.Surface) -> None:
        """Render settings with adaptive layout support."""
        surface.fill((20, 20, 30))
        
        # Get actual surface dimensions
        surface_width = surface.get_width()
        surface_height = surface.get_height()

        # Update scrollable list dimensions if screen size changed
        if hasattr(self, 'settings_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            # Initialize if not done yet
            self._setup_adaptive_scrollable_list()
            self._update_settings_options()

        # Render title with adaptive font size
        title_font_size = min(56, max(40, surface_width // 11))
        font_large = pygame.font.Font(None, title_font_size)
        title = font_large.render("Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface_width // 2, 45))
        surface.blit(title, title_rect)

        # Render the adaptive settings list
        self.settings_list.render(surface)

        # Render adaptive instructions at the bottom
        instruction_font_size = min(24, max(18, surface_width // 25))
        font_small = pygame.font.Font(None, instruction_font_size)
        
        # Base instructions
        instructions = "↑↓ Navigate  |  A/Confirm Select  |  B/Cancel Back"
        
        # Add scrolling hint only if needed and scrolling is actually active
        if (hasattr(self, 'settings_list') and 
            self.settings_list.needs_scrolling and 
            self.settings_list.show_scroll_indicators):
            instructions += "  |  PageUp/Down Fast Scroll"
        
        inst_surface = font_small.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface_width // 2, surface_height - 20))
        surface.blit(inst_surface, inst_rect)