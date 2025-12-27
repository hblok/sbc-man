"""
Game List State Module

State for browsing and selecting games from the library.
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..models.game import Game

logger = logging.getLogger(__name__)


class GameListState(BaseState):
    """
    Game list browsing state.
    
    Displays installed and available games, allows selection and launching.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize game list state."""
        logger.info("Entered game list state")
        self.games = self.game_library.get_all_games()
        self.selected_index = 0
        self.scroll_offset = 0

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
        
        # Navigate list
        if self.input_handler.is_action_pressed("up", events) and self.games:
            self.selected_index = (self.selected_index - 1) % len(self.games)
        
        if self.input_handler.is_action_pressed("down", events) and self.games:
            self.selected_index = (self.selected_index + 1) % len(self.games)
        
        # Select game
        if self.input_handler.is_action_pressed("confirm", events) and self.games:
            self._launch_game()

    def _launch_game(self) -> None:
        """Launch selected game."""
        if not self.games:
            return
        
        game = self.games[self.selected_index]
        
        if not game.installed:
            logger.warning(f"Game not installed: {game.name}")
            return
        
        # Transition to playing state
        self.state_manager.change_state("playing")

    def render(self, surface: pygame.Surface) -> None:
        """Render game list."""
        surface.fill((20, 20, 30))
        
        # Render title
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("Game Library", True, (255, 255, 255))
        surface.blit(title, (50, 30))
        
        # Render game list
        if not self.games:
            font = pygame.font.Font(None, 36)
            text = font.render("No games available", True, (150, 150, 150))
            surface.blit(text, (50, 150))
            return
        
        font = pygame.font.Font(None, 32)
        y_offset = 120
        
        for i, game in enumerate(self.games):
            if i == self.selected_index:
                # Highlight selected game
                pygame.draw.rect(surface, (50, 50, 80), (40, y_offset - 5, surface.get_width() - 80, 40))
            
            color = (255, 255, 255) if game.installed else (150, 150, 150)
            text = font.render(f"{game.name} {'[Installed]' if game.installed else '[Not Installed]'}", True, color)
            surface.blit(text, (50, y_offset))
            
            y_offset += 50
