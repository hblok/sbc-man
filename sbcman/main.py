#!python3
# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later


"""
SBC-Man Game Launcher - Main Entry Point

This is the zero-logic entry point for the application.
It only imports the necessary modules and starts the application.

Usage:
    python main.py
"""

import pathlib

#from sbcman.hardware.compat_sdl import setup_sdl_environment
from sbcman.core.application import Application
from sbcman.path.paths import AppPaths


if __name__ == "__main__":
#    setup_sdl_environment()
    sbc_dir = pathlib.Path(__file__).resolve().parent
    print(sbc_dir)
    Application(AppPaths(sbc_dir)).run()
