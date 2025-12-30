# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for File Operations Service

Tests for file operations including copying, moving, and directory management.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from sbcman.services.file_ops import FileOps


class TestFileOps(unittest.TestCase):
    """Test cases for FileOps service."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.file_ops = FileOps()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_ensure_directory(self):
        """Test ensuring a directory exists."""
        new_dir = self.temp_dir / "new_directory"
        
        # Ensure directory exists
        result = self.file_ops.ensure_directory(new_dir)
        
        # Verify directory was created
        self.assertTrue(result)
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())

    def test_copy_file_source_not_exists(self):
        """Test copying a file that doesn't exist."""
        source_file = self.temp_dir / "nonexistent.txt"
        dest_file = self.temp_dir / "dest.txt"
        
        # Should return False for non-existent source
        result = self.file_ops.copy_file(source_file, dest_file)
        self.assertFalse(result)

    def test_create_directory(self):
        """Test creating a directory."""
        new_dir = self.temp_dir / "new_directory"
        
        # Create directory
        result = self.file_ops.create_directory(new_dir)
        
        # Verify directory was created
        self.assertTrue(result)
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())

    def test_create_directory_already_exists(self):
        """Test creating a directory that already exists."""
        existing_dir = self.temp_dir / "existing"
        existing_dir.mkdir()
        
        # Should still return True for existing directory
        result = self.file_ops.create_directory(existing_dir)
        self.assertTrue(result)

    def test_delete_file(self):
        """Test deleting a file."""
        # Create a file to delete
        test_file = self.temp_dir / "to_delete.txt"
        test_file.write_text("Delete me")
        
        # Delete the file
        result = self.file_ops.delete_file(test_file)
        
        # Verify file was deleted
        self.assertTrue(result)
        self.assertFalse(test_file.exists())

    def test_delete_file_not_exists(self):
        """Test deleting a file that doesn't exist."""
        non_existent = self.temp_dir / "nonexistent.txt"
        
        # Should return False for non-existent file
        result = self.file_ops.delete_file(non_existent)
        self.assertFalse(result)

    def test_delete_directory(self):
        """Test deleting a directory."""
        # Create a directory with content
        test_dir = self.temp_dir / "to_delete"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("Content")
        
        # Delete the directory
        result = self.file_ops.delete_directory(test_dir)
        
        # Verify directory was deleted
        self.assertTrue(result)
        self.assertFalse(test_dir.exists())

    def test_file_exists(self):
        """Test checking if file exists."""
        # Create a file
        test_file = self.temp_dir / "exists.txt"
        test_file.write_text("Content")
        
        # Test existing file
        self.assertTrue(self.file_ops.file_exists(test_file))
        
        # Test non-existent file
        non_existent = self.temp_dir / "nonexistent.txt"
        self.assertFalse(self.file_ops.file_exists(non_existent))

    def test_get_file_size(self):
        """Test getting file size."""
        # Create a file with known content
        test_file = self.temp_dir / "size_test.txt"
        content = "This is test content for size checking"
        test_file.write_text(content)
        
        # Get file size
        size = self.file_ops.get_file_size(test_file)
        
        # Verify size matches content length
        self.assertEqual(size, len(content.encode()))

    def test_get_file_size_not_exists(self):
        """Test getting size of non-existent file."""
        non_existent = self.temp_dir / "nonexistent.txt"
        
        # Should return 0 for non-existent file
        size = self.file_ops.get_file_size(non_existent)
        self.assertEqual(size, 0)

    def test_list_directory(self):
        """Test listing directory contents."""
        # Create directory with files
        test_dir = self.temp_dir / "list_test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("Content 1")
        (test_dir / "file2.txt").write_text("Content 2")
        sub_dir = test_dir / "subdir"
        sub_dir.mkdir()
        
        # List directory
        contents = self.file_ops.list_directory(test_dir)
        
        # Verify contents (order not guaranteed)
        self.assertEqual(len(contents), 3)
        file_names = [item.name for item in contents]
        self.assertIn("file1.txt", file_names)
        self.assertIn("file2.txt", file_names)
        self.assertIn("subdir", file_names)

    def test_list_directory_not_exists(self):
        """Test listing non-existent directory."""
        non_existent = self.temp_dir / "nonexistent"
        
        # Should return empty list for non-existent directory
        contents = self.file_ops.list_directory(non_existent)
        self.assertEqual(contents, [])

    @patch('shutil.disk_usage')
    def test_get_disk_usage(self, mock_disk_usage):
        """Test getting disk usage information."""
        # Mock disk usage
        mock_usage = Mock()
        mock_usage.total = 1000000000  # 1GB
        mock_usage.used = 500000000     # 500MB
        mock_usage.free = 500000000     # 500MB
        mock_disk_usage.return_value = mock_usage
        
        # Get disk usage
        usage = self.file_ops.get_disk_usage(self.temp_dir)
        
        # Verify results
        self.assertEqual(usage['total'], 1000000000)
        self.assertEqual(usage['used'], 500000000)
        self.assertEqual(usage['free'], 500000000)


if __name__ == '__main__':
    unittest.main()