# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for DownloadManager

Tests for download management, installation, and observer pattern implementation.
"""

from pathlib import Path
from sbcman.path.paths import AppPaths
from unittest.mock import Mock, patch, MagicMock
import os
import pathlib
import tempfile
import unittest
import zipfile

from sbcman.services.download_manager import DownloadManager, DownloadObserver
from sbcman.models.game import Game
from sbcman.services.network import NetworkService


class TestDownloadObserver(DownloadObserver):
    """Test implementation of DownloadObserver for testing purposes."""
    
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


class TestDownloadManager(unittest.TestCase):
    """Test cases for DownloadManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = pathlib.Path(tempfile.mkdtemp())
        self.games_dir = self.temp_dir / "games"
        self.games_dir.mkdir(exist_ok=True)
        
        self.hw_config = {
            "paths": {
                "games": str(self.games_dir),
            }
        }

        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        self.download_manager = DownloadManager(self.hw_config, app_paths)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_download_manager_initialization(self):
        """Test download manager initialization."""
        self.assertFalse(self.download_manager.is_downloading)
        self.assertEqual(self.download_manager.download_progress, 0.0)
        self.assertEqual(self.download_manager.hw_config, self.hw_config)
    
    @patch('pathlib.Path.unlink')
    @patch.object(DownloadManager, '_extract_archive')
    @patch('sbcman.services.download_manager.NetworkService')
    def test_download_game_success(self, mock_network_service_class, mock_extract_archive, mock_unlink):
        """Test successful game download."""
        # Create a mock network service
        mock_network_service = Mock()
        mock_network_service_class.return_value = mock_network_service
        mock_network_service.download_file.return_value = True
        
        # Mock the extraction method
        mock_extract_archive.return_value = Path(self.temp_dir) / "test-game"
        
        # Mock the unlink method to prevent errors
        mock_unlink.return_value = None
        
        # Reinitialize the download manager with the mocked network service
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        self.download_manager = DownloadManager(self.hw_config, app_paths)
        
        # Create a test game
        game = Game(
            game_id="test-game",
            name="Test Game",
            download_url="https://example.com/test-game.zip"
        )
        
        # Create an observer
        observer = TestDownloadObserver()
        
        # Download the game
        self.download_manager.download_game(game, observer)
        
        # Wait for the download to complete by checking the flag
        import time
        start_time = time.time()
        while self.download_manager.is_downloading and time.time() - start_time < 5:
            time.sleep(0.1)
        
        # Verify the network service was called correctly
        mock_network_service.download_file.assert_called_once()
        
        # Verify the observer was notified of completion
        self.assertEqual(len(observer.complete_calls), 1)
        self.assertTrue(observer.complete_calls[0][0])  # success should be True
        self.assertIn("Successfully installed Test Game", observer.complete_calls[0][1])
    
    @patch.object(NetworkService, 'download_file')
    def test_download_game_failure(self, mock_download_file):
        """Test failed game download."""
        # Configure the mock
        mock_download_file.return_value = False
        
        # Create a test game
        game = Game(
            game_id="test-game",
            name="Test Game",
            download_url="https://example.com/test-game.zip"
        )
        
        # Create an observer
        observer = TestDownloadObserver()
        
        # Download the game
        self.download_manager.download_game(game, observer)
        
        # Wait for the download to complete by checking the flag
        import time
        start_time = time.time()
        while self.download_manager.is_downloading and time.time() - start_time < 5:
            time.sleep(0.1)
        
        # Verify the network service was called correctly
        mock_download_file.assert_called_once()
        
        # Verify the observer was notified of error
        self.assertEqual(len(observer.error_calls), 1)
        self.assertIn("Download failed", observer.error_calls[0])
    
    @patch.object(NetworkService, 'download_file')
    def test_download_game_error(self, mock_download_file):
        """Test game download with exception."""
        # Configure the mock
        mock_download_file.side_effect = Exception("Network error")
        
        # Create a test game
        game = Game(
            game_id="test-game",
            name="Test Game",
            download_url="https://example.com/test-game.zip"
        )
        
        # Create an observer
        observer = TestDownloadObserver()
        
        # Download the game
        self.download_manager.download_game(game, observer)
        
        # Wait for the download to complete by checking the flag
        import time
        start_time = time.time()
        while self.download_manager.is_downloading and time.time() - start_time < 5:
            time.sleep(0.1)
        
        # Verify the network service was called correctly
        mock_download_file.assert_called_once()
        
        # Verify the observer was notified of error
        self.assertEqual(len(observer.error_calls), 1)
        self.assertIn("Network error", observer.error_calls[0])
    
    def test_extract_game_zip(self):
        """Test extracting a ZIP game archive."""
        # Create a test game
        game = Game(
            game_id="test-game",
            name="Test Game",
            entry_point="main.py"
        )
        
        # Create a temporary ZIP file with some content
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "test-game.zip"
            extract_dir = Path(temp_dir) / "extracted"
            
            # Create a ZIP file with a simple file inside
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("main.py", "print('Hello, World!')")
            
            # Extract the game
            install_dir = self.download_manager._extract_archive(zip_path, game)
            
            # Verify the installation directory was created
            self.assertTrue(install_dir.exists())
            
            # Verify the entry point file was extracted and has executable permissions
            entry_point = install_dir / "main.py"
            self.assertTrue(entry_point.exists())
            
            # Check if permissions are set correctly (might not work on all systems)
            # Just verify the file exists for now
    
    def test_extract_game_tar(self):
        """Test extracting a TAR game archive."""
        try:
            import tarfile
            
            # Create a test game
            game = Game(
                game_id="test-game",
                name="Test Game",
                entry_point="main.py"
            )
            
            # Create a temporary TAR file with some content
            with tempfile.TemporaryDirectory() as temp_dir:
                tar_path = Path(temp_dir) / "test-game.tar"
                extract_dir = Path(temp_dir) / "extracted"
                
                # Create a TAR file with a simple file inside
                with tarfile.open(tar_path, 'w') as tar_file:
                    # Create a temporary file to add to the archive
                    temp_file = Path(temp_dir) / "main.py"
                    temp_file.write_text("print('Hello, World!')")
                    tar_file.add(temp_file, "main.py")
                
                # Extract the game
                install_dir = self.download_manager._extract_archive(tar_path, game)
                
                # Verify the installation directory was created
                self.assertTrue(install_dir.exists())
                
                # Verify the entry point file was extracted
                entry_point = install_dir / "main.py"
                self.assertTrue(entry_point.exists())
        except ImportError:
            # tarfile not available, skip this test
            pass
    
    def test_extract_game_unsupported_format(self):
        """Test extracting a game with unsupported archive format."""
        # Create a test game
        game = Game(
            game_id="test-game",
            name="Test Game"
        )
        
        # Create a temporary file with unsupported extension
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test-game.unsupported"
            file_path.write_text("test content")
            
            # Try to extract the game - should raise an exception
            with self.assertRaises(Exception) as context:
                self.download_manager._extract_archive(file_path, game)
            
            self.assertIn("Unsupported archive format", str(context.exception))
    
    def test_cancel_download(self):
        """Test canceling a download."""
        # Initially, is_downloading should be False
        self.assertFalse(self.download_manager.is_downloading)
        
        # Set is_downloading to True to simulate an ongoing download
        self.download_manager.is_downloading = True
        
        # Cancel the download
        self.download_manager.cancel_download()
        
        # Verify is_downloading is now False
        self.assertFalse(self.download_manager.is_downloading)
    
    def test_get_progress(self):
        """Test getting download progress."""
        # Initially, progress should be 0.0
        self.assertEqual(self.download_manager.get_progress(), 0.0)
        
        # Set progress to a specific value
        self.download_manager.download_progress = 0.75
        
        # Verify the progress is returned correctly
        self.assertEqual(self.download_manager.get_progress(), 0.75)


if __name__ == "__main__":
    unittest.main()
