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


"""Tests for Interactions API."""

from ... import Client
from ... import _base_url
from unittest import mock
import pytest
from httpx import Request, Response
from ..._api_client import AsyncHttpxClient, BaseApiClient
from httpx import Client as HTTPClient
import os

ENV_VARS = [
    "GOOGLE_CLOUD_PROJECT",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_CLOUD_LOCATION",
]

@pytest.fixture(autouse=True)
def clear_env_vars(monkeypatch):
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)

def test_interactions_gemini_url(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()


    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('POST', ''))
        client.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
        )
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url).endswith('/v1beta/interactions')
        assert request.headers['x-goog-api-key'] == 'test-api-key'


def test_interactions_gemini_no_vertex_auth(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()

    with (
        mock.patch.object(BaseApiClient, "_access_token") as mock_access_token,
        mock.patch.object(HTTPClient, "send") as mock_send,
    ):
        mock_send.return_value = Response(200, request=Request('POST', ''))
        client.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
        )
        mock_access_token.assert_not_called()

def test_interactions_gemini_retry(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()
    client._api_client.max_retries = 2

    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.side_effect = [
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(200, request=Request('POST', '')),
        ]
        client.interactions.create(model='gemini-1.5-flash', input='Hello')
        assert mock_send.call_count == 3

def test_interactions_gemini_extra_headers(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()

    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('POST', ''))
        client.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
            extra_headers={'X-Custom-Header': 'TestValue'}
        )
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert request.headers['x-custom-header'] == 'TestValue'
        assert request.headers['x-goog-api-key'] == 'test-api-key'


def test_interactions_vertex_auth_header():
  from ..._api_client import BaseApiClient
  from ..._interactions._base_client import SyncAPIClient
  from httpx import Client as HTTPClient

  creds = mock.Mock()
  creds.quota_project_id = "test-quota-project"
  client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)

  with (
      mock.patch.object(
          BaseApiClient, "_access_token", return_value='fake-vertex-token'
      ) as  mock_access_token,
      mock.patch.object(
          HTTPClient, "send",
          return_value=mock.Mock(),
      ) as mock_send,
  ):

    response = client.interactions.create(
        model='gemini-2.5-flash',
        input='What is the largest planet in our solar system?',
    )

    mock_send.assert_called_once()
    mock_access_token.assert_called_once()
    args, kwargs = mock_send.call_args
    headers = args[0].headers
    assert any(
        key == "authorization" and value == 'Bearer fake-vertex-token'
        for key, value in headers.items())
    assert any(
        key == "x-goog-user-project" and value == 'test-quota-project'
        for key, value in headers.items())

def test_interactions_vertex_key_no_auth_header():
  from ..._api_client import BaseApiClient
  from httpx import Client as HTTPClient

  creds = mock.Mock()
  client = Client(vertexai=True, api_key='test-api-key')

  with (
      mock.patch.object(
          BaseApiClient, "_access_token", return_value='fake-vertex-token'
      ) as  mock_access_token,
      mock.patch.object(
          HTTPClient, "send",
          return_value=mock.Mock(),
      ) as mock_send,
  ):

    response = client.interactions.create(
        model='gemini-2.5-flash',
        input='What is the largest planet in our solar system?',
    )

    mock_send.assert_called_once()
    mock_access_token.assert_not_called()
    args, kwargs = mock_send.call_args
    headers = args[0].headers
    assert any(
        key == "x-goog-api-key" and value == 'test-api-key'
        for key, value in headers.items())

def test_interactions_vertex_url():
    creds = mock.Mock()
    creds.quota_project_id = "test-quota-project"
    client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)

    with mock.patch("httpx.Client.send") as mock_send:
        mock_send.return_value = Response(200, request=Request('POST', ''))
        client.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
        )
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == 'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/test-project/locations/us-central1/interactions'

