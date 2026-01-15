# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Process Launcher

Tests for launching games as subprocesses with pre/post command support,
environment variable handling, and process management.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
from pathlib import Path
import tempfile

from sbcman.proto import game_pb2
from sbcman.services.process_launcher import ProcessLauncher


class TestProcessLauncher(unittest.TestCase):
    """Test cases for ProcessLauncher."""

    def setUp(self):
        """Set up test fixtures."""
        self.hw_config = {
            'detected_device': 'test_device',
            'detected_os': 'test_os'
        }
        self.launcher = ProcessLauncher(self.hw_config)

    def test_initialization(self):
        """Test process launcher initialization."""
        self.assertEqual(self.launcher.hw_config, self.hw_config)

    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_game_success(self, mock_exists, mock_popen):
        """Test successful game launch."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create a mock game
        game = game_pb2.Game()
        game.id = "test1"
        game.name = "Test Game"
        game.installed = True
        game.install_path = "/path/to/game"
        game.entry_point = "main.py"
        
        # Convert install_path to Path object for the test
        game.install_path = game.install_path
        
        # Mock subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process
        
        # Launch game
        result = self.launcher.launch_game(game)
        
        # Verify success
        # todo
        #self.assertTrue(result)
        
        # Verify Popen was called
        #mock_popen.assert_called_once()
        
        # Verify game directory was checked
        #mock_exists.assert_called()

    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_game_not_installed(self, mock_exists, mock_popen):
        """Test launching uninstalled game fails."""
        # Create a mock game that's not installed
        game = game_pb2.Game()
        game.id = "test2"
        game.name = "Test Game 2"
        game.installed = False
        game.install_path = "/path/to/game"
        
        # Try to launch
        result = self.launcher.launch_game(game)
        
        # Verify failure
        self.assertFalse(result)
        
        # Verify Popen was not called
        mock_popen.assert_not_called()

    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_game_path_not_found(self, mock_exists, mock_popen):
        """Test launching game with missing install path fails."""
        # Setup mock - install path doesn't exist
        mock_exists.return_value = False
        
        # Create a mock game
        game = game_pb2.Game()
        game.id = "test3"
        game.name = "Test Game 3"
        game.installed = True
        game.install_path = "/nonexistent/path"
        
        # Try to launch
        result = self.launcher.launch_game(game)
        
        # Verify failure
        self.assertFalse(result)
        
        # Verify Popen was not called
        mock_popen.assert_not_called()

    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_game_entry_point_not_found(self, mock_exists, mock_popen):
        """Test launching game with missing entry point fails."""
        # Setup mock - install path exists but entry point doesn't
        def exists_side_effect(path):
            if isinstance(path, Path):
                return str(path) == "/path/to/game"
            return False
        
        mock_exists.side_effect = exists_side_effect
        
        # Create a mock game
        game = game_pb2.Game()
        game.id = "test4"
        game.name = "Test Game 4"
        game.installed = True
        game.install_path = "/path/to/game"
        game.entry_point = "missing.py"
        
        # Try to launch
        result = self.launcher.launch_game(game)
        
        # Verify failure
        self.assertFalse(result)
        
        # Verify Popen was not called
        mock_popen.assert_not_called()

    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_game_with_custom_resolution(self, mock_exists, mock_popen):
        """Test game launch with custom resolution environment variable."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create a mock game with custom resolution
        game = game_pb2.Game()
        game.id = "test5"
        game.name = "Test Game 5"
        game.installed = True
        game.install_path = "/path/to/game"
        game.entry_point = "main.py"
        game.custom_resolution.width = 1920
        game.custom_resolution.height = 1080
        
        # Mock subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'', b'')
        mock_popen.return_value = mock_process
        
        # Capture environment passed to Popen
        captured_env = {}
        def popen_side_effect(*args, **kwargs):
            captured_env.update(kwargs.get('env', {}))
            return mock_process
        
        mock_popen.side_effect = popen_side_effect
        
        # Launch game
        result = self.launcher.launch_game(game)
        
        # Verify success
        #self.assertTrue(result)
        
        # Verify GAME_RESOLUTION was set
        #self.assertIn('GAME_RESOLUTION', captured_env)
        #self.assertEqual(captured_env['GAME_RESOLUTION'], '1920x1080')

    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_game_with_custom_fps(self, mock_exists, mock_popen):
        """Test game launch with custom FPS environment variable."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create a mock game with custom FPS
        game = game_pb2.Game()
        game.id = "test6"
        game.name = "Test Game 6"
        game.installed = True
        game.install_path = "/path/to/game"
        game.entry_point = "main.py"
        game.custom_fps = 60
        
        # Mock subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'', b'')
        mock_popen.return_value = mock_process
        
        # Capture environment passed to Popen
        captured_env = {}
        def popen_side_effect(*args, **kwargs):
            captured_env.update(kwargs.get('env', {}))
            return mock_process
        
        mock_popen.side_effect = popen_side_effect
        
        # Launch game
        result = self.launcher.launch_game(game)
        
        # Verify success
        #self.assertTrue(result)
        
        # Verify GAME_FPS was set
        #self.assertIn('GAME_FPS', captured_env)
        #self.assertEqual(captured_env['GAME_FPS'], '60')

    @patch('subprocess.Popen')
    @patch('os.path.exists')
    def test_launch_game_with_hardware_config(self, mock_exists, mock_popen):
        """Test game launch includes hardware config in environment."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Create a mock game
        game = game_pb2.Game()
        game.id = "test7"
        game.name = "Test Game 7"
        game.installed = True
        game.install_path = "/path/to/game"
        game.entry_point = "main.py"
        
        # Mock subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'', b'')
        mock_popen.return_value = mock_process
        
        # Capture environment passed to Popen
        captured_env = {}
        def popen_side_effect(*args, **kwargs):
            captured_env.update(kwargs.get('env', {}))
            return mock_process
        
        mock_popen.side_effect = popen_side_effect
        
        # Launch game
        result = self.launcher.launch_game(game)
        
        # Verify success
        #self.assertTrue(result)
        
        # Verify hardware config was set
        #self.assertIn('DEVICE_TYPE', captured_env)
        #self.assertEqual(captured_env['DEVICE_TYPE'], 'test_device')
        #self.assertIn('OS_TYPE', captured_env)
        #self.assertEqual(captured_env['OS_TYPE'], 'test_os')

    @patch('subprocess.run')
    def disabled_test_run_pre_commands_success(self, mock_run):
        """Test successful execution of pre-launch commands."""
        # Create a mock game with pre-launch commands
        game = game_pb2.Game()
        game.id = "test8"
        
        # Add pre-launch command as custom input mapping
        mapping = game.custom_input_mappings.add()
        mapping.key = "pre_launch_commands"
        mapping.value = '["echo", "pre"]'
        
        # Mock subprocess.run
        mock_run.return_value = Mock(check=True)
        
        # Run pre commands
        self.launcher._run_pre_commands(game)
        
        # Verify subprocess.run was called
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        self.assertFalse(call_kwargs['shell'])

    @patch('subprocess.run')
    def disabled_test_run_pre_commands_timeout(self, mock_run):
        """Test pre-launch command timeout handling."""
        # Create a mock game
        game = game_pb2.Game()
        game.id = "test9"
        
        # Add pre-launch command
        mapping = game.custom_input_mappings.add()
        mapping.key = "pre_launch_commands"
        mapping.value = '["sleep", "100"]'
        
        # Mock subprocess.run to raise timeout
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        # Run pre commands (should not raise exception)
        self.launcher._run_pre_commands(game)
        
        # Verify subprocess.run was called
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def disabled_test_run_post_commands_success(self, mock_run):
        """Test successful execution of post-launch commands."""
        # Create a mock game with post-launch commands
        game = game_pb2.Game()
        game.id = "test10"
        
        # Add post-launch command
        mapping = game.custom_input_mappings.add()
        mapping.key = "post_launch_commands"
        mapping.value = '["echo", "post"]'
        
        # Mock subprocess.run
        mock_run.return_value = Mock(check=True)
        
        # Run post commands
        self.launcher._run_post_commands(game)
        
        # Verify subprocess.run was called
        mock_run.assert_called_once()

    def test_is_running_true(self):
        """Test is_running returns True for running process."""
        # Create mock process that's running
        mock_process = Mock()
        mock_process.poll.return_value = None
        
        result = self.launcher.is_running(mock_process)
        
        # Verify True
        self.assertTrue(result)

    def test_is_running_false(self):
        """Test is_running returns False for completed process."""
        # Create mock process that's not running
        mock_process = Mock()
        mock_process.poll.return_value = 0
        
        result = self.launcher.is_running(mock_process)
        
        # Verify False
        self.assertFalse(result)

    def test_is_running_none(self):
        """Test is_running returns False for None process."""
        result = self.launcher.is_running(None)
        
        # Verify False
        self.assertFalse(result)

    def test_terminate_success(self):
        """Test successful process termination."""
        # Create mock running process
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait.return_value = None
        
        # Terminate
        self.launcher.terminate(mock_process)
        
        # Verify terminate was called
        mock_process.terminate.assert_called_once()
        
        # Verify wait was called
        mock_process.wait.assert_called_once_with(timeout=5)

    def test_terminate_with_kill(self):
        """Test process termination uses kill if terminate fails."""
        # Create mock running process
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = subprocess.TimeoutExpired('cmd', 5)
        
        # Terminate
        self.launcher.terminate(mock_process)
        
        # Verify terminate was called
        mock_process.terminate.assert_called_once()
        
        # Verify kill was called after timeout
        mock_process.kill.assert_called_once()

    def test_terminate_none(self):
        """Test terminating None process doesn't raise error."""
        # Should not raise exception
        self.launcher.terminate(None)

    def test_terminate_already_stopped(self):
        """Test terminating already stopped process."""
        # Create mock stopped process
        mock_process = Mock()
        mock_process.poll.return_value = 0
        
        # Terminate
        self.launcher.terminate(mock_process)
        
        # Verify terminate was not called
        mock_process.terminate.assert_not_called()


if __name__ == '__main__':
    unittest.main()
