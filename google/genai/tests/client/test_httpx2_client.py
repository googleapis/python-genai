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

import io
import ssl

import httpx
import pytest

try:
  import httpx2
  import truststore
except ImportError:
  httpx2 = None
  truststore = None

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


def _client_classes(backend):
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  if backend == 'httpx2':
    return (
        httpx2.Client,
        httpx2.AsyncClient,
        target_api_client.SyncHttpx2Client,
        target_api_client.AsyncHttpx2Client,
    )
  return (
      httpx.Client,
      httpx.AsyncClient,
      target_api_client.SyncHttpxClient,
      target_api_client.AsyncHttpxClient,
  )


def _set_default_backend(monkeypatch, backend):
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(
      target_api_client, '_DEFAULT_HTTP_CLIENT_BACKEND', backend
  )


@pytest.mark.parametrize('default_backend', ['httpx', 'httpx2'])
def test_default_client_uses_default_backend(monkeypatch, default_backend):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  _set_default_backend(monkeypatch, default_backend)
  sync_cls, async_cls, sdk_sync_cls, sdk_async_cls = _client_classes(
      default_backend
  )
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, sync_cls)
  assert isinstance(client._api_client._httpx_client, sdk_sync_cls)
  assert isinstance(client._api_client._async_httpx_client, async_cls)
  assert isinstance(client._api_client._async_httpx_client, sdk_async_cls)


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




@pytest.mark.parametrize('default_backend', ['httpx', 'httpx2'])
def test_env_var_auto(monkeypatch, default_backend):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'auto')
  _set_default_backend(monkeypatch, default_backend)
  sync_cls, *_ = _client_classes(default_backend)
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, sync_cls)


@pytest.mark.parametrize('default_backend', ['httpx', 'httpx2'])
def test_env_var_unrecognized_falls_back_to_default(
    monkeypatch, caplog, default_backend
):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'unknown_client')
  _set_default_backend(monkeypatch, default_backend)
  sync_cls, *_ = _client_classes(default_backend)
  with caplog.at_level('WARNING'):
    client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, sync_cls)
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




@pytest.mark.parametrize(
    'default_backend,fallback_backend',
    [('httpx', 'httpx2'), ('httpx2', 'httpx')],
)
def test_default_falls_back_when_default_backend_missing(
    monkeypatch, default_backend, fallback_backend
):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  _set_default_backend(monkeypatch, default_backend)
  monkeypatch.setattr(target_api_client, default_backend, None)
  sync_cls, async_cls, sdk_sync_cls, sdk_async_cls = _client_classes(
      fallback_backend
  )
  client = Client(api_key='fake_api_key')
  assert isinstance(client._api_client._httpx_client, sync_cls)
  assert isinstance(client._api_client._httpx_client, sdk_sync_cls)
  assert isinstance(client._api_client._async_httpx_client, async_cls)
  assert isinstance(client._api_client._async_httpx_client, sdk_async_cls)


def test_default_raises_when_no_backend_installed(monkeypatch):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(target_api_client, 'httpx', None)
  monkeypatch.setattr(target_api_client, 'httpx2', None)
  with pytest.raises(ImportError, match='Neither httpx nor httpx2'):
    target_api_client._get_http_client_backend()


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
  # Keep the async path on httpx2 even when aiohttp is installed.
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(target_api_client, 'has_aiohttp', False)
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


def test_sync_upload_file_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  recorded_requests = []

  def handler(request: httpx2.Request) -> httpx2.Response:
    recorded_requests.append(request)
    return httpx2.Response(
        status_code=200,
        headers={'x-goog-upload-status': 'final'},
        content=b'{"name": "files/test-file"}',
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'transport': httpx2.MockTransport(handler)},
      ),
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  content = b'hello world file content'
  response = client._api_client.upload_file(
      file_path=io.BytesIO(content),
      upload_url='https://upload.example.com/files',
      upload_size=len(content),
  )
  assert len(recorded_requests) == 1
  assert (
      recorded_requests[0].headers['x-goog-upload-command']
      == 'upload, finalize'
  )
  assert recorded_requests[0].headers['x-goog-upload-offset'] == '0'
  assert response.response_stream == ['{"name": "files/test-file"}']


