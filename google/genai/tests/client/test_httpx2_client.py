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

"""Tests for injecting a Pydantic `httpx2` client into the SDK.

`httpx2` (https://github.com/pydantic/httpx2) is a drop-in fork of `httpx` under
a separate import namespace, so `httpx2` classes fail `isinstance(x, httpx.*)`.
These tests pin the two "walls" that must be widened for the SDK to accept an
injected `httpx2` client (see issue #2680):

- WALL 1: `HttpOptions.httpx_async_client` / `httpx_client` must accept an
  `httpx2` client at construction (aliases in the generated `types.py`).
- WALL 2: the hand-written `isinstance` checks in `errors.py` / `_api_client.py`
  must recognize an `httpx2.Response`.
"""

import httpx
import pytest

try:
  import httpx2
except ImportError:
  httpx2 = None

# Mark all tests in this module to be skipped if httpx2 is not available
pytestmark = pytest.mark.skipif(
    httpx2 is None, reason='httpx2 is not available'
)

from ... import _api_client as api_client
from ... import Client
from ... import errors
from ...types import HttpOptions, HttpRetryOptions


# WALL 1 — the client must be accepted at construction.
def test_http_options_accepts_httpx2_clients():
  # Previously raised ValidationError because the aliases were typed to the
  # httpx clients only, so Pydantic emitted an is_instance_of(httpx.*) check.
  http_options = HttpOptions(
      httpx_client=httpx2.Client(trust_env=False),
      httpx_async_client=httpx2.AsyncClient(trust_env=False),
  )
  assert isinstance(http_options.httpx_client, httpx2.Client)
  assert isinstance(http_options.httpx_async_client, httpx2.AsyncClient)


def test_constructor_with_httpx2_clients():
  mldev_client = Client(
      api_key='google_api_key',
      http_options={
          'httpx_client': httpx2.Client(trust_env=False),
          'httpx_async_client': httpx2.AsyncClient(trust_env=False),
      },
  )
  assert not mldev_client.models._api_client._httpx_client.trust_env
  assert not mldev_client.models._api_client._async_httpx_client.trust_env

  vertexai_client = Client(
      vertexai=True,
      project='fake_project_id',
      location='fake-location',
      http_options={
          'httpx_client': httpx2.Client(trust_env=False),
          'httpx_async_client': httpx2.AsyncClient(trust_env=False),
      },
  )
  assert not vertexai_client.models._api_client._httpx_client.trust_env
  assert not vertexai_client.models._api_client._async_httpx_client.trust_env


# WALL 2 — the response must be processed by the error/raise functions.
def test_raise_for_response_httpx2_success():
  assert (
      errors.APIError.raise_for_response(httpx2.Response(status_code=200))
      is None
  )


def test_raise_for_response_httpx2_client_error():
  class FakeResponse(httpx2.Response):

    def read(self) -> bytes:
      self._content = (
          b'{"error": {"code": 400, "message": "error message", "status":'
          b' "INVALID_ARGUMENT"}}'
      )
      return self._content

  with pytest.raises(errors.ClientError) as exc_info:
    errors.APIError.raise_for_response(FakeResponse(status_code=400))
  assert exc_info.value.code == 400
  assert exc_info.value.message == 'error message'
  assert exc_info.value.status == 'INVALID_ARGUMENT'


@pytest.mark.asyncio
async def test_raise_for_async_response_httpx2_success():
  # The async success path early-returns from inside the isinstance branch, so
  # without widening it every httpx2 response (success and error) is rejected.
  assert (
      await errors.APIError.raise_for_async_response(
          httpx2.Response(status_code=200)
      )
      is None
  )


@pytest.mark.asyncio
async def test_raise_for_async_response_httpx2_client_error():
  class FakeResponse(httpx2.Response):

    async def aread(self) -> bytes:
      self._content = (
          b'{"error": {"code": 400, "message": "error message", "status":'
          b' "INVALID_ARGUMENT"}}'
      )
      return self._content

  with pytest.raises(errors.ClientError) as exc_info:
    await errors.APIError.raise_for_async_response(FakeResponse(status_code=400))
  assert exc_info.value.code == 400
  assert exc_info.value.message == 'error message'
  assert exc_info.value.status == 'INVALID_ARGUMENT'


# WALL 2 — an httpx2.Response must flow through the async streaming iterator.
@pytest.mark.asyncio
async def test_httpx2_response_flows_through_async_stream():
  response = httpx2.Response(
      status_code=200,
      content=b'data: {"first": 1}\n\ndata: {"second": 2}\n\n',
  )
  http_response = api_client.HttpResponse(headers={}, response_stream=response)

  chunks = [chunk async for chunk in http_response._aiter_response_stream()]

  assert chunks == ['{"first": 1}', '{"second": 2}']


