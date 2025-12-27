"""
State Manager Module

Implements the state machine pattern for application navigation.
Manages state transitions, lifecycle, and state stack for overlays.
"""

import logging
from typing import Dict, Optional, List

import pygame
from ..hardware.paths import AppPaths

logger = logging.getLogger(__name__)


class StateManager:
    """
    State machine manager for application navigation.
    
    Manages application states, transitions between states, and maintains
    a state stack for overlay support (e.g., pause menus).
    """

    def __init__(
        self,
        screen: pygame.Surface,
        hw_config: dict,
        config: "ConfigManager",
        game_library: "GameLibrary",
        input_handler: "InputHandler",
        app_paths: AppPaths,
    ):
        """
        Initialize state manager with dependencies.
        
        Args:
            screen: Pygame display surface
            hw_config: Hardware configuration dictionary
            config: Configuration manager instance
            game_library: Game library manager instance
            input_handler: Input handler service instance
            app_paths: Application paths instance
        """
        self.screen = screen
        self.hw_config = hw_config
        self.config = config
        self.game_library = game_library
        self.input_handler = input_handler
        self.app_paths = app_paths
        
        self.states: Dict[str, "BaseState"] = {}
        self.current_state: Optional["BaseState"] = None
        self.state_stack: List["BaseState"] = []
        
        # Initialize all states
        self._initialize_states()
        
        # Set initial state to menu
        self.change_state("menu")
        
        logger.info("StateManager initialized")

    def _initialize_states(self) -> None:
        """
        Create instances of all application states.
        
        Imports and instantiates all state classes, storing them
        in the states dictionary.
        """
        from ..states.menu_state import MenuState
        from ..states.game_list_state import GameListState
        from ..states.download_state import DownloadState
        from ..states.settings_state import SettingsState
        from ..states.playing_state import PlayingState
        
        # Create state instances
        self.states["menu"] = MenuState(self)
        self.states["game_list"] = GameListState(self)
        self.states["download"] = DownloadState(self)
        self.states["settings"] = SettingsState(self)
        self.states["playing"] = PlayingState(self)
        
        logger.info(f"Initialized {len(self.states)} states")

    def change_state(self, state_name: str) -> None:
        """
        Transition from current state to a new state.
        
        Calls on_exit() on the current state, then on_enter() on the new state.
        Clears the state stack.
        
        Args:
            state_name: Name of the state to transition to
            
        Raises:
            KeyError: If state_name is not a valid state
        """
        if state_name not in self.states:
            logger.error(f"Invalid state name: {state_name}")
            raise KeyError(f"State '{state_name}' not found")
        
        previous_state = self.current_state
        
        # Exit current state
        if self.current_state:
            logger.info(f"Exiting state: {self.current_state.__class__.__name__}")
            self.current_state.on_exit()
        
        # Change to new state
        self.current_state = self.states[state_name]
        logger.info(f"Entering state: {self.current_state.__class__.__name__}")
        self.current_state.on_enter(previous_state)
        
        # Clear state stack
        self.state_stack.clear()

    def push_state(self, state_name: str) -> None:
        """
        Push a new state onto the stack (for overlays).
        
        Useful for pause menus or dialogs that should return to the
        previous state when closed.
        
        Args:
            state_name: Name of the state to push
            
        Raises:
            KeyError: If state_name is not a valid state
        """
        if state_name not in self.states:
            logger.error(f"Invalid state name: {state_name}")
            raise KeyError(f"State '{state_name}' not found")
        
        # Push current state onto stack
        if self.current_state:
            self.state_stack.append(self.current_state)
            logger.info(f"Pushed state to stack: {self.current_state.__class__.__name__}")
        
        # Change to new state
        self.change_state(state_name)

    def pop_state(self) -> None:
        """
        Return to the previous state from the stack.
        
        Restores the previous state that was pushed onto the stack.
        Does nothing if the stack is empty.
        """
        if not self.state_stack:
            logger.warning("Cannot pop state: stack is empty")
            return
        
        # Exit current state
        if self.current_state:
            logger.info(f"Exiting overlay state: {self.current_state.__class__.__name__}")
            self.current_state.on_exit()
        
        # Restore previous state
        self.current_state = self.state_stack.pop()
        logger.info(f"Restored state from stack: {self.current_state.__class__.__name__}")
        self.current_state.on_enter(None)

    def update(self, dt: float) -> None:
        """
        Update current state logic.
        
        Args:
            dt: Delta time in seconds since last update
        """
        if self.current_state:
            self.current_state.update(dt)

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """
        Route pygame events to current state.
        
        Args:
            events: List of pygame events to process
        """
        if self.current_state:
            self.current_state.handle_events(events)

    def render(self, surface: pygame.Surface) -> None:
        """
        Render current state to screen.
        
        If there are states in the stack, renders them below the current
        state for overlay effect.
        
        Args:
            surface: Surface to render to
        """
        # Render states in stack (for overlay effect)
        for state in self.state_stack:
            state.render(surface)
        
        # Render current state
        if self.current_state:
            self.current_state.render(surface)