def test_interactions_vertex_auth_refresh_on_retry():
    from ..._api_client import BaseApiClient
    from httpx import Client as HTTPClient

    creds = mock.Mock()
    creds.quota_project_id = "test-quota-project"
    client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)
    client._api_client.max_retries = 2

    token_values = ['token1', 'token2', 'token3']
    token_iter = iter(token_values)

    def get_token():
        return next(token_iter)

    with (
        mock.patch.object(BaseApiClient, "_access_token", side_effect=get_token) as mock_access_token,
        mock.patch.object(HTTPClient, "send") as mock_send,
    ):
        mock_send.side_effect = [
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(200, request=Request('POST', '')),
        ]

        client.interactions.create(model='gemini-1.5-flash', input='Hello')

        assert mock_access_token.call_count == 3
        assert mock_send.call_count == 3
        # Check headers of each call
        for i in range(3):
            headers = mock_send.call_args_list[i][0][0].headers
            assert headers['authorization'] == f'Bearer {token_values[i]}'

@pytest.mark.xfail(reason="extra_headers don't override default auth")
def test_interactions_vertex_extra_headers_override():
    from ..._api_client import BaseApiClient
    from httpx import Client as HTTPClient

    creds = mock.Mock()
    creds.quota_project_id = "test-quota-project"
    client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)

    with (
        mock.patch.object(BaseApiClient, "_access_token", return_value='default-token') as mock_access_token,
        mock.patch.object(HTTPClient, "send") as mock_send,
    ):
        mock_send.return_value = Response(200, request=Request('POST', ''))

        # Override Authorization
        client.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
            extra_headers={'Authorization': 'Bearer manual-token'}
        )
        mock_send.assert_called_once()
        headers = mock_send.call_args[0][0].headers
        assert headers['authorization'] == 'Bearer manual-token'
        mock_access_token.assert_not_called() # Should not fetch default token

        mock_send.reset_mock()
        mock_access_token.reset_mock()

        # Provide API Key
        client.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
            extra_headers={'x-goog-api-key': 'manual-key'}
        )
        mock_send.assert_called_once()
        headers = mock_send.call_args[0][0].headers
        assert headers['x-goog-api-key'] == 'manual-key'
        assert 'authorization' not in headers
        mock_access_token.assert_not_called()

@pytest.mark.asyncio
async def test_async_interactions_gemini_url(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()

    with mock.patch.object(AsyncHttpxClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('POST', ''))
        await client.aio.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
        )
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url).endswith('/v1beta/interactions')
        assert request.headers['x-goog-api-key'] == 'test-api-key'

@pytest.mark.asyncio
async def test_async_interactions_gemini_no_vertex_auth(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()

    with (
        mock.patch.object(BaseApiClient, "_async_access_token") as mock_access_token,
        mock.patch.object(AsyncHttpxClient, "send") as mock_send,
    ):
        mock_send.return_value = Response(200, request=Request('POST', ''))
        await client.aio.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
        )
        mock_access_token.assert_not_called()

@pytest.mark.asyncio
async def test_async_interactions_gemini_retry(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()
    client.aio._api_client.max_retries = 2

    with mock.patch.object(AsyncHttpxClient, "send") as mock_send:
        mock_send.side_effect = [
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(200, request=Request('POST', '')),
        ]
        await client.aio.interactions.create(model='gemini-1.5-flash', input='Hello')
        assert mock_send.call_count == 3

@pytest.mark.asyncio
async def test_async_interactions_gemini_extra_headers(monkeypatch):
    monkeypatch.setenv('GOOGLE_API_KEY', 'test-api-key')
    client = Client()

    with mock.patch.object(AsyncHttpxClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('POST', ''))
        await client.aio.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
            extra_headers={'X-Custom-Header': 'TestValue'}
        )
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert request.headers['x-custom-header'] == 'TestValue'
        assert request.headers['x-goog-api-key'] == 'test-api-key'

@pytest.mark.asyncio
async def test_async_interactions_vertex_auth_header():
  from ..._api_client import BaseApiClient
  from ..._interactions._base_client import SyncAPIClient
  from ..._api_client import AsyncHttpxClient

  creds = mock.Mock()
  creds.quota_project_id = "test-quota-project"
  client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)

  with (
      mock.patch.object(
          BaseApiClient, "_async_access_token", return_value='fake-vertex-token'
      ) as  mock_access_token,
      mock.patch.object(
          AsyncHttpxClient, "send",
          return_value=mock.Mock(),
      ) as mock_send,
  ):

    response = await client.aio.interactions.create(
        model='gemini-2.5-flash',
        input='What is the largest planet in our solar system?',
    )

    mock_send.assert_called_once()
    mock_access_token.assert_called_once()
    args, kwargs = mock_send.call_args
    headers = args[0].headers
    assert any(
        key == "authorization" and value == 'Bearer fake-vertex-token'
        for key, value in headers.items())
    assert any(
        key == "x-goog-user-project" and value == 'test-quota-project'
        for key, value in headers.items())

