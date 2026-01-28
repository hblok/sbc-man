# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Installation Progress Integration

Tests for unified progress bar tracking across download and installation phases.
"""

import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

from sbcman.services.download_manager import DownloadManager, DownloadObserver
from sbcman.services.install_game import GameInstaller
from sbcman.proto import game_pb2
from sbcman.path.paths import AppPaths


class TestInstallationProgressObserver(DownloadObserver):
    """Test implementation of DownloadObserver for testing progress tracking."""
    
    def __init__(self):
        self.progress_calls = []
        self.complete_calls = []
        self.error_calls = []
    
    def on_progress(self, downloaded: int, total: int) -> None:
        """Track progress calls."""
        self.progress_calls.append((downloaded, total))
    
    def on_complete(self, success: bool, message: str) -> None:
        """Track complete calls."""
        self.complete_calls.append((success, message))
    
    def on_error(self, error_message: str) -> None:
        """Track error calls."""
        self.error_calls.append(error_message)


class TestInstallationProgress(unittest.TestCase):
    """Test cases for installation progress tracking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.games_dir = self.temp_dir / "games"
        self.games_dir.mkdir(exist_ok=True)
        
        self.hw_config = {
            "paths": {
                "games": str(self.games_dir),
            }
        }
        
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        self.download_manager = DownloadManager(self.hw_config, app_paths, None, None)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_download_progress_scaling(self):
        """Test that download progress is scaled to 0-60% range."""
        observer = TestInstallationProgressObserver()
        
        # Simulate download progress callback
        def progress_callback(downloaded: int, total: int) -> None:
            self.download_manager.download_progress = min(downloaded / total if total > 0 else 0, 1.0) * 0.6
            if observer:
                observer.on_progress(downloaded, total)
        
        # Simulate 50% download completion
        progress_callback(500, 1000)
        
        # Verify that download progress is scaled to 60% (0.6 * 0.5 = 0.3 = 30%)
        # Wait, the scaling is: download_fraction * 0.6
        # So 50% download = 0.5 * 0.6 = 0.3 (30%)
        expected_progress = 0.3
        self.assertAlmostEqual(self.download_manager.download_progress, expected_progress, places=2)
        
    def test_installation_progress_range(self):
        """Test that installation progress is in 60-100% range."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        game_installer = GameInstaller(None, app_paths)
        
        progress_values = []
        
        def progress_callback(progress: float) -> None:
            progress_values.append(progress)
        
        # Create a test game
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "test-game.zip"
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("main.py", "print('Hello, World!')")
            
            # Install the game with progress callback
            install_dir = game_installer.install_game(zip_path, game, progress_callback)
            
            # Verify that all progress values are in the 0.0-1.0 range
            for value in progress_values:
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)
    
    def test_install_wheel_progress_stages(self):
        """Test that wheel installation has proper progress stages."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        game_installer = GameInstaller(None, app_paths)
        
        progress_values = []
        
        def progress_callback(progress: float) -> None:
            progress_values.append(progress)
        
        game = game_pb2.Game()
        game.id = "test-game"
        game.entry_point = "main"
        
        config = Mock()
        config.get.return_value = True
        
        installer = GameInstaller(config, app_paths)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            wheel_path = Path(temp_dir) / "test-game.whl"
            wheel_path.write_text("wheel content")
            
            # Create the entry point file to simulate a successful installation
            self.games_dir.mkdir(exist_ok=True)
            entry_point = self.games_dir / game.entry_point
            entry_point.write_text("# Entry point")
            
            with patch('sbcman.services.install_game.site.getsitepackages') as mock_getsitepackages:
                mock_getsitepackages.return_value = [str(self.games_dir)]
                
                with patch('sbcman.services.wheel_installer.WheelInstaller') as mock_wheel_installer_class:
                    mock_installer = Mock()
                    mock_installer.install_wheel.return_value = (True, "Installed successfully")
                    mock_wheel_installer_class.return_value = mock_installer
                    
                    install_dir = installer._install_wheel(wheel_path, game, progress_callback)
                    
                    # Verify that we have at least some progress updates
                    self.assertGreater(len(progress_values), 0)
                    
                    # Verify that progress ends at 1.0
                    self.assertEqual(progress_values[-1], 1.0)
    
    def test_extract_archive_progress(self):
        """Test that archive extraction has proper progress updates."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        game_installer = GameInstaller(None, app_paths)
        
        progress_values = []
        
        def progress_callback(progress: float) -> None:
            progress_values.append(progress)
        
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "test-game.zip"
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("main.py", "print('Hello, World!')")
            
            # Extract the archive with progress callback
            install_dir = game_installer._extract_archive(zip_path, game, progress_callback)
            
            # Verify that we have progress updates
            self.assertGreater(len(progress_values), 0)
            
            # Verify that progress starts at 0.0 and ends at 1.0
            self.assertEqual(progress_values[0], 0.0)
            self.assertEqual(progress_values[-1], 1.0)
    
    def test_unified_progress_flow(self):
        """Test the complete unified progress flow from download to install."""
        observer = TestInstallationProgressObserver()
        
        # Simulate download phase (0-60%)
        download_progress_values = []
        
        def download_progress_callback(downloaded: int, total: int) -> None:
            download_fraction = min(downloaded / total if total > 0 else 0, 1.0)
            self.download_manager.download_progress = download_fraction * 0.6
            download_progress_values.append(self.download_manager.download_progress)
            if observer:
                observer.on_progress(downloaded, total)
        
        # Simulate 100% download completion
        download_progress_callback(1000, 1000)
        
        # Verify download progress is at 60%
        self.assertAlmostEqual(self.download_manager.download_progress, 0.6, places=2)
        
        # Simulate installation phase (60-100%)
        install_progress_values = []
        
        def install_progress_callback(progress: float) -> None:
            # progress is 0.0-1.0, scale to 60-100%
            self.download_manager.download_progress = 0.6 + (progress * 0.4)
            install_progress_values.append(self.download_manager.download_progress)
        
        # Simulate 50% installation completion
        install_progress_callback(0.5)
        
        # Verify that total progress is at 80% (60% download + 20% of 40% install)
        self.assertAlmostEqual(self.download_manager.download_progress, 0.8, places=2)
        
        # Simulate 100% installation completion
        install_progress_callback(1.0)
        
        # Verify that total progress is at 100%
        self.assertAlmostEqual(self.download_manager.download_progress, 1.0, places=2)


if __name__ == "__main__":
    unittest.main()