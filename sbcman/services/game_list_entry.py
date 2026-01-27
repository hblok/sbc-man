# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Game List Entry Module

Provides data structures for enhanced game list display with
installation status and update information.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pathlib import Path
from typing import Optional

from google.protobuf import message
from sbcman.proto import game_pb2


class GameStatus(Enum):
    """Status of a game in the library."""
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    UPDATE_AVAILABLE = "update_available"


class GameListEntry:
    """Enhanced game entry with installation status and icon information."""
    
    def __init__(self, 
                 game: game_pb2.Game,
                 status: GameStatus = GameStatus.NOT_INSTALLED,
                 icon_path: Optional[Path] = None,
                 icon_url: Optional[str] = None,
                 local_version: Optional[str] = None):
        """Initialize game list entry.
        
        Args:
            game: Game protobuf object
            status: Installation status of the game
            icon_path: Path to local icon file if available
            icon_url: URL to download icon if not local
            local_version: Version of installed game (if installed)
        """
        self.game = game
        self.status = status
        self.icon_path = icon_path
        self.icon_url = icon_url
        self.local_version = local_version
    
    @property
    def name(self) -> str:
        """Get game display name."""
        return self.game.name
    
    @property
    def version(self) -> str:
        """Get game version."""
        return self.game.version
    
    @property
    def id(self) -> str:
        """Get game ID."""
        return self.game.id
    
    @property
    def is_installed(self) -> bool:
        """Check if game is installed."""
        return self.status in [GameStatus.INSTALLED, GameStatus.UPDATE_AVAILABLE]
    
    @property
    def has_update(self) -> bool:
        """Check if an update is available."""
        return self.status == GameStatus.UPDATE_AVAILABLE
    
    @property
    def display_name(self) -> str:
        """Get display name with version info."""
        if self.is_installed:
            version_str = f" (v{self.local_version})" if self.local_version else ""
            if self.has_update:
                return f"{self.name}{version_str} [Update to v{self.version}]"
            return f"{self.name}{version_str}"
        return f"{self.name} (v{self.version})"