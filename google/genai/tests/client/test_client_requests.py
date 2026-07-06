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


"""Tests for client behavior when issuing requests."""

from unittest import mock
import asyncio
import pytest

try:
  import aiohttp

  AIOHTTP_NOT_INSTALLED = False
except ImportError:
  AIOHTTP_NOT_INSTALLED = True
  aiohttp = mock.MagicMock()

from ... import _api_client as api_client
from ... import Client
from ... import types


requires_aiohttp = pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason='aiohttp is not installed, skipping test.'
)


@pytest.fixture(autouse=True)
def reset_has_aiohttp():
  api_client.has_aiohttp = not AIOHTTP_NOT_INSTALLED


def build_test_client(monkeypatch):
  monkeypatch.setenv('GOOGLE_API_KEY', 'google_api_key')
  return Client()


def test_join_url_path_base_url_with_trailing_slash_and_path_with_leading_slash():
  base_url = 'https://fake-url.com/some_path/'
  path = '/v1beta/models'
  assert (
      api_client.join_url_path(base_url, path)
      == 'https://fake-url.com/some_path/v1beta/models'
  )


def test_join_url_path_with_base_url_with_trailing_slash_and_path_without_leading_slash():
  base_url = 'https://fake-url.com/some_path/'
  path = 'v1beta/models'
  assert (
      api_client.join_url_path(base_url, path)
      == 'https://fake-url.com/some_path/v1beta/models'
  )


def test_join_url_path_with_base_url_without_trailing_slash_and_path_with_leading_slash():
  base_url = 'https://fake-url.com/some_path'
  path = '/v1beta/models'
  assert (
      api_client.join_url_path(base_url, path)
      == 'https://fake-url.com/some_path/v1beta/models'
  )


def test_join_url_path_with_base_url_without_trailing_slash_and_path_without_leading_slash():
  base_url = 'https://fake-url.com/some_path'
  path = 'v1beta/models'
  assert (
      api_client.join_url_path(base_url, path)
      == 'https://fake-url.com/some_path/v1beta/models'
  )


def test_join_url_path_base_url_without_path_with_trailing_slash():
  base_url = 'https://fake-url.com/'
  path = 'v1beta/models'
  assert (
      api_client.join_url_path(base_url, path)
      == 'https://fake-url.com/v1beta/models'
  )


def test_join_url_path_base_url_without_path_without_trailing_slash():
  base_url = 'https://fake-url.com'
  path = 'v1beta/models'
  assert (
      api_client.join_url_path(base_url, path)
      == 'https://fake-url.com/v1beta/models'
  )


def test_build_request_sets_library_version_headers(monkeypatch):
  request_client = build_test_client(monkeypatch).models._api_client
  request = request_client._build_request('GET', 'test/path', {'key': 'value'})
  assert 'google-genai-sdk/' in request.headers['user-agent']
  assert 'gl-python/' in request.headers['user-agent']
  assert 'google-genai-sdk/' in request.headers['x-goog-api-client']
  assert 'gl-python/' in request.headers['x-goog-api-client']


def test_build_request_appends_to_user_agent_headers(monkeypatch):
  request_client = build_test_client(monkeypatch).models._api_client
  request = request_client._build_request(
      'GET',
      'test/path',
      {'key': 'value'},
      types.HttpOptionsDict(
          base_url='test/url',
          api_version='1',
          headers={'user-agent': 'test-user-agent'},
      ),
  )
  assert 'test-user-agent' in request.headers['user-agent']
  assert 'google-genai-sdk/' in request.headers['user-agent']
  assert 'gl-python/' in request.headers['user-agent']
  assert 'google-genai-sdk/' in request.headers['x-goog-api-client']


def test_build_request_appends_to_goog_api_client_headers(monkeypatch):
  request_client = build_test_client(monkeypatch).models._api_client
  request = request_client._build_request(
      'GET',
      'test/path',
      {'key': 'value'},
      types.HttpOptionsDict(
          base_url='test/url',
          api_version='1',
          headers={'x-goog-api-client': 'test-goog-api-client'},
      ),
  )
  assert 'google-genai-sdk/' in request.headers['user-agent']
  assert 'test-goog-api-client' in request.headers['x-goog-api-client']
  assert 'google-genai-sdk/' in request.headers['x-goog-api-client']
  assert 'gl-python/' in request.headers['x-goog-api-client']


