# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for GameManager

Tests for game launching and process management.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import multiprocessing

from sbcman.services.game_launcher import GameManager


class TestGameManager(unittest.TestCase):

    def setUp(self):
        self.manager = GameManager()

    def test_initialization(self):
        manager = GameManager()
        self.assertIn('snake', manager.games)
        self.assertIn('pong', manager.games)
        self.assertIn('tetris', manager.games)
        self.assertEqual(manager.games['snake'], 'games.snake')

    def test_launch_game_not_found(self):
        with patch('builtins.print') as mock_print:
            self.manager.launch_game('nonexistent')
            mock_print.assert_called_once()
            self.assertIn('not found', mock_print.call_args[0][0])

    @patch('sbcman.services.game_launcher.multiprocessing.Process')
    def test_launch_game_valid_name(self, mock_process_class):
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process
        
        self.manager.launch_game('snake')
        
        mock_process_class.assert_called_once()
        mock_process.start.assert_called_once()
        mock_process.join.assert_called_once()

    @patch('sbcman.services.game_launcher.multiprocessing.Process')
    def test_launch_game_exits_nonzero(self, mock_process_class):
        mock_process = MagicMock()
        mock_process.exitcode = 1
        mock_process_class.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            self.manager.launch_game('snake')
            mock_print.assert_called()
            self.assertIn('exited with code', mock_print.call_args[0][0])

    @patch('sbcman.services.game_launcher.multiprocessing.Process')
    def test_launch_game_exits_zero(self, mock_process_class):
        mock_process = MagicMock()
        mock_process.exitcode = 0
        mock_process_class.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            self.manager.launch_game('snake')
            calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertFalse(any('exited with code' in call for call in calls))

    @patch('sbcman.services.game_launcher.importlib.import_module')
    @patch('builtins.print')
    @patch('sbcman.services.game_launcher.multiprocessing.Process')
    def test_run_game_import_error(self, mock_process_class):
        mock_process = MagicMock()
        mock_process.exitcode = 1
        mock_process_class.return_value = mock_process
        
        manager = GameManager()
        
        with patch('builtins.print'):
            manager.launch_game('snake')
        
        self.assertEqual(mock_process.exitcode, 1)

    @patch('sbcman.services.game_launcher.multiprocessing.Process')
    def test_launch_game_module_name_passed(self, mock_process_class):
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process
        
        self.manager.launch_game('pong')
        
        args, kwargs = mock_process_class.call_args
        self.assertEqual(kwargs['args'][0], 'games.pong')

    @patch('sbcman.services.game_launcher.multiprocessing.Process')
    def test_launch_game_uses_isolated_process(self, mock_process_class):
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process
        
        self.manager.launch_game('tetris')
        
        mock_process_class.assert_called_once()
        args, kwargs = mock_process_class.call_args
        self.assertIn('target', kwargs)
        self.assertIn('args', kwargs)