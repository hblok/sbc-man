# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for ArchiveExtractor

Tests for secure archive extraction with validation.
"""

import unittest
from pathlib import Path
import tempfile
import zipfile
import tarfile
import io
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sbcman.services.archive_extractor import ArchiveExtractor


class TestArchiveExtractor(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.extractor = ArchiveExtractor()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_default_values(self):
        extractor = ArchiveExtractor()
        self.assertEqual(extractor.max_file_size, 100 * 1024 * 1024)
        self.assertEqual(extractor.max_total_size, 1024 * 1024 * 1024)
        self.assertEqual(extractor.max_compression_ratio, 100)

    def test_initialization_custom_values(self):
        extractor = ArchiveExtractor(
            max_file_size=1024,
            max_total_size=2048,
            max_compression_ratio=50
        )
        self.assertEqual(extractor.max_file_size, 1024)
        self.assertEqual(extractor.max_total_size, 2048)
        self.assertEqual(extractor.max_compression_ratio, 50)

    def test_is_tar_archive_tar(self):
        archive_path = Path("test.tar")
        self.assertTrue(self.extractor._is_tar_archive(archive_path))

    def test_is_tar_archive_tar_gz(self):
        archive_path = Path("test.tar.gz")
        self.assertTrue(self.extractor._is_tar_archive(archive_path))

    def test_is_tar_archive_tar_bz2(self):
        archive_path = Path("test.tar.bz2")
        self.assertTrue(self.extractor._is_tar_archive(archive_path))

    def test_is_tar_archive_tar_xz(self):
        archive_path = Path("test.tar.xz")
        self.assertTrue(self.extractor._is_tar_archive(archive_path))

    def test_is_tar_archive_gz(self):
        archive_path = Path("test.gz")
        self.assertTrue(self.extractor._is_tar_archive(archive_path))

    def test_is_tar_archive_not_tar(self):
        archive_path = Path("test.zip")
        self.assertFalse(self.extractor._is_tar_archive(archive_path))

    def test_extract_zip_creates_directory(self):
        archive_path = self.temp_dir / "test.zip"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("test.txt", "content")
        
        dest_dir = self.temp_dir / "output"
        result = self.extractor.extract(archive_path, dest_dir)
        
        self.assertEqual(result, dest_dir)
        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / "test.txt").exists())

    def test_extract_zip_whl(self):
        archive_path = self.temp_dir / "test.whl"
        
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr("metadata.txt", "content")
        
        dest_dir = self.temp_dir / "output"
        result = self.extractor.extract(archive_path, dest_dir)
        
        self.assertEqual(result, dest_dir)
        self.assertTrue((dest_dir / "metadata.txt").exists())

    def test_extract_tar_creates_directory(self):
        archive_path = self.temp_dir / "test.tar"
        
        with tarfile.open(archive_path, 'w') as tf:
            info = tarfile.TarInfo(name="test.txt")
            info.size = 7
            tf.addfile(info, io.BytesIO(b"content"))
        
        dest_dir = self.temp_dir / "output"
        result = self.extractor.extract(archive_path, dest_dir)
        
        self.assertEqual(result, dest_dir)
        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / "test.txt").exists())

    def test_extract_unsupported_format(self):
        archive_path = self.temp_dir / "test.txt"
        archive_path.write_text("not an archive")
        
        dest_dir = self.temp_dir / "output"
        
        with self.assertRaises(ValueError):
            self.extractor.extract(archive_path, dest_dir)

    def test_validate_path_normal_path(self):
        self.assertTrue(self.extractor._validate_path("normal/path.txt"))

    def test_validate_path_absolute_path(self):
        self.assertFalse(self.extractor._validate_path("/absolute/path.txt"))

    def test_validate_path_traversal(self):
        self.assertFalse(self.extractor._validate_path("../../../etc/passwd"))

    def test_validate_path_traversal_normalized(self):
        self.assertFalse(self.extractor._validate_path("foo/../../bar"))

    def test_validate_path_null_byte(self):
        self.assertFalse(self.extractor._validate_path("path\x00file.txt"))

    def test_validate_size_within_limit(self):
        mock_info = MagicMock()
        mock_info.file_size = 1024
        mock_info.filename = "test.txt"
        
        result = self.extractor._validate_size(mock_info, 0)
        self.assertTrue(result)

    def test_validate_size_exceeds_file_limit(self):
        extractor = ArchiveExtractor(max_file_size=100)
        mock_info = MagicMock()
        mock_info.file_size = 200
        mock_info.filename = "test.txt"
        
        result = extractor._validate_size(mock_info, 0)
        self.assertFalse(result)

    def test_validate_size_exceeds_total_limit(self):
        extractor = ArchiveExtractor(max_total_size=150)
        mock_info = MagicMock()
        mock_info.file_size = 100
        mock_info.filename = "test.txt"
        
        result = extractor._validate_size(mock_info, 100)
        self.assertFalse(result)

    def test_validate_compression_normal(self):
        mock_info = MagicMock()
        mock_info.file_size = 100
        mock_info.compress_size = 50
        
        result = self.extractor._validate_compression(mock_info)
        self.assertTrue(result)

    def test_validate_compression_bomb(self):
        extractor = ArchiveExtractor(max_compression_ratio=10)
        mock_info = MagicMock()
        mock_info.file_size = 1000
        mock_info.compress_size = 10
        
        result = extractor._validate_compression(mock_info)
        self.assertFalse(result)

    def test_validate_compression_zero_compressed(self):
        mock_info = MagicMock()
        mock_info.file_size = 100
        mock_info.compress_size = 0
        
        result = self.extractor._validate_compression(mock_info)
        self.assertTrue(result)

    def test_secure_filter_absolute_path(self):
        mock_tarinfo = MagicMock()
        mock_tarinfo.name = "/absolute/path"
        
        with self.assertRaises(tarfile.ExtractError):
            self.extractor.secure_filter(mock_tarinfo, "/dest")

    def test_secure_filter_traversal(self):
        mock_tarinfo = MagicMock()
        mock_tarinfo.name = "../etc/passwd"
        
        with self.assertRaises(tarfile.ExtractError):
            self.extractor.secure_filter(mock_tarinfo, "/dest")

    def test_secure_filter_symlink(self):
        mock_tarinfo = MagicMock()
        mock_tarinfo.name = "link"
        mock_tarinfo.issym.return_value = True
        
        with self.assertRaises(tarfile.ExtractError):
            self.extractor.secure_filter(mock_tarinfo, "/dest")

    def test_secure_filter_normal_file(self):
        mock_tarinfo = MagicMock()
        mock_tarinfo.name = "normal/file.txt"
        mock_tarinfo.issym.return_value = False
        mock_tarinfo.islnk.return_value = False
        mock_tarinfo.isdev.return_value = False
        mock_tarinfo.ischr.return_value = False
        mock_tarinfo.isblk.return_value = False
        
        result = self.extractor.secure_filter(mock_tarinfo, "/dest")
        self.assertEqual(result, mock_tarinfo)

    def test_get_secure_tar_members_excludes_absolute(self):
        mock_tar = MagicMock()
        mock_member = MagicMock()
        mock_member.name = "/absolute/path"
        mock_tar.getmembers.return_value = [mock_member]
        
        result = self.extractor._get_secure_tar_members(mock_tar)
        self.assertEqual(len(result), 0)

    def test_get_secure_tar_members_excludes_symlink(self):
        mock_tar = MagicMock()
        mock_member = MagicMock()
        mock_member.name = "link"
        mock_member.issym.return_value = True
        mock_member.islnk.return_value = False
        mock_member.isdev.return_value = False
        mock_member.ischr.return_value = False
        mock_member.isblk.return_value = False
        mock_tar.getmembers.return_value = [mock_member]
        
        result = self.extractor._get_secure_tar_members(mock_tar)
        self.assertEqual(len(result), 0)

    def test_get_secure_tar_members_includes_normal(self):
        mock_tar = MagicMock()
        mock_member = MagicMock()
        mock_member.name = "file.txt"
        mock_member.issym.return_value = False
        mock_member.islnk.return_value = False
        mock_member.isdev.return_value = False
        mock_member.ischr.return_value = False
        mock_member.isblk.return_value = False
        mock_tar.getmembers.return_value = [mock_member]
        
        result = self.extractor._get_secure_tar_members(mock_tar)
        self.assertEqual(len(result), 1)