"""
Hardware Prober Module

Probes hardware capabilities including display, input devices, storage, and CPU.
All methods are static - no class instantiation required.

Based on: docs/code/class_hardware_prober.txt
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class HardwareProber:
    """
    Static class for probing hardware capabilities.
    
    Provides methods to detect display resolution, input devices,
    storage locations, and CPU information.
    """

    @staticmethod
    def probe_all() -> Dict[str, Any]:
        """
        Probe all hardware capabilities.
        
        Returns:
            dict: Complete hardware probe results with keys:
                - display: Display information
                - input: Input device information
                - storage: Storage location information
                - cpu: CPU information
        """
        logger.info("Probing hardware capabilities")
        
        # Initialize pygame for probing (required for display/input detection)
        import pygame
        pygame.init()
        pygame.joystick.init()
        
        results = {
            "display": HardwareProber.probe_display(),
            "input": HardwareProber.probe_input(),
            "storage": HardwareProber.probe_storage(),
            "cpu": HardwareProber.probe_cpu(),
        }
        
        logger.info(f"Hardware probe complete: {results}")
        return results

    @staticmethod
    def probe_display() -> Dict[str, Any]:
        """
        Auto-detect display capabilities.
        
        Returns:
            dict: Display information including:
                - current_resolution: [width, height]
                - available_modes: List of available resolutions
                - hardware_accelerated: Boolean indicating HW acceleration
                - bit_depth: Color depth in bits
                - video_mem: Video memory in MB (if available)
        """
        import pygame
        
        try:
            info = pygame.display.Info()
            
            display_info = {
                "current_resolution": [info.current_w, info.current_h],
                "hardware_accelerated": bool(info.hw),
                "bit_depth": info.bitsize,
            }
            
            # Get available display modes
            try:
                modes = pygame.display.list_modes()
                if modes == -1:
                    # All modes available
                    display_info["available_modes"] = []
                else:
                    display_info["available_modes"] = [list(mode) for mode in modes]
            except Exception as e:
                logger.warning(f"Failed to get display modes: {e}")
                display_info["available_modes"] = []
            
            # Video memory (if available)
            if hasattr(info, "video_mem") and info.video_mem > 0:
                display_info["video_mem"] = info.video_mem
            
            logger.info(f"Display probe: {display_info}")
            return display_info
            
        except Exception as e:
            logger.error(f"Display probe failed: {e}")
            # Return safe defaults
            return {
                "current_resolution": [1280, 720],
                "available_modes": [],
                "hardware_accelerated": False,
                "bit_depth": 32,
            }

    @staticmethod
    def probe_input() -> Dict[str, Any]:
        """
        Auto-detect input devices.
        
        Returns:
            dict: Input device information including:
                - has_keyboard: Always True
                - joystick_count: Number of detected joysticks
                - joysticks: List of joystick info dictionaries
        """
        import pygame
        
        joystick_count = pygame.joystick.get_count()
        joysticks: List[Dict[str, Any]] = []
        
        for i in range(joystick_count):
            try:
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                
                joystick_info = {
                    "id": i,
                    "name": joystick.get_name(),
                    "num_axes": joystick.get_numaxes(),
                    "num_buttons": joystick.get_numbuttons(),
                    "num_hats": joystick.get_numhats(),
                }
                
                joysticks.append(joystick_info)
                logger.info(f"Detected joystick {i}: {joystick_info}")
                
            except Exception as e:
                logger.warning(f"Failed to initialize joystick {i}: {e}")
        
        input_info = {
            "has_keyboard": True,
            "joystick_count": joystick_count,
            "joysticks": joysticks,
        }
        
        return input_info

    @staticmethod
    def probe_storage() -> Dict[str, Dict[str, Any]]:
        """
        Probe storage locations and free space.
        
        Checks common mount paths for handheld devices and reports
        available storage space.
        
        Returns:
            dict: Mapping of paths to storage information including:
                - total: Total bytes
                - used: Used bytes
                - free: Free bytes
                - writable: Boolean indicating write permission
        """
        # Common mount paths on handheld devices
        common_paths = [
            "/roms",
            "/storage/roms",
            "/mnt/sdcard",
            "/mnt/SDCARD",
            "/storage",
            "/home",
            str(Path.home()),
        ]
        
        storage_info: Dict[str, Dict[str, Any]] = {}
        
        for path_str in common_paths:
            path = Path(path_str)
            if not path.exists():
                continue
            
            try:
                # Get disk usage
                usage = shutil.disk_usage(path)
                
                # Check if writable
                writable = os.access(path, os.W_OK)
                
                storage_info[path_str] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "writable": writable,
                }
                
                logger.info(f"Storage at {path_str}: {usage.free // (1024**3)} GB free")
                
            except Exception as e:
                logger.warning(f"Failed to probe storage at {path_str}: {e}")
        
        return storage_info

    @staticmethod
    def probe_cpu() -> Dict[str, Any]:
        """
        Probe CPU information for performance profiling.
        
        Returns:
            dict: CPU information including:
                - core_count: Number of CPU cores
                - architecture: CPU architecture (arm, x86, unknown)
        """
        cpu_info = {
            "core_count": 1,
            "architecture": "unknown",
        }
        
        # Read /proc/cpuinfo if available
        cpuinfo_file = Path("/proc/cpuinfo")
        if cpuinfo_file.exists():
            try:
                cpuinfo = cpuinfo_file.read_text().lower()
                
                # Count processor entries
                core_count = cpuinfo.count("processor")
                if core_count > 0:
                    cpu_info["core_count"] = core_count
                
                # Detect architecture
                if "arm" in cpuinfo or "aarch" in cpuinfo:
                    cpu_info["architecture"] = "arm"
                elif "intel" in cpuinfo or "amd" in cpuinfo or "x86" in cpuinfo:
                    cpu_info["architecture"] = "x86"
                
                logger.info(f"CPU probe: {cpu_info}")
                
            except Exception as e:
                logger.warning(f"Failed to read cpuinfo: {e}")
        
        return cpu_info