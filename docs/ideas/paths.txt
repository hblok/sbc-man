"""
Application Paths Centralization

Provides centralized path management for the SBC-Man application.
Replaces scattered hardcoded paths and "~" expansion throughout the codebase.
"""

from pathlib import Path
from typing import Dict, Any, Optional


class AppPaths:
    """
    Centralized path management for the application.
    
    Handles all path operations using pathlib exclusively.
    Provides proper home directory expansion and relative path handling.
    """
    
    def __init__(self, hw_config: Optional[Dict[str, Any]] = None):
        """
        Initialize
        
        Args:
            hw_config: Hardware configuration dictionary containing path overrides
        """
        self.hw_config = hw_config or {}
        self._paths_config = self.hw_config.get("paths", {})
        
        # Cache common paths for performance
        self._data_dir: Optional[Path] = None
        self._games_dir: Optional[Path] = None
        self._src_dir: Optional[Path] = None
    
    @property
    def data_dir(self) -> Path:
        """Get main data directory path."""
        if self._data_dir is None:
            path = self._paths_config.get("data", "~/.local/share/sbc-man")
            self._data_dir = Path(path).expanduser()
        return self._data_dir
    
    @property
    def games_dir(self) -> Path:
        """Get games directory path."""
        if self._games_dir is None:
            path = self._paths_config.get("games", "~/games")
            self._games_dir = Path(path).expanduser()
        return self._games_dir
    
    @property
    def src_dir(self) -> Path:
        """Get source directory path."""
        if self._src_dir is None:
            self._src_dir = Path(__file__).parent.parent
        return self._src_dir
    
    # Data directory subpaths
    @property
    def config_file(self) -> Path:
        """Get main configuration file path."""
        return self.data_dir / "config.json"
    
    @property
    def games_file(self) -> Path:
        """Get games library file path."""
        return self.data_dir / "games.json"
    
    @property
    def input_overrides_dir(self) -> Path:
        """Get input overrides directory path."""
        return self.data_dir / "input_overrides"
    
    @property
    def game_input_overrides_dir(self) -> Path:
        """Get game-specific input overrides directory path."""
        return self.input_overrides_dir / "games"
    
    # Games directory subpaths
    @property
    def downloads_dir(self) -> Path:
        """Get downloads directory path."""
        return self.games_dir / "downloads"
    
    def get_game_install_dir(self, game_id: str) -> Path:
        """
        Get installation directory for a specific game.
        
        Args:
            game_id: Unique identifier for the game
            
        Returns:
            Path to the game's installation directory
        """
        return self.games_dir / game_id
    
    def get_game_input_override_file(self, game_id: str) -> Path:
        """
        Get input override file path for a specific game.
        
        Args:
            game_id: Unique identifier for the game
            
        Returns:
            Path to the game's input override file
        """
        return self.game_input_overrides_dir / f"{game_id}.json"
    
    # Configuration directory paths
    @property
    def config_dir(self) -> Path:
        """Get configuration directory path."""
        return self.src_dir / "config"
    
    @property
    def input_mappings_config_dir(self) -> Path:
        """Get input mappings configuration directory path."""
        return self.config_dir / "input_mappings"
    
    # Utility methods
    def ensure_directories(self) -> None:
        """Create all necessary directories if they don't exist."""
        directories = [
            self.data_dir,
            self.input_overrides_dir,
            self.game_input_overrides_dir,
            self.games_dir,
            self.downloads_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_relative_path(self, path: Path, base: Optional[Path] = None) -> Path:
        """
        Get a path relative to a base directory.
        
        Args:
            path: The path to make relative
            base: Base directory (defaults to src_dir)
            
        Returns:
            Relative path
        """
        if base is None:
            base = self.src_dir
        return path.relative_to(base)
    
    def expand_path(self, path: str) -> Path:
        """
        Expand a path string with proper home directory expansion.
        
        Args:
            path: Path string to expand
            
        Returns:
            Expanded Path object
        """
        return Path(path).expanduser()