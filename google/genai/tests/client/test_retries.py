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

"""Tests for http retries."""

import asyncio
from collections.abc import Sequence
import datetime
from unittest import mock
import pytest
try:
    import aiohttp
    AIOHTTP_NOT_INSTALLED = False
except ImportError:
    AIOHTTP_NOT_INSTALLED = True
    aiohttp = mock.MagicMock()

from google.oauth2 import credentials
import httpx
import tenacity

from ... import _api_client as api_client
from ... import errors
from ... import types


requires_aiohttp = pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason="aiohttp is not installed, skipping test."
)


_RETRIED_CODES = (
    408,  # Request timeout.
    429,  # Too many requests.
    500,  # Internal server error.
    502,  # Bad gateway.
    503,  # Service unavailable.
    504,  # Gateway timeout.
)


@pytest.fixture(autouse=True)
def reset_has_aiohttp():
  yield
  api_client.has_aiohttp = False


def _final_codes(retried_codes: Sequence[int] = _RETRIED_CODES):
  return [code for code in range(100, 600) if code not in retried_codes]


def _httpx_response(code: int):
  return httpx.Response(
      status_code=code,
      headers={'status-code': str(code)},
      content=b'',
  )


# Args


def test_retry_args_disabled():
  args = api_client.retry_args(None)

  assert set(args.keys()) == {'stop', 'reraise'}
  assert args['stop'].max_attempt_number == 1
  assert args['reraise']


def test_retry_args_enabled_with_defaults():
  # Empty options means use the default values whereas None means no retries.
  args = api_client.retry_args(types.HttpRetryOptions())

  assert set(args.keys()) == {
      'stop',
      'retry',
      'wait',
      'reraise',
      'before_sleep',
  }

  assert args['stop'].max_attempt_number == 5

  wait = args['wait']
  assert wait.exp_base == 2
  assert wait.initial == 1
  assert wait.jitter == 1
  assert wait.max == 60

  retry = args['retry']
  for code in _RETRIED_CODES:
    try:
      errors.APIError.raise_for_response(_httpx_response(code))
      assert False, 'Expected APIError to be raised.'
    except errors.APIError as e:
      assert retry.predicate(e)

  for code in _final_codes():
    try:
      errors.APIError.raise_for_response(_httpx_response(code))
      # Does not raise for some codes.
    except errors.APIError as e:
      # Does not retry for error codes outside of the retried codes list.
      assert not retry.predicate(e)

    assert args['reraise']


def test_retry_wait():
  timestamps = []

  def fn():
    now = datetime.datetime.now()
    timestamps.append(now)
    raise errors.APIError.raise_for_response(_httpx_response(429))

  retrying = tenacity.Retrying(
      **api_client.retry_args(types.HttpRetryOptions())
  )

  try:
    retrying(fn)
    assert False, 'Expected APIError to be raised.'
  except errors.APIError:
    pass

  assert len(timestamps) == 5
  assert timestamps[1] - timestamps[0] >= datetime.timedelta(seconds=1)
  assert timestamps[2] - timestamps[1] >= datetime.timedelta(seconds=2)
  assert timestamps[3] - timestamps[2] >= datetime.timedelta(seconds=4)
  assert timestamps[4] - timestamps[3] >= datetime.timedelta(seconds=8)


def test_retry_args_enabled_with_custom_values_are_not_overridden():
  options = types.HttpRetryOptions(
      attempts=10,
      initial_delay=10,
      max_delay=100,
      exp_base=1.5,
      jitter=0.5,
      http_status_codes=[408, 429],
  )
  retry_args = api_client.retry_args(options)
  assert retry_args['stop'].max_attempt_number == 10

  wait = retry_args['wait']
  assert wait.initial == 10
  assert wait.max == 100
  assert wait.exp_base == 1.5
  assert wait.jitter == 0.5

  retry = retry_args['retry']
  for code in [408, 429]:
    try:
      errors.APIError.raise_for_response(_httpx_response(code))
      assert False, 'Expected APIError to be raised.'
    except errors.APIError as e:
      assert retry.predicate(e)

  for code in _final_codes([408, 429]):
    try:
      errors.APIError.raise_for_response(_httpx_response(code))
      # Does not raise for some codes.
    except errors.APIError as e:
      # Does not retry for error codes outside of the retried codes list.
      assert not retry.predicate(e)


def _patch_auth_default():
  return mock.patch(
      'google.auth.default',
      return_value=(credentials.Credentials('magic_token'), 'test_project'),
      autospec=True,
  )


def _transport_options(http_options=None, transport=None, async_transport=None):
  http_options = http_options or types.HttpOptions()
  http_options.client_args = {'transport': transport}
  http_options.async_client_args = {'transport': async_transport}
  return http_options


# Sync


def test_disabled_retries_successful_request_executes_once():
  mock_transport = mock.Mock(spec=httpx.BaseTransport)
  mock_transport.handle_request.return_value = _httpx_response(200)

  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=_transport_options(transport=mock_transport),
  )

  with _patch_auth_default():
    response = client.request(http_method='GET', path='path', request_dict={})
    mock_transport.handle_request.assert_called_once()
    assert response.headers['status-code'] == '200'


