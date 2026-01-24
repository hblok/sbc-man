# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for GameInstaller

Tests for game installation from archives and wheel files.
"""

import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

from sbcman.services.install_game import GameInstaller
from sbcman.proto import game_pb2
from sbcman.path.paths import AppPaths


class TestGameInstaller(unittest.TestCase):
    """Test cases for GameInstaller."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.games_dir = self.temp_dir / "games"
        self.games_dir.mkdir(exist_ok=True)

        self.app_paths = AppPaths(self.temp_dir, self.temp_dir)
        self.game_installer = GameInstaller(None, self.app_paths)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_game_installer_initialization(self):
        """Test game installer initialization."""
        self.assertIsNotNone(self.game_installer.archive_extractor)
        self.assertIsNone(self.game_installer.config)
        self.assertIsNotNone(self.game_installer.app_paths)

    def test_extract_game_zip(self):
        """Test extracting a ZIP game archive."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.download_url = "https://example.com/test-game.zip"

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "test-game.zip"

            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("main.py", "print('Hello, World!')")

            install_dir = self.game_installer._extract_archive(zip_path, game)

            self.assertTrue(install_dir.exists())
            entry_point = install_dir / "main.py"
            self.assertTrue(entry_point.exists())

    def test_install_game_with_zip(self):
        """Test installing a game from ZIP archive."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.name = "Test Game"
        game.download_url = "https://example.com/test-game.zip"

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "test-game.zip"

            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("main.py", "print('Hello, World!')")

            install_dir = self.game_installer.install_game(zip_path, game)

            self.assertTrue(install_dir.exists())
            self.assertEqual(install_dir.name, game.id)

    @patch('sbcman.services.wheel_installer.WheelInstaller')
    def test_install_wheel_success(self, mock_wheel_installer_class):
        """Test installing a wheel file successfully."""
        mock_installer = Mock()
        mock_installer.install_wheel.return_value = (True, "Installed successfully")
        mock_wheel_installer_class.return_value = mock_installer

        game = game_pb2.Game()
        game.id = "test-game"
        game.entry_point = "main"

        config = Mock()
        config.get.return_value = True

        installer = GameInstaller(config, self.app_paths)

        with tempfile.TemporaryDirectory() as temp_dir:
            wheel_path = Path(temp_dir) / "test-game.whl"
            wheel_path.write_text("wheel content")

            # Create the entry point file to simulate a successful installation
            self.games_dir.mkdir(exist_ok=True)
            entry_point = self.games_dir / game.entry_point
            entry_point.write_text("# Entry point")

            with patch('sbcman.services.install_game.site.getsitepackages') as mock_getsitepackages:
                mock_getsitepackages.return_value = [str(self.games_dir)]
                
                install_dir = installer.install_game(wheel_path, game)
                
                # Verify that it returns the site-packages directory
                self.assertEqual(install_dir, self.games_dir)
                # Verify that the wheel installer was called
                mock_installer.install_wheel.assert_called_once_with(wheel_path)

    @patch('sbcman.services.wheel_installer.WheelInstaller')
    def test_install_wheel_failure(self, mock_wheel_installer_class):
        """Test installing a wheel file when installation fails."""
        mock_installer = Mock()
        mock_installer.install_wheel.return_value = (False, "Installation failed")
        mock_wheel_installer_class.return_value = mock_installer

        game = game_pb2.Game()
        game.entry_point = "main"

        config = Mock()
        config.get.return_value = True

        installer = GameInstaller(config, self.app_paths)

        with tempfile.TemporaryDirectory() as temp_dir:
            wheel_path = Path(temp_dir) / "test-game.whl"
            wheel_path.write_text("wheel content")

            with self.assertRaises(Exception) as context:
                installer.install_game(wheel_path, game)

            self.assertIn("Wheel installation failed", str(context.exception))

    def test_get_install_as_pip_with_config(self):
        """Test getting install_as_pip setting with config."""
        config = Mock()
        config.get.return_value = True

        installer = GameInstaller(config, self.app_paths)
        self.assertTrue(installer._get_install_as_pip())

    def test_get_install_as_pip_without_config(self):
        """Test getting install_as_pip setting without config."""
        installer = GameInstaller(None, self.app_paths)
        self.assertFalse(installer._get_install_as_pip())

    def test_get_install_base_dir_with_app_paths(self):
        """Test getting install base directory with app_paths."""
        installer = GameInstaller(None, self.app_paths)
        self.assertEqual(installer._get_install_base_dir(), self.app_paths.games_dir)

    def test_get_install_base_dir_with_portmaster_config(self):
        """Test getting install base directory with portmaster config."""
        config = Mock()
        config.get.side_effect = lambda key, default=False: {
            "install.add_portmaster_entry": True,
            "install.portmaster_base_dir": "/custom/games"
        }.get(key, default)

        installer = GameInstaller(config, self.app_paths)
        base_dir = installer._get_install_base_dir()
        self.assertEqual(base_dir, Path("/custom/games"))

    def test_get_install_base_dir_fallback(self):
        """Test getting install base directory fallback."""
        installer = GameInstaller(None, None)
        base_dir = installer._get_install_base_dir()
        self.assertEqual(base_dir, Path.cwd())

    def test_get_portmaster_image_dir_with_config(self):
        """Test getting portmaster image directory with config."""
        config = Mock()
        config.get.return_value = "/custom/images"
        installer = GameInstaller(config, self.app_paths)
        image_dir = installer._get_portmaster_image_dir()
        self.assertEqual(image_dir, Path("/custom/images"))

    def test_get_portmaster_image_dir_without_config(self):
        """Test getting portmaster image directory without config."""
        installer = GameInstaller(None, self.app_paths)
        image_dir = installer._get_portmaster_image_dir()
        self.assertIsNone(image_dir)

    def test_copy_post_install_files_script_only(self):
        """Test copying only script file."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.startScript = "run.sh"
        
        # Create a temporary install directory with script file
        install_dir = self.temp_dir / "install"
        install_dir.mkdir()
        script_file = install_dir / "run.sh"
        script_file.write_text("#!/bin/bash\necho test")
        
        # Copy the file
        self.game_installer._copy_post_install_files(install_dir, game)
        
        # Verify script was copied to games_dir
        dest_script = self.games_dir / "run.sh"
        self.assertTrue(dest_script.exists())
        self.assertEqual(dest_script.read_text(), "#!/bin/bash\necho test")

    def test_copy_post_install_files_icon_only(self):
        """Test copying only icon file."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.icon = "icon.png"
        
        # Create a temporary install directory with icon file
        install_dir = self.temp_dir / "install"
        install_dir.mkdir()
        icon_file = install_dir / "icon.png"
        icon_file.write_text("fake png content")
        
        # Create image directory in config
        image_dir = self.temp_dir / "images"
        image_dir.mkdir()
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            "install.portmaster_image_dir": str(image_dir)
        }.get(key, default)
        
        installer = GameInstaller(config, self.app_paths)
        installer._copy_post_install_files(install_dir, game)
        
        # Verify icon was copied to image directory
        dest_icon = image_dir / "icon.png"
        self.assertTrue(dest_icon.exists())
        self.assertEqual(dest_icon.read_text(), "fake png content")

    def test_copy_post_install_files_both(self):
        """Test copying both script and icon files."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.startScript = "run.sh"
        game.icon = "icon.png"
        
        # Create a temporary install directory with both files
        install_dir = self.temp_dir / "install"
        install_dir.mkdir()
        (install_dir / "run.sh").write_text("#!/bin/bash\necho test")
        (install_dir / "icon.png").write_text("fake png content")
        
        # Create image directory in config
        image_dir = self.temp_dir / "images"
        image_dir.mkdir()
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            "install.portmaster_image_dir": str(image_dir)
        }.get(key, default)
        
        installer = GameInstaller(config, self.app_paths)
        installer._copy_post_install_files(install_dir, game)
        
        # Verify both files were copied
        dest_script = self.games_dir / "run.sh"
        dest_icon = image_dir / "icon.png"
        self.assertTrue(dest_script.exists())
        self.assertTrue(dest_icon.exists())

    def test_copy_post_install_files_missing_files(self):
        """Test copying post-install files when source files don't exist."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.startScript = "run.sh"
        game.icon = "icon.png"
        
        # Create empty install directory
        install_dir = self.temp_dir / "install"
        install_dir.mkdir()
        
        # Create image directory in config
        image_dir = self.temp_dir / "images"
        image_dir.mkdir()
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            "install.portmaster_image_dir": str(image_dir)
        }.get(key, default)
        
        installer = GameInstaller(config, self.app_paths)
        # Should not raise exception, just log warnings
        installer._copy_post_install_files(install_dir, game)

    def test_copy_post_install_files_no_config(self):
        """Test copying icon when portmaster image dir is not configured."""
        game = game_pb2.Game()
        game.id = "test-game"
        game.icon = "icon.png"
        
        # Create a temporary install directory with icon file
        install_dir = self.temp_dir / "install"
        install_dir.mkdir()
        (install_dir / "icon.png").write_text("fake png content")
        
        # No config for image directory
        installer = GameInstaller(None, self.app_paths)
        # Should not raise exception, just log warning
        installer._copy_post_install_files(install_dir, game)

    def test_copy_post_install_files_none_values(self):
        """Test copying when script and icon are None."""
        game = game_pb2.Game()
        game.id = "test-game"
        
        # Create a temporary install directory
        install_dir = self.temp_dir / "install"
        install_dir.mkdir()
        
        # Should not raise exception, should return early
        self.game_installer._copy_post_install_files(install_dir, game)