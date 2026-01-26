# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Base State Module - Abstract base class for all application states."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from ..core.state_manager import StateManager


# Standard UI colors
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
SUBTITLE_COLOR = (180, 180, 180)
INSTRUCTION_COLOR = (150, 150, 150)

# Default screen dimensions
DEFAULT_SCREEN_WIDTH = 640
DEFAULT_SCREEN_HEIGHT = 480

# Layout constants for title area
TITLE_HEIGHT_SMALL = 80      # game_list, download
TITLE_HEIGHT_MEDIUM = 90     # settings, install_settings
TITLE_HEIGHT_LARGE = 120     # menu

# Layout constants for bottom padding
BOTTOM_PADDING_SMALL = 60    # game_list, download
BOTTOM_PADDING_MEDIUM = 70   # settings, install_settings
BOTTOM_PADDING_LARGE = 80    # menu, update

# Layout constants for list widths
LIST_MIN_WIDTH = 400
LIST_MIN_WIDTH_SMALL = 300   # update options
LIST_MAX_WIDTH_STANDARD = 560
LIST_MAX_WIDTH_LARGE = 600
LIST_MARGIN_STANDARD = 40
LIST_MARGIN_LARGE = 80

# Progress area
PROGRESS_AREA_HEIGHT = 120


class BaseState(ABC):
    """Abstract base class for application states."""

    def __init__(self, state_manager: "StateManager"):
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
        """Check for exit input (ESC key or specific buttons)."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in [8, 13]:
                    return True
        return False

    # -------------------------------------------------------------------------
    # Common Rendering Helper Methods
    # -------------------------------------------------------------------------

    def _render_background(self, surface: pygame.Surface) -> None:
        """Fill surface with standard background color."""
        surface.fill(BACKGROUND_COLOR)

    def _get_surface_dimensions(self, surface: pygame.Surface) -> Tuple[int, int]:
        """Return surface width and height as a tuple."""
        return surface.get_width(), surface.get_height()

    def _calc_font_size(self, surface_width: int, divisor: int,
                        min_size: int, max_size: int) -> int:
        """Calculate adaptive font size based on surface width."""
        return min(max_size, max(min_size, surface_width // divisor))

    def _render_title(self, surface: pygame.Surface, title_text: str,
                      y_position: int = 50, divisor: int = 11,
                      min_size: int = 40, max_size: int = 56) -> None:
        """Render centered title with adaptive font size."""
        surface_width = surface.get_width()
        font_size = self._calc_font_size(surface_width, divisor, min_size, max_size)
        font = pygame.font.Font(None, font_size)
        title = font.render(title_text, True, TEXT_COLOR)
        title_rect = title.get_rect(center=(surface_width // 2, y_position))
        surface.blit(title, title_rect)

    def _render_subtitle(self, surface: pygame.Surface, subtitle_text: str,
                         y_position: int = 85, divisor: int = 25,
                         min_size: int = 20, max_size: int = 28) -> None:
        """Render centered subtitle with adaptive font size."""
        surface_width = surface.get_width()
        font_size = self._calc_font_size(surface_width, divisor, min_size, max_size)
        font = pygame.font.Font(None, font_size)
        subtitle = font.render(subtitle_text, True, SUBTITLE_COLOR)
        subtitle_rect = subtitle.get_rect(center=(surface_width // 2, y_position))
        surface.blit(subtitle, subtitle_rect)

    def _render_instructions(self, surface: pygame.Surface, base_instructions: str,
                             scrollable_list=None, y_offset: int = 20,
                             divisor: int = 25, min_size: int = 18,
                             max_size: int = 24) -> None:
        """Render adaptive instructions at the bottom of the screen."""
        surface_width, surface_height = self._get_surface_dimensions(surface)
        font_size = self._calc_font_size(surface_width, divisor, min_size, max_size)
        font = pygame.font.Font(None, font_size)

        instructions = base_instructions
        if (scrollable_list is not None and
                hasattr(scrollable_list, 'needs_scrolling') and
                scrollable_list.needs_scrolling and
                scrollable_list.show_scroll_indicators):
            instructions += "  |  PageUp/Down Fast Scroll"

        inst_surface = font.render(instructions, True, INSTRUCTION_COLOR)
        inst_rect = inst_surface.get_rect(center=(surface_width // 2, surface_height - y_offset))
        surface.blit(inst_surface, inst_rect)

    def _render_centered_text(self, surface: pygame.Surface, text: str,
                              y_position: int, color: Tuple[int, int, int] = TEXT_COLOR,
                              font_size: int = 32) -> None:
        """Render centered text at specified y position."""
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, y_position))
        surface.blit(text_surface, text_rect)

    # -------------------------------------------------------------------------
    # Common Layout Calculation Helper Methods
    # -------------------------------------------------------------------------

    def _calc_list_width(self, surface_width: int,
                         max_width: int = LIST_MAX_WIDTH_STANDARD,
                         margin: int = LIST_MARGIN_STANDARD,
                         min_width: int = LIST_MIN_WIDTH) -> int:
        """Calculate adaptive list width based on surface width."""
        return max(min_width, min(max_width, surface_width - margin))

    def _calc_list_x(self, surface_width: int, list_width: int) -> int:
        """Calculate centered x position for a list."""
        return (surface_width - list_width) // 2

    def _calc_available_height(self, surface_height: int, title_height: int,
                               bottom_padding: int, extra_height: int = 0) -> int:
        """Calculate available height for content area."""
        return surface_height - title_height - bottom_padding - extra_height
