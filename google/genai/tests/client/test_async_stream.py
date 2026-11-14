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
import io
import json
from typing import Any, List
from unittest import mock
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
import pytest
import requests


try:
  import aiohttp

  AIOHTTP_NOT_INSTALLED = False
except ImportError:
  AIOHTTP_NOT_INSTALLED = True
  aiohttp = mock.MagicMock()

from ... import _api_client as api_client
from ... import Client
from ... import errors
from ... import types

if api_client._get_http_client_backend() == 'httpx2':
  import httpx2 as httpx  # pylint: disable=g-import-not-at-top
else:
  import httpx  # pylint: disable=g-import-not-at-top


EVENT_STREAM_DATA_WITH_ERROR = [
    b'{"candidates":[{"content":{"parts":[{"text":"test"}],"role":"model"}}]}',
    b'\n',
    b'{"error":{"code":500,"message":"Error","status":"INTERNAL"}}',
]


class MockHTTPXResponse(httpx.Response):
  """Mock httpx.Response class for testing."""

  def __init__(self, lines: List[str]):
    self.aiter_bytes = MagicMock(return_value=self._async_byte_iterator(lines))
    self.aclose = AsyncMock()

  async def _async_byte_iterator(self, lines: List[str]):
    for line in lines:
      yield line.encode('utf-8') + b'\n'


def _aiohttp_stream_reader(data: bytes, eof: bool = True):
  """Returns a real aiohttp StreamReader already fed with data."""
  reader = aiohttp.StreamReader(
      mock.Mock(_reading_paused=False),
      2**16,
      loop=asyncio.get_running_loop(),
  )
  reader.feed_data(data)
  if eof:
    reader.feed_eof()
  return reader


class MockAIOHTTPResponse(aiohttp.ClientResponse):

  def __init__(self, lines: List[str]):
    self.content = _aiohttp_stream_reader(
        b'\n'.join(line.encode('utf-8') for line in lines) + b'\n'
    )
    self.release = MagicMock()


class _ChunkedContent:
  """Fake aiohttp content whose iter_any() returns each piece as its own read.

  A real StreamReader that was fed before reading returns everything buffered
  in one iter_any() step, so it cannot exercise lines that span reads.
  """

  def __init__(self, pieces: List[bytes]):
    self._pieces = pieces

  async def iter_any(self):
    for piece in self._pieces:
      await asyncio.sleep(0)
      yield piece


def _split_into_pieces(data: bytes, piece_size: int) -> List[bytes]:
  return [data[i : i + piece_size] for i in range(0, len(data), piece_size)]


class MockAIOHTTPResponseFromReader(aiohttp.ClientResponse):

  def __init__(self, content):
    self.content = content
    self.release = MagicMock()


@pytest.fixture
def responses() -> api_client.HttpResponse:
  return api_client.HttpResponse(headers={})


requires_aiohttp = pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason="aiohttp is not installed, skipping test."
)


