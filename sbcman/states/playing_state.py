# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Playing State Module - State for running a game as a subprocess."""

import logging
import subprocess
from typing import Optional, List

import pygame

from .base_state import BaseState, INSTRUCTION_COLOR
from ..services import process_launcher

logger = logging.getLogger(__name__)


class PlayingState(BaseState):
    """Game playing state - launches and monitors a game process."""

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        logger.info("Entered playing state")

        game = self.state_manager.selected_game

        if game is None:
            logger.error("No game selected for launch")
            self.message = "Error: No game selected"
            self.game_running = False
            return

        logger.info(f"Launching game: {game.name}")

        self.game_running = True
        self.launcher = process_launcher.ProcessLauncher(self.hw_config)
        self.game_process = None

        try:
            self.launcher.launch_game(game)
            self.message = f"Playing: {game.name}"
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            self.message = f"Error launching game: {e}"
            self.game_running = False

    def on_exit(self) -> None:
        logger.info("Exited playing state")

        if self.game_process and self._is_process_running():
            logger.info("Terminating game process")
            self.game_process.terminate()

            try:
                self.game_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate gracefully, killing")
                self.game_process.kill()

        self.game_running = False
        self.game_process = None
        self.state_manager.selected_game = None

    def _is_process_running(self) -> bool:
        if self.game_process is None:
            return False
        return self.game_process.poll() is None

    def update(self, dt: float) -> None:
        if self.game_running and self.game_process is not None:
            if not self._is_process_running():
                logger.info("Game process has exited")

                exit_code = self.game_process.poll()
                if exit_code != 0:
                    logger.error(f"Game exited with error code: {exit_code}")

                self.state_manager.change_state("game_list")

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            logger.info("User requested to exit game")
            self.state_manager.change_state("game_list")

    def render(self, surface: pygame.Surface) -> None:
        self._render_background(surface)
        surface_width, surface_height = self._get_surface_dimensions(surface)

        self._render_centered_text(surface, self.message,
                                   y_position=surface_height // 2,
                                   font_size=48)

        self._render_centered_text(surface, "Press ESC or Cancel to return",
                                   y_position=surface_height // 2 + 50,
                                   color=INSTRUCTION_COLOR,
                                   font_size=32)