def test_build_request_keeps_sdk_version_headers(monkeypatch):
  headers_to_inject = {}
  api_client.append_library_version_headers(headers_to_inject)
  assert 'google-genai-sdk/' in headers_to_inject['user-agent']
  request_client = build_test_client(monkeypatch).models._api_client
  request = request_client._build_request(
      'GET',
      'test/path',
      {'key': 'value'},
      types.HttpOptionsDict(
          base_url='test/url',
          api_version='1',
          headers=headers_to_inject,
      ),
  )
  assert 'google-genai-sdk/' in request.headers['user-agent']
  assert 'gl-python/' in request.headers['x-goog-api-client']
  assert 'google-genai-sdk/' in request.headers['x-goog-api-client']
  assert 'gl-python/' in request.headers['x-goog-api-client']


def test_build_request_with_resource_scope(monkeypatch):
  monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
  monkeypatch.delenv('GEMINI_API_KEY', raising=False)
  monkeypatch.delenv('GOOGLE_CLOUD_PROJECT', raising=False)
  monkeypatch.delenv('GOOGLE_CLOUD_LOCATION', raising=False)

  client = Client(
      vertexai=True,
      http_options=types.HttpOptionsDict(
          base_url='https://custom-base-url.com',
          base_url_resource_scope=types.ResourceScope.COLLECTION,
      ),
  )

  request = client.models._api_client._build_request(
      'post',
      'publishers/google/models/gemini-3-pro-preview',
      {'key': 'value'},
  )
  assert request.url == 'https://custom-base-url.com/publishers/google/models/gemini-3-pro-preview'


def test_build_request_with_resource_scope_with_project_and_location(
    monkeypatch,
):
  monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
  monkeypatch.delenv('GEMINI_API_KEY', raising=False)
  monkeypatch.delenv('GOOGLE_CLOUD_PROJECT', raising=False)
  monkeypatch.delenv('GOOGLE_CLOUD_LOCATION', raising=False)

  client = Client(
      vertexai=True,
      project='test-project',
      location='test-location',
      http_options=types.HttpOptionsDict(
          base_url='https://custom-base-url.com',
          base_url_resource_scope=types.ResourceScope.COLLECTION,
      ),
  )

  request = client.models._api_client._build_request(
      'post',
      'publishers/google/models/gemini-3-pro-preview',
      {'key': 'value'},
  )
  assert request.url == 'https://custom-base-url.com/publishers/google/models/gemini-3-pro-preview'


def build_test_client_no_env_vars(monkeypatch):
  monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
  monkeypatch.delenv('GEMINI_API_KEY', raising=False)
  monkeypatch.delenv('GOOGLE_CLOUD_PROJECT', raising=False)
  monkeypatch.delenv('GOOGLE_CLOUD_LOCATION', raising=False)
  return Client(
      vertexai=True,
      http_options=types.HttpOptionsDict(
          base_url='https://custom-base-url.com',
          headers={'Authorization': 'Bearer fake_access_token'},
      ),
    )


def test_build_request_with_custom_base_url_no_env_vars(monkeypatch):
  request_client = (
      build_test_client_no_env_vars(monkeypatch).models._api_client
  )
  request = request_client._build_request(
      'GET',
      'test/path',
      {'key': 'value'},
  )
  assert request.url == 'https://custom-base-url.com'


def test_sync_request_mtls_regional(monkeypatch):
  mock_session = mock.MagicMock()
  mock_session._is_mtls = True
  mock_response = mock.MagicMock()
  mock_response.status_code = 200
  mock_response.headers = {}
  mock_response.text = '{}'
  mock_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us-central1')
  client._api_client._authorized_session = mock_session
  with mock.patch.object(
      client._api_client, '_use_google_auth_sync', return_value=True
  ), mock.patch.object(
      client._api_client, '_access_token', return_value='mock_token'
  ):
    client._api_client._request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://us-central1-aiplatform.googleapis.com/v1beta1/models',
            headers={},
            data={},
        )
    )
  assert (
      mock_session.request.call_args.kwargs['url']
      == 'https://us-central1-aiplatform.mtls.googleapis.com/v1beta1/models'
  )