def test_invalid_response_stream_type(responses: api_client.HttpResponse):
  """Tests that an invalid response stream type raises an error."""
  api_client.has_aiohttp = False
  with pytest.raises(
      TypeError,
      match="Expected self.response_stream",
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
  mock_response.aiter_bytes.assert_called_once()
  mock_response.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_data_prefix(responses: api_client.HttpResponse):
  lines = ["data: { 'message': 'hello' }", "", "data: { 'status': 'ok' }"]
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ["{ 'message': 'hello' }", "{ 'status': 'ok' }"]
  mock_response.aiter_bytes.assert_called_once()
  mock_response.aclose.assert_called_once()

@pytest.mark.asyncio
async def test_httpx_multiline_data(responses: api_client.HttpResponse) -> None:
  lines = [
      "data: {",
      "data:   'message': 'hello'",
      "data: }",
      "",
  ]
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ["{\n  'message': 'hello'\n}"]
  mock_response.aiter_bytes.assert_called_once()
  mock_response.aclose.assert_called_once()


def test_httpx_multiline_data_sync(responses: api_client.HttpResponse) -> None:
  lines = [
      "data: {",
      "data:   'message': 'hello'",
      "data: }",
      "",
  ]
  mock_response = MagicMock(spec=httpx.Response)
  mock_response.iter_bytes.return_value = iter(
      [b'\n'.join(line.encode('utf-8') for line in lines) + b'\n']
  )
  responses.response_stream = mock_response

  results = list(responses._iter_response_stream())

  assert results == ["{\n  'message': 'hello'\n}"]


@pytest.mark.asyncio
async def test_httpx_multiple_json_chunk(responses: api_client.HttpResponse):
  lines = [
      '{ "id": 1 }',
      "",
      'data: { "id": 2 }',
      "",
      'data: { "id": 3 }',
  ]
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{ "id": 1 }', '{ "id": 2 }', '{ "id": 3 }']
  mock_response.aiter_bytes.assert_called_once()
  mock_response.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_incomplete_json_at_end(responses: api_client.HttpResponse):
  lines = ['{ "partial": "data"']  # Missing closing brace
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  # The remaining chunk is yielded
  assert results == ['{ "partial": "data"']
  mock_response.aiter_bytes.assert_called_once()
  mock_response.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_empty_stream(responses: api_client.HttpResponse):
  lines: List[str] = []
  mock_response = MockHTTPXResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == []
  mock_response.aiter_bytes.assert_called_once()
  mock_response.aclose.assert_called_once()


# Async aiohttp
@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_simple_lines(responses: api_client.HttpResponse):
  api_client.has_aiohttp = True  # Force aiohttp
  lines = ["hello", "world", "testing"]
  # Use the mock class that pretends to be aiohttp.ClientResponse
  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == lines
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_data_prefix(responses: api_client.HttpResponse):
  api_client.has_aiohttp = True  # Force aiohttp
  lines = ["data: { 'message': 'hello' }", "", "data: { 'status': 'ok' }"]
  # Use the mock class that pretends to be aiohttp.ClientResponse
  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ["{ 'message': 'hello' }", "{ 'status': 'ok' }"]
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_multiple_json_chunks(responses: api_client.HttpResponse):
  api_client.has_aiohttp = True  # Force aiohttp
  lines = [
      '{ "id": 1 }',
      "",  # empty line to check robustness
      'data: { "id": 2 }',
      "",
      'data: { "id": 3 }',
  ]
  # Use the mock class that pretends to be aiohttp.ClientResponse
  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{ "id": 1 }', '{ "id": 2 }', '{ "id": 3 }']
  mock_response.release.assert_called_once()


@requires_aiohttp
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
  mock_response.release.assert_called_once()


RAW_LINES_WITH_BRACES_IN_STRINGS = [
    '{"content": {"parts": [{"text": "unmatched {"}]}, "id": "evt1"}',
    '{"content": {"parts": [{"text": "unmatched }"}]}, "id": "evt2"}',
    '{"text": "quote \\" then {", "id": "evt3"}',
    '{"id": "evt4"}',
    '{"path": "C:\\\\", "note": "{", "id": "evt5"}',
]


def test_segments_raw_lines_with_braces_in_strings(
    responses: api_client.HttpResponse,
):
  """Braces inside string values do not merge raw JSON lines."""
  responses.response_stream = httpx.Response(
      200, content='\n'.join(RAW_LINES_WITH_BRACES_IN_STRINGS).encode()
  )

  results = [segment['id'] for segment in responses.segments()]

  assert results == ['evt1', 'evt2', 'evt3', 'evt4', 'evt5']


def test_httpx_raw_lines_with_braces_in_strings_sync(
    responses: api_client.HttpResponse,
):
  """The sync line iterator yields one chunk per raw JSON line."""
  mock_response = MagicMock(spec=httpx.Response)
  mock_response.iter_bytes.return_value = iter([
      line.encode('utf-8') + b'\n' for line in RAW_LINES_WITH_BRACES_IN_STRINGS
  ])
  responses.response_stream = mock_response

  results = list(responses._iter_response_stream())

  assert results == RAW_LINES_WITH_BRACES_IN_STRINGS


@pytest.mark.asyncio
async def test_httpx_raw_lines_with_braces_in_strings(
    responses: api_client.HttpResponse,
):
  """The async httpx iterator yields one chunk per raw JSON line."""
  mock_response = MockHTTPXResponse(RAW_LINES_WITH_BRACES_IN_STRINGS)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == RAW_LINES_WITH_BRACES_IN_STRINGS
  mock_response.aclose.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_raw_lines_with_braces_in_strings(
    responses: api_client.HttpResponse,
):
  """The aiohttp iterator yields one chunk per raw JSON line."""
  api_client.has_aiohttp = True
  mock_response = MockAIOHTTPResponse(RAW_LINES_WITH_BRACES_IN_STRINGS)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == RAW_LINES_WITH_BRACES_IN_STRINGS
  mock_response.release.assert_called_once()


@pytest.mark.asyncio
async def test_httpx_multiline_json_with_brace_in_string(
    responses: api_client.HttpResponse,
):
  """String state carries across the lines of a pretty-printed object."""
  error_lines = [
      '{',
      '  "error": {',
      '    "code": 400,',
      '    "message": "bad template {name"',
      '  }',
      '}',
  ]
  mock_response = MockHTTPXResponse(error_lines + ['{"id": "next"}'])
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == [''.join(error_lines), '{"id": "next"}']
  mock_response.aclose.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_large_sse_line_with_thought_signature(
    responses: api_client.HttpResponse,
):
  """Verifies large SSE lines (e.g. thoughtSignature) don't hit LineTooLong.

  aiohttp's StreamReader.readline() enforces a maximum line length based on
  the session's read_bufsize (default: 2**16), which gives a _high_water limit
  of 131072 bytes. Thinking models can return a thoughtSignature field large
  enough to push a single SSE data: line past this limit, causing LineTooLong.

  This test uses a real aiohttp StreamReader and confirms a 150KB line is
  streamed successfully.
  """
  api_client.has_aiohttp = True

  # Build a single SSE line larger than aiohttp's default limit (131072)
  large_thought_sig = "A" * 150_000  # > 131072 bytes
  large_sse_payload = (
      f'{{"candidates": [{{"content": {{"parts": [{{"text": "",'
      f'"thoughtSignature": "{large_thought_sig}"}}]}}}}]}}'
  )
  lines = [f"data: {large_sse_payload}", ""]

  mock_response = MockAIOHTTPResponse(lines)
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert len(results) == 1
  assert "thoughtSignature" in results[0]
  assert large_thought_sig in results[0]
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_sse_line_larger_than_read_buffer_size(
    responses: api_client.HttpResponse,
):
  """Verifies an SSE line over every aiohttp line cap is delivered whole.

  The payload exceeds both READ_BUFFER_SIZE and the 2 * read_bufsize high-water
  mark of the session the SDK creates.
  """
  api_client.has_aiohttp = True
  payload = (
      '{"inlineData": {"data": "'
      + 'A' * (2 * api_client.READ_BUFFER_SIZE + 1)
      + '"}}'
  )
  body = (
      b'data: {"text": "hi"}\r\n\r\n'
      + b'data: '
      + payload.encode()
      + b'\r\n\r\n'
  )
  mock_response = MockAIOHTTPResponseFromReader(
      _ChunkedContent(_split_into_pieces(body, 65536))
  )
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{"text": "hi"}', payload]
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_lines_split_across_reads(
    responses: api_client.HttpResponse,
):
  """Verifies lines are reassembled when every byte arrives in its own read."""
  api_client.has_aiohttp = True
  body = b'data: { "id": 1 }\r\n\r\ndata: { "id": 2 }\r\n\r\n'
  mock_response = MockAIOHTTPResponseFromReader(
      _ChunkedContent(_split_into_pieces(body, 1))
  )
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{ "id": 1 }', '{ "id": 2 }']
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_line_spanning_several_reads(
    responses: api_client.HttpResponse,
):
  """Verifies a line over three reads and a CRLF split across two reads."""
  api_client.has_aiohttp = True
  pieces = [
      b'data: {"te',
      b'xt": ',
      b'"hi"}\r',
      b'\n\r\ndata: { "id": 2 }',
      b'\r\n\r\n',
  ]
  mock_response = MockAIOHTTPResponseFromReader(_ChunkedContent(pieces))
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{"text": "hi"}', '{ "id": 2 }']
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_trailing_line_without_newline(
    responses: api_client.HttpResponse,
):
  """Verifies a final line with no newline is still yielded."""
  api_client.has_aiohttp = True
  mock_response = MockAIOHTTPResponseFromReader(
      _aiohttp_stream_reader(b'{ "id": 1 }')
  )
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{ "id": 1 }']
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_empty_stream(responses: api_client.HttpResponse):
  """Verifies an empty body yields nothing and releases the response."""
  api_client.has_aiohttp = True
  mock_response = MockAIOHTTPResponseFromReader(_aiohttp_stream_reader(b''))
  responses.response_stream = mock_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == []
  mock_response.release.assert_called_once()


@requires_aiohttp
@pytest.mark.asyncio
async def test_aiohttp_stream_error_releases_response(
    responses: api_client.HttpResponse,
):
  """Verifies a transport error propagates and the response is released."""
  api_client.has_aiohttp = True
  reader = _aiohttp_stream_reader(b'data: { "id": 1 }\r\n', eof=False)
  reader.set_exception(aiohttp.ClientPayloadError('boom'))
  mock_response = MockAIOHTTPResponseFromReader(reader)
  responses.response_stream = mock_response

  with pytest.raises(aiohttp.ClientPayloadError, match='boom'):
    async for _ in responses._aiter_response_stream():
      pass
  mock_response.release.assert_called_once()


def mock_response(chunks):
  mock_stream = MagicMock(spec=httpx.SyncByteStream)
  mock_stream.__iter__.return_value = chunks
  return httpx.Response(
      status_code=200,
      stream=mock_stream,
  )


@patch.object(httpx.Client, 'send')
def test_error_event_in_streamed_responses_bad_json(mock_send_method):
  with_bad_json = [
      b'{"candidates":[{"content":{"parts":[{"text":"test"}],"role":"model"}}]}',
      b'\n',
      b'{"error": bad_json}',
  ]
  mock_send_method.return_value = mock_response(with_bad_json)

  client = api_client.BaseApiClient(api_key='test_api_key')
  stream = client.request_streamed('POST', 'models/gemini-2.5-flash', {})

  chunk = next(stream)
  assert chunk == types.HttpResponse(
      headers={},
      body=(
          '{"candidates": [{"content": {"parts": [{"text": "test"}], "role":'
          ' "model"}}]}'
      ),
  )

  with pytest.raises(errors.UnknownApiResponseError):
    next(stream)


@patch.object(httpx.Client, 'send')
def test_error_event_in_streamed_responses(mock_send_method):
  mock_send_method.return_value = mock_response(EVENT_STREAM_DATA_WITH_ERROR)

  client = api_client.BaseApiClient(api_key='test_api_key')
  stream = client.request_streamed('POST', 'models/gemini-2.5-flash', {})

  chunk = next(stream)
  assert chunk == types.HttpResponse(
      body=(
          '{"candidates": [{"content": {"parts": [{"text": "test"}], "role":'
          ' "model"}}]}'
      ),
      headers={},
  )

  with pytest.raises(errors.ServerError):
    next(stream)


@patch.object(httpx.Client, 'send')
def test_error_event_in_generate_content_stream(mock_send_method):
  mock_send_method.return_value = mock_response(EVENT_STREAM_DATA_WITH_ERROR)

  client = Client(api_key='test_api_key')
  generated_response = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='Tell me a story in 300 words.',
  )

  chunk = next(generated_response)
  assert chunk == types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          text='test'
                      ),
                  ],
                  role='model'
              )
          ),
      ],
      sdk_http_response=types.HttpResponse(headers={})
  )

  with pytest.raises(errors.ServerError):
    next(generated_response)


