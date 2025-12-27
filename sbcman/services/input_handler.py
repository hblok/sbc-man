"""
Input Handler Service

Manages input mapping with hierarchical resolution and per-game overrides.

Based on: docs/code/class_services_input_handler.txt
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

import pygame

from ..hardware.paths import AppPaths


logger = logging.getLogger(__name__)


class InputHandler:
    """
    Input handler with layered mapping system.
    
    Provides action-based input abstraction with support for:
    - Default mappings
    - Device-specific mappings
    - User overrides
    - Per-game mappings
    """

    def __init__(self, hw_config: Dict[str, Any], app_paths: AppPaths):
        """
        Initialize input handler with hierarchical mappings.
        
        Args:
            hw_config: Hardware configuration dictionary
        """
        self.hw_config = hw_config
        self.app_paths = app_paths
        
        # Determine config directories
        #src_dir = Path(__file__).parent.parent
        #self.config_dir = src_dir / "config" / "input_mappings"
        self.config_dir = self.app_paths.input_mappings
        
        #paths = hw_config.get("paths", {})
        #data_dir = Path(paths.get("data", "~/.local/share/sbc-man")).expanduser()
        #self.data_dir = data_dir / "input_overrides"
        self.data_dir = self.app_paths.input_overrides
        
        self.current_game_id: Optional[str] = None
        self.mappings: Dict[str, List[str]] = {}
        self.joysticks: List[pygame.joystick.Joystick] = []
        
        # Load mapping hierarchy
        self._load_mapping_hierarchy()
        
        # Initialize joysticks
        self._initialize_joysticks()
        
        logger.info("InputHandler initialized")

    def _load_mapping_hierarchy(self) -> None:
        """
        Load input mappings with proper hierarchy.
        
        Hierarchy:
        1. config/input_mappings/default.json
        2. config/input_mappings/{device_type}.json
        3. data/input_overrides/device.json (user overrides)
        4. data/input_overrides/games/{game_id}.json (per-game, if set)
        """
        # Layer 1: Default mappings
        default_mappings = self._load_mapping_file(self.config_dir / "default.json")
        self.mappings = default_mappings.copy()
        
        # Layer 2: Device-specific mappings
        device_type = self.hw_config.get("detected_device", "desktop")
        device_mappings = self._load_mapping_file(self.config_dir / f"{device_type}.json")
        self.mappings.update(device_mappings)
        
        # Layer 3: User overrides
        user_mappings = self._load_mapping_file(self.data_dir / "device.json")
        self.mappings.update(user_mappings)
        
        # Layer 4: Per-game mappings (if game context is set)
        if self.current_game_id:
            game_mappings = self._load_mapping_file(
                self.data_dir / "games" / f"{self.current_game_id}.json"
            )
            self.mappings.update(game_mappings)
        
        logger.info(f"Loaded input mappings: {list(self.mappings.keys())}")

    def _load_mapping_file(self, path: Path) -> Dict[str, List[str]]:
        """
        Load a single mapping JSON file.
        
        Args:
            path: Path to mapping file
            
        Returns:
            dict: Mapping dictionary or empty dict if file doesn't exist
        """
        if not path.exists():
            logger.debug(f"Mapping file not found: {path}")
            return {}
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            logger.debug(f"Loaded mappings from {path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return {}

    def _initialize_joysticks(self) -> None:
        """Initialize all detected joysticks."""
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        
        for i in range(joystick_count):
            try:
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self.joysticks.append(joystick)
                logger.info(f"Initialized joystick {i}: {joystick.get_name()}")
            except Exception as e:
                logger.warning(f"Failed to initialize joystick {i}: {e}")

    def set_game_context(self, game_id: Optional[str]) -> None:
        """
        Set current game for per-game mappings.
        
        Args:
            game_id: Game identifier, or None to clear context
        """
        self.current_game_id = game_id
        self._load_mapping_hierarchy()
        logger.info(f"Set game context: {game_id}")

    def clear_game_context(self) -> None:
        """Clear game context (return to launcher)."""
        self.set_game_context(None)

    def is_action_pressed(self, action: str, events: List[pygame.event.Event]) -> bool:
        """
        Check if action was triggered in event list.
        
        Args:
            action: Action name (e.g., 'confirm', 'cancel', 'menu')
            events: List of pygame events
            
        Returns:
            bool: True if action was triggered
        """
        if action not in self.mappings:
            return False
        
        action_keys = self.mappings[action]
        
        for event in events:
            # Check keyboard events
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key).upper()
                if key_name in action_keys:
                    return True
                # Also check for special keys
                if event.key == pygame.K_RETURN and "RETURN" in action_keys:
                    return True
                if event.key == pygame.K_ESCAPE and "ESCAPE" in action_keys:
                    return True
            
            # Check joystick button events
            elif event.type == pygame.JOYBUTTONDOWN:
                button_names = self._get_button_names(event.button)
                for button_name in button_names:
                    if button_name in action_keys:
                        return True
            
            # Check joystick hat (d-pad) events
            elif event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y == 1 and "DPAD_UP" in action_keys:
                    return True
                if hat_y == -1 and "DPAD_DOWN" in action_keys:
                    return True
                if hat_x == -1 and "DPAD_LEFT" in action_keys:
                    return True
                if hat_x == 1 and "DPAD_RIGHT" in action_keys:
                    return True
        
        return False

    def _get_button_names(self, button_index: int) -> List[str]:
        """
        Map button index to common semantic names.
        
        Args:
            button_index: Physical button index
            
        Returns:
            list: List of possible button names
        """
        button_map = {
            0: ["BUTTON_A", "BUTTON_SOUTH"],
            1: ["BUTTON_B", "BUTTON_EAST"],
            2: ["BUTTON_X", "BUTTON_WEST"],
            3: ["BUTTON_Y", "BUTTON_NORTH"],
            4: ["BUTTON_L1", "BUTTON_LB"],
            5: ["BUTTON_R1", "BUTTON_RB"],
            6: ["BUTTON_SELECT", "BUTTON_BACK"],
            7: ["BUTTON_START"],
            8: ["BUTTON_L3"],
            9: ["BUTTON_R3"],
            10: ["BUTTON_L2", "BUTTON_LT"],
            11: ["BUTTON_R2", "BUTTON_RT"],
            12: ["BUTTON_MENU"],
            13: ["BUTTON_MENU"],  # Alternative menu button
        }
        
        names = button_map.get(button_index, [])
        # Always include numeric name as fallback
        names.append(f"BUTTON_{button_index}")
        return names

    def save_mapping(self, action: str, keys: List[str], scope: str = "device") -> None:
        """
        Save custom input mapping.
        
        Args:
            action: Action name
            keys: List of key identifiers
            scope: 'device' or 'game'
        """
        # Update current mappings
        self.mappings[action] = keys
        
        # Determine save path
        if scope == "game" and self.current_game_id:
            save_path = self.data_dir / "games" / f"{self.current_game_id}.json"
        else:
            save_path = self.data_dir / "device.json"
        
        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing mappings
        existing = self._load_mapping_file(save_path)
        
        # Merge new mapping
        existing[action] = keys
        
        # Save to file
        try:
            with open(save_path, "w") as f:
                json.dump(existing, f, indent=2)
            logger.info(f"Saved mapping for {action} to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save mapping: {e}")

    def get_current_mappings(self) -> Dict[str, List[str]]:
        """
        Get current active mappings for display.
        
        Returns:
            dict: Copy of current mappings
        """
        return self.mappings.copy()