def test_sync_request_mtls_sandbox(monkeypatch):
  mock_session = mock.MagicMock()
  mock_session._is_mtls = True
  mock_response = mock.MagicMock()
  mock_response.status_code = 200
  mock_response.headers = {}
  mock_response.text = '{}'
  mock_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us-central1')
  client._api_client._authorized_session = mock_session
  with mock.patch.object(
      client._api_client, '_use_google_auth_sync', return_value=True
  ), mock.patch.object(
      client._api_client, '_access_token', return_value='mock_token'
  ):
    client._api_client._request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://us-central1-aiplatform.sandbox.googleapis.com/v1beta1/models',
            headers={},
            data={},
        )
    )
  assert (
      mock_session.request.call_args.kwargs['url']
      == 'https://us-central1-aiplatform.mtls.sandbox.googleapis.com/v1beta1/models'
  )


def test_sync_request_mtls_multi_regional(monkeypatch):
  mock_session = mock.MagicMock()
  mock_session._is_mtls = True
  mock_response = mock.MagicMock()
  mock_response.status_code = 200
  mock_response.headers = {}
  mock_response.text = '{}'
  mock_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us')
  client._api_client._authorized_session = mock_session
  with mock.patch.object(
      client._api_client, '_use_google_auth_sync', return_value=True
  ), mock.patch.object(
      client._api_client, '_access_token', return_value='mock_token'
  ):
    client._api_client._request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://aiplatform.us.rep.googleapis.com/v1beta1/models',
            headers={},
            data={},
        )
    )
  assert (
      mock_session.request.call_args.kwargs['url']
      == 'https://aiplatform.us.rep.googleapis.com/v1beta1/models'
  )


@requires_aiohttp
@pytest.mark.asyncio
async def test_async_request_mtls_regional(monkeypatch):
  mock_async_session = mock.AsyncMock()
  mock_async_session._is_mtls = True
  mock_async_session.closed = False
  mock_response = mock.MagicMock(spec=aiohttp.ClientResponse)
  mock_response.status = 200
  mock_response.headers = {}
  mock_async_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us-central1')
  client._api_client._http_options.aiohttp_client = mock_async_session
  client._api_client._aiohttp_sessions[asyncio.get_running_loop()] = (
      mock_async_session
  )
  client._api_client._async_client_session_request_args = {}
  with mock.patch.object(
      client._api_client, '_use_aiohttp', return_value=True
  ), mock.patch.object(
      client._api_client, '_use_google_auth_async', return_value=True
  ), mock.patch.object(
      client._api_client, '_async_access_token', return_value='mock_token'
  ), mock.patch(
      'google.auth.transport.mtls.default_client_cert_source',
      return_value='mock_cert_source',
  ):
    await client._api_client._async_request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://us-central1-aiplatform.googleapis.com/v1beta1/models',
            headers={},
            data={},
        )
    )
  mock_async_session.configure_mtls_channel.assert_called_once_with(
      'mock_cert_source'
  )
  assert (
      mock_async_session.request.call_args.kwargs['url']
      == 'https://us-central1-aiplatform.mtls.googleapis.com/v1beta1/models'
  )


@requires_aiohttp
@pytest.mark.asyncio
async def test_async_request_mtls_sandbox(monkeypatch):
  mock_async_session = mock.AsyncMock()
  mock_async_session._is_mtls = True
  mock_async_session.closed = False
  mock_response = mock.MagicMock(spec=aiohttp.ClientResponse)
  mock_response.status = 200
  mock_response.headers = {}
  mock_async_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us-central1')
  client._api_client._http_options.aiohttp_client = mock_async_session
  client._api_client._aiohttp_sessions[asyncio.get_running_loop()] = (
      mock_async_session
  )
  client._api_client._async_client_session_request_args = {}
  with mock.patch.object(
      client._api_client, '_use_aiohttp', return_value=True
  ), mock.patch.object(
      client._api_client, '_use_google_auth_async', return_value=True
  ), mock.patch.object(
      client._api_client, '_async_access_token', return_value='mock_token'
  ), mock.patch(
      'google.auth.transport.mtls.default_client_cert_source',
      return_value='mock_cert_source',
  ):
    await client._api_client._async_request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://us-central1-aiplatform.sandbox.googleapis.com/v1beta1/models',
            headers={},
            data={},
        )
    )
  assert (
      mock_async_session.request.call_args.kwargs['url']
      == 'https://us-central1-aiplatform.mtls.sandbox.googleapis.com/v1beta1/models'
  )