@pytest.mark.asyncio
async def test_async_interactions_vertex_key_no_auth_header():
  from ..._api_client import BaseApiClient
  from ..._api_client import AsyncHttpxClient
  creds = mock.Mock()
  client = Client(vertexai=True, api_key='test-api-key')

  with (
      mock.patch.object(
          BaseApiClient, "_async_access_token", return_value='fake-vertex-token'
      ) as  mock_access_token,
      mock.patch.object(
          AsyncHttpxClient, "send",
          return_value=mock.Mock(),
      ) as mock_send,
  ):

    response = await client.aio.interactions.create(
        model='gemini-2.5-flash',
        input='What is the largest planet in our solar system?',
    )

    mock_send.assert_called_once()
    mock_access_token.assert_not_called()
    args, kwargs = mock_send.call_args
    headers = args[0].headers
    assert any(
        key == "x-goog-api-key" and value == 'test-api-key'
        for key, value in headers.items())

@pytest.mark.asyncio
async def test_async_interactions_vertex_url():
    from ..._api_client import AsyncHttpxClient
    creds = mock.Mock()
    creds.quota_project_id = "test-quota-project"
    client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)

    with mock.patch.object(AsyncHttpxClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('POST', ''))
        await client.aio.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
        )
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == 'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/test-project/locations/us-central1/interactions'

@pytest.mark.asyncio
async def test_async_interactions_vertex_auth_refresh_on_retry():
    from ..._api_client import BaseApiClient
    from ..._api_client import AsyncHttpxClient

    creds = mock.Mock()
    creds.quota_project_id = "test-quota-project"
    client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)
    client.aio._api_client.max_retries = 2

    token_values = ['token1', 'token2', 'token3']
    token_iter = iter(token_values)

    async def get_token():
        return next(token_iter)

    with (
        mock.patch.object(BaseApiClient, "_async_access_token", side_effect=get_token) as mock_access_token,
        mock.patch.object(AsyncHttpxClient, "send") as mock_send,
    ):
        mock_send.side_effect = [
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(500, request=Request('POST', ''), headers={"retry-after-ms": "1"}),
            Response(200, request=Request('POST', '')),
        ]

        await client.aio.interactions.create(model='gemini-1.5-flash', input='Hello')

        assert mock_access_token.call_count == 3
        assert mock_send.call_count == 3
        for i in range(3):
            headers = mock_send.call_args_list[i][0][0].headers
            assert headers['authorization'] == f'Bearer {token_values[i]}'

@pytest.mark.xfail(reason="extra_headers don't override default auth")
@pytest.mark.asyncio
async def test_async_interactions_vertex_extra_headers_override():
    from ..._api_client import BaseApiClient
    from ..._api_client import AsyncHttpxClient

    creds = mock.Mock()
    creds.quota_project_id = "test-quota-project"
    client = Client(vertexai=True, project='test-project', location='us-central1', credentials=creds)

    with (
        mock.patch.object(BaseApiClient, "_async_access_token", return_value='default-token') as mock_access_token,
        mock.patch.object(AsyncHttpxClient, "send") as mock_send,
    ):
        mock_send.return_value = Response(200, request=Request('POST', ''))

        # Override Authorization
        await client.aio.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
            extra_headers={'Authorization': 'Bearer manual-token'}
        )
        mock_send.assert_called_once()
        headers = mock_send.call_args[0][0].headers
        assert headers['authorization'] == 'Bearer manual-token'
        mock_access_token.assert_not_called()

        mock_send.reset_mock()
        mock_access_token.reset_mock()

        # Provide API Key
        await client.aio.interactions.create(
            model='gemini-1.5-flash',
            input='Hello',
            extra_headers={'x-goog-api-key': 'manual-key'}
        )
        mock_send.assert_called_once()
        headers = mock_send.call_args[0][0].headers
        assert headers['x-goog-api-key'] == 'manual-key'
        assert 'authorization' not in headers
        mock_access_token.assert_not_called()