async def _async_httpx_response(_):
  async def _aiter():
    for chunk in EVENT_STREAM_DATA_WITH_ERROR:
      yield chunk

  mock_stream = MagicMock(spec=httpx.AsyncByteStream)
  mock_stream.__aiter__.side_effect = _aiter
  mock_stream.aclose = AsyncMock()
  return httpx.Response(
      status_code=200,
      stream=mock_stream,
  )


@patch.object(httpx, 'AsyncBaseTransport')
@pytest.mark.asyncio
async def test_error_event_in_streamed_responses_async(mock_transport):
  client = api_client.BaseApiClient(
      api_key='test_api_key',
      http_options=types.HttpOptions(
          async_client_args={'transport': mock_transport}
          ),
      )
  mock_transport.handle_async_request = _async_httpx_response
  mock_transport.aclose = AsyncMock()

  resp = await client.async_request_streamed(
      'POST', 'models/gemini-2.5-flash', {'key': 'value'}
  )

  chunk = await anext(resp)
  assert chunk == types.HttpResponse(
      headers={},
      body=(
          '{"candidates": [{"content": {"parts": [{"text": "test"}], "role":'
          ' "model"}}]}'
      ),
  )

  with pytest.raises(errors.ServerError):
    await anext(resp)


@patch.object(httpx, 'AsyncBaseTransport')
@pytest.mark.asyncio
async def test_error_event_in_generate_content_stream_async(mock_transport):
  client = Client(
      api_key='test_api_key',
      http_options=types.HttpOptions(
          async_client_args={'transport': mock_transport}
      ),
  )
  mock_transport.handle_async_request = _async_httpx_response
  mock_transport.aclose = AsyncMock()

  generated_response = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='Tell me a story in 300 words.',
  )

  chunk = await anext(generated_response)
  assert chunk == types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          text='test'
                      ),
                  ],
                  role='model'
              )
          ),
      ],
      sdk_http_response=types.HttpResponse(headers={})
  )

  with pytest.raises(errors.ServerError):
    await anext(generated_response)


