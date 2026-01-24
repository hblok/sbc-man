# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit Tests for Updater Service

Tests the self-update functionality including version checking,
downloading, and installation methods.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

import sbcman.services.updater
import sbcman.services.config_manager
import sbcman.path.paths


class TestUpdaterService(unittest.TestCase):
    """Test cases for UpdaterService."""

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

    def test_init(self):
        """Test updater service initialization."""
        self.assertEqual(self.updater.current_version, "")
        self.assertEqual(self.updater.update_repo_url, "https://github.com/hblok/sbc-man")
        self.mock_config.get.assert_called_with("update.repository_url")

    def test_compare_versions_newer(self):
        """Test version comparison with newer version."""
        self.assertTrue(self.updater._compare_versions("1.0.0", "1.0.1"))
        self.assertTrue(self.updater._compare_versions("1.0.0", "1.1.0"))
        self.assertTrue(self.updater._compare_versions("1.0.0", "2.0.0"))

    def test_compare_versions_same(self):
        """Test version comparison with same version."""
        self.assertFalse(self.updater._compare_versions("1.0.0", "1.0.0"))

    def test_compare_versions_older(self):
        """Test version comparison with older version."""
        self.assertFalse(self.updater._compare_versions("1.0.1", "1.0.0"))
        self.assertFalse(self.updater._compare_versions("1.1.0", "1.0.0"))

    def test_compare_versions_different_length(self):
        """Test version comparison with different length versions."""
        self.assertTrue(self.updater._compare_versions("1.0", "1.0.1"))
        self.assertFalse(self.updater._compare_versions("1.0.1", "1.0"))

    def test_compare_versions_invalid_format(self):
        """Test version comparison with invalid format."""
        self.assertTrue(self.updater._compare_versions("invalid", "1.0.1"))

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_success(self, mock_urlopen):
        """Test successful update checking."""
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
        
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertTrue(update_available)
        self.assertEqual(latest_version, "1.0.1")
        self.assertIsNotNone(download_url)
        self.assertTrue(download_url.endswith(".whl"))

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_no_update_available(self, mock_urlopen):
        """Test update checking when no new version is available."""
        self.updater.current_version = "1.0.1"
        
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
        
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertFalse(update_available)
        self.assertEqual(latest_version, "1.0.1")
        self.assertIsNotNone(download_url)

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_no_version_tag(self, mock_urlopen):
        """Test update checking when no version tag is found."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "tag_name": "",
            "assets": []
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertFalse(update_available)
        self.assertIsNone(latest_version)
        self.assertIsNone(download_url)

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_no_wheel_file(self, mock_urlopen):
        """Test update checking when no wheel file is found."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "tag_name": "v1.0.1",
            "assets": [
                {
                    "name": "source.tar.gz",
                    "browser_download_url": "https://github.com/hblok/sbc-man/releases/download/v1.0.1/source.tar.gz"
                }
            ]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertFalse(update_available)
        self.assertIsNone(latest_version)
        self.assertIsNone(download_url)

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_network_error(self, mock_urlopen):
        """Test update checking with network error."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Network error")
        
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertFalse(update_available)
        self.assertIsNone(latest_version)
        self.assertIsNone(download_url)

    @patch('sbcman.services.updater.urllib.request.urlopen')
    def test_check_for_updates_json_decode_error(self, mock_urlopen):
        """Test update checking with invalid JSON response."""
        mock_response = Mock()
        mock_response.read.return_value = b"invalid json"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        update_available, latest_version, download_url = self.updater.check_for_updates()
        
        self.assertFalse(update_available)
        self.assertIsNone(latest_version)
        self.assertIsNone(download_url)

    @patch('sbcman.services.updater.urllib.request.urlretrieve')
    def test_download_update_success(self, mock_urlretrieve):
        """Test successful update download."""
        download_url = "https://example.com/test.whl"
        
        def mock_urlretrieve_side_effect(url, filename):
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
        import urllib.error
        mock_urlretrieve.side_effect = urllib.error.URLError("Download failed")
        
        result = self.updater.download_update("https://example.com/test.whl")
        
        self.assertIsNone(result)

    def test_download_update_invalid_url(self):
        """Test download update with invalid URL."""
        result = self.updater.download_update("ftp://example.com/test.whl")
        
        self.assertIsNone(result)

    @patch('sbcman.services.updater.WheelInstaller')
    def test_install_update_success(self, mock_wheel_installer_class):
        """Test successful update installation."""
        mock_installer = Mock()
        mock_installer.install_wheel.return_value = (True, "Installation successful")
        mock_wheel_installer_class.return_value = mock_installer
        
        wheel_path = Path("test.whl")
        success, message = self.updater.install_update(wheel_path)
        
        self.assertTrue(success)
        self.assertIn("successful", message.lower())
        mock_installer.install_wheel.assert_called_once_with(wheel_path)

    @patch('sbcman.services.updater.WheelInstaller')
    def test_install_update_failure(self, mock_wheel_installer_class):
        """Test failed update installation."""
        mock_installer = Mock()
        mock_installer.install_wheel.return_value = (False, "Installation failed")
        mock_wheel_installer_class.return_value = mock_installer
        
        wheel_path = Path("test.whl")
        success, message = self.updater.install_update(wheel_path)
        
        self.assertFalse(success)
        self.assertIn("failed", message.lower())
        mock_installer.install_wheel.assert_called_once_with(wheel_path)

    def test_cleanup_temp_files_success(self):
        """Test successful cleanup of temporary files."""
        temp_dir = self.mock_paths.temp_dir / "updates"
        temp_dir.mkdir(parents=True, exist_ok=True)
        test_file = temp_dir / "test.txt"
        test_file.touch()
        
        self.assertTrue(test_file.exists())
        
        self.updater.cleanup_temp_files()
        
        self.assertFalse(temp_dir.exists())

    def test_cleanup_temp_files_no_directory(self):
        """Test cleanup when temp directory doesn't exist."""
        self.updater.cleanup_temp_files()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.mock_paths.temp_dir.exists():
            shutil.rmtree(self.mock_paths.temp_dir)