"""
State for downloading and installing games.
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..models.download_manager import DownloadManager, DownloadObserver

logger = logging.getLogger(__name__)


class DownloadState(BaseState, DownloadObserver):
    """
    Download management state.
    
    Displays available games for download and manages the download process.
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
        
        # Navigate list
        if self.input_handler.is_action_pressed("up", events) and self.available_games:
            self.selected_index = (self.selected_index - 1) % len(self.available_games)
        
        if self.input_handler.is_action_pressed("down", events) and self.available_games:
            self.selected_index = (self.selected_index + 1) % len(self.available_games)
        
        # Start download
        if self.input_handler.is_action_pressed("confirm", events) and self.available_games:
            self._start_download()

    def _start_download(self) -> None:
        """Start downloading selected game."""
        if not self.available_games:
            return
        
        game = self.available_games[self.selected_index]
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

    def on_error(self, error_message: str) -> None:
        """Download error callback."""
        self.download_message = f"Error: {error_message}"

    def render(self, surface: pygame.Surface) -> None:
        """Render download state."""
        surface.fill((20, 20, 30))
        
        # Render title
        font_large = pygame.font.Font(None, 56)
        title = font_large.render("Download Games", True, (255, 255, 255))
        surface.blit(title, (50, 30))
        
        if self.downloading:
            # Render download progress
            font = pygame.font.Font(None, 36)
            text = font.render(self.download_message, True, (255, 255, 255))
            surface.blit(text, (50, 150))
            
            # Progress bar
            bar_width = surface.get_width() - 100
            bar_height = 30
            bar_x = 50
            bar_y = 200
            
            pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * self.download_progress), bar_height))
            
            # Progress percentage
            percent_text = font.render(f"{int(self.download_progress * 100)}%", True, (255, 255, 255))
            surface.blit(percent_text, (bar_x + bar_width // 2 - 30, bar_y + 40))
        else:
            # Render available games list
            if not self.available_games:
                font = pygame.font.Font(None, 36)
                text = font.render("No games available for download", True, (150, 150, 150))
                surface.blit(text, (50, 150))
                return
            
            font = pygame.font.Font(None, 32)
            y_offset = 120
            
            for i, game in enumerate(self.available_games):
                if i == self.selected_index:
                    pygame.draw.rect(surface, (50, 50, 80), (40, y_offset - 5, surface.get_width() - 80, 40))
                
                text = font.render(game.name, True, (255, 255, 255))
                surface.blit(text, (50, y_offset))
                
                y_offset += 50
