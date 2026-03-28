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

import json
import unittest
from unittest import mock

import pytest

from google.genai import errors
from google.genai import types
from google.genai.models import _ensure_file_active, _process_contents_for_generation
from google.genai.types import FileState


def _make_response_body(state: str, error_message: str = None) -> bytes:
  """Create a mock API response body for a file."""
  data = {
      'name': 'files/test123',
      'displayName': 'Test File',
      'mimeType': 'video/mp4',
      'state': state,
  }
  if error_message:
    data['error'] = {'message': error_message}
  return json.dumps(data).encode()


class TestFileStateHandling(unittest.TestCase):
  """Test file state handling functionality."""

  def setUp(self):
    """Set up test fixtures."""
    self.api_client = mock.MagicMock()
    self.file_obj = types.File(
        name='files/test123',
        display_name='Test File',
        mime_type='video/mp4',
        uri='https://example.com/files/test123',
        state=types.FileState.PROCESSING,
    )

  def test_ensure_file_active_with_processing_file(self):
    """Test that _ensure_file_active waits for a PROCESSING file to become ACTIVE."""
    response_mock = mock.MagicMock()
    response_mock.body = _make_response_body('ACTIVE')
    self.api_client.request.return_value = response_mock

    result = _ensure_file_active(
        self.api_client, self.file_obj, max_retries=1, retry_delay_seconds=0
    )

    self.api_client.request.assert_called_once_with(
        'GET', 'files/test123', {}, None
    )
    self.assertEqual(result.state, types.FileState.ACTIVE)

  def test_ensure_file_active_with_failed_file(self):
    """Test that _ensure_file_active raises FileProcessingError for a FAILED file."""
    response_mock = mock.MagicMock()
    response_mock.body = _make_response_body(
        'FAILED', error_message='File processing failed'
    )
    self.api_client.request.return_value = response_mock

    with pytest.raises(errors.FileProcessingError) as excinfo:
      _ensure_file_active(
          self.api_client, self.file_obj, max_retries=1, retry_delay_seconds=0
      )

    assert 'File processing failed' in str(excinfo.value)

  def test_ensure_file_active_with_retries_exhausted(self):
    """Test that _ensure_file_active returns original file after exhausting retries."""
    response_mock = mock.MagicMock()
    response_mock.body = _make_response_body('PROCESSING')
    self.api_client.request.return_value = response_mock

    result = _ensure_file_active(
        self.api_client, self.file_obj, max_retries=2, retry_delay_seconds=0
    )

    self.assertEqual(self.api_client.request.call_count, 2)
    self.assertEqual(result, self.file_obj)
    self.assertEqual(result.state, types.FileState.PROCESSING)

  def test_ensure_file_active_with_already_active_file(self):
    """Test that _ensure_file_active returns immediately for an already ACTIVE file."""
    active_file = types.File(
        name='files/active123',
        display_name='Active File',
        mime_type='video/mp4',
        state=types.FileState.ACTIVE,
    )

    result = _ensure_file_active(
        self.api_client, active_file, max_retries=1, retry_delay_seconds=0
    )

    self.api_client.request.assert_not_called()
    self.assertEqual(result, active_file)
    self.assertEqual(result.state, types.FileState.ACTIVE)


class TestProcessContentsFunction(unittest.TestCase):
  """Test the _process_contents_for_generation function."""

  def setUp(self):
    """Set up test fixtures."""
    self.api_client = mock.MagicMock()
    self.processing_file = types.File(
        name='files/processing123',
        display_name='Processing File',
        mime_type='video/mp4',
        uri='https://example.com/files/processing123',
        state=types.FileState.PROCESSING,
    )
    self.active_file = types.File(
        name='files/active123',
        display_name='Active File',
        mime_type='video/mp4',
        uri='https://example.com/files/active123',
        state=types.FileState.ACTIVE,
    )

  def test_process_contents_with_files(self):
    """Test that _process_contents_for_generation can handle various file scenarios."""
    file_in_list = [self.processing_file, 'Process this file']
    file_in_parts = types.Content(
        role='user',
        parts=[types.Part(text="Here's a video:"), self.processing_file],
    )
    multiple_files = [
        types.Content(
            role='user',
            parts=[types.Part(text='First video:'), self.processing_file],
        ),
        types.Content(
            role='user',
            parts=[types.Part(text='Second video:'), self.active_file],
        ),
    ]

    with mock.patch(
        'google.genai.models._ensure_file_active', side_effect=lambda client, f: f
    ):
      for test_content in [file_in_list, file_in_parts, multiple_files]:
        with mock.patch(
            'google.genai.models.t.t_contents',
            return_value=(
                test_content
                if isinstance(test_content, list)
                else [test_content]
            ),
        ):
          result = _process_contents_for_generation(
              self.api_client, test_content
          )
          self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
