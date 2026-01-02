# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Game utilities for protobuf compatibility.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from ..proto.game_pb2 import Game as ProtoGame
from . import Game


def create_game(
    game_id: str,
    name: str,
    version: str = "",
    description: str = "",
    author: str = "",
    install_path: str = "",
    entry_point: str = "main.py",
    installed: bool = False,
    download_url: str = "",
    custom_input_mappings: Optional[Dict[str, Any]] = None,
    custom_resolution: Optional[Tuple[int, int]] = None,
    custom_fps: Optional[int] = None,
) -> Game:
    """Create a protobuf Game with similar interface to the old dataclass."""
    game = Game()
    game.id = game_id
    game.name = name
    game.version = version
    game.description = description
    game.author = author
    game.install_path = install_path
    game.entry_point = entry_point
    game.installed = installed
    game.download_url = download_url
    
    # Handle custom_input_mappings
    if custom_input_mappings:
        for key, value in custom_input_mappings.items():
            mapping = game.custom_input_mappings.add()
            mapping.key = str(key)
            mapping.value = str(value)
    
    # Handle custom_resolution
    if custom_resolution:
        game.custom_resolution.width = custom_resolution[0]
        game.custom_resolution.height = custom_resolution[1]
    
    # Handle custom_fps
    if custom_fps is not None:
        game.custom_fps = custom_fps
    
    return game


def game_to_dict(game: Game) -> Dict[str, Any]:
    """Convert protobuf Game to dictionary."""
    result = {
        "id": game.id,
        "name": game.name,
        "version": game.version,
        "description": game.description,
        "author": game.author,
        "install_path": game.install_path,
        "entry_point": game.entry_point,
        "installed": game.installed,
        "download_url": game.download_url,
        "custom_input_mappings": {
            mapping.key: mapping.value for mapping in game.custom_input_mappings
        },
    }
    
    # Handle custom_resolution
    if game.HasField('custom_resolution'):
        result["custom_resolution"] = (game.custom_resolution.width, game.custom_resolution.height)
    else:
        result["custom_resolution"] = None
    
    # Handle custom_fps (scalar fields don't have presence check)
    result["custom_fps"] = game.custom_fps if game.custom_fps != 0 else None
    
    return result


def game_from_dict(data: Dict[str, Any]) -> Game:
    """Create protobuf Game from dictionary."""
    custom_resolution = data.get("custom_resolution")
    if isinstance(custom_resolution, list):
        custom_resolution = tuple(custom_resolution)
    
    return create_game(
        game_id=data["id"],
        name=data["name"],
        version=data.get("version", ""),
        description=data.get("description", ""),
        author=data.get("author", ""),
        install_path=data.get("install_path", ""),
        entry_point=data.get("entry_point", "main.py"),
        installed=data.get("installed", False),
        download_url=data.get("download_url", ""),
        custom_input_mappings=data.get("custom_input_mappings", {}),
        custom_resolution=custom_resolution,
        custom_fps=data.get("custom_fps"),
    )


def get_custom_resolution(game: Game) -> Optional[Tuple[int, int]]:
    """Get custom resolution as tuple (compatible with old interface)."""
    if game.HasField('custom_resolution'):
        return (game.custom_resolution.width, game.custom_resolution.height)
    return None


def get_custom_fps(game: Game) -> Optional[int]:
    """Get custom FPS (compatible with old interface)."""
    return game.custom_fps if game.custom_fps != 0 else None
