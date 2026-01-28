# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for DevicePaths

Tests for mounted filesystem detection and path management.
"""

import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch, mock_open

from sbcman.path.device import DevicePaths


class TestDevicePaths(unittest.TestCase):

    def setUp(self):
        self.device_paths = DevicePaths()

    def test_get_mounted_filesystems_empty_file(self):
        mock_data = ""
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_excludes_sys_fs(self):
        mock_data = "sysfs /sys sysfs rw 0 0\nproc /proc proc rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_excludes_tmpfs(self):
        mock_data = "tmpfs /run tmpfs rw 0 0\ndevtmpfs /dev devtmpfs rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_excludes_cgroup(self):
        mock_data = "cgroup /sys/fs/cgroup cgroup2 rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_excludes_special_fs(self):
        mock_data = "debugfs /sys/kernel/debug debugfs rw 0 0\ntracefs /sys/kernel/tracing tracefs rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_excludes_system_prefixes(self):
        mock_data = "/dev/sda1 /dev/sda1 ext4 rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_valid_mount(self):
        mock_data = "/dev/sda1 /mnt ext4 rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'is_dir', return_value=True):
                    result = self.device_paths.get_mounted_filesystems()
                    self.assertEqual(len(result), 1)
                    self.assertEqual(str(result[0]), '/mnt')

    def test_get_mounted_filesystems_multiple_mounts(self):
        mock_data = "/dev/sda1 /mnt/data ext4 rw 0 0\n/dev/sda2 /mnt/backup xfs rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'is_dir', return_value=True):
                    result = self.device_paths.get_mounted_filesystems()
                    self.assertEqual(len(result), 2)
                    self.assertEqual(str(result[0]), '/mnt/data')
                    self.assertEqual(str(result[1]), '/mnt/backup')

    def test_get_mounted_filesystems_filters_non_existent(self):
        mock_data = "/dev/sda1 /nonexistent ext4 rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            with patch.object(Path, 'exists', return_value=False):
                result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_filters_non_directory(self):
        mock_data = "/dev/sda1 /mnt/file ext4 rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'is_dir', return_value=False):
                    result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])

    def test_get_mounted_filesystems_malformed_line(self):
        mock_data = "malformed line\n/dev/sda1 /mnt ext4 rw 0 0\n"
        with patch('builtins.open', mock_open(read_data=mock_data)):
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'is_dir', return_value=True):
                    result = self.device_paths.get_mounted_filesystems()
                    self.assertEqual(len(result), 1)

    def test_get_mounted_filesystems_file_not_found(self):
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = self.device_paths.get_mounted_filesystems()
            self.assertEqual(result, [])