def test_disabled_retries_failed_request_executes_once():
  mock_transport = mock.Mock(spec=httpx.BaseTransport)
  mock_transport.handle_request.return_value = _httpx_response(429)

  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=_transport_options(transport=mock_transport),
  )

  with _patch_auth_default():
    try:
      client.request(http_method='GET', path='path', request_dict={})
      assert False, 'Expected APIError to be raised.'
    except errors.APIError as e:
      assert e.code == 429
    mock_transport.handle_request.assert_called_once()


_RETRY_OPTIONS = types.HttpRetryOptions(
    attempts=2,
    initial_delay=0,
    max_delay=1,
    exp_base=0.1,
    jitter=0.1,
    http_status_codes=[429, 504],
)


def test_retries_successful_request_executes_once():
  mock_transport = mock.Mock(spec=httpx.BaseTransport)
  mock_transport.handle_request.return_value = _httpx_response(200)

  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=_transport_options(
          http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
          transport=mock_transport,
      ),
  )

  with _patch_auth_default():
    response = client.request(http_method='GET', path='path', request_dict={})
    mock_transport.handle_request.assert_called_once()
    assert response.headers['status-code'] == '200'


def test_retries_failed_request_retries_successfully():
  mock_transport = mock.Mock(spec=httpx.BaseTransport)
  mock_transport.handle_request.side_effect = (
      _httpx_response(429),
      _httpx_response(200),
  )

  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=_transport_options(
          http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
          transport=mock_transport,
      ),
  )

  with _patch_auth_default():
    response = client.request(http_method='GET', path='path', request_dict={})
    mock_transport.handle_request.assert_called()
    assert response.headers['status-code'] == '200'


def test_retries_failed_request_retries_successfully_at_request_level():
  mock_transport = mock.Mock(spec=httpx.BaseTransport)
  mock_transport.handle_request.side_effect = (
      _httpx_response(429),
      _httpx_response(200),
  )

  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=_transport_options(
          transport=mock_transport,
      ),
  )

  with _patch_auth_default():
    response = client.request(
        http_method='GET',
        path='path',
        request_dict={},
        http_options=types.HttpOptions(
            retry_options=_RETRY_OPTIONS
        ),  # At request level.
    )
    mock_transport.handle_request.assert_called()
    assert response.headers['status-code'] == '200'


def test_retries_failed_request_retries_unsuccessfully():
  mock_transport = mock.Mock(spec=httpx.BaseTransport)
  mock_transport.handle_request.side_effect = (
      _httpx_response(429),
      _httpx_response(504),
  )

  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=_transport_options(
          http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
          transport=mock_transport,
      ),
  )

  with _patch_auth_default():
    try:
      client.request(http_method='GET', path='path', request_dict={})
      assert False, 'Expected APIError to be raised.'
    except errors.APIError as e:
      assert e.code == 504
    mock_transport.handle_request.assert_called()


def test_retries_failed_request_retries_unsuccessfully_at_request_level():
  mock_transport = mock.Mock(spec=httpx.BaseTransport)
  mock_transport.handle_request.side_effect = (
      _httpx_response(429),
      _httpx_response(504),
  )

  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=_transport_options(
          transport=mock_transport,
      ),
  )

  with _patch_auth_default():
    try:
      client.request(
          http_method='GET',
          path='path',
          request_dict={},
          http_options={'retry_options': _RETRY_OPTIONS},  # At request level.
      )
      assert False, 'Expected APIError to be raised.'
    except errors.APIError as e:
      assert e.code == 504
    mock_transport.handle_request.assert_called()


# Async httpx


def test_async_disabled_retries_successful_request_executes_once():
  api_client.has_aiohttp = False

  async def run():
    mock_transport = mock.Mock(spec=httpx.AsyncBaseTransport)
    mock_transport.handle_async_request.return_value = _httpx_response(200)

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(async_transport=mock_transport),
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_transport.handle_async_request.assert_called_once()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


def test_async_disabled_retries_failed_request_executes_once():
  api_client.has_aiohttp = False

  async def run():
    mock_transport = mock.Mock(spec=httpx.AsyncBaseTransport)
    mock_transport.handle_async_request.return_value = _httpx_response(429)

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(async_transport=mock_transport),
    )

    with _patch_auth_default():
      try:
        await client.async_request(
            http_method='GET', path='path', request_dict={}
        )
        assert False, 'Expected APIError to be raised.'
      except errors.APIError as e:
        assert e.code == 429
      mock_transport.handle_async_request.assert_called_once()

  asyncio.run(run())


def test_async_retries_successful_request_executes_once():
  api_client.has_aiohttp = False

  async def run():
    mock_transport = mock.Mock(spec=httpx.AsyncBaseTransport)
    mock_transport.handle_async_request.return_value = _httpx_response(200)

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
            async_transport=mock_transport,
        ),
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_transport.handle_async_request.assert_called_once()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