_LINE_SEPARATORS = pytest.mark.parametrize(
    'sep', ['\u2028', '\u2029', '\x85'], ids=['u2028', 'u2029', 'u0085']
)


def _sse_body_with_separator(sep: str) -> bytes:
  return b''.join(
      b'data: '
      + json.dumps(c, ensure_ascii=False).encode('utf-8')
      + b'\r\n\r\n'
      for c in _sse_events_with_separator(sep)
  )


def _sse_events_with_separator(sep: str) -> list[dict[str, Any]]:
  return [
      {
          'candidates': [{
              'content': {
                  'role': 'model',
                  'parts': [{'text': f'line one{sep}line two'}],
              }
          }]
      },
      {
          'candidates': [{
              'content': {'role': 'model', 'parts': [{'text': ' done'}]},
              'finishReason': 'STOP',
          }]
      },
  ]


def _sse_handler(sep: str):
  def handler(_: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        content=_sse_body_with_separator(sep),
        headers={'content-type': 'text/event-stream'},
    )

  return handler


@_LINE_SEPARATORS
def test_generate_content_stream_line_separator_in_text(sep):
  """Unicode line separators inside a JSON string do not split an SSE line."""
  client = Client(
      api_key='test_api_key',
      http_options=types.HttpOptions(
          client_args={'transport': httpx.MockTransport(_sse_handler(sep))}
      ),
  )

  stream = client.models.generate_content_stream(
      model='gemini-2.5-flash', contents='hi'
  )

  assert [c.text for c in stream] == [f'line one{sep}line two', ' done']


