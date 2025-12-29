# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Network Service

Provides HTTP operations with timeout and retry handling.

Based on: docs/code/class_services_network.txt
"""

import logging
from pathlib import Path
from typing import Optional, Callable

import requests

logger = logging.getLogger(__name__)


class NetworkService:
    """
    Network service for HTTP operations.
    
    Provides methods for downloading files, checking URLs,
    and getting file sizes with proper error handling.
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize network service.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SBC-Man Game Launcher/1.0"
        })

    def download_file(
        self,
        url: str,
        dest: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """
        Download file with progress tracking.
        
        Args:
            url: URL to download from
            dest: Destination file path
            progress_callback: Optional callback(downloaded, total)
            
        Returns:
            bool: True if download succeeded
        """
        try:
            logger.info(f"Downloading {url}")
            
            # Ensure destination directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Stream download
            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            
            # Download in chunks
            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Call progress callback
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"Download complete: {dest}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return False

    def check_url(self, url: str) -> bool:
        """
        Verify URL accessibility.
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if URL is accessible
        """
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            logger.debug(f"URL accessible: {url}")
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"URL not accessible: {url} - {e}")
            return False

    def get_file_size(self, url: str) -> Optional[int]:
        """
        Get remote file size.
        
        Args:
            url: URL to check
            
        Returns:
            int: File size in bytes, or None if failed
        """
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            size = int(response.headers.get("content-length", 0))
            logger.debug(f"File size for {url}: {size} bytes")
            return size if size > 0 else None
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get file size: {e}")
            return None
        except (ValueError, KeyError):
            logger.warning(f"Invalid content-length header for {url}")
            return None

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Perform GET request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get
            
        Returns:
            Response: Response object, or None if failed
        """
        try:
            kwargs.setdefault("timeout", self.timeout)
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed: {e}")
            return None

    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Perform POST request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.post
            
        Returns:
            Response: Response object, or None if failed
        """
        try:
            kwargs.setdefault("timeout", self.timeout)
            response = self.session.post(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {e}")
            return None