def test_async_retries_failed_request_retries_successfully():
  api_client.has_aiohttp = False

  async def run():
    mock_transport = mock.Mock(spec=httpx.AsyncBaseTransport)
    mock_transport.handle_async_request.side_effect = (
        _httpx_response(429),
        _httpx_response(200),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
            async_transport=mock_transport,
        ),
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_transport.handle_async_request.assert_called()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


def test_async_retries_failed_request_retries_successfully_at_request_level():
  api_client.has_aiohttp = False

  async def run():
    mock_transport = mock.Mock(spec=httpx.AsyncBaseTransport)
    mock_transport.handle_async_request.side_effect = (
        _httpx_response(429),
        _httpx_response(200),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            async_transport=mock_transport,
        ),
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET',
          path='path',
          request_dict={},
          http_options=types.HttpOptions(
              retry_options=_RETRY_OPTIONS
          ),  # At request level.
      )
      mock_transport.handle_async_request.assert_called()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


def test_async_retries_failed_request_retries_unsuccessfully():
  api_client.has_aiohttp = False

  async def run():
    mock_transport = mock.Mock(spec=httpx.AsyncBaseTransport)
    mock_transport.handle_async_request.side_effect = (
        _httpx_response(429),
        _httpx_response(504),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
            async_transport=mock_transport,
        ),
    )

    with _patch_auth_default():
      try:
        await client.async_request(
            http_method='GET', path='path', request_dict={}
        )
        assert False, 'Expected APIError to be raised.'
      except errors.APIError as e:
        assert e.code == 504
      mock_transport.handle_async_request.assert_called()

  asyncio.run(run())


def test_async_retries_failed_request_retries_unsuccessfully_at_request_level():
  api_client.has_aiohttp = False

  async def run():
    mock_transport = mock.Mock(spec=httpx.AsyncBaseTransport)
    mock_transport.handle_async_request.side_effect = (
        _httpx_response(429),
        _httpx_response(504),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            async_transport=mock_transport,
        ),
    )

    with _patch_auth_default():
      try:
        await client.async_request(
            http_method='GET',
            path='path',
            request_dict={},
            http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
        )
        assert False, 'Expected APIError to be raised.'
      except errors.APIError as e:
        assert e.code == 504
      mock_transport.handle_async_request.assert_called()

  asyncio.run(run())


# Async aiohttp


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
def test_aiohttp_disabled_retries_successful_request_executes_once(
    mock_request,
):
  api_client.has_aiohttp = True  # Force aiohttp

  async def run():
    mock_request.return_value = _aiohttp_async_response(200)

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_request.assert_called_once()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_disabled_retries_failed_request_executes_once(mock_request):
  api_client.has_aiohttp = True

  async def run():
    mock_request.return_value = _aiohttp_async_response(429)

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
    )

    with _patch_auth_default():
      try:
        await client.async_request(
            http_method='GET', path='path', request_dict={}
        )
        assert False, 'Expected APIError to be raised.'
      except errors.APIError as e:
        assert e.code == 429
      mock_request.assert_called_once()

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_successful_request_executes_once(mock_request):
  api_client.has_aiohttp = True

  async def run():
    mock_request.return_value = _aiohttp_async_response(200)

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
        ),
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_request.assert_called_once()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_failed_request_retries_successfully(mock_request):
  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        _aiohttp_async_response(429),
        _aiohttp_async_response(200),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
        ),
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_request.assert_called()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_failed_request_retries_successfully_at_request_level(
    mock_request,
):
  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        _aiohttp_async_response(429),
        _aiohttp_async_response(200),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET',
          path='path',
          request_dict={},
          http_options=types.HttpOptions(
              retry_options=_RETRY_OPTIONS
          ),  # At request level.
      )
      mock_request.assert_called()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_failed_request_retries_unsuccessfully(mock_request):
  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        _aiohttp_async_response(429),
        _aiohttp_async_response(504),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=_transport_options(
            http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
        ),
    )

    with _patch_auth_default():
      try:
        await client.async_request(
            http_method='GET', path='path', request_dict={}
        )
        assert False, 'Expected APIError to be raised.'
      except errors.APIError as e:
        assert e.code == 504
      mock_request.assert_called()

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_failed_request_retries_unsuccessfully_at_request_level(
    mock_request,
):
  api_client.has_aiohttp = True

  async def run():
    mock_request.side_effect = (
        _aiohttp_async_response(429),
        _aiohttp_async_response(504),
    )

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
    )

    with _patch_auth_default():
      try:
        await client.async_request(
            http_method='GET',
            path='path',
            request_dict={},
            http_options={'retry_options': _RETRY_OPTIONS},  # At request level.
        )
        assert False, 'Expected APIError to be raised.'
      except errors.APIError as e:
        assert e.code == 504
      mock_request.assert_called()

  asyncio.run(run())


@requires_aiohttp
@mock.patch.object(aiohttp.ClientSession, 'request', autospec=True)
def test_aiohttp_retries_client_connector_error_retries_successfully(
    mock_request,
):
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
    # The request will be automatically retried once, if catching the
    # ClientConnectorError.

    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
    )

    with _patch_auth_default():
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_request.assert_called()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())
