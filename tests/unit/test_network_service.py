"""
Unit Tests for NetworkService

Tests for HTTP operations, download functionality, and error handling.

These tests verify the NetworkService class functionality including:
- HTTP GET and POST operations with success and failure cases
- File download functionality with progress tracking
- Error handling for connection failures and other network issues
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import requests

from sbcman.services.network import NetworkService


class TestNetworkService(unittest.TestCase):
    """Test cases for NetworkService."""

    def setUp(self):
        """Set up test fixtures."""
        self.network_service = NetworkService(timeout=10, max_retries=2)

    def test_network_service_initialization(self):
        """Test network service initialization with custom parameters."""
        service = NetworkService(timeout=15, max_retries=3)
        
        self.assertEqual(service.timeout, 15)
        self.assertEqual(service.max_retries, 3)
        self.assertIsInstance(service.session, requests.Session)
        self.assertEqual(service.session.headers["User-Agent"], "SBC-Man Game Launcher/1.0")

    @patch('requests.Session.get')
    def test_get_success(self, mock_get):
        """Test successful GET request."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = self.network_service.get("https://example.com")
        
        # Verify the mock was called correctly
        mock_get.assert_called_once_with("https://example.com", timeout=10)
        self.assertEqual(response, mock_response)

    @patch('requests.Session.get')
    def test_get_failure(self, mock_get):
        """Test failed GET request."""
        # Configure mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        
        response = self.network_service.get("https://example.com")
        
        # Verify the mock was called and None was returned
        mock_get.assert_called_once_with("https://example.com", timeout=10)
        self.assertIsNone(response)

    @patch('requests.Session.post')
    def test_post_success(self, mock_post):
        """Test successful POST request."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = self.network_service.post("https://example.com", data={"key": "value"})
        
        # Verify the mock was called correctly
        mock_post.assert_called_once_with("https://example.com", timeout=10, data={"key": "value"})
        self.assertEqual(response, mock_response)

    @patch('requests.Session.post')
    def test_post_failure(self, mock_post):
        """Test failed POST request."""
        # Configure mock to raise an exception
        mock_post.side_effect = requests.exceptions.RequestException("Connection failed")
        
        response = self.network_service.post("https://example.com", data={"key": "value"})
        
        # Verify the mock was called and None was returned
        mock_post.assert_called_once_with("https://example.com", timeout=10, data={"key": "value"})
        self.assertIsNone(response)

    @patch('requests.Session.get')
    def test_download_file_success(self, mock_get):
        """Test successful file download."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_path = Path(temp_dir) / "test_file.txt"
            
            # Create a mock response with content
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-length": "1024"}
            mock_response.iter_content.return_value = [b"test content"]
            mock_get.return_value = mock_response
            
            # Mock the progress callback
            progress_callback = Mock()
            
            result = self.network_service.download_file(
                "https://example.com/file.txt", 
                dest_path, 
                progress_callback
            )
            
            # Verify the result and that the file was created
            self.assertTrue(result)
            self.assertTrue(dest_path.exists())
            
            # Verify the progress callback was called
            progress_callback.assert_called()
            
            # Verify the mock was called correctly
            mock_get.assert_called_once_with(
                "https://example.com/file.txt", 
                timeout=10, 
                stream=True
            )

    @patch('requests.Session.get')
    def test_download_file_failure(self, mock_get):
        """Test failed file download."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_path = Path(temp_dir) / "test_file.txt"
            
            # Configure mock to raise an exception
            mock_get.side_effect = requests.exceptions.RequestException("Download failed")
            
            result = self.network_service.download_file("https://example.com/file.txt", dest_path)
            
            # Verify the result and that the file was not created
            self.assertFalse(result)
            self.assertFalse(dest_path.exists())
            
            # Verify the mock was called
            mock_get.assert_called_once_with(
                "https://example.com/file.txt", 
                timeout=10, 
                stream=True
            )

    @patch('requests.Session.head')
    def test_get_file_size_success(self, mock_head):
        """Test successful file size retrieval."""
        # Create a mock response with content-length header
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"content-length": "1024"}
        mock_head.return_value = mock_response
        
        size = self.network_service.get_file_size("https://example.com/file.txt")
        
        # Verify the result and that the mock was called correctly
        self.assertEqual(size, 1024)
        mock_head.assert_called_once_with("https://example.com/file.txt", timeout=10, allow_redirects=True)

    @patch('requests.Session.head')
    def test_get_file_size_failure(self, mock_head):
        """Test failed file size retrieval."""
        # Configure mock to raise an exception
        mock_head.side_effect = requests.exceptions.RequestException("Request failed")
        
        size = self.network_service.get_file_size("https://example.com/file.txt")
        
        # Verify the result and that the mock was called
        self.assertIsNone(size)
        mock_head.assert_called_once_with("https://example.com/file.txt", timeout=10, allow_redirects=True)

    @patch('requests.Session.head')
    def test_get_file_size_invalid_header(self, mock_head):
        """Test file size retrieval with invalid content-length header."""
        # Create a mock response with invalid content-length header
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"content-length": "invalid"}
        mock_head.return_value = mock_response
        
        size = self.network_service.get_file_size("https://example.com/file.txt")
        
        # Verify the result is None
        self.assertIsNone(size)
        mock_head.assert_called_once_with("https://example.com/file.txt", timeout=10, allow_redirects=True)


if __name__ == "__main__":
    unittest.main()