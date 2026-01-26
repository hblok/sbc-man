# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Settings State Module - State for configuring application settings."""

import logging
from typing import Optional, List

import pygame

from . import base_state
from ..views import widgets

logger = logging.getLogger(__name__)


class SettingsState(base_state.BaseState):
    """Settings configuration state with adaptive layout."""

    def on_enter(self, previous_state: Optional[base_state.BaseState]) -> None:
        logger.info("Entered settings state")
        self._setup_adaptive_scrollable_list()
        self._update_settings_options()

    def on_exit(self) -> None:
        logger.info("Exited settings state")
        self.config.save()

    def update(self, dt: float) -> None:
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            self.state_manager.change_state("menu")
            return

        if hasattr(self, 'settings_list'):
            if self.input_handler.is_action_pressed("up", events):
                self.settings_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.settings_list.scroll_down()

            if self.input_handler.is_action_pressed("confirm", events):
                self._select_option()

    def _setup_adaptive_scrollable_list(self) -> None:
        screen_width = base_state.DEFAULT_SCREEN_WIDTH
        screen_height = base_state.DEFAULT_SCREEN_HEIGHT

        title_height = base_state.TITLE_HEIGHT_MEDIUM
        bottom_padding = base_state.BOTTOM_PADDING_MEDIUM
        available_height = self._calc_available_height(screen_height, title_height, bottom_padding)

        list_width = self._calc_list_width(screen_width)
        list_x = self._calc_list_x(screen_width, list_width)
        list_y = title_height

        self.settings_list = widgets.ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,
            item_height=50,
            font_size=30,
            padding=10
        )

        self._last_screen_width = screen_width
        self._last_screen_height = screen_height

    def _update_scrollable_list_dimensions(self, surface_width: int, surface_height: int) -> None:
        if (surface_width == self._last_screen_width and
                surface_height == self._last_screen_height):
            return

        title_height = base_state.TITLE_HEIGHT_MEDIUM
        bottom_padding = base_state.BOTTOM_PADDING_MEDIUM
        available_height = self._calc_available_height(surface_height, title_height, bottom_padding)

        list_width = self._calc_list_width(surface_width)
        list_x = self._calc_list_x(surface_width, list_width)
        list_y = title_height

        self.settings_list.x = list_x
        self.settings_list.y = list_y
        self.settings_list.width = list_width
        self.settings_list.height = available_height

        self.settings_list._calculate_layout_requirements()

        self._last_screen_width = surface_width
        self._last_screen_height = surface_height

        logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _update_settings_options(self) -> None:
        if not hasattr(self, 'settings_list'):
            return

        settings_options = [
            "Install Settings",

# DO NOT REMOVE
#            "Display Settings",
#            "Input Mappings", 
#            "Audio Settings",
#            "Network Settings",
#            "Storage Management",
#            "System Information",
            
            "About SBC-Man",
            "Back to Menu"
        ]

        settings_states = [True] * len(settings_options)
        self.settings_list.set_items(settings_options, settings_states)

    def _select_option(self) -> None:
        if not hasattr(self, 'settings_list'):
            return

        selected_item = self.settings_list.get_selected_item()

        if selected_item == "Back to Menu":
            self.state_manager.change_state("menu")
        elif selected_item == "Install Settings":
            self.state_manager.change_state("install_settings")
        else:
            logger.info(f"Settings option selected: {selected_item}")

    def render(self, surface: pygame.Surface) -> None:
        self._render_background(surface)
        surface_width, surface_height = self._get_surface_dimensions(surface)

        if hasattr(self, 'settings_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            self._setup_adaptive_scrollable_list()
            self._update_settings_options()

        self._render_title(surface, "Settings", y_position=45)

        self.settings_list.render(surface)

        self._render_instructions(
            surface,
            "↑↓ Navigate  |  A/Confirm Select  |  B/Cancel Back",
            scrollable_list=self.settings_list
        )
