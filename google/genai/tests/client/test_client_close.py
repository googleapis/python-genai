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

"""Tests for closing the clients and context managers."""
import asyncio
import gc
from unittest import mock

from google.oauth2 import credentials
import pytest
try:
  import aiohttp
  AIOHTTP_NOT_INSTALLED = False
except ImportError:
  AIOHTTP_NOT_INSTALLED = True
  aiohttp = mock.MagicMock()


from ... import _api_client as api_client
from ... import Client

if api_client._get_http_client_backend() == 'httpx2':
  import httpx2 as httpx  # pylint: disable=g-import-not-at-top
else:
  import httpx  # pylint: disable=g-import-not-at-top

requires_aiohttp = pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason='aiohttp is not installed, skipping test.'
)


def test_close_httpx_client():
  """Tests that the httpx client is closed when the client is closed."""
  api_client.has_aiohttp = False
  client = Client(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=api_client.HttpOptions(client_args={'max_redirects': 10}),
  )
  client.close()
  assert client._api_client._httpx_client.is_closed


def test_httpx_client_context_manager():
  """Tests that the httpx client is closed when the client is closed."""
  api_client.has_aiohttp = False
  with Client(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=api_client.HttpOptions(client_args={'max_redirects': 10}),
  ) as client:
    pass
    assert not client._api_client._httpx_client.is_closed

  assert client._api_client._httpx_client.is_closed


@pytest.mark.asyncio
async def test_aclose_httpx_client():
  """Tests that the httpx async client is closed when the client is closed."""
  api_client.has_aiohttp = False
  async_client = Client(
      vertexai=True,
      project='test_project',
      location='global',
  ).aio
  await async_client.aclose()
  assert async_client._api_client._async_httpx_client.is_closed


@pytest.mark.asyncio
async def test_async_httpx_client_context_manager():
  """Tests that the httpx async client is closed when the client is closed."""
  api_client.has_aiohttp = False
  async with Client(
      vertexai=True,
      project='test_project',
      location='global',
  ).aio as async_client:
    pass
    assert not async_client._api_client._async_httpx_client.is_closed

  assert async_client._api_client._async_httpx_client.is_closed


@pytest.fixture
def mock_request():
  mock_aiohttp_response = mock.Mock(spec=aiohttp.ClientSession.request)
  mock_aiohttp_response.return_value = mock_aiohttp_response
  yield mock_aiohttp_response


def _patch_auth_default():
  return mock.patch(
      'google.auth.default',
      return_value=(credentials.Credentials('magic_token'), 'test_project'),
      autospec=True,
  )


async def _aiohttp_async_response(status: int):
  """Has to return a coroutine hence async."""
  response = mock.Mock(spec=aiohttp.ClientResponse)
  response.status = status
  response.headers = {'status-code': str(status)}
  response.json.return_value = {}
  response.text.return_value = 'test'
  return response


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aclose_aiohttp_session(mock_request):
  """Tests that the aiohttp session is closed when the client is closed."""
  api_client.has_aiohttp = True
  async def run():
    mock_request.side_effect = (
        aiohttp.ClientConnectorError(
            connection_key=aiohttp.client_reqrep.ConnectionKey(
                'localhost', 80, False, True, None, None, None
            ),
            os_error=OSError,
        ),
        _aiohttp_async_response(200),
    )
    with _patch_auth_default():
      async_client = Client(
          vertexai=True,
          project='test_project',
          location='global',
          http_options=api_client.HttpOptions(
              async_client_args={'trust_env': False}
          ),
      ).aio
      # aiohttp session is created in the first request instead of client
      # initialization.
      _ = await async_client._api_client._async_request_once(
          api_client.HttpRequest(
              method='GET',
              url='https://example.com',
              headers={},
              data=None,
              timeout=None,
          )
      )
      assert async_client._api_client._aiohttp_session is not None
      if hasattr(async_client._api_client._aiohttp_session, 'closed'):
        assert not async_client._api_client._aiohttp_session.closed
      # Close the client and check that the session is closed.
      await async_client.aclose()
      if hasattr(async_client._api_client._aiohttp_session, 'closed'):
        assert async_client._api_client._aiohttp_session.closed
      else:
        from google.auth.aio.transport.sessions import AsyncAuthorizedSession

        if isinstance(
            async_client._api_client._aiohttp_session, AsyncAuthorizedSession
        ):
          assert async_client._api_client._aiohttp_session._auth_request._closed

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_session_context_manager(mock_request):
  """Tests that the aiohttp session is closed when the client is closed."""
  api_client.has_aiohttp = True
  async def run():
    mock_request.side_effect = (
        aiohttp.ClientConnectorError(
            connection_key=aiohttp.client_reqrep.ConnectionKey(
                'localhost', 80, False, True, None, None, None
            ),
            os_error=OSError,
        ),
        _aiohttp_async_response(200),
    )
    with _patch_auth_default():
      async with Client(
          vertexai=True,
          project='test_project',
          location='global',
          http_options=api_client.HttpOptions(
              async_client_args={'trust_env': False}
          ),
      ).aio as async_client:
        # aiohttp session is created in the first request instead of client
        # initialization.
        _ = await async_client._api_client._async_request_once(
            api_client.HttpRequest(
                method='GET',
                url='https://example.com',
                headers={},
                data=None,
                timeout=None,
            )
        )
        assert async_client._api_client._aiohttp_session is not None
        if hasattr(async_client._api_client._aiohttp_session, 'closed'):
          assert not async_client._api_client._aiohttp_session.closed

      if hasattr(async_client._api_client._aiohttp_session, 'closed'):
        assert async_client._api_client._aiohttp_session.closed
      else:
        from google.auth.aio.transport.sessions import AsyncAuthorizedSession

        if isinstance(
            async_client._api_client._aiohttp_session, AsyncAuthorizedSession
        ):
          assert async_client._api_client._aiohttp_session._auth_request._closed

  asyncio.run(run())


