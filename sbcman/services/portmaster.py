# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
PortMaster interface module.

Finds settings and paths for the PortMaster install on the device.
"""

import logging
import pathlib

from sbcman.path import paths
from sbcman.path import device


logger = logging.getLogger(__name__)

class PortMaster:

    def __init__(self, device_paths : device.DevicePaths):
        self.device_paths = device_paths
    
    def find_ports_dir(self) -> pathlib.Path :
        """ Attempts to find the PortMaster base install directory, e.g. "ports".
        """
        mounts = self.device_paths.get_mounted_filesystems()

        # Some filesystems are not case senstive; not sure if it matters.
        rom_base_dirs = ["roms", "Roms", "ROMS", "EASYROMS", "easyroms"]
        port_dirs = ["PORTS", "ports", "Ports"]

        rom_base_exists = None

        candidates = []

        for m in mounts:
            for r in rom_base_dirs:
                rom_base = m / r
                try:
                    if rom_base.exists():
                        rom_base_exists = rom_base
                        for p in port_dirs:
                            port_base = rom_base / p

                            if port_base.exists():
                                candidates.append(port_base)
                except PermissionError:
                    pass

        logger.info(f"PortMaster candidate directories: {str(candidates)}")

        for c in candidates:
            if str(c).lower() == "/roms/ports":
                logger.info(f"Found {c}, but skipping.")
                continue

            if not list(c.glob("*")):
                logger.info(f"Found {c}, bug looks empty; skipping.")
                continue

            logger.info(f"Found PortMaster directory at {c}")
            return c

        logger.warning("Could NOT find PortMaster base directory")

        if rom_base_exists:
            return rom_base_exists

        return pathlib.Path("/")

    def find_game_image_dir(self, port_base):
        """ Attempts to find the Image directory for the game ports. """

        candidates = [
            port_base / "Imgs",  # Stock Anbernic with Ubuntu base
            port_base / "../../Imgs",         # Trimui Smart Pro with TinaLinux
        ]

        for c in candidates:
            if c.exists():
                logger.info(f"Found PortMaster image directory at {c}")
                return c

        logger.warning("Could NOT find PortMaster image directory.")

        return pathlib.Path("/")
