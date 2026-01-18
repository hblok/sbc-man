# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Install Settings State Module

State for configuring installation settings with adaptive layout support.
"""

import logging
import pathlib
from pathlib import Path
from typing import Optional, List

import pygame

from .base_state import BaseState
from ..path import device
from ..services import portmaster
from ..views.widgets import ScrollableList

logger = logging.getLogger(__name__)


class InstallSettingsState(BaseState):
    """
    Install settings configuration state with adaptive layout.
    
    Allows users to configure installation-related settings including
    pip package installation, Portmaster integration, and directory paths.
    Automatically adapts to screen size.
    """

    def on_enter(self, previous_state: Optional[BaseState]) -> None:
        """Initialize install settings state."""
        logger.info("Entered install settings state")
        
        # Load current settings
        self._load_settings()
        
        # Initialize adaptive scrollable list
        self._setup_adaptive_scrollable_list()
        self._update_settings_options()

    def on_exit(self) -> None:
        """Cleanup install settings state."""
        logger.info("Exited install settings state - saving settings")
        self.config.save()

    def update(self, dt: float) -> None:
        """Update install settings logic."""
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle install settings input."""
        # Check for back/exit
        if self.input_handler.is_action_pressed("cancel", events) or self._handle_exit_input(events):
            self.state_manager.change_state("settings")
            return

        # Handle scrolling through settings options
        if hasattr(self, 'settings_list'):
            if self.input_handler.is_action_pressed("up", events):
                self.settings_list.scroll_up()
            elif self.input_handler.is_action_pressed("down", events):
                self.settings_list.scroll_down()

            # Toggle or edit option
            if self.input_handler.is_action_pressed("confirm", events):
                self._select_option()

    def _load_settings(self) -> None:
        """Load install settings from configuration."""
        self.install_as_pip = self.config.get("install.install_as_pip", False)
        self.add_portmaster_entry = self.config.get("install.add_portmaster_entry", False)
        self.portmaster_base_dir = self.config.get("install.portmaster_base_dir",
                                                   str(self._get_portmaster_base_dir()))
        self.portmaster_image_dir = self.config.get("install.portmaster_image_dir",
                                                    str(self._get_portmaster_image_dir()))

    def _get_portmaster_base_dir(self) -> pathlib.Path:
        dp = device.DevicePaths()
        pm = portmaster.PortMaster(dp)
        return pm.find_ports_dir()

    def _get_portmaster_image_dir(self) -> pathlib.Path:
        dp = device.DevicePaths()
        pm = portmaster.PortMaster(dp)
        return pm.find_game_image_dir(self._get_portmaster_base_dir())        

    def _save_settings(self) -> None:
        """Save install settings to configuration."""
        self.config.set("install.install_as_pip", self.install_as_pip)
        self.config.set("install.add_portmaster_entry", self.add_portmaster_entry)
        self.config.set("install.portmaster_base_dir", self.portmaster_base_dir)
        self.config.set("install.portmaster_image_dir", self.portmaster_image_dir)
        logger.info("Install settings saved")

    def _setup_adaptive_scrollable_list(self) -> None:
        """
        Setup the adaptive scrollable list that responds to screen size.
        
        This method creates a list that will automatically detect if scrolling is needed
        based on the available screen space and content length.
        """
        # Get screen dimensions from the surface (will be called in render)
        # For now, use defaults that work for both 640x480 and larger screens
        screen_width = 640  # Default, will be updated in render
        screen_height = 480  # Default, will be updated in render
        
        # Calculate adaptive dimensions
        title_height = 90  # Space for title
        bottom_padding = 70  # Space for instructions
        available_height = screen_height - title_height - bottom_padding
        
        # Calculate adaptive width (responsive to screen size)
        max_width = min(560, screen_width - 40)  # Max 560px or screen width minus margins
        list_width = max(400, max_width)  # Min 400px for usability
        
        # Position the list
        list_x = (screen_width - list_width) // 2
        list_y = title_height
        
        # Create adaptive scrollable list
        self.settings_list = ScrollableList(
            x=list_x,
            y=list_y,
            width=list_width,
            height=available_height,  # Maximum available space
            item_height=50,
            font_size=30,
            padding=10
        )
        
        # Store dimensions for potential updates
        self._last_screen_width = screen_width
        self._last_screen_height = screen_height

    def _update_scrollable_list_dimensions(self, surface_width: int, surface_height: int) -> None:
        """
        Update scrollable list dimensions if screen size changed.
        
        Args:
            surface_width: Current surface width
            surface_height: Current surface height
        """
        # Only update if dimensions actually changed
        if (surface_width != self._last_screen_width or 
            surface_height != self._last_screen_height):
            
            # Recalculate adaptive dimensions
            title_height = 90
            bottom_padding = 70
            available_height = surface_height - title_height - bottom_padding
            
            max_width = min(560, surface_width - 40)
            list_width = max(400, max_width)
            list_x = (surface_width - list_width) // 2
            list_y = title_height
            
            # Update scrollable list properties
            self.settings_list.x = list_x
            self.settings_list.y = list_y
            self.settings_list.width = list_width
            self.settings_list.height = available_height
            
            # Recalculate layout requirements
            self.settings_list._calculate_layout_requirements()
            
            # Store new dimensions
            self._last_screen_width = surface_width
            self._last_screen_height = surface_height
            
            logger.debug(f"Updated adaptive layout for {surface_width}x{surface_height}")

    def _update_settings_options(self) -> None:
        """Update the adaptive scrollable list with settings options."""
        if not hasattr(self, 'settings_list'):
            return

        # Build display strings with current values
        settings_options = [
            f"Install as pip package: {'ON' if self.install_as_pip else 'OFF'}",
            f"Add Portmaster entry: {'ON' if self.add_portmaster_entry else 'OFF'}",
            f"Portmaster base dir: {self._truncate_path(str(self.portmaster_base_dir))}",
            f"Portmaster image dir: {self._truncate_path(str(self.portmaster_image_dir))}",
            "Back to Settings"
        ]
        
        # All settings options are selectable
        settings_states = [True] * len(settings_options)

        self.settings_list.set_items(settings_options, settings_states)

    def _truncate_path(self, path: str, max_length: int = 40) -> str:
        """Truncate path string for display if too long."""
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length - 3):]

    def _select_option(self) -> None:
        """Handle settings option selection."""
        if not hasattr(self, 'settings_list'):
            return

        selected_index = self.settings_list.get_selected_index()
        
        if selected_index == 0:  # Install as pip package
            self.install_as_pip = not self.install_as_pip
            logger.info(f"Install as pip: {self.install_as_pip}")
            
        elif selected_index == 1:  # Add Portmaster entry
            self.add_portmaster_entry = not self.add_portmaster_entry
            logger.info(f"Add Portmaster entry: {self.add_portmaster_entry}")
            
        elif selected_index == 2:  # Portmaster base dir
            self.portmaster_base_dir = self._browse_directory(self.portmaster_base_dir)
            
        elif selected_index == 3:  # Portmaster image dir
            self.portmaster_image_dir = self._browse_directory(self.portmaster_image_dir)
            
        elif selected_index == 4:  # Back to Settings
            self._save_settings()
            self.state_manager.change_state("settings")
            return

        # Update display after modification
        self._update_settings_options()

    def _browse_directory(self, current_path : pathlib.Path) -> None:
        """
        Open directory browser dialog.
        """
        try:
            # Hide pygame window temporarily
            #pygame.display.iconify()
            
            if not current_path or not current_path.exists():
                initial_dir = Path.home()
            
            # Open directory browser
            dir_path = filedialog.askdirectory(
                title=f"Select Portmaster {dir_type} directory",
                initialdir=initial_dir
            )
            
            # Restore pygame window
            #pygame.display.set_mode((self.screen.get_width(), self.screen.get_height()))
            
            if dir_path:
                # Validate directory
                path = pathlib.Path(dir_path)
                if not path.exists():
                    logger.error(f"Selected directory does not exist: {dir_path}")
                    return
                
                if not path.is_dir():
                    logger.error(f"Selected path is not a directory: {dir_path}")
                    return

                return dir_path
            
        except Exception as e:
            logger.error(f"Error browsing directory: {e}")
            # Ensure pygame window is restored
            #try:
            #    #pygame.display.set_mode((self.screen.get_width(), self.screen.get_height()))
            #except:
            #    pass

        return pathlib.Path("/")

    def render(self, surface: pygame.Surface) -> None:
        """Render install settings with adaptive layout support."""
        surface.fill((20, 20, 30))
        
        # Get actual surface dimensions
        surface_width = surface.get_width()
        surface_height = surface.get_height()

        # Update scrollable list dimensions if screen size changed
        if hasattr(self, 'settings_list'):
            self._update_scrollable_list_dimensions(surface_width, surface_height)
        else:
            # Initialize if not done yet
            self._setup_adaptive_scrollable_list()
            self._update_settings_options()

        # Render title with adaptive font size
        title_font_size = min(56, max(40, surface_width // 11))
        font_large = pygame.font.Font(None, title_font_size)
        title = font_large.render("Install Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface_width // 2, 45))
        surface.blit(title, title_rect)

        # Render the adaptive settings list
        self.settings_list.render(surface)

        # Render adaptive instructions at the bottom
        instruction_font_size = min(24, max(18, surface_width // 25))
        font_small = pygame.font.Font(None, instruction_font_size)
        
        # Base instructions
        instructions = "↑↓ Navigate  |  A/Confirm Select  |  B/Cancel Back"
        
        # Add scrolling hint only if needed and scrolling is actually active
        if (hasattr(self, 'settings_list') and 
            self.settings_list.needs_scrolling and 
            self.settings_list.show_scroll_indicators):
            instructions += "  |  PageUp/Down Fast Scroll"
        
        inst_surface = font_small.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(surface_width // 2, surface_height - 20))
        surface.blit(inst_surface, inst_rect)
