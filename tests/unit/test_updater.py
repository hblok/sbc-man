"""
Unit Tests for Updater Service

Tests the self-update functionality including version checking,
downloading, and installation methods.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

from sbcman.services.updater import UpdaterService
from sbcman.models.config_manager import ConfigManager
from sbcman.hardware.paths import AppPaths


class TestUpdaterService(unittest.TestCase):
    """Test cases for UpdaterService."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_config = Mock(spec=ConfigManager)
        self.mock_paths = Mock(spec=AppPaths)
        self.mock_paths.temp_dir = Path(tempfile.mkdtemp())
        
        # Configure mock config
        self.mock_config.get.return_value = "https://github.com/hblok/sbc-man"
        
        # Create updater service
        self.updater = UpdaterService(self.mock_config, self.mock_paths)

    def test_init(self):
        """Test updater service initialization."""
        self.assertEqual(self.updater.current_version, "1.0.0")
        self.assertEqual(self.updater.update_repo_url, "https://github.com/hblok/sbc-man")
        self.mock_config.get.assert_called_with(
            "update.repository_url", 
            "https://github.com/hblok/sbc-man"
        )

    def test_compare_versions(self):
        """Test version comparison logic."""
        # Test newer version
        self.assertTrue(self.updater._compare_versions("1.0.0", "1.0.1"))
        self.assertTrue(self.updater._compare_versions("1.0.0", "1.1.0"))
        self.assertTrue(self.updater._compare_versions("1.0.0", "2.0.0"))
        
        # Test same version
        self.assertFalse(self.updater._compare_versions("1.0.0", "1.0.0"))
        
        # Test older version
        self.assertFalse(self.updater._compare_versions("1.0.1", "1.0.0"))
        self.assertFalse(self.updater._compare_versions("1.1.0", "1.0.0"))
        
        # Test different length versions
        self.assertTrue(self.updater._compare_versions("1.0", "1.0.1"))
        self.assertFalse(self.updater._compare_versions("1.0.1", "1.0"))

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_success(self, mock_urlopen):
        """Test successful update checking."""
        # Mock GitHub API response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "tag_name": "v1.0.1",
            "assets": [
                {
                    "name": "sbc_man-1.0.1-py3-none-any.whl",
                    "browser_download_url": "https://github.com/hblok/sbc-man/releases/download/v1.0.1/sbc_man-1.0.1-py3-none-any.whl"
                }
            ]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Test update checking
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertTrue(update_available)
        self.assertEqual(latest_version, "1.0.1")
        self.assertIsNotNone(download_url)
        self.assertTrue(download_url.endswith(".whl"))

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_no_new_version(self, mock_urlopen):
        """Test update checking when no new version is available."""
        # Mock GitHub API response with same version
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "tag_name": "v1.0.0",
            "assets": [
                {
                    "name": "sbc_man-1.0.0-py3-none-any.whl",
                    "browser_download_url": "https://github.com/hblok/sbc-man/releases/download/v1.0.0/sbc_man-1.0.0-py3-none-any.whl"
                }
            ]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Test update checking
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertFalse(update_available)
        self.assertEqual(latest_version, "1.0.0")

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_network_error(self, mock_urlopen):
        """Test update checking with network error."""
        # Mock network error
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Network error")
        
        # Test update checking
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertFalse(update_available)
        self.assertIsNone(latest_version)
        self.assertIsNone(download_url)

    @patch('sbcman.services.updater.urllib.request.urlretrieve')
    def test_download_update_success(self, mock_urlretrieve):
        """Test successful update download."""
        # Create temp directory
        temp_dir = self.mock_paths.temp_dir / "updates"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock successful download
        download_url = "https://example.com/test.whl"
        expected_path = temp_dir / "test.whl"
        
        # Create the file for the mock to find
        expected_path.touch()
        expected_path.write_text("dummy content")  # Add content so file is not empty
        
        # Mock urlretrieve to create the file
        def mock_urlretrieve_side_effect(url, filename):
            # Create the file at the expected location
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("dummy content")
        
        mock_urlretrieve.side_effect = mock_urlretrieve_side_effect
        
        result = self.updater.download_update(download_url)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "test.whl")

    @patch('sbcman.services.updater.urllib.request.urlretrieve')
    def test_download_update_failure(self, mock_urlretrieve):
        """Test failed update download."""
        # Mock download failure
        import urllib.error
        mock_urlretrieve.side_effect = urllib.error.URLError("Download failed")
        
        result = self.updater.download_update("https://example.com/test.whl")
        
        self.assertIsNone(result)

    @patch('sbcman.services.updater.subprocess.run')
    def test_find_pip_command_success(self, mock_run):
        """Test successful pip command detection."""
        # Mock successful pip command
        mock_run.return_value.returncode = 0
        
        result = self.updater._find_pip_command()
        
        self.assertEqual(result, "pip")

    @patch('sbcman.services.updater.subprocess.run')
    def test_find_pip_command_failure(self, mock_run):
        """Test pip command detection failure."""
        # Mock failed pip command
        mock_run.side_effect = FileNotFoundError()
        
        result = self.updater._find_pip_command()
        
        self.assertIsNone(result)

    @patch('sbcman.services.updater.subprocess.run')
    def test_install_with_pip_success(self, mock_run):
        """Test successful pip installation."""
        # Mock successful pip installation
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        with patch.object(self.updater, '_find_pip_command', return_value='pip'):
            success, message = self.updater._install_with_pip(Path("test.whl"))
        
        self.assertTrue(success)
        self.assertIn("successful", message.lower())

    @patch('sbcman.services.updater.subprocess.run')
    def test_install_with_pip_failure(self, mock_run):
        """Test failed pip installation."""
        # Mock failed pip installation
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Installation failed"
        
        with patch.object(self.updater, '_find_pip_command', return_value='pip'):
            success, message = self.updater._install_with_pip(Path("test.whl"))
        
        self.assertFalse(success)
        self.assertIn("failed", message.lower())

    @patch('sbcman.services.updater.zipfile.ZipFile')
    def test_install_with_extraction_success(self, mock_zipfile):
        """Test successful manual extraction installation."""
        # Mock successful extraction
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        # Create mock wheel path
        wheel_path = Path("test.whl")
        
        success, message = self.updater._install_with_extraction(wheel_path)
        
        self.assertTrue(success)
        self.assertIn("successful", message.lower())

    @patch('sbcman.services.updater.zipfile.ZipFile')
    def test_install_with_extraction_failure(self, mock_zipfile):
        """Test failed manual extraction installation."""
        # Mock extraction failure
        import zipfile
        mock_zipfile.side_effect = zipfile.BadZipFile("Invalid zip")
        
        wheel_path = Path("test.whl")
        
        success, message = self.updater._install_with_extraction(wheel_path)
        
        self.assertFalse(success)
        self.assertIn("not a valid zip", message.lower())

    def test_cleanup_temp_files(self):
        """Test cleanup of temporary files."""
        # Create some temp files
        temp_dir = self.mock_paths.temp_dir / "updates"
        temp_dir.mkdir(parents=True, exist_ok=True)
        test_file = temp_dir / "test.txt"
        test_file.touch()
        
        # Verify file exists
        self.assertTrue(test_file.exists())
        
        # Cleanup
        self.updater.cleanup_temp_files()
        
        # Verify cleanup (should not raise exception even if cleanup fails)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        if self.mock_paths.temp_dir.exists():
            shutil.rmtree(self.mock_paths.temp_dir)


if __name__ == '__main__':
    unittest.main()