# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Settings State Module

State for configuring application settings.

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
    Settings configuration state.
    
    Allows users to configure application settings and input mappings.
    Now includes scrolling functionality for 640x480 resolution compatibility
    and future expansion of settings options.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize settings state."""
        logger.info("Entered settings state")
        
        # Initialize scrollable list for 640x480 compatibility
        self._setup_scrollable_list()
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

    def _setup_scrollable_list(self, surface_height: int = 480) -> None:
        """Setup the scrollable list with appropriate dimensions."""
        # Reserve space for title (80px) and bottom padding (60px)
        list_height = surface_height - 140
        
        self.settings_list = ScrollableList(
            x=40,
            y=100,
            width=560,  # 640 - 80px for margins
            height=list_height,
            item_height=50,
            font_size=30,
            padding=10
        )

    def _update_settings_options(self) -> None:
        """Update the scrollable list with settings options."""
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
        """Render settings with scrolling support."""
        surface.fill((20, 20, 30))

        # Render title
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("Settings", True, (255, 255, 255))
        surface.blit(title, (50, 30))

        # Initialize scrollable list if needed
        if not hasattr(self, 'settings_list'):
            self._setup_scrollable_list(surface.get_height())
            self._update_settings_options()

        # Render the scrollable settings list
        self.settings_list.render(surface)

        # Render instructions at the bottom
        font_small = pygame.font.Font(None, 24)
        instructions = "↑↓ Navigate  |  A/Confirm Select  |  B/Cancel Back"
        if hasattr(self, 'settings_list') and self.settings_list.visible_items_count < len(self.settings_list.items):
            instructions += "  |  PageUp/Down Fast Scroll"
        
        inst_surface = font_small.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() - 20))
        surface.blit(inst_surface, inst_rect)