# WALL 2 — an httpx2.Response must flow through the sync streaming iterator.
def test_httpx2_response_flows_through_sync_stream():
  response = httpx2.Response(
      status_code=200,
      content=b'data: {"first": 1}\n\ndata: {"second": 2}\n\n',
  )
  http_response = api_client.HttpResponse(headers={}, response_stream=response)

  chunks = list(http_response._iter_response_stream())

  assert chunks == ['{"first": 1}', '{"second": 2}']


def test_default_client_uses_httpx(monkeypatch):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx.Client)
  assert isinstance(
      client._api_client._httpx_client, target_api_client.SyncHttpxClient
  )
  assert isinstance(client._api_client._async_httpx_client, httpx.AsyncClient)
  assert isinstance(
      client._api_client._async_httpx_client, target_api_client.AsyncHttpxClient
  )


def test_env_var_override_to_httpx(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx.Client)
  assert isinstance(
      client._api_client._httpx_client, target_api_client.SyncHttpxClient
  )
  assert isinstance(client._api_client._async_httpx_client, httpx.AsyncClient)
  assert isinstance(
      client._api_client._async_httpx_client, target_api_client.AsyncHttpxClient
  )


def test_env_var_override_to_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  assert isinstance(
      client._api_client._httpx_client, target_api_client.SyncHttpx2Client
  )
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)
  assert isinstance(
      client._api_client._async_httpx_client, target_api_client.AsyncHttpx2Client
  )


def test_env_var_auto(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'auto')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx.Client)


def test_env_var_unrecognized_falls_back_to_default(monkeypatch, caplog):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'unknown_client')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  with caplog.at_level('WARNING'):
    client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx.Client)
  assert 'Unrecognized GOOGLE_GENAI_HTTP_CLIENT' in caplog.text


def test_env_var_httpx2_missing_raises(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(target_api_client, 'httpx2', None)
  with pytest.raises(ImportError, match='httpx2 is configured'):
    Client(api_key='fake_api_key')


def test_env_var_httpx_missing_raises(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(target_api_client, 'httpx', None)
  with pytest.raises(ImportError, match='httpx is configured'):
    Client(api_key='fake_api_key')


def test_default_falls_back_to_httpx2_when_httpx_missing(monkeypatch):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(target_api_client, 'httpx', None)
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  assert isinstance(
      client._api_client._httpx_client, target_api_client.SyncHttpx2Client
  )
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)
  assert isinstance(
      client._api_client._async_httpx_client, target_api_client.AsyncHttpx2Client
  )


# High-level feature tests: end-to-end generate_content and streaming with httpx2
def test_generate_content_sync_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')

  def handler(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(
        status_code=200,
        json={
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Hello from httpx2 sync!'}],
                    'role': 'model',
                },
                'finishReason': 'STOP',
            }]
        },
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'transport': httpx2.MockTransport(handler)}
      ),
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='Hello',
  )
  assert response.text == 'Hello from httpx2 sync!'


@pytest.mark.asyncio
async def test_generate_content_async_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')

  def handler(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(
        status_code=200,
        json={
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Hello from httpx2 async!'}],
                    'role': 'model',
                },
                'finishReason': 'STOP',
            }]
        },
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          async_client_args={'transport': httpx2.MockTransport(handler)}
      ),
  )
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='Hello',
  )
  assert response.text == 'Hello from httpx2 async!'


def test_generate_content_stream_sync_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')

  def handler(request: httpx2.Request) -> httpx2.Response:
    stream_content = (
        b'data: {"candidates": [{"content": {"parts": [{"text": "Hello "}], "role": "model"}}]}\n\n'
        b'data: {"candidates": [{"content": {"parts": [{"text": "streaming world!"}], "role": "model"}}]}\n\n'
    )
    return httpx2.Response(
        status_code=200,
        content=stream_content,
        headers={'content-type': 'text/event-stream'},
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'transport': httpx2.MockTransport(handler)}
      ),
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  stream = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='Hello',
  )
  chunks = list(stream)
  assert len(chunks) == 2
  assert chunks[0].text == 'Hello '
  assert chunks[1].text == 'streaming world!'
  assert ''.join(c.text for c in chunks) == 'Hello streaming world!'