@pytest.mark.asyncio
async def test_async_upload_file_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  target_api_client = getattr(api_client, 'public_api_client', api_client)
  monkeypatch.setattr(target_api_client, 'has_aiohttp', False)
  recorded_requests = []

  def handler(request: httpx2.Request) -> httpx2.Response:
    recorded_requests.append(request)
    return httpx2.Response(
        status_code=200,
        headers={'x-goog-upload-status': 'final'},
        content=b'{"name": "files/async-test-file"}',
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          async_client_args={'transport': httpx2.MockTransport(handler)},
      ),
  )
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)
  content = b'async hello world file content'
  response = await client._api_client.async_upload_file(
      file_path=io.BytesIO(content),
      upload_url='https://upload.example.com/files',
      upload_size=len(content),
  )
  assert len(recorded_requests) == 1
  assert (
      recorded_requests[0].headers['x-goog-upload-command']
      == 'upload, finalize'
  )
  assert recorded_requests[0].headers['x-goog-upload-offset'] == '0'
  assert recorded_requests[0].read() == content
  assert response.response_stream == ['{"name": "files/async-test-file"}']


def test_retries_on_http_status_codes_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  attempts = 0

  def handler(request: httpx2.Request) -> httpx2.Response:
    nonlocal attempts
    attempts += 1
    if attempts < 2:
      return httpx2.Response(
          status_code=429,
          json={
              'error': {
                  'message': 'Resource has been exhausted (rate limit)',
                  'code': 429,
              }
          },
      )
    return httpx2.Response(
        status_code=200,
        json={
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Retried after rate limit'}],
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
  assert response.text == 'Retried after rate limit'
  assert attempts == 2


@pytest.mark.asyncio
async def test_async_retries_on_http_status_codes_with_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  attempts = 0

  def handler(request: httpx2.Request) -> httpx2.Response:
    nonlocal attempts
    attempts += 1
    if attempts < 2:
      return httpx2.Response(
          status_code=503,
          text='Service Unavailable',
      )
    return httpx2.Response(
        status_code=200,
        json={
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Retried after 503'}],
                    'role': 'model',
                },
                'finishReason': 'STOP',
            }]
        },
    )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          async_client_args={'transport': httpx2.MockTransport(handler)},
          retry_options=HttpRetryOptions(attempts=3, initial_delay=0.01),
      ),
  )
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='Hello',
  )
  assert response.text == 'Retried after 503'
  assert attempts == 2


def test_ensure_httpx2_ssl_ctx_default_uses_truststore(monkeypatch):
  monkeypatch.delenv('SSL_CERT_FILE', raising=False)
  monkeypatch.delenv('SSL_CERT_DIR', raising=False)
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(
          HttpOptions(),
          vertexai=False,
          client_cls=api_client.SyncHttpx2Client,
          async_client_cls=api_client.AsyncHttpx2Client,
      )
  )
  assert isinstance(client_args['verify'], truststore.SSLContext)
  assert isinstance(async_client_args['verify'], truststore.SSLContext)


def test_ensure_httpx2_ssl_ctx_custom_verify():
  custom_ctx = ssl.create_default_context()
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(
          HttpOptions(
              client_args={'verify': custom_ctx},
              async_client_args={'verify': custom_ctx},
          ),
          vertexai=False,
          client_cls=api_client.SyncHttpx2Client,
          async_client_cls=api_client.AsyncHttpx2Client,
      )
  )
  assert client_args['verify'] is custom_ctx
  assert async_client_args['verify'] is custom_ctx
  assert client_args.get('timeout') is None


def test_ensure_httpx2_ssl_ctx_filters_unsupported_params():
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(
          HttpOptions(
              client_args={'unsupported_dummy_key': 'foo'},
              async_client_args={'unsupported_dummy_key': 'foo'},
          ),
          vertexai=False,
          client_cls=api_client.SyncHttpx2Client,
          async_client_cls=api_client.AsyncHttpx2Client,
      )
  )
  assert 'unsupported_dummy_key' not in client_args
  assert 'unsupported_dummy_key' not in async_client_args
  assert isinstance(client_args['verify'], ssl.SSLContext)


def test_client_init_with_custom_ssl_context_httpx2(monkeypatch):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  custom_ctx = ssl.create_default_context()
  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          client_args={'verify': custom_ctx},
          async_client_args={'verify': custom_ctx},
      ),
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)


def test_ensure_httpx2_ssl_ctx_with_ssl_cert_file_env(monkeypatch):
  import certifi

  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  monkeypatch.setenv('SSL_CERT_FILE', certifi.where())
  monkeypatch.delenv('SSL_CERT_DIR', raising=False)
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(
          HttpOptions(),
          vertexai=False,
      )
  )
  assert isinstance(client_args['verify'], ssl.SSLContext)
  assert not isinstance(client_args['verify'], truststore.SSLContext)
  assert isinstance(async_client_args['verify'], ssl.SSLContext)


