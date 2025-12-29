# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Base State Module

Abstract base class for all application states.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from ..core.state_manager import StateManager


class BaseState(ABC):
    """
    Abstract base class for application states.
    
    Defines the interface that all states must implement for
    lifecycle management, event handling, updates, and rendering.
    """

    def __init__(self, state_manager: "StateManager"):
        """
        Initialize base state.
        
        Args:
            state_manager: Reference to the state manager
        """
        self.state_manager = state_manager
        self.screen = state_manager.screen
        self.hw_config = state_manager.hw_config
        self.config = state_manager.config
        self.game_library = state_manager.game_library
        self.input_handler = state_manager.input_handler
        self.app_paths = state_manager.app_paths

    @abstractmethod
    def on_enter(self, previous_state: Optional["BaseState"]) -> None:
        """
        Called when entering this state.
        
        Use this to initialize state-specific resources and setup.
        
        Args:
            previous_state: The state we're transitioning from, or None
        """
        pass

    @abstractmethod
    def on_exit(self) -> None:
        """
        Called when exiting this state.
        
        Use this to cleanup state-specific resources.
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update state logic.
        
        Called every frame to update state-specific logic.
        
        Args:
            dt: Delta time in seconds since last update
        """
        pass

    @abstractmethod
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """
        Handle pygame events.
        
        Process input events and update state accordingly.
        
        Args:
            events: List of pygame events to process
        """
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """
        Render state to surface.
        
        Draw all state-specific UI elements.
        
        Args:
            surface: Surface to render to
        """
        pass

    def _handle_exit_input(self, events: List[pygame.event.Event]) -> bool:
        """
        Check for exit input (ESC key or specific buttons).
        
        Args:
            events: List of pygame events
            
        Returns:
            bool: True if exit was requested
        """

        # FIXME
        for event in events:
            # ESC key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            
            # Hardware buttons 8, 13, or menu button
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in [8, 13]:
                    return True
        
        return False
