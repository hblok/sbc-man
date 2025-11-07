"""
Process Launcher Service

Launches games as subprocesses with pre/post command support.

Based on: docs/code/class_services_process_launcher.txt
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..models.game import Game

logger = logging.getLogger(__name__)


class ProcessLauncher:
    """
    Game process launcher.
    
    Handles launching games as subprocesses with support for
    pre-launch and post-launch commands, environment variables,
    and working directory management.
    """

    def __init__(self, hw_config: Dict[str, Any]):
        """
        Initialize
        
        Args:
            hw_config: Hardware configuration dictionary
        """
        self.hw_config = hw_config

    def launch_game(self, game: Game) -> bool:
        """
        Launch game process.
        
        Args:
            game: Game to launch
            
        Returns:
            bool: True if launch succeeded
        """
        if not game.installed:
            logger.error(f"Cannot launch uninstalled game: {game.name}")
            return False
        
        if not game.install_path.exists():
            logger.error(f"Game installation path not found: {game.install_path}")
            return False
        
        entry_point = game.install_path / game.entry_point
        if not entry_point.exists():
            logger.error(f"Game entry point not found: {entry_point}")
            return False
        
        try:
            logger.info(f"Launching game: {game.name}")
            
            # Run pre-launch commands
            self._run_pre_commands(game)
            
            # Build environment
            env = self._build_environment(game)
            
            # Launch game process
            process = subprocess.Popen(
                ["python3", str(entry_point)],
                cwd=str(game.install_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Wait for game to finish
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Game exited with error code {process.returncode}")
                if stderr:
                    logger.error(f"Error output: {stderr.decode()}")
            else:
                logger.info(f"Game exited normally: {game.name}")
            
            # Run post-launch commands
            self._run_post_commands(game)
            
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            return False

    def _run_pre_commands(self, game: Game) -> None:
        """
        Execute pre-launch commands.
        
        Args:
            game: Game being launched
        """
        # Get pre-launch commands from game or config
        pre_commands = game.custom_input_mappings.get("pre_launch_commands", [])
        
        for cmd in pre_commands:
            try:
                logger.info(f"Running pre-launch command: {cmd}")
                subprocess.run(cmd, shell=True, check=True, timeout=30)
            except subprocess.TimeoutExpired:
                logger.warning(f"Pre-launch command timed out: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Pre-launch command failed: {cmd} - {e}")

    def _run_post_commands(self, game: Game) -> None:
        """
        Execute post-launch commands.
        
        Args:
            game: Game that was launched
        """
        # Get post-launch commands from game or config
        post_commands = game.custom_input_mappings.get("post_launch_commands", [])
        
        for cmd in post_commands:
            try:
                logger.info(f"Running post-launch command: {cmd}")
                subprocess.run(cmd, shell=True, check=True, timeout=30)
            except subprocess.TimeoutExpired:
                logger.warning(f"Post-launch command timed out: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Post-launch command failed: {cmd} - {e}")

    def _build_environment(self, game: Game) -> Dict[str, str]:
        """
        Build environment variables for game process.
        
        Args:
            game: Game being launched
            
        Returns:
            dict: Environment variables
        """
        # Start with current environment
        env = os.environ.copy()
        
        # Add game-specific environment variables
        if game.custom_resolution:
            width, height = game.custom_resolution
            env["GAME_RESOLUTION"] = f"{width}x{height}"
        
        if game.custom_fps:
            env["GAME_FPS"] = str(game.custom_fps)
        
        # Add hardware config info
        env["DEVICE_TYPE"] = self.hw_config.get("detected_device", "desktop")
        env["OS_TYPE"] = self.hw_config.get("detected_os", "standard_linux")
        
        return env

    def is_running(self, process: Optional[subprocess.Popen]) -> bool:
        """
        Check if process is still running.
        
        Args:
            process: Process to check
            
        Returns:
            bool: True if process is running
        """
        if process is None:
            return False
        
        return process.poll() is None

    def terminate(self, process: Optional[subprocess.Popen]) -> None:
        """
        Terminate a running process.
        
        Args:
            process: Process to terminate
        """
        if process and self.is_running(process):
            logger.info("Terminating game process")
            process.terminate()
            
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate, killing")
                process.kill()