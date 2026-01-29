# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for Updater Async Progress

Tests for async update functionality with progress tracking.
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

import sbcman.services.updater
import sbcman.services.config_manager
import sbcman.path.paths


class TestUpdaterAsync(unittest.TestCase):
    """Test cases for async updater functionality."""
    
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
    
    def disabled_test_install_with_pip_timeouttest_async_start_update(self):
        """Test that start_update starts a background thread."""
        download_url = "https://example.com/test.whl"
        
        def create_mock_file(url, filename, reporthook=None):
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("dummy content")
        
        with patch('sbcman.services.updater.urllib.request.urlretrieve') as mock_retrieve:
            with patch('sbcman.services.updater.WheelInstaller') as mock_installer:
                # Setup mocks
                mock_retrieve.side_effect = create_mock_file
                mock_installer.return_value.install_wheel.return_value = (True, "Success")
                
                # Start update (should be non-blocking)
                self.updater.start_update(download_url)
                
                # Check that updater is marked as updating
                self.assertTrue(self.updater.is_updating)
                
                # Wait a bit for thread to complete
                import time
                time.sleep(0.2)
                
                # Thread should have completed
                self.assertFalse(self.updater.is_updating)
                self.assertEqual(self.updater.get_progress(), 1.0)

    def test_get_progress(self):
        """Test getting progress from async update."""
        self.assertEqual(self.updater.get_progress(), 0.0)
        
        with patch.object(self.updater, '_update_lock'):
            self.updater.update_progress = 0.5
            self.assertEqual(self.updater.get_progress(), 0.5)

    def test_get_message(self):
        """Test getting message from async update."""
        self.assertEqual(self.updater.get_message(), "")
        
        with patch.object(self.updater, '_update_lock'):
            self.updater.update_message = "Downloading..."
            self.assertEqual(self.updater.get_message(), "Downloading...")

    def disabled_test_cancel_update(self):
        """Test cancelling an update."""
        download_url = "https://example.com/test.whl"
        
        with patch('sbcman.services.updater.urllib.request.urlretrieve') as mock_retrieve:
            # Make download take a long time
            def slow_download(*args, **kwargs):
                import time
                time.sleep(0.3)
            
            mock_retrieve.side_effect = slow_download
            
            # Start update
            self.updater.start_update(download_url)
            self.assertTrue(self.updater.is_updating)
            
            # Cancel update
            self.updater.cancel_update()
            
            # Wait a bit
            import time
            time.sleep(0.2)
            
            # Should not be updating anymore
            self.assertFalse(self.updater.is_updating)

    def disabled_test_async_update_progress_flow(self):
        """Test the complete async update progress flow."""
        download_url = "https://example.com/test.whl"
        
        def create_mock_file(url, filename, reporthook=None):
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("dummy content")
        
        with patch('sbcman.services.updater.urllib.request.urlretrieve') as mock_retrieve:
            with patch('sbcman.services.updater.WheelInstaller') as mock_installer:
                # Setup mocks
                mock_retrieve.side_effect = create_mock_file
                mock_installer.return_value.install_wheel.return_value = (True, "Installed")
                
                # Start update
                self.updater.start_update(download_url)
                
                # Check initial state
                self.assertTrue(self.updater.is_updating)
                initial_message = self.updater.get_message()
                self.assertIn("Downloading", initial_message)
                
                # Wait for completion
                import time
                time.sleep(0.2)
                
                # Check final state
                self.assertFalse(self.updater.is_updating)
                self.assertEqual(self.updater.get_progress(), 1.0)
                final_message = self.updater.get_message()
                self.assertIn("complete", final_message.lower())


if __name__ == '__main__':
    unittest.main()
