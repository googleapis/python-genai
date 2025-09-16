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

"""Tests for async stream."""

import asyncio
from collections.abc import Sequence
import datetime
from typing import List
from unittest import mock
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
import pytest

try:
  import aiohttp

  AIOHTTP_NOT_INSTALLED = False
except ImportError:
  AIOHTTP_NOT_INSTALLED = True
  aiohttp = mock.MagicMock()

import httpx

from ... import _api_client as api_client
from ... import errors
from ... import types


class MockHTTPXResponse(httpx.Response):
  """Mock httpx.Response class for testing."""

  def __init__(self, lines: List[str]):
    self.aiter_lines = MagicMock()
    self.aiter_lines.return_value.__aiter__ = MagicMock(
        return_value=self._async_line_iterator(lines)
    )
    self.aclose = AsyncMock()

  async def _async_line_iterator(self, lines: List[str]):
    for line in lines:
      yield line


class MockAIOHTTPResponse(aiohttp.ClientResponse):

  def __init__(self, lines: List[str]):
    self.content = MagicMock()
    self.content.readline = AsyncMock()
    # Simulate reading lines, each ending with newline bytes for readline behavior
    self._read_data = b"\n".join(line.encode("utf-8") for line in lines) + b"\n"
    self._read_pos = 0
    self.content.readline.side_effect = self._async_read_line
    self.release = MagicMock()

  async def _async_read_line(self) -> bytes:
    if self._read_pos >= len(self._read_data):
      return b""  # End of stream

    newline_pos = self._read_data.find(b"\n", self._read_pos)
    if newline_pos == -1:  # Should not happen with the appended '\n'
      line = self._read_data[self._read_pos :]
      self._read_pos = len(self._read_data)
      return line
    else:
      line = self._read_data[self._read_pos : newline_pos + 1]
      self._read_pos = newline_pos + 1
      return line


@pytest.fixture
def responses() -> api_client.HttpResponse:
  return api_client.HttpResponse(headers={})


def test_invalid_response_stream_type(responses: api_client.HttpResponse):
  """Tests that an invalid response stream type raises an error."""
  api_client.has_aiohttp = False
  with pytest.raises(
      TypeError,
      match=(
          "Expected self.response_stream to be an httpx.Response or"
          " aiohttp.ClientResponse object"
      ),
  ):

    async def run():
      async for _ in responses._aiter_response_stream():
        pass

    asyncio.run(run())


@pytest.mark.asyncio
async def test_httpx_simple_lines(responses: api_client.HttpResponse):
  lines = ["hello", "world", "testing"]
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == lines
  mock_response.aiter_lines.assert_called_once()
  mock_response.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_data_prefix(responses: api_client.HttpResponse):
  lines = ["data: { 'message': 'hello' }", "data: { 'status': 'ok' }"]
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ["{ 'message': 'hello' }", "{ 'status': 'ok' }"]
  mock_response.aiter_lines.assert_called_once()
  mock_response.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_multiple_json_chunk(responses: api_client.HttpResponse):
  lines = [
      '{ "id": 1 }',
      "",
      'data: { "id": 2 }',
      'data: { "id": 3 }',
  ]
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{ "id": 1 }', '{ "id": 2 }', '{ "id": 3 }']
  mock_response.aiter_lines.assert_called_once()
  mock_response.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_incomplete_json_at_end(responses: api_client.HttpResponse):
  lines = ['{ "partial": "data"']  # Missing closing brace
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  # The remaining chunk is yielded
  assert results == ['{ "partial": "data"']
  mock_response.aiter_lines.assert_called_once()
  mock_response.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_empty_stream(responses: api_client.HttpResponse):
  lines: List[str] = []
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == []
  mock_response.aiter_lines.assert_called_once()
  mock_response.aclose.assert_called_once()


# Async aiohttp
@pytest.mark.asyncio
async def test_aiohttp_simple_lines(responses: api_client.HttpResponse):
  api_client.has_aiohttp = True  # Force aiohttp
  lines = ["hello", "world", "testing"]
  # Use the mock class that pretends to be aiohttp.ClientResponse
  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == lines
  mock_response.content.readline.assert_any_call()
  mock_response.release.assert_called_once()


@pytest.mark.asyncio
async def test_aiohttp_data_prefix(responses: api_client.HttpResponse):
  api_client.has_aiohttp = True  # Force aiohttp
  lines = ["data: { 'message': 'hello' }", "data: { 'status': 'ok' }"]
  # Use the mock class that pretends to be aiohttp.ClientResponse
  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ["{ 'message': 'hello' }", "{ 'status': 'ok' }"]
  mock_response.content.readline.assert_any_call()
  mock_response.release.assert_called_once()


@pytest.mark.asyncio
async def test_aiohttp_multiple_json_chunks(responses: api_client.HttpResponse):
  api_client.has_aiohttp = True  # Force aiohttp
  lines = [
      '{ "id": 1 }',
      "",  # empty line to check robustness
      'data: { "id": 2 }',
      'data: { "id": 3 }',
  ]
  # Use the mock class that pretends to be aiohttp.ClientResponse
  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{ "id": 1 }', '{ "id": 2 }', '{ "id": 3 }']
  mock_response.content.readline.assert_any_call()
  mock_response.release.assert_called_once()


@pytest.mark.asyncio
async def test_aiohttp_incomplete_json_at_end(
    responses: api_client.HttpResponse,
):
  api_client.has_aiohttp = True  # Force aiohttp
  lines = ['{ "partial": "data"']  # Missing closing brace
  # Use the mock class that pretends to be aiohttp.ClientResponse
  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{ "partial": "data"']
  mock_response.content.readline.assert_any_call()
  mock_response.release.assert_called_once()
