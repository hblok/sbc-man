# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Update State Module

Handles the self-update process including checking for updates,
downloading, and installing with user feedback.

Based on: docs/code/class_states_update_state.txt
"""

import logging
from typing import Optional, List
import pygame

from .base_state import BaseState
from ..services.updater import UpdaterService
from ..views.widgets import ScrollableList

logger = logging.getLogger(__name__)


class UpdateState(BaseState):
    """
    Update state for handling self-updating functionality.
    
    Provides UI for checking, downloading, and installing updates
    with progress indication and error handling.
    Now optimized for 640x480 resolution with scrolling for long messages.
    """

    def __init__(self, state_manager: "StateManager"):
        """Initialize update state."""
        super().__init__(state_manager)
        self.updater = UpdaterService(self.config, self.app_paths)
        
        # Update process state
        self.stage = "checking"  # "checking", "available", "downloading", "installing", "complete", "error"
        self.message = "Checking for updates..."
        self.latest_version = None
        self.download_url = None
        self.update_available = False
        
        # UI state
        self.selected_option = 0
        self.options = []
        
        # Scrolling for long messages
        self.message_lines = []
        self.message_scroll_offset = 0
        self.max_visible_message_lines = 6  # For 640x480 constraint

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize update state."""
        logger.info("Entered update state")
        
        # Initialize scrollable list for options
        self._setup_scrollable_list()
        
        # Start update check
        self._start_update_check()

    def on_exit(self) -> None:
        """Cleanup update state."""
        logger.info("Exited update state")
        # Clean up any temporary files
        self.updater.cleanup_temp_files()

    def update(self, dt: float) -> None:
        """Update logic."""
        pass  # Updates are handled asynchronously in events

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle input events."""
        # Check for exit
        if self._handle_exit_input(events):
            self.state_manager.change_state("menu")
            return

        # Handle navigation based on current stage
        if self.stage == "available":
            self._handle_available_stage_events(events)
        elif self.stage in ["complete", "error"]:
            self._handle_completion_stage_events(events)

    def _setup_scrollable_list(self, surface_height: int = 480) -> None:
        """Setup the scrollable list for options."""
        # Options list positioned at bottom of screen
        self.options_list = ScrollableList(
            x=80,   # Centered
            y=380,  # Near bottom for options
            width=480,
            height=80,  # Small area for 1-2 options
            item_height=40,
            font_size=28,
            padding=10
        )

    def _update_options_list(self) -> None:
        """Update the options scrollable list."""
        if not hasattr(self, 'options_list'):
            return

        self.options_list.set_items(self.options, [True] * len(self.options))

    def _wrap_message(self, message: str, max_width: int = 50) -> List[str]:
        """Wrap message text to fit within screen width."""
        if not message:
            return []
        
        words = message.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word if not current_line else current_line + " " + word
            
            # Simple character count approximation (could be improved with font metrics)
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
        """Handle events when update is available."""
        # Handle scrolling through options
        if hasattr(self, 'options_list'):
            if self.input_handler.is_action_pressed("up", events):
                self.options_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.options_list.scroll_down()

        # Select option
        if self.input_handler.is_action_pressed("confirm", events):
            selected_option = self.options_list.get_selected_item() if hasattr(self, 'options_list') else self.options[self.selected_option]
            
            if selected_option == "Download and Install":
                self._start_download()
            elif selected_option == "Cancel":
                self.state_manager.change_state("menu")

    def _handle_completion_stage_events(self, events: List[pygame.event.Event]) -> None:
        """Handle events when update is complete or failed."""
        # Handle scrolling through long messages
        if self.input_handler.is_action_pressed("up", events):
            self.message_scroll_offset = max(0, self.message_scroll_offset - 1)
        elif self.input_handler.is_action_pressed("down", events):
            max_scroll = max(0, len(self.message_lines) - self.max_visible_message_lines)
            self.message_scroll_offset = min(max_scroll, self.message_scroll_offset + 1)

        # Handle option selection
        if self.input_handler.is_action_pressed("confirm", events):
            self.state_manager.change_state("menu")

    def _start_update_check(self) -> None:
        """Start checking for updates."""
        self.stage = "checking"
        self.message = "Checking for updates..."
        self.options = []
        self._update_message_display()
        
        try:
            # Check for updates
            self.update_available, self.latest_version, self.download_url = self.updater.check_for_updates()
            
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
        """Start downloading the update."""
        self.stage = "downloading"
        self.message = "Downloading update..."
        self.options = []
        self._update_message_display()
        self._update_options_list()
        
        try:
            # Download the update
            wheel_path = self.updater.download_update(self.download_url)
            
            if wheel_path:
                self._start_installation(wheel_path)
            else:
                self.stage = "error"
                self.message = "Failed to download update"
                self.options = ["OK"]
                self.selected_option = 0
                self._update_message_display()
                self._update_options_list()
                
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            self.stage = "error"
            self.message = f"Error downloading update: {str(e)}"
            self.options = ["OK"]
            self.selected_option = 0
            self._update_message_display()
            self._update_options_list()

    def _start_installation(self, wheel_path) -> None:
        """Start installing the update."""
        self.stage = "installing"
        self.message = "Installing update..."
        self.options = []
        self._update_message_display()
        self._update_options_list()
        
        try:
            # Install the update
            success, message = self.updater.install_update(wheel_path)
            
            # Ensure we have valid success state and message
            if success is True and message:
                self.stage = "complete"
                self.message = f"Update installed successfully!\n{message}\n\nRestart the application to apply changes."
                self.options = ["OK"]
                self.selected_option = 0
                logger.info("Update installation completed successfully")
            else:
                # Handle failure case with detailed error information
                self.stage = "error"
                error_message = message if message else "Unknown installation error"
                self.message = f"Installation failed: {error_message}"
                self.options = ["OK"]
                self.selected_option = 0
                logger.error(f"Update installation failed: {error_message}")
                
            self._update_message_display()
            self._update_options_list()
                
        except Exception as e:
            # Catch any unexpected exceptions during the installation process
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
        """Update the wrapped message lines and reset scroll."""
        self.message_lines = self._wrap_message(self.message, max_width=40)
        self.message_scroll_offset = 0

    def render(self, surface: pygame.Surface) -> None:
        """Render the update screen optimized for 640x480."""
        surface.fill((20, 20, 30))
        
        # Render title
        font_large = pygame.font.Font(None, 64)  # Slightly smaller for space
        title = font_large.render("Self-Update", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 50))
        surface.blit(title, title_rect)
        
        # Render current version info
        font_medium = pygame.font.Font(None, 28)  # Smaller for space
        current_version_text = f"Current version: {self.updater.current_version}"
        version_text = font_medium.render(current_version_text, True, (200, 200, 200))
        version_rect = version_text.get_rect(center=(surface.get_width() // 2, 90))
        surface.blit(version_text, version_rect)
        
        # Calculate message area (constrained for 640x480)
        message_area_start = 140
        message_area_height = 180  # Constrained height
        message_area_end = message_area_start + message_area_height
        
        # Render status message with scrolling support
        font = pygame.font.Font(None, 32)  # Slightly smaller for more content
        
        if self.message_lines:
            # Calculate visible range
            start_idx = self.message_scroll_offset
            end_idx = min(start_idx + self.max_visible_message_lines, len(self.message_lines))
            
            y_offset = message_area_start
            for i in range(start_idx, end_idx):
                line = self.message_lines[i]
                color = self._get_message_color()
                text = font.render(line, True, color)
                text_rect = text.get_rect(center=(surface.get_width() // 2, y_offset))
                surface.blit(text, text_rect)
                y_offset += 30
            
            # Show scroll indicators if needed
            if len(self.message_lines) > self.max_visible_message_lines:
                self._render_scroll_indicators(surface, message_area_start, message_area_end)
        
        # Render progress indicator for active stages
        if self.stage in ["checking", "downloading", "installing"]:
            self._render_progress_indicator(surface)
        
        # Initialize and render options list
        if not hasattr(self, 'options_list'):
            self._setup_scrollable_list(surface.get_height())
        
        self._update_options_list()
        self.options_list.render(surface)
        
        # Render instructions at the bottom
        font_instruction = pygame.font.Font(None, 22)
        if self.stage in ["complete", "error"] and len(self.message_lines) > self.max_visible_message_lines:
            instructions = "↑↓ Scroll Message  |  A/Confirm Continue"
        else:
            instructions = "A/Confirm Select  |  B/Cancel Back"
        
        inst_surface = font_instruction.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() - 15))
        surface.blit(inst_surface, inst_rect)

    def _render_scroll_indicators(self, surface: pygame.Surface, top: int, bottom: int) -> None:
        """Render scroll indicators for long messages."""
        font_small = pygame.font.Font(None, 20)
        
        # Up indicator
        if self.message_scroll_offset > 0:
            up_arrow = font_small.render("▲", True, (150, 150, 150))
            surface.blit(up_arrow, (surface.get_width() - 30, top))
        
        # Down indicator
        max_scroll = max(0, len(self.message_lines) - self.max_visible_message_lines)
        if self.message_scroll_offset < max_scroll:
            down_arrow = font_small.render("▼", True, (150, 150, 150))
            surface.blit(down_arrow, (surface.get_width() - 30, bottom - 20))

    def _get_message_color(self) -> tuple:
        """Get color for the current message based on stage."""
        if self.stage == "error":
            return (255, 100, 100)  # Red for errors
        elif self.stage == "complete":
            return (100, 255, 100)  # Green for success
        else:
            return (255, 255, 255)  # White for normal messages

    def _render_progress_indicator(self, surface: pygame.Surface) -> None:
        """Render a simple progress indicator."""
        # Draw animated dots for progress indication
        import time
        dot_count = int(time.time() * 2) % 4
        dots = "." * dot_count
        
        font = pygame.font.Font(None, 36)
        progress_text = font.render(dots, True, (255, 255, 0))
        progress_rect = progress_text.get_rect(center=(surface.get_width() // 2, 340))
        surface.blit(progress_text, progress_rect)