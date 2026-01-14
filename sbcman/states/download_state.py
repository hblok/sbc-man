# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
State for downloading and installing games with adaptive layout support.
"""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..services.download_manager import DownloadManager, DownloadObserver
from ..views.widgets import ScrollableList

logger = logging.getLogger(__name__)


class DownloadState(BaseState, DownloadObserver):
    """
    Download management state with adaptive layout.
    
    Displays available games for download and manages the download process.
    Automatically adapts to screen size and only shows scroll indicators
    when content exceeds available vertical space.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize download state."""
        logger.info("Entered download state")
        self.download_manager = DownloadManager(self.hw_config, self.app_paths, self.game_library)
        self.available_games = self.game_library.get_available_games()
        self.selected_index = 0
        self.downloading = False
        self.download_progress = 0.0
        self.download_message = ""
        
        # Initialize adaptive scrollable list
        self._setup_adaptive_scrollable_list()
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
        progress_area_height = 120  # Space for download progress area
        bottom_padding = 60  # Space for instructions
        available_height = screen_height - title_height - progress_area_height - bottom_padding
        
        # Calculate adaptive width (responsive to screen size)
        max_width = min(560, screen_width - 40)  # Max 560px or screen width minus margins
        list_width = max(400, max_width)  # Min 400px for usability
        
        # Position the list
        list_x = (screen_width - list_width) // 2
        list_y = title_height + progress_area_height
        
        # Create adaptive scrollable list
        self.game_list = ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,  # Maximum available space
            item_height=45,
            font_size=28,
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
            progress_area_height = 120
            bottom_padding = 60
            available_height = surface_height - title_height - progress_area_height - bottom_padding
            
            max_width = min(560, surface_width - 40)
            list_width = max(400, max_width)
            list_x = (surface_width - list_width) // 2
            list_y = title_height + progress_area_height
            
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

    def _update_game_list(self) -> None:
        """Update the adaptive scrollable list with available games."""
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
        """Render download state with adaptive layout support."""
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
        title = font_large.render("Download Games", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface_width // 2, 40))
        surface.blit(title, title_rect)

        if self.downloading:
            # Render download progress with adaptive sizing
            font = pygame.font.Font(None, min(36, max(28, surface_width // 18)))
            text = font.render(self.download_message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(surface_width // 2, 90))
            surface.blit(text, text_rect)

            # Adaptive progress bar
            bar_width = min(surface_width - 100, 600)
            bar_height = min(30, surface_height // 16)
            bar_x = (surface_width - bar_width) // 2
            bar_y = 120

            pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * self.download_progress), bar_height))

            # Progress percentage
            percent_text = font.render(f"{int(self.download_progress * 100)}%", True, (255, 255, 255))
            percent_rect = percent_text.get_rect(center=(surface_width // 2, bar_y + bar_height + 25))
            surface.blit(percent_text, percent_rect)
        else:
            # Render the adaptive game list
            self.game_list.render(surface)

            # Render adaptive instructions at the bottom
            instruction_font_size = min(24, max(18, surface_width // 25))
            font_small = pygame.font.Font(None, instruction_font_size)
            
            # Base instructions
            instructions = "↑↓ Navigate  |  A/Confirm Download  |  B/Cancel Back"
            
            # Add scrolling hint only if needed and scrolling is actually active
            if (hasattr(self, 'game_list') and 
                self.game_list.needs_scrolling and 
                self.game_list.show_scroll_indicators):
                instructions += "  |  PageUp/Down Fast Scroll"
            
            inst_surface = font_small.render(instructions, True, (150, 150, 150))
            inst_rect = inst_surface.get_rect(center=(surface_width // 2, surface_height - 20))
            surface.blit(inst_surface, inst_rect)
