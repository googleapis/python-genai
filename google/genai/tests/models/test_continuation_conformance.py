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


"""Runs the shared automatic continuation conformance cases.

The cases live in a language-neutral JSON file shared by all the SDKs
(google/cloud/aiplatform/sdk/genai/replays/conformance/
automatic_continuation.json); its "notation" section describes the format. Each
case scripts the server's response to every HTTP request; this runner fakes the
API client's transport accordingly, calls the SDK (sync and async), and checks
the requests it sent and what it returned.
"""

import base64
import json
import os
from typing import Any, Optional

import httpx
import pytest

from ... import client as client_lib
from ... import errors
from ... import types

_SPEC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '../../../../../../google/cloud/aiplatform/sdk/genai/replays/'
        'conformance/automatic_continuation.json',
    )
)

if os.path.isfile(_SPEC_PATH):
  with open(_SPEC_PATH) as _f:
    _CASES = json.load(_f)['cases']
else:
  _CASES = []

pytestmark = pytest.mark.skipif(
    not _CASES, reason=f'Conformance spec not found: {_SPEC_PATH}'
)


def _encode_token(name: str) -> str:
  return base64.b64encode(name.encode()).decode()


def _decode_token(value: Any) -> Optional[str]:
  if value is None:
    return None
  if isinstance(value, bytes):
    return value.decode()
  value = value.replace('-', '+').replace('_', '/')
  return base64.b64decode(value + '=' * (-len(value) % 4)).decode()


def _wire_response(r: dict[str, Any]) -> dict[str, Any]:
  """Converts a case response to the API's JSON wire format."""
  payload: dict[str, Any] = {}
  if any(k in r for k in ('text', 'token', 'finish')):
    candidate: dict[str, Any] = {'index': 0}
    if 'text' in r:
      candidate['content'] = {'role': 'model', 'parts': [{'text': r['text']}]}
    if 'finish' in r:
      candidate['finishReason'] = r['finish']
    if 'token' in r:
      candidate['continuationToken'] = _encode_token(r['token'])
    payload['candidates'] = [candidate]
  if 'prompt_feedback' in r:
    payload['promptFeedback'] = {'blockReason': r['prompt_feedback']}
  if 'usage' in r:
    names = {
        'prompt': 'promptTokenCount',
        'candidates': 'candidatesTokenCount',
        'total': 'totalTokenCount',
    }
    payload['usageMetadata'] = {names[k]: v for k, v in r['usage'].items()}
  return payload


def _error_body(code: int) -> str:
  return json.dumps(
      {'error': {'code': code, 'message': 'conformance', 'status': 'ERROR'}}
  )


def _transport_error() -> Exception:
  return httpx.RemoteProtocolError('peer closed connection')


class _SyncStream(httpx.SyncByteStream):

  def __init__(self, hop: dict[str, Any]):
    self._hop = hop

  def __iter__(self):
    for chunk in self._hop['chunks']:
      payload = (
          _error_body(chunk['error'])
          if 'error' in chunk
          else json.dumps(_wire_response(chunk))
      )
      yield f'data: {payload}\n\n'.encode()
    if self._hop.get('then') == 'drop':
      raise _transport_error()


class _AsyncStream(httpx.AsyncByteStream):

  def __init__(self, hop: dict[str, Any]):
    self._hop = hop

  async def __aiter__(self):
    for chunk in self._hop['chunks']:
      payload = (
          _error_body(chunk['error'])
          if 'error' in chunk
          else json.dumps(_wire_response(chunk))
      )
      yield f'data: {payload}\n\n'.encode()
    if self._hop.get('then') == 'drop':
      raise _transport_error()


class _FakeServer:
  """Answers each request with the next scripted hop."""

  def __init__(self, hops: list[dict[str, Any]]):
    self._hops = hops
    self.request_tokens: list[Optional[str]] = []

  def _next_hop(self, request: httpx.Request) -> dict[str, Any]:
    request_dict = json.loads(request.content.decode())
    self.request_tokens.append(
        _decode_token(request_dict.get('continuationToken'))
    )
    if len(self.request_tokens) > len(self._hops):
      raise AssertionError(
          f'Unexpected request #{len(self.request_tokens)}; the case scripts'
          f' {len(self._hops)}.'
      )
    return self._hops[len(self.request_tokens) - 1]

  def handle_sync(self, request: httpx.Request) -> httpx.Response:
    hop = self._next_hop(request)
    if 'status' in hop:
      return httpx.Response(
          hop['status'],
          headers={'content-type': 'application/json'},
          text=_error_body(hop['status']),
      )
    if hop.get('transport_error'):
      raise _transport_error()
    if 'response' in hop:
      return httpx.Response(
          200,
          headers={'content-type': 'application/json'},
          text=json.dumps(_wire_response(hop['response'])),
      )
    return httpx.Response(
        200,
        headers={'content-type': 'text/event-stream'},
        stream=_SyncStream(hop),
    )

  async def handle_async(self, request: httpx.Request) -> httpx.Response:
    hop = self._next_hop(request)
    if 'status' in hop:
      return httpx.Response(
          hop['status'],
          headers={'content-type': 'application/json'},
          text=_error_body(hop['status']),
      )
    if hop.get('transport_error'):
      raise _transport_error()
    if 'response' in hop:
      return httpx.Response(
          200,
          headers={'content-type': 'application/json'},
          text=json.dumps(_wire_response(hop['response'])),
      )
    return httpx.Response(
        200,
        headers={'content-type': 'text/event-stream'},
        stream=_AsyncStream(hop),
    )


