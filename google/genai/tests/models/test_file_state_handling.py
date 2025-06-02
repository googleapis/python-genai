#!/usr/bin/env python
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Tests for file state handling in content generation."""

import unittest
from unittest import mock
import time

import pytest

from google.genai import types
from google.genai import errors
from google.genai.models import _ensure_file_active, _process_contents_for_generation
from google.genai.types import FileState


class TestFileStateHandling(unittest.TestCase):
    """Test file state handling functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_client = mock.MagicMock()
        self.file_obj = types.File(
            name="files/test123",
            display_name="Test File",
            mime_type="video/mp4",
            uri="https://example.com/files/test123",
            state=types.FileState.PROCESSING,
        )

    @mock.patch("google.genai.files._File_from_mldev")
    def test_ensure_file_active_with_processing_file(self, mock_file_from_mldev):
        """Test that _ensure_file_active properly handles a file in PROCESSING state."""

        response_mock = mock.MagicMock()
        response_mock.json = {
            "file": {
                "name": "files/test123",
                "displayName": "Test File",
                "mimeType": "video/mp4",
                "state": "ACTIVE",
            }
        }
        self.api_client.call_api.return_value = response_mock

        # Set up the mock to return a dict that will create an ACTIVE file
        mock_file_from_mldev.return_value = {
            "name": "files/test123",
            "display_name": "Test File",
            "mime_type": "video/mp4",
            "state": types.FileState.ACTIVE,
        }

        result = _ensure_file_active(
            self.api_client, self.file_obj, max_retries=1, retry_delay_seconds=0.1
        )

        self.api_client.call_api.assert_called_once_with(
            method="GET",
            url="files/test123",
            api_client_type="mldev",
        )

        # Verify the result has ACTIVE state
        self.assertEqual(result.state, types.FileState.ACTIVE)

    def test_ensure_file_active_with_failed_file(self):
        """Test that _ensure_file_active properly handles a file in FAILED state."""

        response_mock = mock.MagicMock()
        response_mock.json = {
            "file": {
                "name": "files/test123",
                "displayName": "Test File",
                "mimeType": "video/mp4",
                "state": "FAILED",
                "error": {"message": "File processing failed"},
            }
        }

        # Set up a side effect for call_api that returns the response with FAILED state
        def mock_call_api(**kwargs):
            # Only return the mock for the expected file API call
            if kwargs.get("method") == "GET" and "files/" in kwargs.get("url", ""):
                return response_mock
            return mock.DEFAULT

        self.api_client.call_api.side_effect = mock_call_api


        with pytest.raises(errors.FileProcessingError) as excinfo:
            _ensure_file_active(
                self.api_client, self.file_obj, max_retries=1, retry_delay_seconds=0.1
            )

        assert "File processing failed" in str(excinfo.value)

    def test_ensure_file_active_with_retries_exhausted(self):
        """Test that _ensure_file_active handles a file that remains in PROCESSING state after all retries."""
        # Mock the response for file state check - file stays in PROCESSING
        response_mock = mock.MagicMock()
        response_mock.json = {
            "file": {
                "name": "files/test123",
                "displayName": "Test File",
                "mimeType": "video/mp4",
                "state": "PROCESSING",
            }
        }
        self.api_client.call_api.return_value = response_mock

        # Call the function
        result = _ensure_file_active(
            self.api_client, self.file_obj, max_retries=2, retry_delay_seconds=0.1
        )

        # Verify the file state was checked multiple times
        self.assertEqual(self.api_client.call_api.call_count, 2)

        # Verify the original file is returned
        self.assertEqual(result, self.file_obj)
        self.assertEqual(result.state, types.FileState.PROCESSING)

    def test_ensure_file_active_with_already_active_file(self):
        """Test that _ensure_file_active returns immediately for an already ACTIVE file."""
        active_file = types.File(
            name="files/active123",
            display_name="Active File",
            mime_type="video/mp4",
            state=types.FileState.ACTIVE,
        )

        result = _ensure_file_active(
            self.api_client, active_file, max_retries=1, retry_delay_seconds=0.1
        )

        # Verify no API calls were made
        self.api_client.call_api.assert_not_called()

        # Verify the original file is returned unchanged
        self.assertEqual(result, active_file)
        self.assertEqual(result.state, types.FileState.ACTIVE)


class TestProcessContentsFunction(unittest.TestCase):
    """Test the _process_contents_for_generation function."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_client = mock.MagicMock()
        self.processing_file = types.File(
            name="files/processing123",
            display_name="Processing File",
            mime_type="video/mp4",
            uri="https://example.com/files/processing123",
            state=types.FileState.PROCESSING
        )
        self.active_file = types.File(
            name="files/active123",
            display_name="Active File",
            mime_type="video/mp4",
            uri="https://example.com/files/active123",
            state=types.FileState.ACTIVE
        )

    def test_process_contents_with_files(self):
        """Test that _process_contents_for_generation can handle various file scenarios."""
        # Scenarios:
        # - File directly in content list
        # - File in content parts
        # - Multiple files in different parts
        
        # Test data
        file_in_list = [self.processing_file, "Process this file"]
        
        file_in_parts = types.Content(
            role="user",
            parts=[types.Part(text="Here's a video:"), self.processing_file]
        )
        
        multiple_files = [
            types.Content(
                role="user",
                parts=[types.Part(text="First video:"), self.processing_file]
            ),
            types.Content(
                role="user",
                parts=[types.Part(text="Second video:"), self.active_file]
            )
        ]
        
        # Mock _ensure_file_active to return the file unchanged
        # This allows us to test the function without changing file states
        with mock.patch("google.genai.models._ensure_file_active", 
                      side_effect=lambda client, file: file):
            
            # Test all three cases
            for test_content in [file_in_list, file_in_parts, multiple_files]:
                with mock.patch("google.genai.models.t.t_contents", 
                              return_value=test_content if isinstance(test_content, list) else [test_content]):
                    # Just verify it runs without errors
                    result = _process_contents_for_generation(self.api_client, test_content)
                    # Basic assertion that we got something back
                    self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
