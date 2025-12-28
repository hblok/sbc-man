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

logger = logging.getLogger(__name__)


class UpdateState(BaseState):
    """
    Update state for handling self-updating functionality.
    
    Provides UI for checking, downloading, and installing updates
    with progress indication and error handling.
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

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize update state."""
        logger.info("Entered update state")
        
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

    def _handle_available_stage_events(self, events: List[pygame.event.Event]) -> None:
        """Handle events when update is available."""
        # Navigate options
        if self.input_handler.is_action_pressed("up", events):
            self.selected_option = (self.selected_option - 1) % len(self.options)

        if self.input_handler.is_action_pressed("down", events):
            self.selected_option = (self.selected_option + 1) % len(self.options)

        # Select option
        if self.input_handler.is_action_pressed("confirm", events):
            option = self.options[self.selected_option]
            
            if option == "Download and Install":
                self._start_download()
            elif option == "Cancel":
                self.state_manager.change_state("menu")

    def _handle_completion_stage_events(self, events: List[pygame.event.Event]) -> None:
        """Handle events when update is complete or failed."""
        if self.input_handler.is_action_pressed("confirm", events):
            self.state_manager.change_state("menu")

    def _start_update_check(self) -> None:
        """Start checking for updates."""
        self.stage = "checking"
        self.message = "Checking for updates..."
        self.options = []
        
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
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            self.stage = "error"
            self.message = f"Error checking for updates: {str(e)}"
            self.options = ["OK"]
            self.selected_option = 0

    def _start_download(self) -> None:
        """Start downloading the update."""
        self.stage = "downloading"
        self.message = "Downloading update..."
        self.options = []
        
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
                
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            self.stage = "error"
            self.message = f"Error downloading update: {str(e)}"
            self.options = ["OK"]
            self.selected_option = 0

    def _start_installation(self, wheel_path) -> None:
        """Start installing the update."""
        self.stage = "installing"
        self.message = "Installing update..."
        self.options = []
        
        try:
            # Install the update
            success, message = self.updater.install_update(wheel_path)
            
            if success:
                self.stage = "complete"
                self.message = "Update installed successfully!\nRestart the application to apply changes."
                self.options = ["OK"]
                self.selected_option = 0
            else:
                self.stage = "error"
                self.message = f"Installation failed: {message}"
                self.options = ["OK"]
                self.selected_option = 0
                
        except Exception as e:
            logger.error(f"Error installing update: {e}")
            self.stage = "error"
            self.message = f"Error installing update: {str(e)}"
            self.options = ["OK"]
            self.selected_option = 0

    def render(self, surface: pygame.Surface) -> None:
        """Render the update screen."""
        # Clear screen
        surface.fill((20, 20, 30))
        
        # Render title
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("Self-Update", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(title, title_rect)
        
        # Render current version info
        font_medium = pygame.font.Font(None, 36)
        current_version_text = f"Current version: {self.updater.current_version}"
        version_text = font_medium.render(current_version_text, True, (200, 200, 200))
        version_rect = version_text.get_rect(center=(surface.get_width() // 2, 180))
        surface.blit(version_text, version_rect)
        
        # Render status message
        font = pygame.font.Font(None, 48)
        
        # Handle multi-line messages
        lines = self.message.split('\n')
        y_offset = 280
        
        for line in lines:
            color = self._get_message_color()
            text = font.render(line, True, color)
            text_rect = text.get_rect(center=(surface.get_width() // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 50
        
        # Render options if available
        if self.options:
            y_offset = 450
            for i, option in enumerate(self.options):
                color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
                text = font.render(option, True, color)
                text_rect = text.get_rect(center=(surface.get_width() // 2, y_offset + i * 60))
                surface.blit(text, text_rect)
        
        # Render progress indicator for active stages
        if self.stage in ["checking", "downloading", "installing"]:
            self._render_progress_indicator(surface)

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
        progress_rect = progress_text.get_rect(center=(surface.get_width() // 2, 400))
        surface.blit(progress_text, progress_rect)