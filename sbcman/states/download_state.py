# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
State for downloading and installing games.
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..models.download_manager import DownloadManager, DownloadObserver
from ..views.widgets import ScrollableList

logger = logging.getLogger(__name__)


class DownloadState(BaseState, DownloadObserver):
    """
    Download management state.
    
    Displays available games for download and manages the download process.
    Now includes scrolling functionality for 640x480 resolution compatibility.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize download state."""
        logger.info("Entered download state")
        self.download_manager = DownloadManager(self.hw_config, self.app_paths)
        self.available_games = self.game_library.get_available_games()
        self.selected_index = 0
        self.downloading = False
        self.download_progress = 0.0
        self.download_message = ""
        
        # Initialize scrollable list for 640x480 compatibility
        self._setup_scrollable_list()
        self._update_game_list()

    def on_exit(self) -> None:
        """Cleanup download state."""
        logger.info("Exited download state")

    def update(self, dt: float) -> None:
        """Update download state logic."""
        if self.downloading:
            self.download_progress = self.download_manager.get_progress()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle download state input."""
        # Check for back/exit
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            if not self.downloading:
                self.state_manager.change_state("menu")
            return

        if self.downloading:
            return  # Don't handle input during download

        # Handle scrolling through available games
        if hasattr(self, 'game_list') and self.available_games:
            if self.input_handler.is_action_pressed("up", events):
                self.game_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.game_list.scroll_down()

            # Start download
            if self.input_handler.is_action_pressed("confirm", events):
                self._start_download()

    def _setup_scrollable_list(self, surface_height: int = 480) -> None:
        """Setup the scrollable list with appropriate dimensions."""
        # Reserve space for title (80px), progress area (120px), and bottom padding (40px)
        list_height = surface_height - 240
        
        self.game_list = ScrollableList(
            x=40,
            y=180,
            width=560,  # 640 - 80px for margins
            height=list_height,
            item_height=45,
            font_size=28,
            padding=10
        )

    def _update_game_list(self) -> None:
        """Update the scrollable list with available games."""
        if not hasattr(self, 'game_list'):
            return

        game_names = [game.name for game in self.available_games]
        game_states = [True] * len(self.available_games)  # All games are selectable

        self.game_list.set_items(game_names, game_states)

    def _start_download(self) -> None:
        """Start downloading selected game."""
        if not self.available_games or not hasattr(self, 'game_list'):
            return

        selected_index = self.game_list.get_selected_index()
        if selected_index >= len(self.available_games):
            return

        game = self.available_games[selected_index]
        self.downloading = True
        self.download_message = f"Downloading {game.name}..."
        self.download_manager.download_game(game, self)

    def on_progress(self, downloaded: int, total: int) -> None:
        """Download progress callback."""
        self.download_progress = downloaded / total if total > 0 else 0

    def on_complete(self, success: bool, message: str) -> None:
        """Download complete callback."""
        self.downloading = False
        self.download_message = message
        
        if success:
            # Refresh game library
            self.game_library.save_games()
            self.available_games = self.game_library.get_available_games()
            self._update_game_list()

    def on_error(self, error_message: str) -> None:
        """Download error callback."""
        self.download_message = f"Error: {error_message}"

    def render(self, surface: pygame.Surface) -> None:
        """Render download state with scrolling support."""
        surface.fill((20, 20, 30))

        # Render title
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("Download Games", True, (255, 255, 255))
        surface.blit(title, (50, 30))

        if self.downloading:
            # Render download progress
            font = pygame.font.Font(None, 36)
            text = font.render(self.download_message, True, (255, 255, 255))
            surface.blit(text, (50, 100))

            # Progress bar
            bar_width = surface.get_width() - 100
            bar_height = 30
            bar_x = 50
            bar_y = 140

            pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * self.download_progress), bar_height))

            # Progress percentage
            percent_text = font.render(f"{int(self.download_progress * 100)}%", True, (255, 255, 255))
            surface.blit(percent_text, (bar_x + bar_width // 2 - 30, bar_y + 40))
        else:
            # Initialize scrollable list if needed
            if not hasattr(self, 'game_list'):
                self._setup_scrollable_list(surface.get_height())
                self._update_game_list()

            # Render the scrollable game list
            self.game_list.render(surface)

            # Render instructions at the bottom
            font_small = pygame.font.Font(None, 24)
            instructions = "↑↓ Navigate  |  A/Confirm Download  |  B/Cancel Back"
            if hasattr(self, 'game_list') and len(self.available_games) > self.game_list.visible_items_count:
                instructions += "  |  PageUp/Down Fast Scroll"
            
            inst_surface = font_small.render(instructions, True, (150, 150, 150))
            inst_rect = inst_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() - 20))
            surface.blit(inst_surface, inst_rect)