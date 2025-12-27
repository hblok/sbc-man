"""
Playing State Module

State for running a game as a subprocess.

Based on: docs/code/class_states_playing_state.txt
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..services.process_launcher import ProcessLauncher

logger = logging.getLogger(__name__)


class PlayingState(BaseState):
    """
    Game playing state.
    
    Launches and monitors a game process, handling the transition
    back to the game list when the game exits.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize playing state and launch game."""
        logger.info("Entered playing state")
        
        # Get the selected game from game_list_state
        # For now, we'll just show a placeholder
        self.game_running = True
        self.launcher = ProcessLauncher(self.hw_config)
        
        # TODO: Get actual game from previous state
        # For now, just display a message
        self.message = "Game would be launched here"

    def on_exit(self) -> None:
        """Cleanup playing state."""
        logger.info("Exited playing state")
        self.game_running = False

    def update(self, dt: float) -> None:
        """Update playing state logic."""
        # Check if game is still running
        # For now, just a placeholder
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle playing state input."""
        # Allow returning to game list
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            self.state_manager.change_state("game_list")

    def render(self, surface: pygame.Surface) -> None:
        """Render playing state."""
        surface.fill((20, 20, 30))
        
        # Render message
        font = pygame.font.Font(None, 48)
        text = font.render(self.message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text, text_rect)
        
        # Render instructions
        font_small = pygame.font.Font(None, 32)
        instruction = font_small.render("Press ESC or Cancel to return", True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 50))
        surface.blit(instruction, instruction_rect)