def _patch_aclose(**kwargs):
  return mock.patch.object(api_client.BaseApiClient, 'aclose', **kwargs)


@pytest.mark.asyncio
async def test_del_after_aclose_does_not_schedule_aclose():
  """Collecting a client that is already closed schedules no aclose task."""
  api_client.has_aiohttp = False
  client = Client(
      vertexai=True,
      project='test_project',
      location='global',
  )
  await client.aio.aclose()
  client.close()
  # Collect clients that other tests left on the heap before patching.
  gc.collect()

  with _patch_aclose(new_callable=mock.AsyncMock) as mock_aclose:
    del client
    gc.collect()
    await asyncio.sleep(0)

  mock_aclose.assert_not_called()


@requires_aiohttp
@pytest.mark.asyncio
async def test_del_after_aclose_with_aiohttp_session_does_not_schedule_aclose():
  """Collecting a client whose aiohttp session is closed schedules no task."""
  api_client.has_aiohttp = True
  client = Client(
      api_key='test_api_key',
      http_options=api_client.HttpOptions(
          async_client_args={'trust_env': False}
      ),
  )
  await client._api_client._get_aiohttp_session()
  assert client._api_client._aiohttp_sessions
  await client.aio.aclose()
  client.close()
  gc.collect()

  with _patch_aclose(new_callable=mock.AsyncMock) as mock_aclose:
    del client
    gc.collect()
    await asyncio.sleep(0)

  mock_aclose.assert_not_called()


@pytest.mark.asyncio
async def test_del_without_aclose_closes_the_httpx_client():
  """Collecting a client that is still open closes the async httpx client."""
  api_client.has_aiohttp = False
  client = Client(
      vertexai=True,
      project='test_project',
      location='global',
  )
  httpx_client = client._api_client._async_httpx_client
  gc.collect()
  real_aclose = api_client.BaseApiClient.aclose
  closed = asyncio.Event()

  async def aclose_and_signal(self):
    await real_aclose(self)
    closed.set()

  with _patch_aclose(autospec=True, side_effect=aclose_and_signal):
    del client
    gc.collect()
    await asyncio.wait_for(closed.wait(), timeout=5)

  assert httpx_client.is_closed


@pytest.mark.asyncio
async def test_del_with_user_supplied_async_client_does_not_schedule_aclose():
  """The SDK schedules no close task for an httpx client it does not own."""
  api_client.has_aiohttp = False
  httpx_client = httpx.AsyncClient()
  client = Client(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=api_client.HttpOptions(httpx_async_client=httpx_client),
  )
  gc.collect()

  with _patch_aclose(new_callable=mock.AsyncMock) as mock_aclose:
    del client
    gc.collect()
    await asyncio.sleep(0)

  mock_aclose.assert_not_called()
  assert not httpx_client.is_closed
  await httpx_client.aclose()
