# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Playing State Module

State for running a game as a subprocess.

Based on: docs/code/class_states_playing_state.txt
"""

from pathlib import Path
import logging
import subprocess
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..services.process_launcher import ProcessLauncher

logger = logging.getLogger(__name__)


class PlayingState(BaseState):
    """
    Game playing state.

    Launches and monitors a game process, handling the transition
    back to the game list when the game exits.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize playing state and launch game."""
        logger.info("Entered playing state")

        # Get the selected game from state manager
        game = self.state_manager.selected_game
        
        if game is None:
            logger.error("No game selected for launch")
            self.message = "Error: No game selected"
            self.game_running = False
            return

        logger.info(f"Launching game: {game.name}")

        # Initialize the process launcher
        self.game_running = True
        self.launcher = ProcessLauncher(self.hw_config)
        self.game_process = None

        # Launch the game in a non-blocking way
        try:
            self.launcher.launch_game(game)
            self.message = f"Playing: {game.name}"
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            self.message = f"Error launching game: {e}"
            self.game_running = False

    def DELETE_launch_game_async(self, game) -> None:
        """
        Launch game as an asynchronous subprocess.
        
        Args:
            game: Game object to launch
            
        Raises:
            Exception: If game launch fails
        """
        if not game.installed:
            raise ValueError(f"Game not installed: {game.name}")

        # Get install path as string
        install_path_str = game.install_path
        
        # Validate install path exists
        if not install_path_str:
            raise ValueError(f"Game install path is empty: {game.name}")

        # TODO
        import os
        if not os.path.exists(install_path_str):
            raise ValueError(f"Game installation path not found: {install_path_str}")

        # Build entry point path
        entry_point = os.path.join(install_path_str, game.entry_point)
        #entry_point = Path("~/.local/lib/python3.11/site-packages/maxblok/fish/main.py").resolve()
        #entry_point = Path.home() / ".local/lib/python3.11/site-packages/maxblok/fish/main.py"
        if not os.path.exists(entry_point):
            raise ValueError(f"Game entry point not found: {entry_point}")

        logger.info(f"Launching game subprocess: {game.name}")
        logger.info(f"  Install path: {install_path_str}")
        logger.info(f"  Entry point: {entry_point}")

        # Build environment variables
        env = self._build_environment(game)

        # Launch game process (non-blocking)
        try:
            self.game_process = subprocess.Popen(
                ["python3", entry_point],
                cwd=install_path_str,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info(f"Game process started with PID: {self.game_process.pid}")
        except Exception as e:
            logger.error(f"Failed to start game process: {e}")
            raise

    def _build_environment(self, game) -> dict:
        """
        Build environment variables for game process.
        
        Args:
            game: Game being launched
            
        Returns:
            dict: Environment variables
        """
        import os
        
        # Start with current environment
        env = os.environ.copy()

        # Add game-specific environment variables
        if hasattr(game, 'custom_resolution') and game.custom_resolution:
            env["GAME_RESOLUTION"] = f"{game.custom_resolution.width}x{game.custom_resolution.height}"

        if hasattr(game, 'custom_fps') and game.custom_fps:
            env["GAME_FPS"] = str(game.custom_fps)

        # Add hardware config info
        env["DEVICE_TYPE"] = self.hw_config.get("detected_device", "desktop")
        env["OS_TYPE"] = self.hw_config.get("detected_os", "standard_linux")

        return env

    def on_exit(self) -> None:
        """Cleanup playing state."""
        logger.info("Exited playing state")
        
        # Terminate game process if still running
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
        
        # Clear selected game from state manager
        self.state_manager.selected_game = None

    def _is_process_running(self) -> bool:
        """
        Check if the game process is still running.
        
        Returns:
            bool: True if process is running
        """
        if self.game_process is None:
            return False
        return self.game_process.poll() is None

    def update(self, dt: float) -> None:
        """Update playing state logic."""
        # Check if game is still running
        if self.game_running and self.game_process is not None:
            if not self._is_process_running():
                logger.info("Game process has exited")
                
                # Get exit code
                exit_code = self.game_process.poll()
                if exit_code != 0:
                    logger.error(f"Game exited with error code: {exit_code}")
                
                # Return to game list
                self.state_manager.change_state("game_list")

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle playing state input."""
        # Allow returning to game list (user-initiated exit)
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            logger.info("User requested to exit game")
            self.state_manager.change_state("game_list")

    def render(self, surface: pygame.Surface) -> None:
        """Render playing state."""
        surface.fill((20, 20, 30))

        # Render message
        font = pygame.font.Font(None, 48)
        text = font.render(self.message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text, text_rect)

        # Render instructions
        font_small = pygame.font.Font(None, 32)
        instruction = font_small.render("Press ESC or Cancel to return", True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 50))
        surface.blit(instruction, instruction_rect)
