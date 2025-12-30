# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Menu State Module

Main menu state for the game launcher.

Based on: docs/code/class_states_menu_state.txt
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..views.widgets import ScrollableList

logger = logging.getLogger(__name__)


class MenuState(BaseState):
    """
    Main menu state.
    
    Displays the main menu with options to browse games, download games,
    access settings, or exit the application.
    Now includes scrolling for 640x480 resolution compatibility and future expansion.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize menu state."""
        logger.info("Entered menu state")
        self.selected_option = 0
        
        # Initialize scrollable list for 640x480 compatibility and future expansion
        self._setup_scrollable_list()
        self._update_menu_options()

    def on_exit(self) -> None:
        """Cleanup menu state."""
        logger.info("Exited menu state")

    def update(self, dt: float) -> None:
        """Update menu logic."""
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle menu input."""
        # Check for exit
        if self._handle_exit_input(events):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        # Handle scrolling through menu options
        if hasattr(self, 'menu_list'):
            if self.input_handler.is_action_pressed("up", events):
                self.menu_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.menu_list.scroll_down()

            # Select option
            if self.input_handler.is_action_pressed("confirm", events):
                self._select_option()

    def _setup_scrollable_list(self, surface_height: int = 480) -> None:
        """Setup the scrollable list with appropriate dimensions."""
        # Reserve space for title (120px) and bottom padding (60px)
        list_height = surface_height - 180
        
        self.menu_list = ScrollableList(
            x=80,   # Centered horizontally (640 - 480)/2
            y=140,  # Below title
            width=480,  # Fixed width for centered appearance
            height=list_height,
            item_height=60,  # Spacious touch targets
            font_size=36,    # Larger font for main menu
            padding=20       # More padding for visual appeal
        )

    def _update_menu_options(self) -> None:
        """Update the scrollable list with menu options."""
        if not hasattr(self, 'menu_list'):
            return

        # Main menu options (can be easily expanded)
        menu_options = [
            "Browse Games",
            "Download Games", 
            "Self-Update",
            "Settings",
            "Help & Support",
            "About SBC-Man",
            "Exit"
        ]
        
        # All menu options are selectable
        menu_states = [True] * len(menu_options)

        self.menu_list.set_items(menu_options, menu_states)

    def _select_option(self) -> None:
        """Handle menu option selection."""
        if not hasattr(self, 'menu_list'):
            return

        selected_option = self.menu_list.get_selected_item()
        
        if selected_option == "Browse Games":
            self.state_manager.change_state("game_list")
        elif selected_option == "Download Games":
            self.state_manager.change_state("download")
        elif selected_option == "Self-Update":
            self.state_manager.change_state("update")
        elif selected_option == "Settings":
            self.state_manager.change_state("settings")
        elif selected_option == "Help & Support":
            # TODO: Implement help system
            logger.info("Help & Support selected - not yet implemented")
        elif selected_option == "About SBC-Man":
            # TODO: Implement about dialog
            logger.info("About SBC-Man selected - not yet implemented")
        elif selected_option == "Exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, surface: pygame.Surface) -> None:
        """Render menu with scrolling support."""
        surface.fill((20, 20, 30))

        # Render title with larger font for main menu
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("SBC-Man", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 60))
        surface.blit(title, title_rect)
        
        # Render subtitle
        font_small = pygame.font.Font(None, 28)
        subtitle = font_small.render("Game Launcher & Manager", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(subtitle, subtitle_rect)

        # Initialize scrollable list if needed
        if not hasattr(self, 'menu_list'):
            self._setup_scrollable_list(surface.get_height())
            self._update_menu_options()

        # Render the scrollable menu list
        self.menu_list.render(surface)

        # Render instructions at the bottom
        font_instruction = pygame.font.Font(None, 24)
        instructions = "↑↓ Navigate  |  A/Confirm Select  |  ESC/Exit"
        
        # Show scrolling hint if needed
        if hasattr(self, 'menu_list') and len(self.menu_list.items) > self.menu_list.visible_items_count:
            instructions += "  |  PageUp/Down Fast Scroll"
        
        inst_surface = font_instruction.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() - 20))
        surface.blit(inst_surface, inst_rect)