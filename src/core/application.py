"""
Application Module

Main application orchestrator that manages the startup lifecycle,
component initialization, and application shutdown.

Based on: docs/code/package_core.txt and docs/other/sequence_startup.txt
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import pygame

from ..hardware.detector import HardwareDetector
from ..models.config_manager import ConfigManager
from ..models.game_library import GameLibrary
from ..services.input_handler import InputHandler
from .state_manager import StateManager
from .game_loop import GameLoop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Application:
    """
    Main application class that orchestrates the game launcher.
    
    Handles hardware detection, configuration loading, pygame initialization,
    component creation, and the main game loop.
    """

    def __init__(self) -> None:
        """Initialize the application (does not start it)."""
        self.hw_config: Optional[dict] = None
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.config_manager: Optional[ConfigManager] = None
        self.game_library: Optional[GameLibrary] = None
        self.input_handler: Optional[InputHandler] = None
        self.state_manager: Optional[StateManager] = None
        self.running = False
        
        logger.info("Application instance created")

    def run(self) -> None:
        """
        Main entry point to run the application.
        
        Executes the complete startup sequence:
        1. Hardware detection and configuration loading
        2. Pygame initialization
        3. Component initialization
        4. Main game loop
        5. Cleanup and shutdown
        """
        try:
            logger.info("Starting SBC-Man Game Launcher")
            
            # Phase 1: Hardware detection and configuration
            self._detect_hardware()
            
            # Phase 2: Initialize pygame
            self._initialize_pygame()
            
            # Phase 3: Initialize components
            self._initialize_components()
            
            # Phase 4: Run main game loop
            self._run_game_loop()
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)
        finally:
            self._shutdown()

    def _detect_hardware(self) -> None:
        """
        Detect hardware and load configuration.
        
        Uses HardwareDetector to identify device type, OS, and capabilities,
        then loads the appropriate configuration.
        """
        logger.info("Detecting hardware and loading configuration")
        self.hw_config = HardwareDetector().get_config()
        logger.info(f"Configuration loaded for {self.hw_config['detected_device']}")

    def _initialize_pygame(self) -> None:
        """
        Initialize pygame with detected hardware configuration.
        
        Sets up display, clock, and other pygame subsystems based on
        the hardware configuration.
        """
        logger.info("Initializing pygame")
        
        pygame.init()
        
        # Get display configuration
        display_config = self.hw_config.get("display", {})
        resolution = display_config.get("resolution", [1280, 720])
        fullscreen = display_config.get("fullscreen", False)
        fps_target = display_config.get("fps_target", 60)
        
        # Create display
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode(resolution, flags)
        pygame.display.set_caption("Max Bloks Games")
        
        # Hide cursor on handheld devices
        if display_config.get("hide_cursor", False):
            pygame.mouse.set_visible(False)
        
        # Create clock for FPS limiting
        self.clock = pygame.time.Clock()
        
        logger.info(f"Display initialized: {resolution} @ {fps_target} FPS")

    def _initialize_components(self):
        logger.info("Initializing application components")
        
        self._ensure_data_directories()
        
        self.config_manager = ConfigManager(self.hw_config)
        self.game_library = GameLibrary(self.hw_config)
        self.input_handler = InputHandler(self.hw_config)
        
        self.state_manager = StateManager(
            screen=self.screen,
            hw_config=self.hw_config,
            config=self.config_manager,
            game_library=self.game_library,
            input_handler=self.input_handler,
        )
        
        logger.info("All components initialized")

    def _ensure_data_directories(self):
        """
        Ensure all required data directories exist.
        
        Creates data directory structure if it doesn't exist.
        """
        #FIXME
        paths = self.hw_config.get("paths", {})
        data_dir = Path(paths.get("data", "~/.local/share/sbc-man")).expanduser()
        
        # Create directory structure
        directories = [
            data_dir,
            data_dir / "input_overrides",
            data_dir / "input_overrides" / "games",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def _run_game_loop(self):
        """
        Run the main game loop.
        
        Delegates to GameLoop class for the actual loop execution.
        """
        logger.info("Starting main game loop")
        self.running = True
        
        fps_target = self.hw_config.get("display", {}).get("fps_target", 60)
        
        game_loop = GameLoop()
        game_loop.run(self.state_manager, self.clock, fps_target)

    def _shutdown(self) -> None:
        """
        Clean shutdown of the application.
        
        Saves state, closes resources, and quits pygame.
        """
        logger.info("Shutting down application")
        
        # Save any pending data
        if self.game_library:
            try:
                self.game_library.save_games()
            except Exception as e:
                logger.error(f"Failed to save game library: {e}")
        
        if self.config_manager:
            try:
                self.config_manager.save()
            except Exception as e:
                logger.error(f"Failed to save configuration: {e}")
        
        # Quit pygame
        pygame.quit()
        
        logger.info("Application shutdown complete")
