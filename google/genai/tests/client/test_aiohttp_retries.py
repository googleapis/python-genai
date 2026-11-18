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

"""Tests that HttpRetryOptions governs retries of aiohttp connection and timeout errors."""

import asyncio
import contextlib
from unittest import mock

from google.auth import exceptions as auth_exceptions
from google.oauth2 import credentials
import pytest

from ... import _api_client as api_client
from ... import types

aiohttp = pytest.importorskip('aiohttp')


@contextlib.contextmanager
def _patch_auth_default():
  with (
      mock.patch(
          'google.auth.default',
          return_value=(credentials.Credentials('magic_token'), 'test_project'),
          autospec=True,
      ),
      mock.patch.object(
          api_client.BaseApiClient,
          '_use_google_auth_async',
          return_value=False,
      ),
  ):
    yield


async def _aiohttp_async_response(status: int):
  """Has to return a coroutine hence async."""
  response = mock.Mock(spec=aiohttp.ClientResponse)
  response.status = status
  response.headers = {'status-code': str(status)}
  response.text.return_value = 'test'
  return response


def _client(retry_options=None):
  return api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=types.HttpOptions(retry_options=retry_options),
  )


def test_retry_args_retries_aiohttp_transport_errors():
  """HttpRetryOptions retries aiohttp connection and timeout errors, like httpx."""

  retry = api_client.retry_args(types.HttpRetryOptions())['retry']

  assert retry.predicate(aiohttp.ServerDisconnectedError())
  assert retry.predicate(aiohttp.ClientOSError())
  assert retry.predicate(
      aiohttp.ClientConnectorError(
          connection_key=aiohttp.client_reqrep.ConnectionKey(
              'localhost', 80, False, True, None, None, None
          ),
          os_error=OSError(),
      )
  )
  assert retry.predicate(asyncio.TimeoutError())
  assert retry.predicate(aiohttp.ServerTimeoutError())
  assert retry.predicate(aiohttp.ConnectionTimeoutError())
  assert retry.predicate(
      auth_exceptions.TimeoutError('Request timed out after 120.0 seconds.')
  )

  wrapped_disconnect = auth_exceptions.TransportError('Failed to send request.')
  wrapped_disconnect.__cause__ = aiohttp.ServerDisconnectedError()
  assert retry.predicate(wrapped_disconnect)

  wrapped_payload_error = auth_exceptions.TransportError('Bad payload.')
  wrapped_payload_error.__cause__ = aiohttp.ClientPayloadError()
  assert not retry.predicate(wrapped_payload_error)
  assert not retry.predicate(auth_exceptions.TransportError('No aiohttp cause'))
  assert not retry.predicate(auth_exceptions.RefreshError('Invalid grant'))
  assert not retry.predicate(aiohttp.ClientPayloadError())
  assert not retry.predicate(ValueError('not a transport error'))


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_single_attempt_server_disconnected_error_executes_once(
    mock_request,
):
  """attempts=1 means no retries, so a dropped connection is not resent."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = aiohttp.ServerDisconnectedError()
    client = _client(types.HttpRetryOptions(attempts=1))

    with _patch_auth_default():
      with pytest.raises(aiohttp.ServerDisconnectedError):
        await client.async_request(
            http_method='POST', path='path', request_dict={}
        )
    assert mock_request.call_count == 1

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_single_attempt_server_disconnected_error_executes_once_at_request_level(
    mock_request,
):
  """Request-level attempts=1 also disables the implicit aiohttp reconnect."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = aiohttp.ServerDisconnectedError()
    client = _client()

    with _patch_auth_default():
      with pytest.raises(aiohttp.ServerDisconnectedError):
        await client.async_request(
            http_method='POST',
            path='path',
            request_dict={},
            http_options={'retry_options': {'attempts': 1}},
        )
    assert mock_request.call_count == 1

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_single_attempt_streamed_server_disconnected_error_executes_once(
    mock_request,
):
  """The streaming branch honors attempts=1 the same way."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = aiohttp.ServerDisconnectedError()
    client = _client(types.HttpRetryOptions(attempts=1))

    with _patch_auth_default():
      with pytest.raises(aiohttp.ServerDisconnectedError):
        await client.async_request_streamed(
            http_method='POST', path='path', request_dict={}
        )
    assert mock_request.call_count == 1

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_server_disconnected_error_up_to_attempts(
    mock_request,
):
  """With retry options, tenacity retries aiohttp errors up to `attempts`."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = aiohttp.ServerDisconnectedError()
    client = _client(
        types.HttpRetryOptions(
            attempts=3, initial_delay=0, max_delay=0, jitter=0
        )
    )

    with _patch_auth_default():
      with pytest.raises(aiohttp.ServerDisconnectedError):
        await client.async_request(
            http_method='POST', path='path', request_dict={}
        )
    assert mock_request.call_count == 3

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_server_disconnected_error_retries_successfully(
    mock_request,
):
  """A dropped connection is still retried when attempts > 1."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        aiohttp.ServerDisconnectedError(),
        _aiohttp_async_response(200),
    )
    client = _client(
        types.HttpRetryOptions(
            attempts=2, initial_delay=0, max_delay=0, jitter=0
        )
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
    assert mock_request.call_count == 2
    assert response.headers['status-code'] == '200'

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_without_retry_options_reconnects_once(mock_request):
  """Without retry options, the legacy single reconnect is kept."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        aiohttp.ServerDisconnectedError(),
        _aiohttp_async_response(200),
    )
    client = _client()

    with _patch_auth_default(), mock.patch.object(
        asyncio, 'sleep', new=mock.AsyncMock()
    ):
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
    assert mock_request.call_count == 2
    assert response.headers['status-code'] == '200'

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_without_retry_options_timeout_error_executes_once(
    mock_request,
):
  """Without retry options, client-side timeouts are not implicitly retried."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = asyncio.TimeoutError()
    client = _client()

    with _patch_auth_default():
      with pytest.raises((asyncio.TimeoutError, auth_exceptions.TimeoutError)):
        await client.async_request(
            http_method='POST', path='path', request_dict={}
        )
    assert mock_request.call_count == 1

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_timeout_error_up_to_attempts(mock_request):
  """With retry options, tenacity retries aiohttp timeouts up to `attempts`."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = asyncio.TimeoutError()
    client = _client(
        types.HttpRetryOptions(
            attempts=3, initial_delay=0, max_delay=0, jitter=0
        )
    )

    with _patch_auth_default():
      with pytest.raises((asyncio.TimeoutError, auth_exceptions.TimeoutError)):
        await client.async_request(
            http_method='POST', path='path', request_dict={}
        )
    assert mock_request.call_count == 3

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_timeout_error_retries_successfully(mock_request):
  """A timed-out aiohttp request is retried and succeeds when attempts > 1."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        asyncio.TimeoutError(),
        _aiohttp_async_response(200),
    )
    client = _client(
        types.HttpRetryOptions(
            attempts=2, initial_delay=0, max_delay=0, jitter=0
        )
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='POST', path='path', request_dict={}
      )
    assert mock_request.call_count == 2
    assert response.headers['status-code'] == '200'

  asyncio.run(run())


@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_google_auth_timeout_error_retries_successfully(
    mock_request,
):
  """A google.auth.exceptions.TimeoutError from AsyncAuthorizedSession is retried."""

  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        auth_exceptions.TimeoutError('Request timed out after 120.0 seconds.'),
        _aiohttp_async_response(200),
    )
    client = _client(
        types.HttpRetryOptions(
            attempts=2, initial_delay=0, max_delay=0, jitter=0
        )
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='POST', path='path', request_dict={}
      )
    assert mock_request.call_count == 2
    assert response.headers['status-code'] == '200'

  asyncio.run(run())
