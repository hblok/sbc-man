# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Update State Module - Handles the self-update process."""

import logging
import time
from typing import Optional, List

import pygame

from . import base_state
from ..services import updater
from ..views import widgets

logger = logging.getLogger(__name__)


class UpdateState(base_state.BaseState):
    """Update state for handling self-updating functionality with adaptive layout."""

    def __init__(self, state_manager: "StateManager"):
        super().__init__(state_manager)
        self.updater = updater.UpdaterService(self.config, self.app_paths)

        self.stage = "checking"
        self.message = "Checking for updates..."
        self.latest_version = None
        self.download_url = None
        self.update_available = False

        self.selected_option = 0
        self.options = []

        self.message_lines = []
        self.message_scroll_offset = 0

        self._last_surface_width = base_state.DEFAULT_SCREEN_WIDTH
        self._last_surface_height = base_state.DEFAULT_SCREEN_HEIGHT

        # Progress tracking
        self.progress = 0.0
        self.progress_message = ""

    def on_enter(self, previous_state: Optional[base_state.BaseState]) -> None:
        logger.info("Entered update state")
        self._setup_adaptive_scrollable_list()
        self._start_update_check()

    def on_exit(self) -> None:
        logger.info("Exited update state")
        self.updater.cleanup_temp_files()

    def update(self, dt: float) -> None:
        """Update method to poll for async update progress."""
        if self.stage == "updating" and self.updater.is_updating:
            # Poll for progress
            self.progress = self.updater.get_progress()
            self.progress_message = self.updater.get_message()
            
            # Check if update completed
            if self.progress >= 1.0:
                self._check_update_completion()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if self._handle_exit_input(events):
            self.state_manager.change_state("menu")
            return

        if self.stage == "available":
            self._handle_available_stage_events(events)
        elif self.stage in ["complete", "error"]:
            self._handle_completion_stage_events(events)

    def _setup_adaptive_scrollable_list(self) -> None:
        surface_width = base_state.DEFAULT_SCREEN_WIDTH
        surface_height = base_state.DEFAULT_SCREEN_HEIGHT

        bottom_padding = base_state.BOTTOM_PADDING_LARGE
        available_height = surface_height - bottom_padding

        options_height = min(120, available_height // 3)

        max_width = min(500, surface_width - base_state.LIST_MARGIN_LARGE)
        options_width = max(base_state.LIST_MIN_WIDTH_SMALL, max_width)
        options_x = self._calc_list_x(surface_width, options_width)
        options_y = available_height - options_height

        self.options_list = widgets.ScrollableList(
            x=options_x,
            y=options_y,
            width=options_width,
            height=options_height,
            item_height=40,
            font_size=28,
            padding=10
        )

        self._last_surface_width = surface_width
        self._last_surface_height = surface_height

    def _update_adaptive_layout(self, surface_width: int, surface_height: int) -> None:
        if (surface_width == self._last_surface_width and
                surface_height == self._last_surface_height):
            return

        bottom_padding = base_state.BOTTOM_PADDING_LARGE
        available_height = surface_height - bottom_padding
        options_height = min(120, available_height // 3)

        max_width = min(500, surface_width - base_state.LIST_MARGIN_LARGE)
        options_width = max(base_state.LIST_MIN_WIDTH_SMALL, max_width)
        options_x = self._calc_list_x(surface_width, options_width)
        options_y = available_height - options_height

        self.options_list.x = options_x
        self.options_list.y = options_y
        self.options_list.width = options_width
        self.options_list.height = options_height

        self.options_list._calculate_layout_requirements()

        self._last_surface_width = surface_width
        self._last_surface_height = surface_height

        logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _update_options_list(self) -> None:
        if not hasattr(self, 'options_list'):
            return
        self.options_list.set_items(self.options, [True] * len(self.options))

    def _calculate_adaptive_message_lines(self, surface_width: int) -> int:
        if surface_width >= 1024:
            return 12
        elif surface_width >= 800:
            return 8
        else:
            return 6

    def _wrap_message(self, message: str, max_width: int = 50) -> List[str]:
        if not message:
            return []

        words = message.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word if not current_line else current_line + " " + word

            if len(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def _handle_available_stage_events(self, events: List[pygame.event.Event]) -> None:
        if hasattr(self, 'options_list'):
            if self.input_handler.is_action_pressed("up", events):
                self.options_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.options_list.scroll_down()

        if self.input_handler.is_action_pressed("confirm", events):
            selected_option = (self.options_list.get_selected_item()
                             if hasattr(self, 'options_list')
                             else self.options[self.selected_option])

            if selected_option == "Download and Install":
                self._start_download()
            elif selected_option == "Cancel":
                self.state_manager.change_state("menu")

    def _handle_completion_stage_events(self, events: List[pygame.event.Event]) -> None:
        max_visible_lines = self._calculate_adaptive_message_lines(self._last_surface_width)

        if self.input_handler.is_action_pressed("up", events):
            self.message_scroll_offset = max(0, self.message_scroll_offset - 1)
        elif self.input_handler.is_action_pressed("down", events):
            max_scroll = max(0, len(self.message_lines) - max_visible_lines)
            self.message_scroll_offset = min(max_scroll, self.message_scroll_offset + 1)

        if self.input_handler.is_action_pressed("confirm", events):
            self.state_manager.change_state("menu")

    def _start_update_check(self) -> None:
        self.stage = "checking"
        self.message = "Checking for updates..."
        self.options = []
        self._update_message_display()

        try:
            self.update_available, self.latest_version, self.download_url = (
                self.updater.check_for_updates())

            if self.update_available and self.download_url:
                self.stage = "available"
                self.message = f"Update available: version {self.latest_version}"
                self.options = ["Download and Install", "Cancel"]
                self.selected_option = 0
            else:
                self.stage = "complete"
                self.message = "You are running the latest version"
                self.options = ["OK"]
                self.selected_option = 0

            self._update_message_display()
            self._update_options_list()

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            self.stage = "error"
            self.message = f"Error checking for updates: {str(e)}"
            self.options = ["OK"]
            self.selected_option = 0
            self._update_message_display()
            self._update_options_list()

    def _start_download(self) -> None:
        self.stage = "downloading"
        self.message = "Downloading update..."
        self.progress = 0.0
        self.progress_message = "Downloading update..."
        self.options = []
        self._update_message_display()
        self._update_options_list()

        try:
            wheel_path = self.updater.start_update(
                self.download_url,
#                progress_callback=self._update_progress
            )

            # if wheel_path:
            #     self._start_installation(wheel_path)
            # else:
            #     self.stage = "error"
            #     self.message = "Failed to download update"
            #     self.options = ["OK"]
            #     self.selected_option = 0
            #     self._update_message_display()
            #     self._update_options_list()

        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            self.stage = "error"
            self.message = f"Error downloading update: {str(e)}"
            self.options = ["OK"]
            self.selected_option = 0
            self._update_message_display()
            self._update_options_list()

    def _start_installation(self, wheel_path) -> None:
        self.stage = "installing"
        self.message = "Installing update..."
        self.progress = 0.6  # Start at 60% (download complete)
        self.progress_message = "Installing update..."
        self.options = []
        self._update_message_display()
        self._update_options_list()

        try:
            success, message = self.updater.install_update(
                wheel_path,
#                progress_callback=self._update_progress
            )

            if success is True and message:
                self.stage = "complete"
                self.message = (f"Update installed successfully!\n{message}\n\n"
                              "Restart the application to apply changes.")
                self.options = ["OK"]
                self.selected_option = 0
                logger.info("Update installation completed successfully")
            else:
                self.stage = "error"
                error_message = message if message else "Unknown installation error"
                self.message = f"Installation failed: {error_message}"
                self.options = ["OK"]
                self.selected_option = 0
                logger.error(f"Update installation failed: {error_message}")

            self._update_message_display()
            self._update_options_list()

        except Exception as e:
            import traceback
            error_details = str(e)
            error_traceback = traceback.format_exc()

            logger.error(f"Unexpected error installing update: {error_details}")
            logger.error(f"Full traceback: {error_traceback}")

            self.stage = "error"
            self.message = f"Unexpected error during installation: {error_details}"
            self.options = ["OK"]
            self.selected_option = 0
            self._update_message_display()
            self._update_options_list()

    def _update_message_display(self) -> None:
        self.message_lines = self._wrap_message(self.message, max_width=40)
        self.message_scroll_offset = 0

    def render(self, surface: pygame.Surface) -> None:
        self._render_background(surface)
        surface_width, surface_height = self._get_surface_dimensions(surface)

        logger.info(f"render, stage={self.stage}")

        if hasattr(self, 'options_list'):
            self._update_adaptive_layout(surface_width, surface_height)
        else:
            self._setup_adaptive_scrollable_list()

        self._render_title(surface, "Self-Update", y_position=50,
                          divisor=10, min_size=48, max_size=64)

        self._render_subtitle(surface, f"Current version: {self.updater.current_version}",
                             y_position=85)

        self._render_message_area(surface, surface_width, surface_height)

        if self.stage in ["checking", "downloading", "installing"]:
            self._render_progress_indicator(surface, surface_width, surface_height)

        self._update_options_list()
        self.options_list.render(surface)

        self._render_update_instructions(surface, surface_width, surface_height)

    def _update_progress(self, progress: float) -> None:
        """Update progress tracking.
        
        Args:
            progress: Progress value from 0.0 to 1.0
        """
        self.progress = progress

    def _render_message_area(self, surface: pygame.Surface,
                             surface_width: int, surface_height: int) -> None:
        message_area_start = 120
        options_list_bottom = (self.options_list.y + self.options_list.actual_height
                              if hasattr(self, 'options_list') else surface_height - 100)

        font_size = self._calc_font_size(surface_width, 20, 24, 32)
        font = pygame.font.Font(None, font_size)
        max_visible_lines = self._calculate_adaptive_message_lines(surface_width)

        if self.message_lines:
            start_idx = self.message_scroll_offset
            end_idx = min(start_idx + max_visible_lines, len(self.message_lines))

            y_offset = message_area_start
            for i in range(start_idx, end_idx):
                line = self.message_lines[i]
                color = self._get_message_color()
                text = font.render(line, True, color)
                text_rect = text.get_rect(center=(surface_width // 2, y_offset))
                surface.blit(text, text_rect)
                y_offset += min(30, surface_height // 16)

            if len(self.message_lines) > max_visible_lines:
                self._render_scroll_indicators(surface, message_area_start, y_offset)

    def _render_scroll_indicators(self, surface: pygame.Surface, top: int, bottom: int) -> None:
        font_small = pygame.font.Font(None, 20)

        if self.message_scroll_offset > 0:
            up_arrow = font_small.render("▲", True, (150, 150, 150))
            surface.blit(up_arrow, (surface.get_width() - 30, top))

        max_visible_lines = self._calculate_adaptive_message_lines(surface.get_width())
        max_scroll = max(0, len(self.message_lines) - max_visible_lines)
        if self.message_scroll_offset < max_scroll:
            down_arrow = font_small.render("▼", True, (150, 150, 150))
            surface.blit(down_arrow, (surface.get_width() - 30, bottom - 20))

    def _get_message_color(self) -> tuple:
        if self.stage == "error":
            return (255, 100, 100)
        elif self.stage == "complete":
            return (100, 255, 100)
        else:
            return (255, 255, 255)

    def _render_progress_indicator(self, surface: pygame.Surface,
                                     surface_width: int, surface_height: int) -> None:
        """Render a progress bar showing download/installation progress."""
        font_size = self._calc_font_size(surface_width, 18, 28, 36)
        bar_width = min(surface_width - 100, 600)
        bar_height = min(30, surface_height // 16)
        bar_x = (surface_width - bar_width) // 2
        bar_y = 120

        progress_bar = widgets.ProgressBar(
            x=bar_x,
            y=bar_y,
            width=bar_width,
            height=bar_height,
            font_size=font_size
        )
        progress_bar.render(surface, self.progress, self.progress_message)

    def _render_update_instructions(self, surface: pygame.Surface,
                                    surface_width: int, surface_height: int) -> None:
        max_visible_lines = self._calculate_adaptive_message_lines(surface_width)

        if (self.stage in ["complete", "error"] and
                len(self.message_lines) > max_visible_lines):
            instructions = "↑↓ Scroll Message  |  A/Confirm Continue"
        elif self.options_list.needs_scrolling and self.options_list.show_scroll_indicators:
            instructions = "↑↓ Navigate  |  A/Confirm Select  |  PageUp/Down Fast Scroll"
        else:
            instructions = "A/Confirm Select  |  B/Cancel Back"

        self._render_instructions(surface, instructions, y_offset=15,
                                 divisor=35, min_size=16, max_size=22)