@pytest.mark.asyncio
async def test_generate_content_stream_async_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')

  def handler(request: httpx2.Request) -> httpx2.Response:
    stream_content = (
        b'data: {"candidates": [{"content": {"parts": [{"text": "Hello "}], "role": "model"}}]}\n\n'
        b'data: {"candidates": [{"content": {"parts": [{"text": "async streaming world!"}], "role": "model"}}]}\n\n'
    )
    return httpx2.Response(
        status_code=200,
        content=stream_content,
        headers={'content-type': 'text/event-stream'},
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          async_client_args={'transport': httpx2.MockTransport(handler)}
      ),
  )
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)
  stream = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='Hello',
  )
  chunks = [chunk async for chunk in stream]
  assert len(chunks) == 2
  assert chunks[0].text == 'Hello '
  assert chunks[1].text == 'async streaming world!'
  assert ''.join(c.text for c in chunks) == 'Hello async streaming world!'


def test_generate_content_injected_httpx2_client():
  def handler(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(
        status_code=200,
        json={
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Hello from injected httpx2!'}],
                    'role': 'model',
                },
                'finishReason': 'STOP',
            }]
        },
    )

  client = Client(
      api_key='fake_api_key',
      http_options={
          'httpx_client': httpx2.Client(transport=httpx2.MockTransport(handler)),
      },
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='Hello',
  )
  assert response.text == 'Hello from injected httpx2!'


def test_retry_on_httpx2_transient_exceptions():
  """Verifies tenacity retry predicate retries on httpx2 ConnectError and TimeoutException."""
  retry_opts = HttpOptions(
      retry_options=HttpRetryOptions(attempts=3, initial_delay=0.01)
  )
  retry_dict = api_client.retry_args(retry_opts.retry_options)
  predicate = retry_dict['retry'].predicate

  req = httpx2.Request('GET', 'https://example.com')
  assert predicate(httpx2.ConnectError('connection failed', request=req))
  assert predicate(httpx2.TimeoutException('timeout', request=req))
  assert predicate(httpx2.ReadTimeout('read timeout', request=req))


def test_retries_with_httpx2_client(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  attempts = 0

  def handler(request: httpx2.Request) -> httpx2.Response:
    nonlocal attempts
    attempts += 1
    if attempts < 2:
      raise httpx2.ConnectError('transient failure', request=request)
    return httpx2.Response(
        status_code=200,
        json={
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Retried successfully'}],
                    'role': 'model',
                },
                'finishReason': 'STOP',
            }]
        },
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'transport': httpx2.MockTransport(handler)},
          retry_options=HttpRetryOptions(attempts=3, initial_delay=0.01),
      ),
  )
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='Hello',
  )
  assert response.text == 'Retried successfully'
  assert attempts == 2


@pytest.mark.asyncio
async def test_async_download_file_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(target_api_client, 'has_aiohttp', False)

  def handler(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(status_code=200, content=b'file bytes content')

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          async_client_args={'transport': httpx2.MockTransport(handler)},
      ),
  )
  downloaded = await client._api_client.async_download_file('download/file.bin')
  assert downloaded == b'file bytes content'


def test_httpx2_filters_invalid_client_args(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'unsupported_dummy_arg': 123},
          async_client_args={'unsupported_dummy_arg': 123},
      ),
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)
  assert 'unsupported_dummy_arg' not in client._api_client._async_httpx_client_args


def test_httpx_filters_invalid_client_args(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx')
  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'unsupported_dummy_arg': 123},
          async_client_args={'unsupported_dummy_arg': 123},
      ),
  )
  assert isinstance(client._api_client._httpx_client, httpx.Client)
  assert isinstance(client._api_client._async_httpx_client, httpx.AsyncClient)
  assert 'unsupported_dummy_arg' not in client._api_client._async_httpx_client_args


