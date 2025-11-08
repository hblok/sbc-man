"""
Configuration Loader Module

Loads and merges configuration from multiple sources following a hierarchy:
1. Default configuration
2. Device-specific configuration
3. OS-specific configuration
4. User overrides

Based on: docs/code/class_hardware_config_loader.txt
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..hardware.paths import AppPaths


logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Configuration loader with hierarchical merging.
    
    Loads configuration files from multiple sources and merges them
    according to a defined hierarchy, with later sources overriding earlier ones.
    """

    def __init__(self, device_type: str, os_type: str, probed_hardware: Dict[str, Any], app_paths: AppPaths):
        """
        Initialize configuration loader.
        
        Args:
            device_type: Detected device type identifier
            os_type: Detected OS type identifier
            probed_hardware: Hardware capabilities from HardwareProber
        """
        self.device_type = device_type
        self.os_type = os_type
        self.probed_hardware = probed_hardware
        self.app_paths = app_paths
        
        # Determine config directory (relative to src/)
        self.config_dir = Path(__file__).parent.parent / "config"
        
        logger.info(f"ConfigLoader initialized: device={device_type}, os={os_type}")

    def load_config(self) -> Dict[str, Any]:
        """
        Load and merge configuration from all sources.
        
        Merging hierarchy:
        1. config/devices/default.json (base)
        2. config/devices/{device_type}.json (device-specific)
        3. config/os_types/{os_type}.json (OS-specific)
        4. Probed hardware overrides (resolution, FPS)
        5. data/user_config.json (user overrides)
        
        Returns:
            dict: Complete merged configuration
            
        Raises:
            RuntimeError: If default configuration cannot be loaded
        """
        # Layer 1: Load default configuration
        default_config = self._load_json(self.config_dir / "devices" / "default.json")
        if not default_config:
            raise RuntimeError("Failed to load default configuration")
        
        config = default_config.copy()
        
        # Layer 2: Merge device-specific configuration
        device_config = self._load_json(self.config_dir / "devices" / f"{self.device_type}.json")
        if device_config:
            config = self._deep_merge(config, device_config)
            logger.info(f"Merged device config: {self.device_type}")
        
        # Layer 3: Merge OS-specific configuration
        os_config = self._load_json(self.config_dir / "os_types" / f"{self.os_type}.json")
        if os_config:
            config = self._deep_merge(config, os_config)
            logger.info(f"Merged OS config: {self.os_type}")
        
        # Layer 4: Apply probed hardware overrides
        self._apply_probed_hardware(config)
        
        # Layer 5: Merge user overrides
        user_config_path = self._get_user_config_path(config)
        if user_config_path and user_config_path.exists():
            user_config = self._load_json(user_config_path)
            if user_config:
                config = self._deep_merge(config, user_config)
                logger.info("Merged user config")
        
        return config

    def _load_json(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a single JSON configuration file.
        
        Args:
            path: Path to JSON file
            
        Returns:
            dict: Parsed JSON data, or None if file doesn't exist or is invalid
        """
        if not path.exists():
            logger.debug(f"Config file not found: {path}")
            return None
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            logger.debug(f"Loaded config: {path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return None

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Recursively merges nested dictionaries. Lists are replaced, not merged.
        Later values override earlier values.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            dict: Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value (including lists)
                result[key] = value
        
        return result

    def _apply_probed_hardware(self, config: Dict[str, Any]) -> None:
        """
        Apply probed hardware values to configuration.
        
        Overrides configuration with actual hardware capabilities when
        config specifies "auto" or when probed values are more appropriate.
        
        Args:
            config: Configuration dictionary to modify in place
        """
        if "display" not in config:
            config["display"] = {}
        
        display_config = config["display"]
        probed_display = self.probed_hardware.get("display", {})
        
        # Override resolution if set to "auto"
        if display_config.get("resolution") == "auto":
            resolution = probed_display.get("current_resolution", [1280, 720])
            display_config["resolution"] = resolution
            logger.info(f"Using probed resolution: {resolution}")
        
        # Store probed hardware for reference
        config["probed_hardware"] = self.probed_hardware

    def _get_user_config_path(self, config: Dict[str, Any]) -> Optional[Path]:
        """
        Get path to user configuration file.
        
        Args:
            config: Current configuration (to get data directory)
            
        Returns:
            Path: Path to user_config.json, or None if paths not configured
        """
        if "paths" not in config or "data" not in config["paths"]:
            return None
        
        data_dir = Path(config["paths"]["data"]).expanduser()
        return data_dir / "user_config.json"
