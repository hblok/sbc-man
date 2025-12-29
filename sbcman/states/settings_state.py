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

logger = logging.getLogger(__name__)


class SettingsState(BaseState):
    """
    Settings configuration state.
    
    Allows users to configure application settings and input mappings.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize settings state."""
        logger.info("Entered settings state")
        self.selected_option = 0
        self.settings_options = [
            "Display Settings",
            "Input Mappings",
            "Audio Settings",
            "Back to Menu",
        ]

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
        
        # Navigate options
        if self.input_handler.is_action_pressed("up", events):
            self.selected_option = (self.selected_option - 1) % len(self.settings_options)
        
        if self.input_handler.is_action_pressed("down", events):
            self.selected_option = (self.selected_option + 1) % len(self.settings_options)
        
        # Select option
        if self.input_handler.is_action_pressed("confirm", events):
            self._select_option()

    def _select_option(self) -> None:
        """Handle settings option selection."""
        option = self.settings_options[self.selected_option]
        
        if option == "Back to Menu":
            self.state_manager.change_state("menu")
        else:
            logger.info(f"Settings option selected: {option}")
            # TODO: Implement settings sub-menus

    def render(self, surface: pygame.Surface) -> None:
        """Render settings."""
        surface.fill((20, 20, 30))
        
        # Render title
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("Settings", True, (255, 255, 255))
        surface.blit(title, (50, 30))
        
        # Render settings options
        font = pygame.font.Font(None, 36)
        y_offset = 150
        
        for i, option in enumerate(self.settings_options):
            if i == self.selected_option:
                pygame.draw.rect(surface, (50, 50, 80), (40, y_offset - 5, surface.get_width() - 80, 45))
            
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = font.render(option, True, color)
            surface.blit(text, (50, y_offset))
            
            y_offset += 60