@pytest.mark.asyncio
async def test_httpx2_client_close(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  client = Client(api_key='fake_api_key')
  sync_client = client._api_client._httpx_client
  async_client = client._api_client._async_httpx_client
  assert not sync_client.is_closed
  assert not async_client.is_closed

  client.close()
  assert sync_client.is_closed

  await client.aio.aclose()
  assert async_client.is_closed


@pytest.mark.asyncio
async def test_aclose_when_async_httpx_client_is_none(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  client = Client(api_key='fake_api_key')
  client._api_client._async_httpx_client = None
  # Should not raise AttributeError when _async_httpx_client is None
  await client.aio.aclose()


def test_vertexai_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  client = Client(
      vertexai=True,
      project='fake-project',
      location='us-central1',
      credentials=None,
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)


def test_env_var_case_insensitivity_and_whitespace(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', '  HTTPX2  ')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  assert isinstance(
      client._api_client._httpx_client, target_api_client.SyncHttpx2Client
  )

  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', '  HttPx  ')
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, httpx.Client)
  assert isinstance(
      client._api_client._httpx_client, target_api_client.SyncHttpxClient
  )


def test_raise_for_response_with_httpx2_json_error():
  response = httpx2.Response(
      status_code=400,
      json={
          'error': {
              'message': 'Invalid argument',
              'code': 400,
              'status': 'INVALID_ARGUMENT',
          }
      },
  )
  with pytest.raises(errors.ClientError) as exc_info:
    errors.APIError.raise_for_response(response)
  assert exc_info.value.code == 400
  assert 'Invalid argument' in str(exc_info.value)
  assert exc_info.value.response is response


def test_raise_for_response_with_httpx2_plain_text_error():
  response = httpx2.Response(
      status_code=503,
      text='Service Unavailable',
  )
  with pytest.raises(errors.ServerError) as exc_info:
    errors.APIError.raise_for_response(response)
  assert exc_info.value.code == 503
  assert 'Service Unavailable' in str(exc_info.value)
  assert exc_info.value.response is response


@pytest.mark.asyncio
async def test_raise_for_async_response_with_httpx2():
  response = httpx2.Response(
      status_code=404,
      json={'error': {'message': 'Resource not found', 'code': 404}},
  )
  with pytest.raises(errors.ClientError) as exc_info:
    await errors.APIError.raise_for_async_response(response)
  assert exc_info.value.code == 404
  assert 'Resource not found' in str(exc_info.value)
  assert exc_info.value.response is response


def test_generate_content_api_error_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')

  def handler(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(
        status_code=400,
        json={'error': {'message': 'Invalid prompt', 'code': 400}},
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'transport': httpx2.MockTransport(handler)},
          retry_options=HttpRetryOptions(attempts=1),
      ),
  )
  with pytest.raises(errors.ClientError) as exc_info:
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello',
    )
  assert exc_info.value.code == 400
  assert 'Invalid prompt' in str(exc_info.value)


@pytest.mark.asyncio
async def test_mcp_utils_respects_backend(monkeypatch):
  from ... import _mcp_utils
  from unittest import mock
  import contextlib

  captured_client = None

  @contextlib.asynccontextmanager
  async def mock_streamable_ctx(*args, **kwargs):
    yield (mock.Mock(), mock.Mock())

  def fake_streamable(*args, **kwargs):
    nonlocal captured_client
    captured_client = kwargs.get('http_client')
    return mock_streamable_ctx(*args, **kwargs)

  class DummySession:

    async def initialize(self):
      pass

  @contextlib.asynccontextmanager
  async def mock_session_ctx(*args, **kwargs):
    yield DummySession()

  monkeypatch.setattr(_mcp_utils, 'streamable_http_client', fake_streamable)
  monkeypatch.setattr(_mcp_utils, 'McpClientSession', mock_session_ctx)

  # Test httpx2 backend
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  client_httpx2 = Client(api_key='fake_key')
  monkeypatch.setattr(
      client_httpx2._api_client,
      '_async_access_token',
      mock.AsyncMock(return_value='fake-token'),
  )
  async with _mcp_utils._connect_agent_platform_mcp(
      client_httpx2._api_client, 'endpoints'
  ):
    pass
  assert isinstance(captured_client, httpx2.AsyncClient)

  # Test httpx backend
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx')
  client_httpx = Client(api_key='fake_key')
  monkeypatch.setattr(
      client_httpx._api_client,
      '_async_access_token',
      mock.AsyncMock(return_value='fake-token'),
  )
  async with _mcp_utils._connect_agent_platform_mcp(
      client_httpx._api_client, 'endpoints'
  ):
    pass
  assert isinstance(captured_client, httpx.AsyncClient)

  # Test when httpx is None (auto-fallback to httpx2)
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  monkeypatch.setattr(_mcp_utils, 'httpx', None)
  monkeypatch.setattr(target_api_client, 'httpx', None)
  client_fallback = Client(api_key='fake_key')
  monkeypatch.setattr(
      client_fallback._api_client,
      '_async_access_token',
      mock.AsyncMock(return_value='fake-token'),
  )
  async with _mcp_utils._connect_agent_platform_mcp(
      client_fallback._api_client, 'endpoints'
  ):
    pass
  assert isinstance(captured_client, httpx2.AsyncClient)



