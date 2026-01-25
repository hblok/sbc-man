# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Version overlay widget for displaying application version."""

import pygame

from sbcman import version


class VersionOverlay:
    """Renders the application version in a subtle corner overlay."""

    def __init__(self, font_size: int = 16, padding: int = 8):
        self.font_size = font_size
        self.padding = padding
        self.text_color = (120, 120, 120)
        self._font = None

    def _get_font(self) -> pygame.font.Font:
        if self._font is None:
            self._font = pygame.font.Font(None, self.font_size)
        return self._font

    def render(self, surface: pygame.Surface) -> None:
        """Render version text in bottom-right corner."""
        font = self._get_font()
        version_text = f"v{version.VERSION}"
        text_surface = font.render(version_text, True, self.text_color)

        surface_width = surface.get_width()
        surface_height = surface.get_height()

        x = surface_width - text_surface.get_width() - self.padding
        y = surface_height - text_surface.get_height() - self.padding

        surface.blit(text_surface, (x, y))
