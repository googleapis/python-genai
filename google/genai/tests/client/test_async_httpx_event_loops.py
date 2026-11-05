# Copyright 2026 Google LLC
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

"""Tests for reusing the async httpx and httpx2 clients across event loops."""

import asyncio
import http.server
import json
import threading
import time
from typing import Optional

import httpx
import pytest

try:
  import httpx2
except ImportError:
  httpx2 = None

from ... import _api_client as api_client
from ... import Client

_GENERATE_CONTENT_RESPONSE = json.dumps({
    'candidates': [{
        'content': {'role': 'model', 'parts': [{'text': 'ok'}]},
        'finishReason': 'STOP',
    }]
})


@pytest.fixture(params=['httpx', 'httpx2'])
def backend(request, monkeypatch):
  if request.param == 'httpx2' and httpx2 is None:
    pytest.skip('httpx2 is not available')
  # Kokoro runs the whole suite with GOOGLE_GENAI_HTTP_CLIENT=httpx2.
  monkeypatch.setenv('GOOGLE_GENAI_HTTP_CLIENT', request.param)
  return request.param


@pytest.fixture
def httpx_module(backend):
  return httpx2 if backend == 'httpx2' else httpx


@pytest.fixture
def client_cls(backend):
  if backend == 'httpx2':
    return api_client.AsyncHttpx2Client
  return api_client.AsyncHttpxClient


def test_one_client_per_loop(client_cls, httpx_module):
  """All requests on one loop share one inner client."""

  async def get_client():
    return client._client_for_running_loop()

  async def get_twice():
    return await get_client(), await get_client()

  client = client_cls()
  first, second = asyncio.run(get_twice())
  third = asyncio.run(get_client())

  assert first is second
  assert third is not first
  assert type(first) is httpx_module.AsyncClient


def test_aclose_closes_client_for_current_loop(client_cls):
  """aclose() closes the current loop's pool and rejects later sends."""

  async def run():
    outer = client_cls()
    inner = outer._client_for_running_loop()
    await outer.aclose()
    assert outer.is_closed
    assert inner.is_closed
    assert not outer._loop_clients
    with pytest.raises(RuntimeError, match='client has been closed'):
      await outer.send(outer.build_request('GET', 'http://example.com/'))

  asyncio.run(run())


def test_aclose_closes_client_for_other_running_loop(client_cls, httpx_module):
  """aclose() schedules closing a pool that belongs to another live loop."""
  other_loop = asyncio.new_event_loop()
  thread = threading.Thread(target=other_loop.run_forever, daemon=True)
  thread.start()
  try:
    outer = client_cls()
    inner = httpx_module.AsyncClient()
    outer._loop_clients[other_loop] = inner

    async def close():
      await outer.aclose()

    asyncio.run(close())
    deadline = time.monotonic() + 5
    while not inner.is_closed and time.monotonic() < deadline:
      time.sleep(0.01)

    assert outer.is_closed
    assert inner.is_closed
  finally:
    other_loop.call_soon_threadsafe(other_loop.stop)
    thread.join(5)
    other_loop.close()


def test_custom_transport_uses_single_client(client_cls, httpx_module):
  """A caller-supplied transport keeps the single outer client."""
  transport = httpx_module.MockTransport(
      lambda request: httpx_module.Response(200)
  )
  client = client_cls(transport=transport)

  async def call():
    return await client.get('http://example.com/')

  assert asyncio.run(call()).status_code == 200
  assert not client._loop_clients


class _Handler(http.server.BaseHTTPRequestHandler):
  """Keep-alive server that records each request's Cookie header."""

  protocol_version = 'HTTP/1.1'
  cookies: list[Optional[str]] = []

  def _respond(self, content_type: str, body: str) -> None:
    self.cookies.append(self.headers.get('Cookie'))
    payload = body.encode()
    self.send_response(200)
    self.send_header('Content-Type', content_type)
    self.send_header('Content-Length', str(len(payload)))
    self.send_header('Set-Cookie', 'session=abc; Path=/')
    self.end_headers()
    self.wfile.write(payload)

  def do_POST(self) -> None:
    self.rfile.read(int(self.headers.get('Content-Length', 0)))
    if 'streamGenerateContent' in self.path:
      self._respond(
          'text/event-stream', f'data: {_GENERATE_CONTENT_RESPONSE}\r\n\r\n'
      )
    else:
      self._respond('application/json', _GENERATE_CONTENT_RESPONSE)

  def do_GET(self) -> None:
    self._respond(
        'application/json', json.dumps({'id': 'test-id', 'status': 'completed'})
    )

  def log_message(self, *args) -> None:
    pass


@pytest.fixture
def handler():
  return type('Handler', (_Handler,), {'cookies': []})


@pytest.fixture
def base_url(handler, monkeypatch):
  for var in (
      'http_proxy',
      'https_proxy',
      'all_proxy',
      'HTTP_PROXY',
      'HTTPS_PROXY',
      'ALL_PROXY',
  ):
    monkeypatch.delenv(var, raising=False)
  server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  yield f'http://127.0.0.1:{server.server_port}/'
  server.shutdown()
  server.server_close()


@pytest.fixture
def client(base_url, backend, monkeypatch):
  monkeypatch.setattr(api_client, 'has_aiohttp', False)
  return Client(
      vertexai=False,
      api_key='test-api-key',
      http_options={'base_url': base_url},
  )


def test_client_uses_backend_async_client(client, client_cls):
  """The SDK client below is built on the selected backend's async client."""
  assert type(client._api_client._async_httpx_client) is client_cls


def test_generate_content_across_event_loops(client):
  """Each asyncio.run() call succeeds on a client shared across loops."""

  async def call():
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash', contents='hi'
    )
    return response.text

  assert [asyncio.run(call()) for _ in range(3)] == ['ok', 'ok', 'ok']


def test_generate_content_stream_across_event_loops(client):
  """Streaming succeeds on every loop, not only every other one."""

  async def call():
    stream = await client.aio.models.generate_content_stream(
        model='gemini-2.5-flash', contents='hi'
    )
    return [chunk.text async for chunk in stream]

  assert [asyncio.run(call()) for _ in range(3)] == [['ok']] * 3


def test_interactions_across_event_loops(client):
  """The interactions bridge shares the httpx client and must work too."""

  async def call():
    interaction = await client.aio.interactions.get(id='test-id')
    return interaction.status

  assert [asyncio.run(call()) for _ in range(3)] == ['completed'] * 3


def test_closed_loop_pools_are_discarded(client):
  """Only the pool for a live loop is kept; closed loops are pruned."""

  async def call():
    await client.aio.models.generate_content(
        model='gemini-2.5-flash', contents='hi'
    )

  for _ in range(3):
    asyncio.run(call())

  assert len(client._api_client._async_httpx_client._loop_clients) == 1


def test_cookies_persist_across_event_loops(client, handler):
  """A cookie set on one loop is sent on the next loop."""

  async def call():
    await client.aio.models.generate_content(
        model='gemini-2.5-flash', contents='hi'
    )

  asyncio.run(call())
  asyncio.run(call())

  assert handler.cookies == [None, 'session=abc']