def test_auto_detect_httpx_from_injected_client_when_default_httpx2(
    monkeypatch,
):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  _set_default_backend(monkeypatch, 'httpx2')

  # Only sync httpx.Client injected -> async client should also use httpx
  sync_injected = httpx.Client()
  client_sync = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(httpx_client=sync_injected),
  )
  assert client_sync._api_client._httpx_client is sync_injected
  assert isinstance(
      client_sync._api_client._async_httpx_client, httpx.AsyncClient
  )

  # Only async httpx.AsyncClient injected -> sync client should also use httpx
  async_injected = httpx.AsyncClient()
  client_async = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(httpx_async_client=async_injected),
  )
  assert isinstance(client_async._api_client._httpx_client, httpx.Client)
  assert client_async._api_client._async_httpx_client is async_injected


def test_auto_detect_httpx2_from_injected_client_when_default_httpx(
    monkeypatch,
):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  _set_default_backend(monkeypatch, 'httpx')

  # Only sync httpx2.Client injected -> async client should also use httpx2
  sync_injected = httpx2.Client()
  client_sync = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(httpx_client=sync_injected),
  )
  assert client_sync._api_client._httpx_client is sync_injected
  assert isinstance(
      client_sync._api_client._async_httpx_client, httpx2.AsyncClient
  )

  # Only async httpx2.AsyncClient injected -> sync client should also use httpx2
  async_injected = httpx2.AsyncClient()
  client_async = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(httpx_async_client=async_injected),
  )
  assert isinstance(client_async._api_client._httpx_client, httpx2.Client)
  assert client_async._api_client._async_httpx_client is async_injected


@pytest.mark.parametrize(
    'arg_key,httpx_val_fn,httpx2_val_fn',
    [
        (
            'transport',
            lambda: httpx.MockTransport(lambda req: httpx.Response(200)),
            lambda: httpx2.MockTransport(lambda req: httpx2.Response(200)),
        ),
        ('timeout', lambda: httpx.Timeout(5.0), lambda: httpx2.Timeout(5.0)),
        (
            'auth',
            lambda: httpx.BasicAuth('u', 'p'),
            lambda: httpx2.BasicAuth('u', 'p'),
        ),
        (
            'limits',
            lambda: httpx.Limits(max_connections=5),
            lambda: httpx2.Limits(max_connections=5),
        ),
        (
            'proxy',
            lambda: httpx.Proxy('http://localhost:8080'),
            lambda: httpx2.Proxy('http://localhost:8080'),
        ),
    ],
)
def test_auto_detect_backend_from_client_args(
    monkeypatch, arg_key, httpx_val_fn, httpx2_val_fn
):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'auto')

  # When default is httpx2, passing httpx.* object in client_args selects httpx
  _set_default_backend(monkeypatch, 'httpx2')
  client_httpx = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(client_args={arg_key: httpx_val_fn()}),
  )
  assert isinstance(client_httpx._api_client._httpx_client, httpx.Client)
  assert isinstance(
      client_httpx._api_client._async_httpx_client, httpx.AsyncClient
  )

  # When default is httpx, passing httpx2.* object in client_args selects httpx2
  _set_default_backend(monkeypatch, 'httpx')
  client_httpx2 = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(client_args={arg_key: httpx2_val_fn()}),
  )
  assert isinstance(client_httpx2._api_client._httpx_client, httpx2.Client)
  assert isinstance(
      client_httpx2._api_client._async_httpx_client, httpx2.AsyncClient
  )


def test_auto_detect_backend_from_async_client_args(monkeypatch):
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)

  class CustomAsyncTransport(httpx.AsyncBaseTransport):

    async def handle_async_request(
        self, request: httpx.Request
    ) -> httpx.Response:
      return httpx.Response(200)

  class CustomAsyncTransport2(httpx2.AsyncBaseTransport):

    async def handle_async_request(
        self, request: httpx2.Request
    ) -> httpx2.Response:
      return httpx2.Response(200)

  _set_default_backend(monkeypatch, 'httpx2')
  client_httpx = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          async_client_args={'transport': CustomAsyncTransport()}
      ),
  )
  assert isinstance(client_httpx._api_client._httpx_client, httpx.Client)
  assert isinstance(
      client_httpx._api_client._async_httpx_client, httpx.AsyncClient
  )

  _set_default_backend(monkeypatch, 'httpx')
  client_httpx2 = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          async_client_args={'transport': CustomAsyncTransport2()}
      ),
  )
  assert isinstance(client_httpx2._api_client._httpx_client, httpx2.Client)
  assert isinstance(
      client_httpx2._api_client._async_httpx_client, httpx2.AsyncClient
  )


