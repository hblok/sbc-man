# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""State for downloading and installing games with adaptive layout support."""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..services import download_manager
from ..views import widgets

logger = logging.getLogger(__name__)


class DownloadState(BaseState, download_manager.DownloadObserver):
    """Download management state with adaptive layout."""

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        logger.info("Entered download state")
        self.download_manager = download_manager.DownloadManager(
            self.hw_config, self.app_paths, self.game_library, self.config)
        self.available_games = self.game_library.get_available_games()
        self.selected_index = 0
        self.downloading = False
        self.download_progress = 0.0
        self.download_message = ""

        self._setup_adaptive_scrollable_list()
        self._update_game_list()

    def on_exit(self) -> None:
        logger.info("Exited download state")

    def update(self, dt: float) -> None:
        if self.downloading:
            self.download_progress = self.download_manager.get_progress()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            if not self.downloading:
                self.state_manager.change_state("menu")
            return

        if self.downloading:
            return

        if hasattr(self, 'game_list') and self.available_games:
            if self.input_handler.is_action_pressed("up", events):
                self.game_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.game_list.scroll_down()

            if self.input_handler.is_action_pressed("confirm", events):
                self._start_download()

    def _setup_adaptive_scrollable_list(self) -> None:
        screen_width = 640
        screen_height = 480

        title_height = 80
        progress_area_height = 120
        bottom_padding = 60
        available_height = screen_height - title_height - progress_area_height - bottom_padding

        max_width = min(560, screen_width - 40)
        list_width = max(400, max_width)

        list_x = (screen_width - list_width) // 2
        list_y = title_height + progress_area_height

        self.game_list = widgets.ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,
            item_height=45,
            font_size=28,
            padding=10
        )

        self._last_screen_width = screen_width
        self._last_screen_height = screen_height

    def _update_scrollable_list_dimensions(self, surface_width: int, surface_height: int) -> None:
        if (surface_width == self._last_screen_width and
                surface_height == self._last_screen_height):
            return

        title_height = 80
        progress_area_height = 120
        bottom_padding = 60
        available_height = surface_height - title_height - progress_area_height - bottom_padding

        max_width = min(560, surface_width - 40)
        list_width = max(400, max_width)
        list_x = (surface_width - list_width) // 2
        list_y = title_height + progress_area_height

        self.game_list.x = list_x
        self.game_list.y = list_y
        self.game_list.width = list_width
        self.game_list.height = available_height

        self.game_list._calculate_layout_requirements()

        self._last_screen_width = surface_width
        self._last_screen_height = surface_height

        logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _update_game_list(self) -> None:
        if not hasattr(self, 'game_list'):
            return

        game_names = [game.name for game in self.available_games]
        game_states = [True] * len(self.available_games)

        self.game_list.set_items(game_names, game_states)

    def _start_download(self) -> None:
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
        self.download_progress = min(downloaded / total if total > 0 else 0, 1.0)

    def on_complete(self, success: bool, message: str) -> None:
        self.downloading = False
        self.download_message = message

        if success:
            self.game_library.save_games()
            self.available_games = self.game_library.get_available_games()
            self._update_game_list()

    def on_error(self, error_message: str) -> None:
        self.download_message = f"Error: {error_message}"

    def render(self, surface: pygame.Surface) -> None:
        self._render_background(surface)
        surface_width, surface_height = self._get_surface_dimensions(surface)

        if hasattr(self, 'game_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            self._setup_adaptive_scrollable_list()
            self._update_game_list()

        self._render_title(surface, "Download Games", y_position=40)

        if self.downloading:
            self._render_download_progress(surface, surface_width, surface_height)
        else:
            self.game_list.render(surface)
            self._render_instructions(
                surface,
                "↑↓ Navigate  |  A/Confirm Download  |  B/Cancel Back",
                scrollable_list=self.game_list
            )

    def _render_download_progress(self, surface: pygame.Surface,
                                   surface_width: int, surface_height: int) -> None:
        font_size = self._calc_font_size(surface_width, 18, 28, 36)
        font = pygame.font.Font(None, font_size)
        text = font.render(self.download_message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface_width // 2, 90))
        surface.blit(text, text_rect)

        bar_width = min(surface_width - 100, 600)
        bar_height = min(30, surface_height // 16)
        bar_x = (surface_width - bar_width) // 2
        bar_y = 120

        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 200, 0),
                        (bar_x, bar_y, int(bar_width * self.download_progress), bar_height))

        percent_text = font.render(f"{int(self.download_progress * 100)}%", True, (255, 255, 255))
        percent_rect = percent_text.get_rect(center=(surface_width // 2, bar_y + bar_height + 25))
        surface.blit(percent_text, percent_rect)