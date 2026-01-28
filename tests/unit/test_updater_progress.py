# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Updater Progress Integration

Tests for unified progress bar tracking across update download and installation phases.
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

import sbcman.services.updater
import sbcman.services.config_manager
import sbcman.path.paths


class TestUpdaterProgress(unittest.TestCase):
    """Test cases for updater progress tracking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock(spec=sbcman.services.config_manager.ConfigManager)
        self.mock_paths = Mock(spec=sbcman.path.paths.AppPaths)
        self.mock_paths.temp_dir = Path(tempfile.mkdtemp())
        
        self.mock_config.get.return_value = "https://github.com/hblok/sbc-man"
        
        self.updater = sbcman.services.updater.UpdaterService(
            self.mock_config,
            self.mock_paths
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.mock_paths.temp_dir.exists():
            shutil.rmtree(self.mock_paths.temp_dir)
    
    def test_download_progress_callback(self):
        """Test that download progress callback is called during download."""
        download_url = "https://example.com/test.whl"
        progress_values = []
        
        def progress_callback(progress: float) -> None:
            progress_values.append(progress)
        
        def mock_urlretrieve_side_effect(url, filename, reporthook=None):
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("dummy content")
            # Simulate progress updates
            if reporthook:
                reporthook(10, 100, 1000)  # 10% downloaded
                reporthook(50, 100, 1000)  # 50% downloaded
                reporthook(100, 100, 1000)  # 100% downloaded
        
        with patch('sbcman.services.updater.urllib.request.urlretrieve') as mock_urlretrieve:
            mock_urlretrieve.side_effect = mock_urlretrieve_side_effect
            
            result = self.updater.download_update(download_url, progress_callback)
            
            # Verify download succeeded
            self.assertIsNotNone(result)
            
            # Verify that progress values are in the 0-0.6 range (scaled to 60%)
            for value in progress_values:
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 0.6)
            
            # Verify that we have multiple progress updates
            self.assertGreater(len(progress_values), 0)
    
    def test_download_progress_scaling(self):
        """Test that download progress is correctly scaled to 0-60% range."""
        download_url = "https://example.com/test.whl"
        
        def mock_urlretrieve_side_effect(url, filename, reporthook=None):
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("dummy content")
            # Simulate progress updates - use blocks that actually add up to total
            if reporthook:
                # block_num, block_size, total_size
                # At block 0 of 100: 0% -> 0.0
                reporthook(0, 10, 1000)      
                # At block 50 of 100: 500/1000 = 50% -> 0.3
                reporthook(50, 10, 1000)    
                # At block 100 of 100: 1000/1000 = 100% -> 0.6
                reporthook(100, 10, 1000)   
        
        with patch('sbcman.services.updater.urllib.request.urlretrieve') as mock_urlretrieve:
            mock_urlretrieve.side_effect = mock_urlretrieve_side_effect
            
            progress_values = []
            
            def progress_callback(progress: float) -> None:
                progress_values.append(progress)
            
            self.updater.download_update(download_url, progress_callback)
            
            # Verify we have progress updates
            self.assertGreater(len(progress_values), 0)
            
            # Verify that values are in correct range
            for value in progress_values:
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 0.6)
            
            # Verify that the final value is 0.6 (complete download)
            self.assertEqual(progress_values[-1], 0.6)
    
    def test_download_without_progress_callback(self):
        """Test that download works without progress callback."""
        download_url = "https://example.com/test.whl"
        
        def mock_urlretrieve_side_effect(url, filename, reporthook=None):
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("dummy content")
            # Simulate progress updates even without callback
            if reporthook:
                reporthook(100, 100, 1000)
        
        with patch('sbcman.services.updater.urllib.request.urlretrieve') as mock_urlretrieve:
            mock_urlretrieve.side_effect = mock_urlretrieve_side_effect
            
            result = self.updater.download_update(download_url)
            
            # Verify download succeeded
            self.assertIsNotNone(result)
    
    def test_install_progress_callback(self):
        """Test that install progress callback is called during installation."""
        wheel_path = Path("test.whl")
        progress_values = []
        
        def progress_callback(progress: float) -> None:
            progress_values.append(progress)
        
        with patch('sbcman.services.updater.WheelInstaller') as mock_wheel_installer_class:
            mock_installer = Mock()
            mock_installer.install_wheel.return_value = (True, "Installation successful")
            mock_wheel_installer_class.return_value = mock_installer
            
            success, message = self.updater.install_update(wheel_path, progress_callback)
            
            # Verify installation succeeded
            self.assertTrue(success)
            
            # Verify that progress values are in the 0.6-1.0 range
            for value in progress_values:
                self.assertGreaterEqual(value, 0.6)
                self.assertLessEqual(value, 1.0)
            
            # Verify that we have at least start and end progress
            self.assertGreater(len(progress_values), 0)
            self.assertEqual(progress_values[0], 0.6)
            self.assertEqual(progress_values[-1], 1.0)
    
    def test_install_progress_start_and_end(self):
        """Test that installation progress starts at 0.6 and ends at 1.0."""
        wheel_path = Path("test.whl")
        
        with patch('sbcman.services.updater.WheelInstaller') as mock_wheel_installer_class:
            mock_installer = Mock()
            mock_installer.install_wheel.return_value = (True, "Installation successful")
            mock_wheel_installer_class.return_value = mock_installer
            
            progress_values = []
            
            def progress_callback(progress: float) -> None:
                progress_values.append(progress)
            
            self.updater.install_update(wheel_path, progress_callback)
            
            # Verify start and end points
            self.assertEqual(progress_values[0], 0.6)
            self.assertEqual(progress_values[-1], 1.0)
    
    def test_install_without_progress_callback(self):
        """Test that installation works without progress callback."""
        wheel_path = Path("test.whl")
        
        with patch('sbcman.services.updater.WheelInstaller') as mock_wheel_installer_class:
            mock_installer = Mock()
            mock_installer.install_wheel.return_value = (True, "Installation successful")
            mock_wheel_installer_class.return_value = mock_installer
            
            success, message = self.updater.install_update(wheel_path)
            
            # Verify installation succeeded
            self.assertTrue(success)
    
    def test_unified_progress_flow(self):
        """Test the complete unified progress flow from download to install."""
        download_url = "https://example.com/test.whl"
        wheel_path = Path("test.whl")
        
        all_progress_values = []
        
        # Download phase
        def mock_urlretrieve_side_effect(url, filename, reporthook=None):
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("dummy content")
            if reporthook:
                reporthook(100, 100, 1000)
        
        with patch('sbcman.services.updater.urllib.request.urlretrieve') as mock_urlretrieve:
            mock_urlretrieve.side_effect = mock_urlretrieve_side_effect
            
            def download_progress_callback(progress: float) -> None:
                all_progress_values.append(("download", progress))
            
            result = self.updater.download_update(download_url, download_progress_callback)
            self.assertIsNotNone(result)
        
        # Install phase
        with patch('sbcman.services.updater.WheelInstaller') as mock_wheel_installer_class:
            mock_installer = Mock()
            mock_installer.install_wheel.return_value = (True, "Installation successful")
            mock_wheel_installer_class.return_value = mock_installer
            
            def install_progress_callback(progress: float) -> None:
                all_progress_values.append(("install", progress))
            
            success, message = self.updater.install_update(wheel_path, install_progress_callback)
            self.assertTrue(success)
        
        # Verify that we have progress updates from both phases
        download_updates = [v for phase, v in all_progress_values if phase == "download"]
        install_updates = [v for phase, v in all_progress_values if phase == "install"]
        
        self.assertGreater(len(download_updates), 0)
        self.assertGreater(len(install_updates), 0)
        
        # Verify that download progress is in 0-0.6 range
        for value in download_updates:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 0.6)
        
        # Verify that install progress is in 0.6-1.0 range
        for value in install_updates:
            self.assertGreaterEqual(value, 0.6)
            self.assertLessEqual(value, 1.0)


if __name__ == "__main__":
    unittest.main()