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


"""Tests for how `HttpRetryOptions` applies to the Interactions API."""

from unittest import mock

import pytest

from ... import _api_client
from ... import Client
from ... import types
from ..._gaos import google_genai
from ..._gaos.lib import compat_errors

if _api_client._get_http_client_backend() == 'httpx2':
  from httpx2 import Client as HTTPClient, Request, Response  # pylint: disable=g-import-not-at-top

  AsyncHttpxClient = _api_client.AsyncHttpx2Client
else:
  from httpx import Client as HTTPClient, Request, Response  # pylint: disable=g-import-not-at-top

  AsyncHttpxClient = _api_client.AsyncHttpxClient

ENV_VARS = [
    'GOOGLE_CLOUD_PROJECT',
    'GEMINI_API_KEY',
    'GOOGLE_API_KEY',
    'GOOGLE_CLOUD_LOCATION',
]


@pytest.fixture(autouse=True)
def clear_env_vars(monkeypatch):
  for var in ENV_VARS:
    monkeypatch.delenv(var, raising=False)


def _rate_limited():
  return Response(
      429,
      request=Request('POST', ''),
      headers={'retry-after-ms': '1', 'content-type': 'application/json'},
      content='{"error": {"code": "too_many_requests", "message": "quota"}}',
  )


def _completed():
  return Response(
      200,
      request=Request('POST', ''),
      headers={'content-type': 'application/json'},
      content='{"status": "completed"}',
  )


@pytest.mark.parametrize(
    'attempts, expected_retries',
    [
        (None, google_genai._api_client._RETRY_ATTEMPTS - 1),
        (0, 0),
        (1, 0),
        (2, 1),
        (5, 4),
    ],
)
def test_translate_retry_config_counts_the_original_request(
    attempts, expected_retries
):
  retry_options = None
  if attempts is not None:
    retry_options = types.HttpRetryOptions(attempts=attempts)
  http_options = types.HttpOptions(retry_options=retry_options)

  config = google_genai._translate_retry_config(http_options)

  assert config.max_retries == expected_retries


@pytest.mark.parametrize('attempts', [0, 1])
def test_interactions_do_not_retry_when_attempts_disable_retries(
    monkeypatch, attempts
):
  monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
  client = Client(
      http_options=types.HttpOptions(
          retry_options=types.HttpRetryOptions(attempts=attempts)
      )
  )

  with mock.patch.object(HTTPClient, 'send') as mock_send:
    mock_send.side_effect = [_rate_limited(), _rate_limited()]
    with pytest.raises(compat_errors.RateLimitError):
      client.interactions.create(model='gemini-1.5-flash', input='Hello')
    assert mock_send.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('attempts', [0, 1])
async def test_async_interactions_do_not_retry_when_attempts_disable_retries(
    monkeypatch, attempts
):
  monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
  client = Client(
      http_options=types.HttpOptions(
          retry_options=types.HttpRetryOptions(attempts=attempts)
      )
  )

  with mock.patch.object(AsyncHttpxClient, 'send') as mock_send:
    mock_send.side_effect = [_rate_limited(), _rate_limited()]
    with pytest.raises(compat_errors.RateLimitError):
      await client.aio.interactions.create(
          model='gemini-1.5-flash', input='Hello'
      )
    assert mock_send.call_count == 1


def test_interactions_retry_up_to_attempts(monkeypatch):
  monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
  client = Client(
      http_options=types.HttpOptions(
          retry_options=types.HttpRetryOptions(attempts=3)
      )
  )

  with mock.patch.object(HTTPClient, 'send') as mock_send:
    mock_send.side_effect = [_rate_limited(), _rate_limited(), _completed()]
    client.interactions.create(model='gemini-1.5-flash', input='Hello')
    assert mock_send.call_count == 3

  with mock.patch.object(HTTPClient, 'send') as mock_send:
    mock_send.side_effect = [_rate_limited()] * 4
    with pytest.raises(compat_errors.RateLimitError):
      client.interactions.create(model='gemini-1.5-flash', input='Hello')
    assert mock_send.call_count == 3


def test_interactions_default_matches_generate_content_attempts(monkeypatch):
  monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
  client = Client(
      http_options=types.HttpOptions(retry_options=types.HttpRetryOptions())
  )

  with mock.patch.object(HTTPClient, 'send') as mock_send:
    mock_send.side_effect = [_rate_limited()] * 6
    with pytest.raises(compat_errors.RateLimitError):
      client.interactions.create(model='gemini-1.5-flash', input='Hello')
    assert mock_send.call_count == google_genai._api_client._RETRY_ATTEMPTS
