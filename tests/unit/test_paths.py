# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for AppPaths

Tests for application paths management and directory creation.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from sbcman.hardware.paths import AppPaths


class TestAppPaths(unittest.TestCase):
    """Test cases for AppPaths."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_app_paths_default_initialization(self):
        """Test AppPaths initialization with default values."""
        app_paths = AppPaths()
        
        # Verify default paths
        self.assertIsInstance(app_paths.base_dir, Path)
        self.assertIsInstance(app_paths.home, Path)
        self.assertIsInstance(app_paths.temp_dir, Path)
        
        # Verify specific path properties
        self.assertEqual(app_paths.config_dir, Path(".") / "config")
        self.assertEqual(app_paths.data_dir, Path(".") / "data")

    def test_app_paths_custom_initialization(self):
        """Test AppPaths initialization with custom paths."""
        custom_base = self.temp_dir / "base"
        custom_home = self.temp_dir / "home"
        
        app_paths = AppPaths(custom_base, custom_home)
        
        # Verify custom paths
        self.assertEqual(app_paths.base_dir, custom_base)
        self.assertEqual(app_paths.home, custom_home)

    def test_games_directory_path(self):
        """Test games directory path calculation."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        
        expected_games_dir = self.temp_dir / "games"
        self.assertEqual(app_paths.games_dir, expected_games_dir)

    def test_downloads_directory_path(self):
        """Test downloads directory path calculation."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        
        expected_downloads_dir = self.temp_dir / "games" / "downloads"
        self.assertEqual(app_paths.downloads_dir, expected_downloads_dir)

    def test_config_paths(self):
        """Test configuration related paths."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        
        # Test config directory and subdirectories
        self.assertEqual(app_paths.config_dir, self.temp_dir / "config")
        self.assertEqual(app_paths.config_devices, self.temp_dir / "config" / "devices")
        self.assertEqual(app_paths.config_os, self.temp_dir / "config" / "os")
        self.assertEqual(app_paths.config_input_mappings, self.temp_dir / "config" / "input_mappings")

    def test_data_paths(self):
        """Test data related paths."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        
        # Test data directory and subdirectories
        self.assertEqual(app_paths.data_dir, self.temp_dir / "data")
        self.assertEqual(app_paths.data_games_dir, self.temp_dir / "data" / "games")
        self.assertEqual(app_paths.games_installed, self.temp_dir / "data" / "games" / "installed.json")
        self.assertEqual(app_paths.games_available, self.temp_dir / "data" / "games" / "available.json")

    def test_temp_directory_creation(self):
        """Test that temporary directory is created."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        
        # Verify temp directory exists
        self.assertTrue(app_paths.temp_dir.exists())
        self.assertTrue(app_paths.temp_dir.is_dir())

    def test_input_overrides_path(self):
        """Test input overrides path."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        
        expected_path = self.temp_dir / "input_overrides"
        self.assertEqual(app_paths.input_overrides, expected_path)

    def test_src_config_directory(self):
        """Test source configuration directory path."""
        app_paths = AppPaths(self.temp_dir, self.temp_dir)
        
        # Should point to the config directory relative to source code
        self.assertTrue(app_paths.src_config_dir.name == "config")
        self.assertTrue("sbcman" in str(app_paths.src_config_dir))


if __name__ == '__main__':
    unittest.main()