"""
Configuration Manager Module

Manages runtime configuration with get/set operations and persistence.

Based on: docs/code/class_models_config_manager.txt
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Runtime configuration manager.
    
    Wraps hardware configuration with runtime overrides and provides
    convenient get/set operations with dot notation support.
    """

    def __init__(self, hw_config: Dict[str, Any]):
        """
        Initialize configuration manager.
        
        Args:
            hw_config: Hardware configuration from HardwareDetector
        """
        self.hw_config = hw_config
        self.runtime_config: Dict[str, Any] = {}
        
        # Determine config file path
        paths = hw_config.get("paths", {})
        data_dir = Path(paths.get("data", "~/.local/share/sbc-man")).expanduser()
        self.config_file = data_dir / "config.json"
        
        # Load runtime config
        self._load_runtime_config()
        
        logger.info("ConfigManager initialized")

    def _load_runtime_config(self) -> None:
        """
        Load runtime configuration from file.
        
        Creates an empty config file if it doesn't exist.
        """
        if not self.config_file.exists():
            logger.info("Runtime config file not found, creating empty config")
            self.runtime_config = {}
            self.save()
            return
        
        try:
            with open(self.config_file, "r") as f:
                self.runtime_config = json.load(f)
            logger.info(f"Loaded runtime config from {self.config_file}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            self.runtime_config = {}
        except Exception as e:
            logger.error(f"Failed to load runtime config: {e}")
            self.runtime_config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with dot notation support.
        
        Checks runtime config first, then falls back to hardware config.
        Supports nested keys with dot notation (e.g., "display.resolution").
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Try runtime config first
        value = self._get_nested(self.runtime_config, key)
        if value is not None:
            return value
        
        # Fall back to hardware config
        value = self._get_nested(self.hw_config, key)
        if value is not None:
            return value
        
        return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value with dot notation support.
        
        Sets value in runtime config, which takes precedence over
        hardware config.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        self._set_nested(self.runtime_config, key, value)
        logger.debug(f"Set config: {key} = {value}")

    def save(self) -> None:
        """
        Save runtime configuration to file.
        
        Persists the current runtime configuration to disk.
        """
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(self.config_file, "w") as f:
                json.dump(self.runtime_config, f, indent=2)
            
            logger.info(f"Saved runtime config to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save runtime config: {e}")

    def _get_nested(self, config: Dict[str, Any], key: str) -> Any:
        """
        Get nested value using dot notation.
        
        Args:
            config: Configuration dictionary
            key: Key with dot notation (e.g., "display.resolution")
            
        Returns:
            Value if found, None otherwise
        """
        keys = key.split(".")
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value

    def _set_nested(self, config: Dict[str, Any], key: str, value: Any) -> None:
        """
        Set nested value using dot notation.
        
        Creates intermediate dictionaries as needed.
        
        Args:
            config: Configuration dictionary to modify
            key: Key with dot notation (e.g., "display.resolution")
            value: Value to set
        """
        keys = key.split(".")
        current = config
        
        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """
        Get complete merged configuration.
        
        Returns:
            dict: Merged hardware and runtime configuration
        """
        # Deep merge hw_config and runtime_config
        merged = self._deep_merge(self.hw_config.copy(), self.runtime_config)
        return merged

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            dict: Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result