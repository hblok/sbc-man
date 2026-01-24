# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Archive Extraction Module

Provides secure extraction of zip and tar archives with validation
against path traversal, compression bombs, and other security issues.
"""

import logging
import os
import tarfile
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)


class ArchiveExtractor:
    """Handles secure extraction of zip and tar archives."""

    def __init__(
        self,
        max_file_size: int = 100 * 1024 * 1024,
        max_total_size: int = 1024 * 1024 * 1024,
        max_compression_ratio: float = 100,
    ):
        self.max_file_size = max_file_size
        self.max_total_size = max_total_size
        self.max_compression_ratio = max_compression_ratio

    def extract(self, archive_path: Path, dest_dir: Path) -> Path:
        """
        Extract archive to destination directory.

        Args:
            archive_path: Path to the archive file
            dest_dir: Directory to extract to

        Returns:
            Path to the extraction directory

        Raises:
            ValueError: If archive format is unsupported
            Exception: If extraction fails
        """
        dest_dir.mkdir(parents=True, exist_ok=True)
        suffix = archive_path.suffix.lower()

        if suffix == ".zip" or suffix == ".whl":
            self._extract_zip(archive_path, dest_dir)
        elif self._is_tar_archive(archive_path):
            self._extract_tar(archive_path, dest_dir)
        else:
            raise ValueError(
                f"Unsupported archive format: {suffix}. "
                "Supported formats: .zip, .whl, .tar, .tar.gz, .tar.bz2, .tar.xz"
            )

        logger.info(f"Extracted to {dest_dir}")
        return dest_dir

    def _is_tar_archive(self, archive_path: Path) -> bool:
        """Check if file is a tar archive."""
        suffix = archive_path.suffix.lower()
        name = archive_path.name.lower()
        return suffix in [".tar", ".gz", ".bz2", ".xz"] or name.endswith(
            (".tar.gz", ".tar.bz2", ".tar.xz")
        )

    def _extract_zip(self, archive_path: Path, dest_dir: Path) -> None:
        """Extract zip archive with security validation."""
        logger.info(f"Extracting zip file: {archive_path}")
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            safe_members = self._get_secure_zip_members(zip_ref)
            zip_ref.extractall(dest_dir, members=safe_members)  # nosec

    def _extract_tar(self, archive_path: Path, dest_dir: Path) -> None:
        """Extract tar archive with security validation."""
        logger.info(f"Extracting tar file: {archive_path}")
        with tarfile.open(archive_path, "r:*") as tar_ref:
            safe_members = self._get_secure_tar_members(tar_ref)
            tar_ref.extractall(dest_dir, members=safe_members)  # nosec

    def _get_secure_zip_members(self, zip_file: zipfile.ZipFile) -> list:
        """Get list of safe members from zip archive."""
        safe_members = []
        total_size = 0
        rejected_count = 0
        accepted_count = 0

        for member_info in zip_file.infolist():
            member_name = member_info.filename

            if not self._validate_path(member_name):
                rejected_count += 1
                continue

            if not self._validate_compression(member_info):
                rejected_count += 1
                continue

            if not self._validate_size(member_info, total_size):
                rejected_count += 1
                continue

            if not member_name.endswith("/"):
                logger.debug(f"✓ {member_name} ({member_info.file_size} bytes)")
                total_size += member_info.file_size
                accepted_count += 1

            safe_members.append(member_name)

        logger.info(f"Zip validation: {accepted_count} accepted, {rejected_count} rejected")
        return safe_members

    def _get_secure_tar_members(self, tar: tarfile.TarFile) -> list:
        """Get list of safe members from tar archive."""
        safe_members = []

        for member in tar.getmembers():
            if member.name.startswith("/"):
                logger.warning(f"Skipping absolute path: {member.name}")
                continue

            if ".." in member.name.split(os.sep):
                logger.warning(f"Skipping path traversal: {member.name}")
                continue

            if member.issym() or member.islnk():
                logger.warning(f"Skipping symlink: {member.name}")
                continue

            if member.isdev() or member.ischr() or member.isblk():
                logger.warning(f"Skipping device file: {member.name}")
                continue

            safe_members.append(member)

        return safe_members

    def _validate_path(self, member_name: str) -> bool:
        """Validate member path for security issues."""
        if member_name.startswith("/"):
            logger.warning(f"Absolute path: {member_name}")
            return False

        if ".." in member_name.split(os.sep):
            logger.warning(f"Path traversal: {member_name}")
            return False

        normalized = os.path.normpath(member_name)
        if normalized.startswith(".."):
            logger.warning(f"Normalized path traversal: {member_name}")
            return False

        if "\x00" in member_name:
            logger.warning(f"Null byte in path: {member_name}")
            return False

        return True

    def _validate_size(self, member_info: zipfile.ZipInfo, current_total: int) -> bool:
        """Validate member size."""
        if member_info.file_size > self.max_file_size:
            logger.warning(
                f"File too large ({member_info.file_size} bytes): {member_info.filename}"
            )
            return False

        if current_total + member_info.file_size > self.max_total_size:
            logger.warning(f"Total size would exceed limit: {member_info.filename}")
            return False

        return True

    def _validate_compression(self, member_info: zipfile.ZipInfo) -> bool:
        """Detect compression bombs."""
        if member_info.compress_size > 0:
            ratio = member_info.file_size / member_info.compress_size
            if ratio > self.max_compression_ratio:
                logger.warning(
                    f"Suspicious compression ratio ({ratio:.1f}x): {member_info.filename}"
                )
                return False

        return True

    def secure_filter(self, tarinfo: tarfile.TarInfo, targetpath: str) -> tarfile.TarInfo:
        """Secure filter for Python 3.12+ tar extraction."""
        if tarinfo.name.startswith("/"):
            raise tarfile.ExtractError(f"Absolute path not allowed: {tarinfo.name}")

        if ".." in tarinfo.name.split(os.sep):
            raise tarfile.ExtractError(f"Path traversal not allowed: {tarinfo.name}")

        if tarinfo.issym() or tarinfo.islnk():
            raise tarfile.ExtractError(f"Symlinks not allowed: {tarinfo.name}")

        if tarinfo.isdev() or tarinfo.ischr() or tarinfo.isblk():
            raise tarfile.ExtractError(f"Device files not allowed: {tarinfo.name}")

        return tarinfo
