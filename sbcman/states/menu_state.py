# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Menu State Module - Main menu state for the game launcher."""

import logging
from typing import Optional, List

import pygame

from . import base_state
from ..views import widgets

logger = logging.getLogger(__name__)


class MenuState(base_state.BaseState):
    """Main menu state with adaptive layout."""

    def on_enter(self, previous_state: Optional[base_state.BaseState]) -> None:
        logger.info("Entered menu state")
        self.selected_option = 0
        self._setup_adaptive_scrollable_list()
        self._update_menu_options()

    def on_exit(self) -> None:
        logger.info("Exited menu state")

    def update(self, dt: float) -> None:
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if self._handle_exit_input(events):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if hasattr(self, 'menu_list'):
            if self.input_handler.is_action_pressed("up", events):
                self.menu_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.menu_list.scroll_down()

            if self.input_handler.is_action_pressed("confirm", events):
                self._select_option()

    def _setup_adaptive_scrollable_list(self) -> None:
        screen_width = base_state.DEFAULT_SCREEN_WIDTH
        screen_height = base_state.DEFAULT_SCREEN_HEIGHT

        title_height = base_state.TITLE_HEIGHT_LARGE
        bottom_padding = base_state.BOTTOM_PADDING_LARGE
        available_height = self._calc_available_height(screen_height, title_height, bottom_padding)

        list_width = self._calc_list_width(screen_width,
                                           max_width=base_state.LIST_MAX_WIDTH_LARGE,
                                           margin=base_state.LIST_MARGIN_LARGE)
        list_x = self._calc_list_x(screen_width, list_width)
        list_y = title_height

        self.menu_list = widgets.ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,
            item_height=60,
            font_size=36,
            padding=20
        )

        self._last_screen_width = screen_width
        self._last_screen_height = screen_height

    def _update_scrollable_list_dimensions(self, surface_width: int, surface_height: int) -> None:
        if (surface_width == self._last_screen_width and
                surface_height == self._last_screen_height):
            return

        title_height = base_state.TITLE_HEIGHT_LARGE
        bottom_padding = base_state.BOTTOM_PADDING_LARGE
        available_height = self._calc_available_height(surface_height, title_height, bottom_padding)

        list_width = self._calc_list_width(surface_width,
                                           max_width=base_state.LIST_MAX_WIDTH_LARGE,
                                           margin=base_state.LIST_MARGIN_LARGE)
        list_x = self._calc_list_x(surface_width, list_width)
        list_y = title_height

        self.menu_list.x = list_x
        self.menu_list.y = list_y
        self.menu_list.width = list_width
        self.menu_list.height = available_height

        self.menu_list._calculate_layout_requirements()

        self._last_screen_width = surface_width
        self._last_screen_height = surface_height

        logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _update_menu_options(self) -> None:
        if not hasattr(self, 'menu_list'):
            return

        menu_options = [
            "Browse Games",
            "Download Games",
            "Self-Update",
            "Settings",
            "Help & Support",
            "About SBC-Man",
            "Exit"
        ]

        menu_states = [True] * len(menu_options)
        self.menu_list.set_items(menu_options, menu_states)

    def _select_option(self) -> None:
        if not hasattr(self, 'menu_list'):
            return

        selected_option = self.menu_list.get_selected_item()

        if selected_option == "Browse Games":
            self.state_manager.change_state("game_list")
        elif selected_option == "Download Games":
            self.state_manager.change_state("download")
        elif selected_option == "Self-Update":
            self.state_manager.change_state("update")
        elif selected_option == "Settings":
            self.state_manager.change_state("settings")
        elif selected_option == "Help & Support":
            logger.info("Help & Support selected - not yet implemented")
        elif selected_option == "About SBC-Man":
            logger.info("About SBC-Man selected - not yet implemented")
        elif selected_option == "Exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, surface: pygame.Surface) -> None:
        self._render_background(surface)
        surface_width, surface_height = self._get_surface_dimensions(surface)

        if hasattr(self, 'menu_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            self._setup_adaptive_scrollable_list()
            self._update_menu_options()

        self._render_title(surface, "SBC-Man", y_position=50,
                          divisor=9, min_size=48, max_size=72)
        self._render_subtitle(surface, "Game Launcher & Manager", y_position=85)

        self.menu_list.render(surface)

        self._render_instructions(
            surface,
            "↑↓ Navigate  |  A/Confirm Select  |  ESC/Exit",
            scrollable_list=self.menu_list
        )