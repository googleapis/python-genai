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

import pytest

httpx2 = pytest.importorskip('httpx2')

from ... import _api_client as api_client
from ... import Client
from ... import errors
from ...types import HttpOptions


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
