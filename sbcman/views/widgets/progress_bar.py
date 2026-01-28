# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Progress Bar Widget Module

Provides a reusable progress bar widget for displaying download/installation progress.
"""

import pygame
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class ProgressBar:
    """A progress bar widget for displaying progress information."""

    def __init__(self,
                 x: int,
                 y: int,
                 width: int,
                 height: int = 30,
                 font_size: int = 24,
                 background_color: Tuple[int, int, int] = (100, 100, 100),
                 progress_color: Tuple[int, int, int] = (0, 200, 0),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        """Initialize the progress bar.

        Args:
            x: X position of the progress bar
            y: Y position of the progress bar
            width: Width of the progress bar
            height: Height of the progress bar
            font_size: Font size for text rendering
            background_color: RGB color for the background bar
            progress_color: RGB color for the progress fill
            text_color: RGB color for text
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.background_color = background_color
        self.progress_color = progress_color
        self.text_color = text_color
        self._font = None

    def _get_font(self) -> pygame.font.Font:
        """Get or create the font for rendering text."""
        if self._font is None:
            self._font = pygame.font.Font(None, self.font_size)
        return self._font

    def render(self,
               surface: pygame.Surface,
               progress: float,
               message: str = "") -> None:
        """Render the progress bar on the given surface.

        Args:
            surface: The pygame surface to render on
            progress: Progress value between 0.0 and 1.0
            message: Optional message to display above the progress bar
        """
        logger.debug(f"progress {progress}")
        
        clamped_progress = max(0.0, min(1.0, progress))
        font = self._get_font()

        # Render message if provided
        if message:
            text = font.render(message, True, self.text_color)
            text_rect = text.get_rect(center=(surface.get_width() // 2, self.y - 30))
            surface.blit(text, text_rect)

        # Draw background bar
        pygame.draw.rect(surface, self.background_color,
                        (self.x, self.y, self.width, self.height))

        # Draw progress fill
        fill_width = int(self.width * clamped_progress)
        pygame.draw.rect(surface, self.progress_color,
                        (self.x, self.y, fill_width, self.height))

        # Draw percentage text
        percent_text = font.render(f"{int(clamped_progress * 100)}%", True, self.text_color)
        percent_rect = percent_text.get_rect(center=(surface.get_width() // 2,
                                                    self.y + self.height + 25))
        surface.blit(percent_text, percent_rect)
