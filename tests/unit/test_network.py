# Copyright (C) 2025 H. Blok
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Unit Tests for NetworkService

Tests for HTTP operations with timeout and retry handling.
"""

import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock, mock_open

from sbcman.services.network import NetworkService
import requests


class TestNetworkService(unittest.TestCase):

    def setUp(self):
        self.service = NetworkService()
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_default_values(self):
        service = NetworkService()
        self.assertEqual(service.timeout, 30)
        self.assertEqual(service.max_retries, 3)
        self.assertIsNotNone(service.session)

    def test_initialization_custom_values(self):
        service = NetworkService(timeout=60, max_retries=5)
        self.assertEqual(service.timeout, 60)
        self.assertEqual(service.max_retries, 5)

    def test_session_has_user_agent(self):
        service = NetworkService()
        self.assertIn('User-Agent', service.session.headers)
        self.assertIn('SBC-Man', service.session.headers['User-Agent'])

    def test_download_file_success(self):
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '100'}
        mock_response.iter_content = MagicMock(return_value=[b'chunk'])
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'get', return_value=mock_response):
            dest = self.temp_dir / "test.txt"
            result = self.service.download_file("http://example.com/file.txt", dest)
            
            self.assertTrue(result)
            self.assertTrue(dest.exists())

    def test_download_file_with_progress_callback(self):
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '200'}
        mock_response.iter_content = MagicMock(return_value=[b'chunk1', b'chunk2'])
        mock_response.raise_for_status = MagicMock()
        
        callback = MagicMock()
        
        with patch.object(self.service.session, 'get', return_value=mock_response):
            dest = self.temp_dir / "test.txt"
            self.service.download_file("http://example.com/file.txt", dest, callback)
            
            self.assertTrue(callback.called)

    def test_download_file_request_exception(self):
        with patch.object(self.service.session, 'get', side_effect=requests.exceptions.RequestException("Error")):
            dest = self.temp_dir / "test.txt"
            result = self.service.download_file("http://example.com/file.txt", dest)
            
            self.assertFalse(result)

    def test_download_file_creates_directory(self):
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '100'}
        mock_response.iter_content = MagicMock(return_value=[b'chunk'])
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'get', return_value=mock_response):
            dest = self.temp_dir / "subdir" / "test.txt"
            result = self.service.download_file("http://example.com/file.txt", dest)
            
            self.assertTrue(result)
            self.assertTrue(dest.exists())
            self.assertTrue(dest.parent.exists())

    def test_check_url_success(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'head', return_value=mock_response):
            result = self.service.check_url("http://example.com")
            self.assertTrue(result)

    def test_check_url_failure(self):
        with patch.object(self.service.session, 'head', side_effect=requests.exceptions.RequestException("Error")):
            result = self.service.check_url("http://example.com")
            self.assertFalse(result)

    def test_check_url_with_redirect(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'head', return_value=mock_response) as mock_head:
            self.service.check_url("http://example.com")
            args, kwargs = mock_head.call_args
            self.assertTrue(kwargs.get('allow_redirects', False))

    def test_get_file_size_success(self):
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '12345'}
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'head', return_value=mock_response):
            result = self.service.get_file_size("http://example.com/file.txt")
            self.assertEqual(result, 12345)

    def test_get_file_size_zero(self):
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '0'}
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'head', return_value=mock_response):
            result = self.service.get_file_size("http://example.com/file.txt")
            self.assertIsNone(result)

    def test_get_file_size_no_header(self):
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'head', return_value=mock_response):
            result = self.service.get_file_size("http://example.com/file.txt")
            self.assertIsNone(result)

    def test_get_file_size_request_exception(self):
        with patch.object(self.service.session, 'head', side_effect=requests.exceptions.RequestException("Error")):
            result = self.service.get_file_size("http://example.com/file.txt")
            self.assertIsNone(result)

    def test_get_file_size_invalid_header(self):
        mock_response = MagicMock()
        mock_response.headers = {'content-length': 'invalid'}
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'head', return_value=mock_response):
            result = self.service.get_file_size("http://example.com/file.txt")
            self.assertIsNone(result)

    def test_get_success(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'get', return_value=mock_response):
            result = self.service.get("http://example.com")
            self.assertEqual(result, mock_response)

    def test_get_failure(self):
        with patch.object(self.service.session, 'get', side_effect=requests.exceptions.RequestException("Error")):
            result = self.service.get("http://example.com")
            self.assertIsNone(result)

    def test_get_with_custom_timeout(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'get', return_value=mock_response) as mock_get:
            self.service.get("http://example.com", timeout=60)
            args, kwargs = mock_get.call_args
            self.assertEqual(kwargs.get('timeout'), 60)

    def test_post_success(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'post', return_value=mock_response):
            result = self.service.post("http://example.com")
            self.assertEqual(result, mock_response)

    def test_post_failure(self):
        with patch.object(self.service.session, 'post', side_effect=requests.exceptions.RequestException("Error")):
            result = self.service.post("http://example.com")
            self.assertIsNone(result)

    def test_get_uses_default_timeout(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'get', return_value=mock_response) as mock_get:
            service = NetworkService(timeout=45)
            service.get("http://example.com")
            args, kwargs = mock_get.call_args
            self.assertEqual(kwargs.get('timeout'), 45)

    def test_post_uses_default_timeout(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'post', return_value=mock_response) as mock_post:
            service = NetworkService(timeout=45)
            service.post("http://example.com")
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs.get('timeout'), 45)

    def test_download_file_empty_content(self):
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '0'}
        mock_response.iter_content = MagicMock(return_value=[])
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(self.service.session, 'get', return_value=mock_response):
            dest = self.temp_dir / "test.txt"
            result = self.service.download_file("http://example.com/file.txt", dest)
            
            self.assertTrue(result)
            self.assertTrue(dest.exists())