@requires_aiohttp
@pytest.mark.asyncio
async def test_async_request_mtls_multi_regional(monkeypatch):
  mock_async_session = mock.AsyncMock()
  mock_async_session._is_mtls = True
  mock_async_session.closed = False
  mock_response = mock.MagicMock(spec=aiohttp.ClientResponse)
  mock_response.status = 200
  mock_response.headers = {}
  mock_async_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us')
  client._api_client._http_options.aiohttp_client = mock_async_session
  client._api_client._aiohttp_sessions[asyncio.get_running_loop()] = (
      mock_async_session
  )
  client._api_client._async_client_session_request_args = {}
  with mock.patch.object(
      client._api_client, '_use_aiohttp', return_value=True
  ), mock.patch.object(
      client._api_client, '_use_google_auth_async', return_value=True
  ), mock.patch.object(
      client._api_client, '_async_access_token', return_value='mock_token'
  ), mock.patch(
      'google.auth.transport.mtls.default_client_cert_source',
      return_value='mock_cert_source',
  ):
    await client._api_client._async_request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://aiplatform.us.rep.googleapis.com/v1beta1/models',
            headers={},
            data={},
        )
    )
  assert (
      mock_async_session.request.call_args.kwargs['url']
      == 'https://aiplatform.us.rep.googleapis.com/v1beta1/models'
  )


@requires_aiohttp
@pytest.mark.asyncio
async def test_async_stream_request_mtls_regional(monkeypatch):
  mock_async_session = mock.AsyncMock()
  mock_async_session._is_mtls = True
  mock_async_session.closed = False
  mock_response = mock.MagicMock(spec=aiohttp.ClientResponse)
  mock_response.status = 200
  mock_response.headers = {}
  mock_async_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us-central1')
  client._api_client._http_options.aiohttp_client = mock_async_session
  client._api_client._aiohttp_sessions[asyncio.get_running_loop()] = (
      mock_async_session
  )
  client._api_client._async_client_session_request_args = {}
  with mock.patch.object(
      client._api_client, '_use_aiohttp', return_value=True
  ), mock.patch.object(
      client._api_client, '_use_google_auth_async', return_value=True
  ), mock.patch.object(
      client._api_client, '_async_access_token', return_value='mock_token'
  ), mock.patch(
      'google.auth.transport.mtls.default_client_cert_source',
      return_value='mock_cert_source',
  ):
    await client._api_client._async_request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://us-central1-aiplatform.googleapis.com/v1beta1/models',
            headers={},
            data={},
        ),
        stream=True,
    )
  assert (
      mock_async_session.request.call_args.kwargs['url']
      == 'https://us-central1-aiplatform.mtls.googleapis.com/v1beta1/models'
  )


@requires_aiohttp
@pytest.mark.asyncio
async def test_async_stream_request_mtls_multi_regional(monkeypatch):
  mock_async_session = mock.AsyncMock()
  mock_async_session._is_mtls = True
  mock_async_session.closed = False
  mock_response = mock.MagicMock(spec=aiohttp.ClientResponse)
  mock_response.status = 200
  mock_response.headers = {}
  mock_async_session.request.return_value = mock_response

  client = Client(vertexai=True, project='test-project', location='us')
  client._api_client._http_options.aiohttp_client = mock_async_session
  client._api_client._aiohttp_sessions[asyncio.get_running_loop()] = (
      mock_async_session
  )
  client._api_client._async_client_session_request_args = {}
  with mock.patch.object(
      client._api_client, '_use_aiohttp', return_value=True
  ), mock.patch.object(
      client._api_client, '_use_google_auth_async', return_value=True
  ), mock.patch.object(
      client._api_client, '_async_access_token', return_value='mock_token'
  ), mock.patch(
      'google.auth.transport.mtls.default_client_cert_source',
      return_value='mock_cert_source',
  ):
    await client._api_client._async_request_once(
        api_client.HttpRequest(
            method='GET',
            url='https://aiplatform.us.rep.googleapis.com/v1beta1/models',
            headers={},
            data={},
        ),
        stream=True,
    )
  assert (
      mock_async_session.request.call_args.kwargs['url']
      == 'https://aiplatform.us.rep.googleapis.com/v1beta1/models'
  )
