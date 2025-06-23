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
from unittest import mock

from ... import _api_client as api_client
from ... import types


_RETRIED_CODES = (
    408,  # Request timeout.
    429,  # Too many requests.
    500,  # Internal server error.
    502,  # Bad gateway.
    503,  # Service unavailable.
    504,  # Gateway timeout.
)


def _final_codes(retried_codes: Sequence[int] = _RETRIED_CODES):
  return [code for code in range(100, 600) if code not in retried_codes]


def _response(code: int):
  response = api_client.HttpResponse(
      headers={'status-code': str(code)},
      response_stream=[''],  # empty response body
  )
  response.status_code = code
  return response


# Args


def test_retry_args_disabled():
  args = api_client._retry_args(None)

  assert set(args.keys()) == {'stop'}
  assert args['stop'].max_attempt_number == 1


def test_retry_args_enabled_with_defaults():
  # Empty options means use the default values whereas None means no retries.
  args = api_client._retry_args(types.HttpRetryOptions())

  assert set(args.keys()) == {'stop', 'retry', 'retry_error_callback', 'wait'}

  assert args['stop'].max_attempt_number == 3

  wait = args['wait']
  assert wait.exp_base == 2
  assert wait.initial == 1
  assert wait.jitter == 1
  assert wait.max == 120

  retry = args['retry']
  for code in _RETRIED_CODES:
    assert retry.predicate(_response(code))

  for code in _final_codes():
    assert not retry.predicate(_response(code))


def test_retry_args_enabled_with_custom_values_are_not_overridden():
  options = types.HttpRetryOptions(
      attempts=10,
      initial_delay=10,
      max_delay=100,
      exp_base=1.5,
      jitter=0.5,
      http_status_codes=[408, 429],
  )
  retry_args = api_client._retry_args(options)
  assert retry_args['stop'].max_attempt_number == 10

  wait = retry_args['wait']
  assert wait.initial == 10
  assert wait.max == 100
  assert wait.exp_base == 1.5
  assert wait.jitter == 0.5

  retry = retry_args['retry']
  for code in [408, 429]:
    assert retry.predicate(_response(code))

  for code in _final_codes([408, 429]):
    assert not retry.predicate(_response(code))


# Sync


def test_disabled_retries_successful_request_executes_once():
  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
  )
  with mock.patch.object(
      client, '_request_once', return_value=_response(200)
  ) as mock_request_once:
    response = client.request(http_method='GET', path='path', request_dict={})
    mock_request_once.assert_called_once()
    assert response.headers['status-code'] == '200'


def test_disabled_retries_failed_request_executes_once():
  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
  )
  with mock.patch.object(
      client, '_request_once', return_value=_response(429)
  ) as mock_request_once:
    response = client.request(http_method='GET', path='path', request_dict={})
    mock_request_once.assert_called_once()
    assert response.headers['status-code'] == '429'


_RETRY_OPTIONS = types.HttpRetryOptions(
    attempts=2,
    initial_delay=0,
    max_delay=1,
    exp_base=0.1,
    jitter=0.1,
    http_status_codes=[429, 504],
)


def test_retries_successful_request_executes_once():
  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
  )
  with mock.patch.object(
      client, '_request_once', return_value=_response(200)
  ) as mock_request_once:
    response = client.request(http_method='GET', path='path', request_dict={})
    mock_request_once.assert_called_once()
    assert response.headers['status-code'] == '200'


def test_retries_failed_request_retries_successfully():
  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
  )
  with mock.patch.object(
      client, '_request_once', side_effect=[_response(429), _response(200)]
  ) as mock_request_once:
    response = client.request(http_method='GET', path='path', request_dict={})
    assert mock_request_once.call_count == 2
    assert response.headers['status-code'] == '200'


def test_retries_failed_request_retries_unsuccessfully():
  client = api_client.BaseApiClient(
      vertexai=True,
      project='test_project',
      location='global',
      http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
  )
  with mock.patch.object(
      client, '_request_once', side_effect=[_response(429), _response(504)]
  ) as mock_request_once:
    response = client.request(http_method='GET', path='path', request_dict={})
    assert mock_request_once.call_count == 2
    assert response.headers['status-code'] == '504'


# Async


def test_async_disabled_retries_successful_request_executes_once():
  async def run():
    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
    )
    with mock.patch.object(
        client, '_async_request_once', return_value=_response(200)
    ) as mock_async_request_once:
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_async_request_once.assert_called_once()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


def test_async_disabled_retries_failed_request_executes_once():
  async def run():
    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
    )
    with mock.patch.object(
        client, '_async_request_once', return_value=_response(429)
    ) as mock_async_request_once:
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_async_request_once.assert_called_once()
      assert response.headers['status-code'] == '429'

  asyncio.run(run())


def test_async_retries_successful_request_executes_once():
  async def run():
    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
    )
    with mock.patch.object(
        client, '_async_request_once', return_value=_response(200)
    ) as mock_async_request_once:
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      mock_async_request_once.assert_called_once()
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


def test_async_retries_failed_request_retries_successfully():
  async def run():
    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
    )
    with mock.patch.object(
        client,
        '_async_request_once',
        side_effect=[_response(429), _response(200)],
    ) as mock_async_request_once:
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      assert mock_async_request_once.call_count == 2
      assert response.headers['status-code'] == '200'

  asyncio.run(run())


def test_async_retries_failed_request_retries_unsuccessfully():
  async def run():
    client = api_client.BaseApiClient(
        vertexai=True,
        project='test_project',
        location='global',
        http_options=types.HttpOptions(retry_options=_RETRY_OPTIONS),
    )
    with mock.patch.object(
        client,
        '_async_request_once',
        side_effect=[_response(429), _response(504)],
    ) as mock_async_request_once:
      response = await client.async_request(
          http_method='GET', path='path', request_dict={}
      )
      assert mock_async_request_once.call_count == 2
      assert response.headers['status-code'] == '504'

    asyncio.run(run())
