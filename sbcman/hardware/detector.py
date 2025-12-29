# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Hardware Detector Module

Detects device type and OS distribution for configuration selection.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

from .config_loader import ConfigLoader
from .paths import AppPaths
from .prober import HardwareProber

logger = logging.getLogger(__name__)


class HardwareDetector:
    """
    Provides methods to identify the hardware platform and operating system
    to enable device-specific configuration loading.
    """

    def get_config(self) -> Dict[str, Any]:
        """
        Main entry point for hardware detection and config loading.
        
        Returns:
            dict: Complete merged hardware configuration including:
                - detected_device: Device type identifier
                - detected_os: OS type identifier
                - probed_hardware: Hardware capabilities
                - All merged configuration values
        
        Raises:
            RuntimeError: If critical configuration loading fails
        """
        from .prober import HardwareProber
        from .config_loader import ConfigLoader
        
        logger.info("Starting hardware detection")
        
        # Detect device and OS
        device_type = HardwareDetector().detect_device()
        os_type = HardwareDetector().detect_os()
        
        logger.info(f"Detected device: {device_type}, OS: {os_type}")
        
        # Probe hardware capabilities
        probed_hardware = HardwareProber.probe_all()
        
        # Load and merge configuration
        config_loader = ConfigLoader(device_type, os_type, probed_hardware, AppPaths())
        config = config_loader.load_config()
        
        # Add detection metadata
        config["detected_device"] = device_type
        config["detected_os"] = os_type
        
        # Expand path variables
        HardwareDetector().expand_paths(config)
        
        return config

    def detect_device(self) -> str:
        """
        Detect device type from hardware identifiers.
        
        Checks various system files and mount points to identify the device.
        
        Returns:
            str: Device type identifier (e.g., 'anbernic', 'miyoo', 'retroid', 'desktop')
        """
        # Check environment variable override (useful for testing)
        if "DEVICE_TYPE" in os.environ:
            device = os.environ["DEVICE_TYPE"]
            logger.info(f"Device type from environment: {device}")
            return device
        
        # Check ARM device tree model (common on handhelds)
        model_file = Path("/sys/firmware/devicetree/base/model")
        if model_file.exists():
            try:
                model = model_file.read_text().lower()
                if "anbernic" in model or "rg" in model:
                    return "anbernic"
                if "miyoo" in model:
                    return "miyoo"
                if "retroid" in model:
                    return "retroid"
            except Exception as e:
                logger.warning(f"Failed to read device tree model: {e}")
        
        # Check for Miyoo-specific mount point
        if Path("/mnt/SDCARD/.system").exists():
            return "miyoo"
        
        # Check for Android build.prop
        if Path("/system/build.prop").exists():
            try:
                build_prop = Path("/system/build.prop").read_text()
                if "retroid" in build_prop.lower():
                    return "retroid"
            except Exception as e:
                logger.warning(f"Failed to read build.prop: {e}")
        
        # Default fallback
        logger.info("No specific device detected, using desktop")
        return "desktop"

    def detect_os(self) -> str:
        """
        Detect OS distribution type.
        
        Reads /etc/os-release to identify the Linux distribution.
        
        Returns:
            str: OS type identifier (e.g., 'arkos', 'jelos', 'batocera', 'android', 'standard_linux')
        """
        # Check environment variable override
        if "OS_TYPE" in os.environ:
            os_type = os.environ["OS_TYPE"]
            logger.info(f"OS type from environment: {os_type}")
            return os_type
        
        # Check for Android
        if Path("/system/build.prop").exists():
            return "android"
        
        # Read /etc/os-release
        os_release_file = Path("/etc/os-release")
        if os_release_file.exists():
            try:
                os_release = os_release_file.read_text().lower()
                if "arkos" in os_release:
                    return "arkos"
                if "jelos" in os_release:
                    return "jelos"
                if "batocera" in os_release:
                    return "batocera"
            except Exception as e:
                logger.warning(f"Failed to read os-release: {e}")
        
        # Default fallback
        logger.info("No specific OS detected, using standard_linux")
        return "standard_linux"

    def expand_paths(self, config: Dict[str, Any]) -> None:
        """
        Expand environment variables and user home in path strings.
        
        Recursively processes the configuration dictionary and expands
        any path strings containing environment variables or ~.
        
        Args:
            config: Configuration dictionary to modify in place
        """
        if "paths" not in config:
            return
        
        def expand_value(value: Any) -> Any:
            """Recursively expand paths in nested structures."""
            if isinstance(value, str):
                # Expand environment variables and user home
                expanded = os.path.expandvars(value)
                expanded = str(Path(expanded).expanduser())
                return expanded
            elif isinstance(value, dict):
                return {k: expand_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [expand_value(item) for item in value]
            else:
                return value
        
        config["paths"] = expand_value(config["paths"])
