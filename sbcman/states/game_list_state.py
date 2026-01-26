# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Game List State Module - State for browsing and selecting games."""

import logging
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..views import widgets

logger = logging.getLogger(__name__)


class GameListState(BaseState):
    """Game list browsing state with adaptive layout."""

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        logger.info("Entered game list state")
        self.games = self.game_library.get_all_games()
        self._setup_adaptive_scrollable_list()
        self._update_game_list()

    def on_exit(self) -> None:
        logger.info("Exited game list state")

    def update(self, dt: float) -> None:
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            self.state_manager.change_state("menu")
            return

        if hasattr(self, 'game_list') and self.games:
            if self.input_handler.is_action_pressed("up", events):
                self.game_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.game_list.scroll_down()

            if self.input_handler.is_action_pressed("confirm", events):
                self._launch_game()

    def _setup_adaptive_scrollable_list(self) -> None:
        screen_width = 640
        screen_height = 480

        title_height = 80
        bottom_padding = 60
        available_height = screen_height - title_height - bottom_padding

        max_width = min(560, screen_width - 40)
        list_width = max(400, max_width)

        list_x = (screen_width - list_width) // 2
        list_y = title_height

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
        bottom_padding = 60
        available_height = surface_height - title_height - bottom_padding

        max_width = min(560, surface_width - 40)
        list_width = max(400, max_width)
        list_x = (surface_width - list_width) // 2
        list_y = title_height

        self.game_list.x = list_x
        self.game_list.y = list_y
        self.game_list.width = list_width
        self.game_list.height = available_height

        self.game_list._calculate_layout_requirements()

        self._last_screen_width = surface_width
        self._last_screen_height = surface_height

        logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _launch_game(self) -> None:
        if not self.games or not hasattr(self, 'game_list'):
            return

        selected_index = self.game_list.get_selected_index()
        if selected_index >= len(self.games):
            return

        game = self.games[selected_index]

        if not game.installed:
            logger.warning(f"Game not installed: {game.name}")
            return

        self.state_manager.selected_game = game
        logger.info(f"Selected game for launch: {game.name}")
        self.state_manager.change_state("playing")

    def _update_game_list(self) -> None:
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
        self._render_background(surface)
        surface_width, surface_height = self._get_surface_dimensions(surface)

        if hasattr(self, 'game_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            self._setup_adaptive_scrollable_list()
            self._update_game_list()

        self._render_title(surface, "Game Library", y_position=40)

        self.game_list.render(surface)

        self._render_instructions(
            surface,
            "↑↓ Navigate  |  A/Confirm Launch  |  B/Cancel Back",
            scrollable_list=self.game_list
        )

    @property
    def selected_index(self):
        if hasattr(self, 'game_list'):
            return self.game_list.get_selected_index()
        return 0

    @selected_index.setter
    def selected_index(self, value):
        pass

    @property
    def scroll_offset(self):
        if hasattr(self, 'game_list'):
            return getattr(self.game_list, 'scroll_offset', 0)
        return 0

    @scroll_offset.setter
    def scroll_offset(self, value):
        if hasattr(self, 'game_list'):
            self.game_list.scroll_offset = value