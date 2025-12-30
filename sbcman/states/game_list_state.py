# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Game List State Module

State for browsing and selecting games from the library.
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
    Game list browsing state.
    
    Displays installed and available games, allows selection and launching.
    Now includes scrolling functionality for 640x480 resolution compatibility.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize game list state."""
        logger.info("Entered game list state")
        self.games = self.game_library.get_all_games()
        
        # Initialize scrollable list for 640x480 compatibility
        # Reserve space for title (80px) and bottom padding (60px)
        self._setup_scrollable_list()
        
        # Populate the list with games
        self._update_game_list()

    def on_exit(self) -> None:
        """Cleanup game list state."""
        logger.info("Exited game list state")

    def update(self, dt: float) -> None:
        """Update game list logic."""
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
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

    def _setup_scrollable_list(self, surface_height: int = 480) -> None:
        """Setup the scrollable list with appropriate dimensions."""
        list_height = surface_height - 120  # Title (80px) + bottom padding (40px)
        
        self.game_list = ScrollableList(
            x=40,
            y=120,
            width=560,  # 640 - 80px for margins
            height=list_height,
            item_height=45,  # Slightly larger for better touch targets
            font_size=28,    # Smaller font for better space utilization
            padding=10
        )

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
        """Update the scrollable list with current games."""
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
        """Render game list with scrolling support."""
        surface.fill((20, 20, 30))

        # Render title
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("Game Library", True, (255, 255, 255))
        surface.blit(title, (50, 30))

        # Initialize scrollable list if needed
        if not hasattr(self, 'game_list'):
            self._setup_scrollable_list(surface.get_height())
            self._update_game_list()

        # Render the scrollable game list
        self.game_list.render(surface)

        # Render instructions at the bottom
        font_small = pygame.font.Font(None, 24)
        instructions = "↑↓ Navigate  |  A/Confirm Launch  |  B/Cancel Back"
        if hasattr(self, 'game_list') and len(self.games) > self.game_list.visible_items_count:
            instructions += "  |  PageUp/Down Fast Scroll"
        
        inst_surface = font_small.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() - 20))
        surface.blit(inst_surface, inst_rect)