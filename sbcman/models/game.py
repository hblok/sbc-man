# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Game Model - Direct Protobuf Implementation

This module directly exports the protobuf Game class, completely replacing the old dataclass.
"""

from ..proto.game_pb2 import Game

# Direct re-export of protobuf Game class - this completely replaces the old dataclass
__all__ = ["Game"]