@_LINE_SEPARATORS
@pytest.mark.asyncio
async def test_generate_content_stream_line_separator_in_text_async(sep):
  """Async httpx streams keep Unicode line separators inside JSON strings."""
  client = Client(
      api_key='test_api_key',
      http_options=types.HttpOptions(
          async_client_args={
              'transport': httpx.MockTransport(_sse_handler(sep))
          }
      ),
  )

  stream = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash', contents='hi'
  )

  assert [c.text async for c in stream] == [
      f'line one{sep}line two',
      ' done',
  ]


@_LINE_SEPARATORS
def test_requests_stream_line_separator_in_text(sep):
  """The requests transport splits SSE lines only at CR, LF and CRLF."""
  resp = requests.Response()
  resp.status_code = 200
  resp.raw = io.BytesIO(_sse_body_with_separator(sep))
  resp.encoding = 'utf-8'

  results = list(
      api_client.HttpResponse(
          headers={}, response_stream=resp
      )._iter_response_stream()
  )

  assert results == [
      json.dumps(c, ensure_ascii=False) for c in _sse_events_with_separator(sep)
  ]


def test_httpx_stream_crlf_split_across_chunks():
  """A CRLF split across two chunks ends exactly one line.

  A spurious empty line would end the event early and split the multi-line
  data field into two events.
  """
  chunks = [b'data: {"a":\r', b'\ndata: 1}\r\n\r\n']
  resp = api_client.HttpResponse(
      headers={}, response_stream=mock_response(chunks)
  )

  assert list(resp._iter_response_stream()) == ['{"a":\n1}']


