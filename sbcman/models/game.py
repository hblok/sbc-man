"""
Game Model

Data model representing a game with metadata and installation information.

Based on: docs/code/class_models_game.txt
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class Game:
    """
    Game data model.
    
    Represents a game with all its metadata, installation status,
    and custom configuration options.
    """

    def __init__(
        self,
        game_id: str,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        install_path: str = "",
        entry_point: str = "main.py",
        installed: bool = False,
        download_url: str = "",
        custom_input_mappings: Optional[Dict[str, Any]] = None,
        custom_resolution: Optional[Tuple[int, int]] = None,
        custom_fps: Optional[int] = None,
    ):
        """
        Initialize game instance with metadata.
        
        Args:
            game_id: Unique identifier for the game
            name: Display name of the game
            version: Game version string
            description: Game description text
            author: Game author/developer name
            install_path: Path to game installation directory
            entry_point: Name of main Python file to execute
            installed: Whether game is currently installed
            download_url: URL to download game package
            custom_input_mappings: Per-game input overrides
            custom_resolution: Per-game resolution override
            custom_fps: Per-game FPS target override
        """
        self.id = game_id
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.install_path = Path(install_path) if install_path else Path()
        self.entry_point = entry_point
        self.installed = installed
        self.download_url = download_url
        self.custom_input_mappings = custom_input_mappings or {}
        self.custom_resolution = custom_resolution
        self.custom_fps = custom_fps

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize game instance to dictionary for persistence.
        
        Returns:
            dict: Game data as dictionary with all attributes
        """
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "install_path": str(self.install_path),
            "entry_point": self.entry_point,
            "installed": self.installed,
            "download_url": self.download_url,
            "custom_input_mappings": self.custom_input_mappings,
            "custom_resolution": self.custom_resolution,
            "custom_fps": self.custom_fps,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Game":
        """
        Deserialize game instance from dictionary.
        
        Args:
            data: Game data dictionary
            
        Returns:
            Game: New Game instance with data from dictionary
        """
        return Game(
            game_id=data["id"],
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            install_path=data.get("install_path", ""),
            entry_point=data.get("entry_point", "main.py"),
            installed=data.get("installed", False),
            download_url=data.get("download_url", ""),
            custom_input_mappings=data.get("custom_input_mappings", {}),
            custom_resolution=data.get("custom_resolution"),
            custom_fps=data.get("custom_fps"),
        )

    def __repr__(self) -> str:
        """String representation of game."""
        return f"Game(id='{self.id}', name='{self.name}', installed={self.installed})"