def _actual(response: types.GenerateContentResponse) -> dict[str, Any]:
  """Extracts the checked properties from a response or chunk."""
  candidate = response.candidates[0] if response.candidates else None
  parts = (candidate.content.parts if candidate and candidate.content else None)
  usage = response.usage_metadata
  return {
      'text': ''.join(p.text for p in parts or [] if p.text is not None),
      'token': _decode_token(candidate.continuation_token if candidate else None),
      'finish': (
          candidate.finish_reason.value
          if candidate and candidate.finish_reason
          else None
      ),
      'prompt_feedback': (
          response.prompt_feedback.block_reason.value
          if response.prompt_feedback and response.prompt_feedback.block_reason
          else None
      ),
      'usage': {
          'prompt': usage.prompt_token_count if usage else None,
          'candidates': usage.candidates_token_count if usage else None,
          'total': usage.total_token_count if usage else None,
      },
  }


def _check(label: str, response: types.GenerateContentResponse, want: dict):
  actual = _actual(response)
  for key, expected in want.items():
    got = actual[key]
    if key == 'usage':
      got = {k: got[k] for k in expected}
    assert got == expected, f'{label}.{key}: got {got!r}, want {expected!r}'


def _check_error(error: Optional[Exception], want: Optional[dict]):
  if want is None:
    if error is not None:
      raise error
    return
  assert error is not None, f'Expected an error {want}, but the call succeeded.'
  if want['type'] == 'api':
    assert isinstance(error, errors.APIError), repr(error)
    assert error.code == want['code'], repr(error)
  elif want['type'] == 'transport':
    assert isinstance(error, httpx.TransportError), repr(error)
  else:
    raise ValueError(f'Unknown error type: {want}')


def _check_results(case, server, response, chunks, error):
  expect = case['expect']
  _check_error(error, expect.get('error'))
  assert server.request_tokens == expect['request_tokens'], (
      f'request tokens: got {server.request_tokens},'
      f' want {expect["request_tokens"]}'
  )
  if case['method'] == 'generate_content':
    if 'response' in expect:
      _check('response', response, expect['response'])
  else:
    want_chunks = expect.get('chunks', [])
    assert len(chunks) == len(want_chunks), (
        f'chunks: got {len(chunks)}: {[_actual(c) for c in chunks]},'
        f' want {len(want_chunks)}'
    )
    for i, (chunk, want) in enumerate(zip(chunks, want_chunks)):
      _check(f'chunks[{i}]', chunk, want)


_REQUEST = dict(model='gemini-2.5-pro', contents='Hello')


def _make_client(server: _FakeServer) -> client_lib.Client:
  return client_lib.Client(
      api_key='test-key',
      http_options=types.HttpOptions(
          httpx_client=httpx.Client(
              transport=httpx.MockTransport(server.handle_sync)
          ),
          httpx_async_client=httpx.AsyncClient(
              transport=httpx.MockTransport(server.handle_async)
          ),
          retry_options=types.HttpRetryOptions(attempts=1),
      ),
  )


@pytest.mark.parametrize('case', _CASES, ids=[c['name'] for c in _CASES])
def test_sync(case):
  server = _FakeServer(case['hops'])
  client = _make_client(server)
  response, chunks, error = None, [], None
  try:
    if case['method'] == 'generate_content':
      response = client.models.generate_content(
          **_REQUEST, config=case.get('config')
      )
    else:
      for chunk in client.models.generate_content_stream(
          **_REQUEST, config=case.get('config')
      ):
        chunks.append(chunk)
  except (errors.APIError, httpx.TransportError) as e:
    error = e
  _check_results(case, server, response, chunks, error)


@pytest.mark.asyncio
@pytest.mark.parametrize('case', _CASES, ids=[c['name'] for c in _CASES])
async def test_async(case):
  server = _FakeServer(case['hops'])
  client = _make_client(server)
  response, chunks, error = None, [], None
  try:
    if case['method'] == 'generate_content':
      response = await client.aio.models.generate_content(
          **_REQUEST, config=case.get('config')
      )
    else:
      async for chunk in await client.aio.models.generate_content_stream(
          **_REQUEST, config=case.get('config')
      ):
        chunks.append(chunk)
  except (errors.APIError, httpx.TransportError) as e:
    error = e
  _check_results(case, server, response, chunks, error)
