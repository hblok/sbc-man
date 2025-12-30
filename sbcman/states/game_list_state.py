# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Game List State Module

State for browsing and selecting games from the library with adaptive layout support.
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..models.game import Game
from ..views.widgets import ScrollableList

logger = logging.getLogger(__name__)


class GameListState(BaseState):
    """
    Game list browsing state with adaptive layout.
    
    Displays installed and available games, allows selection and launching.
    Automatically adapts to screen size and only shows scroll indicators
    when content exceeds available vertical space.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize game list state."""
        logger.info("Entered game list state")
        self.games = self.game_library.get_all_games()
        
        # Initialize adaptive scrollable list
        self._setup_adaptive_scrollable_list()
        
        # Populate the list with games
        self._update_game_list()

    def on_exit(self) -> None:
        """Cleanup game list state."""
        logger.info("Exited game list state")

    def update(self, dt: float) -> None:
        """Update game list logic."""
        pass

    def handle_events(self, List[pygame.event.Event]) -> None:
        """Handle game list input."""
        # Check for back/exit
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            self.state_manager.change_state("menu")
            return

        # Handle scrolling through the game list
        if hasattr(self, 'game_list') and self.games:
            if self.input_handler.is_action_pressed("up", events):
                self.game_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.game_list.scroll_down()

            # Select game
            if self.input_handler.is_action_pressed("confirm", events):
                self._launch_game()

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
        title_height = 80  # Space for title
        bottom_padding = 60  # Space for instructions
        available_height = screen_height - title_height - bottom_padding
        
        # Calculate adaptive width (responsive to screen size)
        max_width = min(560, screen_width - 40)  # Max 560px or screen width minus margins
        list_width = max(400, max_width)  # Min 400px for usability
        
        # Position the list
        list_x = (screen_width - list_width) // 2
        list_y = title_height
        
        # Create adaptive scrollable list
        self.game_list = ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,  # Maximum available space
            item_height=45,  # Slightly larger for better touch targets
            font_size=28,    # Smaller font for better space utilization
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
            title_height = 80
            bottom_padding = 60
            available_height = surface_height - title_height - bottom_padding
            
            max_width = min(560, surface_width - 40)
            list_width = max(400, max_width)
            list_x = (surface_width - list_width) // 2
            list_y = title_height
            
            # Update scrollable list properties
            self.game_list.x = list_x
            self.game_list.y = list_y
            self.game_list.width = list_width
            self.game_list.height = available_height
            
            # Recalculate layout requirements
            self.game_list._calculate_layout_requirements()
            
            # Store new dimensions
            self._last_screen_width = surface_width
            self._last_screen_height = surface_height
            
            logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _launch_game(self) -> None:
        """Launch selected game."""
        if not self.games or not hasattr(self, 'game_list'):
            return

        selected_index = self.game_list.get_selected_index()
        if selected_index >= len(self.games):
            return

        game = self.games[selected_index]

        if not game.installed:
            logger.warning(f"Game not installed: {game.name}")
            return

        # Transition to playing state
        self.state_manager.change_state("playing")

    def _update_game_list(self) -> None:
        """Update the adaptive scrollable list with current games."""
        if not hasattr(self, 'game_list'):
            return

        game_names = []
        game_states = []
        
        for game in self.games:
            status = " [Installed]" if game.installed else " [Not Installed]"
            game_names.append(game.name + status)
            game_states.append(game.installed)

        self.game_list.set_items(game_names, game_states)

    def render(self, surface: pygame.Surface) -> None:
        """Render game list with adaptive layout support."""
        surface.fill((20, 20, 30))
        
        # Get actual surface dimensions
        surface_width = surface.get_width()
        surface_height = surface.get_height()

        # Update scrollable list dimensions if screen size changed
        if hasattr(self, 'game_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            # Initialize if not done yet
            self._setup_adaptive_scrollable_list()
            self._update_game_list()

        # Render title with adaptive font size
        title_font_size = min(56, max(40, surface_width // 11))
        font_large = pygame.font.Font(None, title_font_size)
        title = font_large.render("Game Library", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface_width // 2, 40))
        surface.blit(title, title_rect)

        # Render the adaptive game list
        self.game_list.render(surface)

        # Render adaptive instructions at the bottom
        instruction_font_size = min(24, max(18, surface_width // 25))
        font_small = pygame.font.Font(None, instruction_font_size)
        
        # Base instructions
        instructions = "↑↓ Navigate  |  A/Confirm Launch  |  B/Cancel Back"
        
        # Add scrolling hint only if needed and scrolling is actually active
        if (hasattr(self, 'game_list') and 
            self.game_list.needs_scrolling and 
            self.game_list.show_scroll_indicators):
            instructions += "  |  PageUp/Down Fast Scroll"
        
        inst_surface = font_small.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface_width // 2, surface_height - 20))
        surface.blit(inst_surface, inst_rect)