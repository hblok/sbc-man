"""
Unit Tests for Base State Module

Tests for base state functionality.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pygame

from src.states.base_state import BaseState


class TestBaseState(unittest.TestCase):
    
    def test_base_state_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            base_state = BaseState(Mock())