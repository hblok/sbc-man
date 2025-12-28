"""
Menu State Module

Main menu state for the game launcher.

Based on: docs/code/class_states_menu_state.txt
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState

logger = logging.getLogger(__name__)


class MenuState(BaseState):
    """
    Main menu state.
    
    Displays the main menu with options to browse games, download games,
    access settings, or exit the application.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize menu state."""
        logger.info("Entered menu state")
        self.selected_option = 0
        self.menu_options = [
            "Browse Games",
            "Download Games",
            "Self-Update",
            "Settings",
            "Exit",
        ]

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
        
        # Navigate menu
        if self.input_handler.is_action_pressed("up", events):
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        
        if self.input_handler.is_action_pressed("down", events):
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        
        # Select option
        if self.input_handler.is_action_pressed("confirm", events):
            self._select_option()

    def _select_option(self) -> None:
        """Handle menu option selection."""
        option = self.menu_options[self.selected_option]
        
        if option == "Browse Games":
            self.state_manager.change_state("game_list")
        elif option == "Download Games":
            self.state_manager.change_state("download")
        elif option == "Self-Update":
            self.state_manager.change_state("update")
        elif option == "Settings":
            self.state_manager.change_state("settings")
        elif option == "Exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, surface: pygame.Surface) -> None:
        """Render menu."""
        # Clear screen
        surface.fill((20, 20, 30))
        
        # Render title
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("SBC-Man", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(title, title_rect)
        
        # Render menu options
        font = pygame.font.Font(None, 48)
        y_offset = 250
        
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(surface.get_width() // 2, y_offset + i * 60))
            surface.blit(text, text_rect)