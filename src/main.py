#!python3

"""
SBC-Man Game Launcher - Main Entry Point

This is the zero-logic entry point for the application.
It only imports the necessary modules and starts the application.

Usage:
    python main.py
"""

#from src.hardware.compat_sdl import setup_sdl_environment
from src.core.application import Application
from src.hardware.paths import AppPaths


if __name__ == "__main__":
#    setup_sdl_environment()
    Application(AppPaths()).run()
