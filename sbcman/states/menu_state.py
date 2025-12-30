# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Menu State Module

Main menu state for the game launcher with adaptive layout support.

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
    Main menu state with adaptive layout.
    
    Displays the main menu with options that adapt to available screen space.
    Only shows scroll indicators when content exceeds available vertical space.
    Automatically centers content when it fits within the available area.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize menu state."""
        logger.info("Entered menu state")
        self.selected_option = 0
        
        # Initialize adaptive scrollable list
        self._setup_adaptive_scrollable_list()
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
        title_height = 120  # Space for title and subtitle
        bottom_padding = 80  # Space for instructions
        available_height = screen_height - title_height - bottom_padding
        
        # Calculate adaptive width (responsive to screen size)
        max_width = min(600, screen_width - 80)  # Max 600px or screen width minus margins
        list_width = max(400, max_width)  # Min 400px for usability
        
        # Center the list horizontally
        list_x = (screen_width - list_width) // 2
        list_y = title_height
        
        # Create adaptive scrollable list
        self.menu_list = ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,  # Maximum available space
            item_height=60,  # Spacious touch targets
            font_size=36,    # Larger font for main menu
            padding=20       # More padding for visual appeal
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
            title_height = 120
            bottom_padding = 80
            available_height = surface_height - title_height - bottom_padding
            
            max_width = min(600, surface_width - 80)
            list_width = max(400, max_width)
            list_x = (surface_width - list_width) // 2
            list_y = title_height
            
            # Update scrollable list properties
            self.menu_list.x = list_x
            self.menu_list.y = list_y
            self.menu_list.width = list_width
            self.menu_list.height = available_height
            
            # Recalculate layout requirements
            self.menu_list._calculate_layout_requirements()
            
            # Store new dimensions
            self._last_screen_width = surface_width
            self._last_screen_height = surface_height
            
            logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _update_menu_options(self) -> None:
        """Update the adaptive scrollable list with menu options."""
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
        """Render menu with adaptive layout support."""
        surface.fill((20, 20, 30))
        
        # Get actual surface dimensions
        surface_width = surface.get_width()
        surface_height = surface.get_height()

        # Update scrollable list dimensions if screen size changed
        if hasattr(self, 'menu_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            # Initialize if not done yet
            self._setup_adaptive_scrollable_list()
            self._update_menu_options()

        # Render title with adaptive font size
        title_font_size = min(72, max(48, surface_width // 9))  # Adaptive title font
        font_large = pygame.font.Font(None, title_font_size)
        title = font_large.render("SBC-Man", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface_width // 2, 50))
        surface.blit(title, title_rect)
        
        # Render subtitle with adaptive font size
        subtitle_font_size = min(28, max(20, surface_width // 25))
        font_small = pygame.font.Font(None, subtitle_font_size)
        subtitle = font_small.render("Game Launcher & Manager", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(surface_width // 2, 85))
        surface.blit(subtitle, subtitle_rect)

        # Render the adaptive menu list
        self.menu_list.render(surface)

        # Render adaptive instructions at the bottom
        instruction_font_size = min(24, max(18, surface_width // 30))
        font_instruction = pygame.font.Font(None, instruction_font_size)
        instructions = "↑↓ Navigate  |  A/Confirm Select  |  ESC/Exit"
        
        # Show scrolling hint only if needed and scrolling is actually active
        if (hasattr(self, 'menu_list') and 
            self.menu_list.needs_scrolling and 
            self.menu_list.show_scroll_indicators):
            instructions += "  |  PageUp/Down Fast Scroll"
        
        inst_surface = font_instruction.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface_width // 2, surface_height - 20))
        surface.blit(inst_surface, inst_rect)