def test_skips_ensure_httpx_ssl_ctx_when_both_custom_clients_provided(
    monkeypatch,
):
  from unittest import mock

  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  with (
      mock.patch.object(
          api_client.BaseApiClient,
          '_ensure_httpx_ssl_ctx',
          wraps=api_client.BaseApiClient._ensure_httpx_ssl_ctx,
      ) as spy_ensure,
      mock.patch.object(
          httpx2, 'create_ssl_context', wraps=httpx2.create_ssl_context
      ) as spy_create_ssl,
  ):
    client = Client(
        api_key='fake_api_key',
        http_options=HttpOptions(
            httpx_client=httpx2.Client(trust_env=False),
            httpx_async_client=httpx2.AsyncClient(trust_env=False),
        ),
    )
    spy_ensure.assert_not_called()
    spy_create_ssl.assert_not_called()
    assert client._api_client._async_httpx_client_args == {}


def test_gaos_basesdk_use_client_default_and_timeout():
  from ..._gaos import basesdk

  httpx_client = httpx.Client()
  httpx2_client = httpx2.Client()
  assert (
      basesdk._use_client_default(httpx_client) is httpx.USE_CLIENT_DEFAULT
  )
  assert (
      basesdk._use_client_default(httpx2_client) is httpx2.USE_CLIENT_DEFAULT
  )

  client = Client(
      api_key='fake_api_key',
      http_options=HttpOptions(
          httpx_client=httpx2_client,
          httpx_async_client=httpx2.AsyncClient(),
      ),
  )
  req_default = client.interactions._build_request(
      method='GET',
      path='/v1beta/interactions/123',
      base_url='https://example.com',
      url_variables=None,
      request=None,
      request_body_required=False,
      request_has_path_params=False,
      request_has_query_params=False,
      user_agent_header='user-agent',
      accept_header_value='application/json',
      timeout_ms=None,
  )
  assert req_default.extensions['timeout'] == {
      'connect': 5.0,
      'read': 5.0,
      'write': 5.0,
      'pool': 5.0,
  }

  req_timeout = client.interactions._build_request(
      method='GET',
      path='/v1beta/interactions/123',
      base_url='https://example.com',
      url_variables=None,
      request=None,
      request_body_required=False,
      request_has_path_params=False,
      request_has_query_params=False,
      user_agent_header='user-agent',
      accept_header_value='application/json',
      timeout_ms=2500,
  )
  assert req_timeout.extensions['timeout'] == {
      'connect': 2.5,
      'read': 2.5,
      'write': 2.5,
      'pool': 2.5,
  }

  async_req_default = client.aio.interactions._build_request_async(
      method='GET',
      path='/v1beta/interactions/123',
      base_url='https://example.com',
      url_variables=None,
      request=None,
      request_body_required=False,
      request_has_path_params=False,
      request_has_query_params=False,
      user_agent_header='user-agent',
      accept_header_value='application/json',
      timeout_ms=None,
  )
  assert async_req_default.extensions['timeout'] == {
      'connect': 5.0,
      'read': 5.0,
      'write': 5.0,
      'pool': 5.0,
  }

  async_req_timeout = client.aio.interactions._build_request_async(
      method='GET',
      path='/v1beta/interactions/123',
      base_url='https://example.com',
      url_variables=None,
      request=None,
      request_body_required=False,
      request_has_path_params=False,
      request_has_query_params=False,
      user_agent_header='user-agent',
      accept_header_value='application/json',
      timeout_ms=2500,
  )
  assert async_req_timeout.extensions['timeout'] == {
      'connect': 2.5,
      'read': 2.5,
      'write': 2.5,
      'pool': 2.5,
  }



# SSL / mTLS security tests.
#
# These record the kwargs passed to the SDK-built client constructors, so they
# assert on the `verify` SSL context each real client is created with (rather
# than on intermediate helper return values).

_VERTEX_URL = 'https://us-central1-aiplatform.googleapis.com/v1'
_VERTEX_MTLS_URL = 'https://us-central1-aiplatform.mtls.googleapis.com/v1'


def _target_api_client():
  return getattr(api_client, 'public_api_client', api_client)