@pytest.mark.parametrize(
    'chunks, expected',
    [
        ([b'x\r', b'\ny\n'], ['x', 'y']),
        ([b'x\r', b'y\n'], ['x', 'y']),
        ([b'x\r', b'\r\n'], ['x', '']),
        ([b'x\r'], ['x']),
    ],
    ids=['crlf_split', 'cr_then_text', 'cr_then_crlf', 'cr_at_end'],
)
def test_iter_sse_lines_trailing_cr_at_chunk_end(chunks, expected):
  """A CR at a chunk end is held until the next chunk shows if LF follows."""
  assert list(api_client._iter_sse_lines(chunks)) == expected


def test_httpx_stream_cr_only_terminators():
  """A bare CR ends a line, as the SSE format requires."""
  chunks = [b'data: {"a": 1}\r\rdata: {"b": 2}\r\r']
  resp = api_client.HttpResponse(
      headers={}, response_stream=mock_response(chunks)
  )

  assert list(resp._iter_response_stream()) == ['{"a": 1}', '{"b": 2}']


def test_httpx_stream_multibyte_char_split_across_chunks():
  """A UTF-8 character split across chunks decodes as one character."""
  chunks = [b'data: {"t": "x\xe2\x80', b'\xa8y"}\n\n']
  resp = api_client.HttpResponse(
      headers={}, response_stream=mock_response(chunks)
  )

  assert list(resp._iter_response_stream()) == ['{"t": "x\u2028y"}']


def test_httpx_stream_multiline_data_with_line_separator():
  """Multi-line data fields still join with LF around a U+2028."""
  chunks = [b'data: {"t": "a\xe2\x80\xa8b",\n', b'data: "u": 1}\n\n']
  resp = api_client.HttpResponse(
      headers={}, response_stream=mock_response(chunks)
  )

  assert list(resp._iter_response_stream()) == ['{"t": "a\u2028b",\n"u": 1}']


def test_httpx_stream_invalid_utf8_is_replaced():
  """Invalid UTF-8 bytes become U+FFFD instead of raising."""
  chunks = [b'data: {"t": "\xff"}\n\n']
  resp = api_client.HttpResponse(
      headers={}, response_stream=mock_response(chunks)
  )

  assert list(resp._iter_response_stream()) == ['{"t": "\ufffd"}']


def test_httpx_stream_final_line_without_terminator():
  """A last line with no terminator is still yielded at end of stream."""
  chunks = [b'data: {"a": 1}\n\n{"error": ', b'{"code": 500}}']
  resp = api_client.HttpResponse(
      headers={}, response_stream=mock_response(chunks)
  )

  assert list(resp._iter_response_stream()) == [
      '{"a": 1}',
      '{"error": {"code": 500}}',
  ]


@pytest.mark.asyncio
async def test_httpx_async_stream_line_separator_in_text(
    responses: api_client.HttpResponse,
):
  """The async httpx branch keeps a U+2028 line whole and closes once."""
  httpx_response = MockHTTPXResponse(
      ['data: {"t": "a\u2028b"}', '', 'data: {"t": "c"}', '']
  )
  responses.response_stream = httpx_response

  results = [line async for line in responses._aiter_response_stream()]

  assert results == ['{"t": "a\u2028b"}', '{"t": "c"}']
  httpx_response.aclose.assert_called_once()
