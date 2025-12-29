# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Game Loop Module

Main game loop implementation with event handling, update, and render cycles.

Based on: docs/other/sequence_game_loop.txt
"""

import logging
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .state_manager import StateManager

logger = logging.getLogger(__name__)


class GameLoop:
    """
    Main game loop wrapper.
    
    Handles the core game loop: event processing, state updates,
    rendering, and FPS limiting.
    """

    def __init__(self) -> None:
        """Initialize game loop."""
        self.running = False

    def run(
        self,
        state_manager: "StateManager",
        clock: pygame.time.Clock,
        target_fps: int = 60,
    ) -> None:
        """
        Execute the main game loop.
        
        Runs until the application is terminated via quit event or
        state manager signals exit.
        
        Args:
            state_manager: State manager to update and render
            clock: Pygame clock for FPS limiting
            target_fps: Target frames per second
        """
        self.running = True
        logger.info(f"Game loop started (target FPS: {target_fps})")
        
        while self.running:
            # Calculate delta time
            dt = clock.tick(target_fps) / 1000.0  # Convert to seconds
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    logger.info("Quit event received")
                    self.running = False
                    break
            
            if not self.running:
                break
            
            # Route events to state manager
            state_manager.handle_events(events)
            
            # Update state logic
            state_manager.update(dt)
            
            # Render
            state_manager.render(state_manager.screen)
            
            # Flip display
            pygame.display.flip()
        
        logger.info("Game loop ended")