def _record_client_init(monkeypatch, backend):
  """Records constructor kwargs for the SDK's sync/async clients of `backend`."""
  _, _, sdk_sync_cls, sdk_async_cls = _client_classes(backend)
  calls = {'sync': [], 'async': []}
  for key, cls in (('sync', sdk_sync_cls), ('async', sdk_async_cls)):
    original_init = cls.__init__

    def _init(self, _original_init=original_init, _key=key, **kwargs):
      calls[_key].append(kwargs)
      _original_init(self, **kwargs)

    monkeypatch.setattr(cls, '__init__', _init)
  return calls


@pytest.fixture
def no_ssl_env(monkeypatch):
  monkeypatch.delenv('SSL_CERT_FILE', raising=False)
  monkeypatch.delenv('SSL_CERT_DIR', raising=False)


@pytest.fixture
def client_cert(monkeypatch):
  """Simulates a configured default client certificate; returns its context."""
  from google.auth.transport import mtls

  cert_ctx = ssl.create_default_context()
  monkeypatch.delenv('GOOGLE_API_USE_MTLS_ENDPOINT', raising=False)
  monkeypatch.setattr(
      mtls, 'should_use_client_cert', lambda: True, raising=False
  )
  monkeypatch.setattr(mtls, 'has_default_client_cert_source', lambda: True)
  monkeypatch.setattr(mtls, 'get_default_ssl_context', lambda: cert_ctx)
  # Keep the async path on httpx (not AsyncAuthorizedSession/aiohttp) so the
  # SDK-built async httpx client is exercised.
  monkeypatch.setattr(_target_api_client(), 'has_aiohttp', False)
  return cert_ctx


def _vertex_client(**http_options):
  return Client(
      vertexai=True,
      project='fake-project',
      location='us-central1',
      http_options=http_options,
  )


@pytest.mark.parametrize('backend', ['httpx', 'httpx2'])
@pytest.mark.parametrize('injected', ['sync', 'async'])
def test_single_injected_client_other_client_still_gets_sdk_ssl_ctx(
    monkeypatch, no_ssl_env, backend, injected
):
  """Injecting one client must not skip SSL setup for the SDK-built one."""
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', backend)
  sync_cls, async_cls, _, _ = _client_classes(backend)
  calls = _record_client_init(monkeypatch, backend)

  if injected == 'sync':
    http_options = HttpOptions(httpx_client=sync_cls())
    built = 'async'
  else:
    http_options = HttpOptions(httpx_async_client=async_cls())
    built = 'sync'
  Client(api_key='fake_api_key', http_options=http_options)

  assert calls[injected] == []
  assert len(calls[built]) == 1
  verify = calls[built][0]['verify']
  assert isinstance(verify, ssl.SSLContext)
  assert isinstance(verify, truststore.SSLContext) == (backend == 'httpx2')


@pytest.mark.parametrize('backend', ['httpx', 'httpx2'])
@pytest.mark.parametrize('injected', ['sync', 'async'])
def test_vertex_single_injected_client_other_client_keeps_client_cert(
    monkeypatch, client_cert, backend, injected
):
  """The SDK-built client keeps the client cert and uses the mTLS endpoint."""
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', backend)
  sync_cls, async_cls, _, _ = _client_classes(backend)
  calls = _record_client_init(monkeypatch, backend)

  if injected == 'sync':
    client = _vertex_client(httpx_client=sync_cls())
    built = 'async'
  else:
    client = _vertex_client(httpx_async_client=async_cls())
    built = 'sync'

  assert calls[injected] == []
  assert len(calls[built]) == 1
  assert calls[built][0]['verify'] is client_cert
  assert client._api_client._httpx_url(
      _VERTEX_URL, is_async=(built == 'async')
  ) == _VERTEX_MTLS_URL
  # The caller-supplied client does not present the SDK's client cert, so it
  # must not be routed to the mTLS endpoint.
  assert client._api_client._httpx_url(
      _VERTEX_URL, is_async=(injected == 'async')
  ) == _VERTEX_URL


