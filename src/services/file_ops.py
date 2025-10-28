"""
File Operations Service

Provides pathlib-based file operations with error handling.

Based on: docs/code/class_services_file_ops.txt
"""

import shutil
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileOps:
    """
    File operations service using pathlib.
    
    Provides safe file operations with proper error handling
    and logging.
    """

    @staticmethod
    def ensure_directory(path: Path) -> bool:
        """
        Create directory if it doesn't exist.
        
        Args:
            path: Directory path to create
            
        Returns:
            bool: True if directory exists or was created
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False

    @staticmethod
    def copy_file(src: Path, dst: Path) -> bool:
        """
        Copy file from source to destination.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Returns:
            bool: True if copy succeeded
        """
        try:
            # Ensure destination directory exists
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src, dst)
            logger.info(f"Copied file: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy {src} to {dst}: {e}")
            return False

    @staticmethod
    def move_file(src: Path, dst: Path) -> bool:
        """
        Move file from source to destination.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Returns:
            bool: True if move succeeded
        """
        try:
            # Ensure destination directory exists
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src), str(dst))
            logger.info(f"Moved file: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"Failed to move {src} to {dst}: {e}")
            return False

    @staticmethod
    def delete_file(path: Path) -> bool:
        """
        Delete file safely.
        
        Args:
            path: File path to delete
            
        Returns:
            bool: True if deletion succeeded
        """
        try:
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete {path}: {e}")
            return False

    @staticmethod
    def delete_directory(path: Path, recursive: bool = False) -> bool:
        """
        Delete directory.
        
        Args:
            path: Directory path to delete
            recursive: If True, delete directory and all contents
            
        Returns:
            bool: True if deletion succeeded
        """
        try:
            if not path.exists():
                logger.warning(f"Directory not found for deletion: {path}")
                return False
            
            if recursive:
                shutil.rmtree(path)
                logger.info(f"Deleted directory recursively: {path}")
            else:
                path.rmdir()
                logger.info(f"Deleted empty directory: {path}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete directory {path}: {e}")
            return False

    @staticmethod
    def read_text(path: Path, encoding: str = "utf-8") -> Optional[str]:
        """
        Read text file content.
        
        Args:
            path: File path to read
            encoding: Text encoding (default: utf-8)
            
        Returns:
            str: File content, or None if read failed
        """
        try:
            content = path.read_text(encoding=encoding)
            logger.debug(f"Read text file: {path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read {path}: {e}")
            return None

    @staticmethod
    def write_text(path: Path, content: str, encoding: str = "utf-8") -> bool:
        """
        Write text to file.
        
        Args:
            path: File path to write
            content: Text content to write
            encoding: Text encoding (default: utf-8)
            
        Returns:
            bool: True if write succeeded
        """
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            path.write_text(content, encoding=encoding)
            logger.debug(f"Wrote text file: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
            return False

    @staticmethod
    def get_size(path: Path) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            path: File path
            
        Returns:
            int: File size in bytes, or None if failed
        """
        try:
            size = path.stat().st_size
            return size
        except Exception as e:
            logger.error(f"Failed to get size of {path}: {e}")
            return None

    @staticmethod
    def exists(path: Path) -> bool:
        """
        Check if path exists.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path exists
        """
        return path.exists()

    @staticmethod
    def is_file(path: Path) -> bool:
        """
        Check if path is a file.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is a file
        """
        return path.is_file()

    @staticmethod
    def is_directory(path: Path) -> bool:
        """
        Check if path is a directory.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is a directory
        """
        return path.is_dir()