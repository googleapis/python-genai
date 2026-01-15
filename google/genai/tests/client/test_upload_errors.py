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

"""Tests for error handling in the client api client layer for uploads."""

import io
import json
from unittest import mock
import pytest

import httpx

from ... import _api_client as api_client
from ... import errors
from ... import types

try:
    import aiohttp
    AIOHTTP_NOT_INSTALLED = False
except ImportError:
    AIOHTTP_NOT_INSTALLED = True

def _httpx_response(code: int, headers: dict = None, content: bytes = b''):
  headers = headers or {}
  headers['status-code'] = str(code)
  return httpx.Response(
      status_code=code,
      headers=headers,
      content=content,
  )

@pytest.fixture
def client():
  return api_client.BaseApiClient(vertexai=False, api_key='test_api_key')

def test_upload_fd_error(client: api_client.BaseApiClient):
  error_content = json.dumps({
      "error": {
          "code": 400,
          "message": "Unsupported MIME type: bad/mime_type",
          "status": "INVALID_ARGUMENT"
      }
  }).encode('utf-8')

  mock_httpx_client = mock.MagicMock(spec=httpx.Client)
  mock_httpx_client.request.side_effect = [
      _httpx_response(200, headers={"X-Goog-Upload-URL": "http://fake/upload"}), # Initial request to get upload URL
      _httpx_response(400, content=error_content, headers={"X-Goog-Upload-Status": "final"}), # Upload request failing
  ]
  client._httpx_client = mock_httpx_client

  with pytest.raises(errors.APIError, match='Unsupported MIME type: bad/mime_type'), io.BytesIO(b"test") as f:
    client._upload_fd(
        f,  # Pass file object directly
        "http://fake/upload",
        4,
        http_options=types.HttpOptions(),
    )

  assert mock_httpx_client.request.call_count == 2

@pytest.mark.asyncio
async def test_async_upload_fd_error_httpx(client: api_client.BaseApiClient):
  error_content = json.dumps({
      "error": {
          "code": 400,
          "message": "Unsupported MIME type: bad/mime_type",
          "status": "INVALID_ARGUMENT"
      }
  }).encode('utf-8')

  # Mock for httpx.AsyncClient
  mock_async_httpx_client = mock.MagicMock(spec=httpx.AsyncClient)
  mock_async_httpx_client.request = mock.AsyncMock(side_effect=[
      _httpx_response(200, headers={"X-Goog-Upload-URL": "http://fake/upload"}), # Initial request
      _httpx_response(400, content=error_content, headers={"X-Goog-Upload-Status": "final"}), # Upload request
  ])
  client._async_httpx_client = mock_async_httpx_client

  # Patch the _use_aiohttp method to control which client is used
  with mock.patch.object(client, '_use_aiohttp', return_value=False), \
       pytest.raises(errors.APIError, match='Unsupported MIME type: bad/mime_type'), \
       io.BytesIO(b"test") as f:
    await client._async_upload_fd(
        f,  # Pass file object directly
        "http://fake/upload",
        4,
        http_options=types.HttpOptions(),

    )
  assert mock_async_httpx_client.request.call_count == 2

@pytest.mark.asyncio
@pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason="aiohttp is not installed, skipping test."
)
async def test_async_upload_fd_error_aiohttp(client: api_client.BaseApiClient):
  error_content = json.dumps({
      "error": {
          "code": 400,
          "message": "Unsupported MIME type: bad/mime_type",
          "status": "INVALID_ARGUMENT"
      }
  }).encode('utf-8')

  # Mock for aiohttp.ClientSession
  mock_aiohttp_session = mock.MagicMock()
  mock_aiohttp_session.request = mock.AsyncMock(side_effect=[
      _httpx_response(200, headers={"X-Goog-Upload-URL": "http://fake/upload"}), # Initial request
      _httpx_response(400, content=error_content, headers={"X-Goog-Upload-Status": "final"}), # Upload request
  ])

  with mock.patch.object(client, '_use_aiohttp', return_value=True), \
       mock.patch.object(client, '_get_aiohttp_session', return_value=mock_aiohttp_session), \
       pytest.raises(errors.APIError, match='Unsupported MIME type: bad/mime_type'), \
       io.BytesIO(b"test") as f:
    await client._async_upload_fd(
        f,  # Pass file object directly
        "http://fake/upload",
        4,
        http_options=types.HttpOptions(),
    )
  assert mock_aiohttp_session.request.call_count == 2

