# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for PortMaster

Tests for PortMaster directory detection and path management.
"""

import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock

from sbcman.services.portmaster import PortMaster
from sbcman.path.device import DevicePaths


class TestPortMaster(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_device_paths = MagicMock(spec=DevicePaths)
        self.portmaster = PortMaster(self.mock_device_paths)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        portmaster = PortMaster(self.mock_device_paths)
        self.assertEqual(portmaster.device_paths, self.mock_device_paths)

    def test_find_ports_dir_no_mounts(self):
        self.mock_device_paths.get_mounted_filesystems.return_value = []
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, Path("/"))

    def test_find_ports_dir_roms_ports_exists(self):
        mount = self.temp_dir / "mount"
        roms = mount / "roms"
        ports = roms / "ports"
        ports.mkdir(parents=True)
        (ports / "game.txt").write_text("test")
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, ports)

    def test_find_ports_dir_case_insensitive_roms(self):
        mount = self.temp_dir / "mount"
        roms = mount / "Roms"
        ports = roms / "PORTS"
        ports.mkdir(parents=True)
        (ports / "game.txt").write_text("test")
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, ports)

    def test_find_ports_dir_skips_roms_ports(self):
        mount = Path("/roms")
        ports = mount / "ports"
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, Path("/"))

    def test_find_ports_dir_skips_empty_directory(self):
        mount2 = self.temp_dir / "mount2"
        roms = mount2 / "roms"
        ports = roms / "ports"
        ports.mkdir(parents=True)
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount2]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, roms)

    def test_find_ports_dir_nonempty_directory(self):
        mount = self.temp_dir / "mount"
        roms = mount / "roms"
        ports = roms / "ports"
        ports.mkdir(parents=True)
        (ports / "test.txt").write_text("content")
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, ports)

    def test_find_ports_dir_returns_rom_base_when_no_ports(self):
        mount = self.temp_dir / "mount"
        roms = mount / "roms"
        roms.mkdir(parents=True)
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, roms)

    def test_find_ports_dir_permission_error(self):
        mount = Path("/permission")
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, Path("/"))

    def test_find_ports_dir_multiple_candidates(self):
        mount1 = self.temp_dir / "mount1"
        mount2 = self.temp_dir / "mount2"
        
        roms1 = mount1 / "roms"
        ports1 = roms1 / "ports"
        ports1.mkdir(parents=True)
        (ports1 / "game1.txt").write_text("game1")
        
        roms2 = mount2 / "roms"
        ports2 = roms2 / "PORTS"
        ports2.mkdir(parents=True)
        (ports2 / "game2.txt").write_text("game2")
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount1, mount2]
        
        result = self.portmaster.find_ports_dir()
        self.assertIn(result, [ports1, ports2])

    def test_find_game_image_dir_imgs_exists(self):
        port_base = self.temp_dir / "ports"
        imgs = port_base / "Imgs"
        imgs.mkdir(parents=True)
        
        result = self.portmaster.find_game_image_dir(port_base)
        self.assertEqual(result, imgs.resolve())

    def test_find_game_image_dir_relative_path_exists(self):
        port_base = self.temp_dir / "ports"
        port_base.mkdir(parents=True)
        imgs = self.temp_dir / "Imgs"
        imgs.mkdir(parents=True)
        
        result = self.portmaster.find_game_image_dir(port_base)
        self.assertTrue(result.exists())

    def test_find_game_image_dir_not_found(self):
        # Create a port_base in a nested directory so ../../Imgs doesn't exist
        port_base = self.temp_dir / "deep" / "nested" / "ports_no_images"
        port_base.mkdir(parents=True)
        
        result = self.portmaster.find_game_image_dir(port_base)
        self.assertEqual(result, Path("/"))

    def test_find_ports_dir_tries_multiple_port_dir_names(self):
        mount = self.temp_dir / "mount"
        roms = mount / "roms"
        ports = roms / "Ports"
        ports.mkdir(parents=True)
        (ports / "test.txt").write_text("content")
        
        self.mock_device_paths.get_mounted_filesystems.return_value = [mount]
        
        result = self.portmaster.find_ports_dir()
        self.assertEqual(result, ports)

    def test_find_game_image_dir_resolves_symlink(self):
        port_base = self.temp_dir / "ports"
        port_base.mkdir(parents=True)
        actual_imgs = self.temp_dir / "actual_images"
        actual_imgs.mkdir(parents=True)
        symlink = port_base / "Imgs"
        symlink.symlink_to(actual_imgs)
        
        result = self.portmaster.find_game_image_dir(port_base)
        self.assertTrue(result.exists())