@pytest.mark.parametrize('backend', ['httpx', 'httpx2'])
def test_vertex_both_injected_clients_skip_ssl_and_mtls_endpoint(
    monkeypatch, client_cert, backend
):
  """With both clients injected, no httpx SSL setup and no mTLS routing."""
  from unittest import mock

  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', backend)
  sync_cls, async_cls, _, _ = _client_classes(backend)
  calls = _record_client_init(monkeypatch, backend)
  sync_injected = sync_cls()
  async_injected = async_cls()

  with mock.patch.object(
      _target_api_client().BaseApiClient,
      '_ensure_httpx_ssl_ctx',
      wraps=_target_api_client().BaseApiClient._ensure_httpx_ssl_ctx,
  ) as spy_ensure:
    client = _vertex_client(
        httpx_client=sync_injected, httpx_async_client=async_injected
    )

  spy_ensure.assert_not_called()
  assert calls == {'sync': [], 'async': []}
  assert client._api_client._httpx_client is sync_injected
  assert client._api_client._async_httpx_client is async_injected
  assert client._api_client._httpx_url(_VERTEX_URL, is_async=False) == (
      _VERTEX_URL
  )
  assert client._api_client._httpx_url(_VERTEX_URL, is_async=True) == (
      _VERTEX_URL
  )


@pytest.mark.parametrize('backend', ['httpx', 'httpx2'])
def test_vertex_client_cert_takes_precedence_over_default_ctx(
    monkeypatch, client_cert, no_ssl_env, backend
):
  """The client-cert context wins over truststore/certifi for both clients."""
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', backend)
  calls = _record_client_init(monkeypatch, backend)

  client = _vertex_client()

  assert calls['sync'][0]['verify'] is client_cert
  assert calls['async'][0]['verify'] is client_cert
  assert client._api_client._httpx_url(_VERTEX_URL, is_async=False) == (
      _VERTEX_MTLS_URL
  )
  assert client._api_client._httpx_url(_VERTEX_URL, is_async=True) == (
      _VERTEX_MTLS_URL
  )


@pytest.mark.parametrize(
    'default_backend,detected_backend', [('httpx2', 'httpx'), ('httpx', 'httpx2')]
)
def test_auto_detected_backend_selects_matching_ssl_ctx(
    monkeypatch, no_ssl_env, default_backend, detected_backend
):
  """Auto-detection picks the SSL context for the detected backend.

  httpx -> certifi-based `ssl.SSLContext`; httpx2 -> truststore. Both the sync
  client (with the detected transport) and the async client (built from empty
  async_client_args, i.e. a real network client) must get it.
  """
  monkeypatch.delenv('GOOGLE_GENAI_HTTP_CLIENT', raising=False)
  _set_default_backend(monkeypatch, default_backend)
  calls = _record_client_init(monkeypatch, detected_backend)
  module = httpx2 if detected_backend == 'httpx2' else httpx
  transport = module.MockTransport(lambda req: module.Response(200))

  Client(api_key='fake_api_key', http_options={'client_args': {'transport': transport}})

  for key in ('sync', 'async'):
    assert len(calls[key]) == 1
    verify = calls[key][0]['verify']
    assert isinstance(verify, ssl.SSLContext)
    assert isinstance(verify, truststore.SSLContext) == (
        detected_backend == 'httpx2'
    )
  assert calls['sync'][0]['transport'] is transport


def test_ensure_httpx2_ssl_ctx_with_ssl_cert_dir_env(monkeypatch, tmp_path):
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', 'httpx2')
  monkeypatch.delenv('SSL_CERT_FILE', raising=False)
  monkeypatch.setenv('SSL_CERT_DIR', str(tmp_path))
  client_args, async_client_args = (
      api_client.BaseApiClient._ensure_httpx_ssl_ctx(HttpOptions())
  )
  for args in (client_args, async_client_args):
    assert isinstance(args['verify'], ssl.SSLContext)
    assert not isinstance(args['verify'], truststore.SSLContext)


@pytest.mark.parametrize('backend', ['httpx', 'httpx2'])
def test_custom_verify_in_client_args_is_not_overridden(
    monkeypatch, client_cert, backend
):
  """A caller's `verify` SSL context is never replaced by the SDK's."""
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', backend)
  calls = _record_client_init(monkeypatch, backend)
  custom_ctx = ssl.create_default_context()

  client = _vertex_client(
      client_args={'verify': custom_ctx},
      async_client_args={'verify': custom_ctx},
  )

  assert calls['sync'][0]['verify'] is custom_ctx
  assert calls['async'][0]['verify'] is custom_ctx
  # The custom context doesn't carry the SDK's client cert: no mTLS routing.
  assert client._api_client._httpx_url(_VERTEX_URL, is_async=False) == (
      _VERTEX_URL
  )
  assert client._api_client._httpx_url(_VERTEX_URL, is_async=True) == (
      _VERTEX_URL
  )
