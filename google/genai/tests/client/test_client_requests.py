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

import httpx

from ... import _api_client as api_client
from ... import Client
from ... import types


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


def test_build_request_dedupes_title_case_user_agent():
  """A title-case User-Agent in client options yields one user-agent key."""
  client = Client(
      api_key='test_api_key',
      http_options=types.HttpOptions(headers={'User-Agent': 'test-user-agent'}),
  )
  request = client.models._api_client._build_request(
      'GET', 'test/path', {'key': 'value'}
  )
  ua_keys = [k for k in request.headers if k.lower() == 'user-agent']
  assert ua_keys == ['user-agent']
  assert 'test-user-agent' in request.headers['user-agent']
  assert 'google-genai-sdk/' in request.headers['user-agent']
  assert 'gl-python/' in request.headers['user-agent']


def test_build_request_dedupes_per_request_title_case_user_agent():
  """A per-request title-case User-Agent matches the lowercase result."""
  request_client = Client(api_key='test_api_key').models._api_client
  title_request = request_client._build_request(
      'GET',
      'test/path',
      {'key': 'value'},
      types.HttpOptionsDict(headers={'User-Agent': 'test-user-agent'}),
  )
  lower_request = request_client._build_request(
      'GET',
      'test/path',
      {'key': 'value'},
      types.HttpOptionsDict(headers={'user-agent': 'test-user-agent'}),
  )
  ua_keys = [k for k in title_request.headers if k.lower() == 'user-agent']
  assert ua_keys == ['user-agent']
  assert (
      title_request.headers['user-agent'] == lower_request.headers['user-agent']
  )


def test_build_request_dedupes_title_case_goog_api_client():
  """A title-case X-Goog-Api-Client yields one x-goog-api-client key."""
  request_client = Client(api_key='test_api_key').models._api_client
  request = request_client._build_request(
      'GET',
      'test/path',
      {'key': 'value'},
      types.HttpOptionsDict(headers={'X-Goog-Api-Client': 'test-client'}),
  )
  keys = [k for k in request.headers if k.lower() == 'x-goog-api-client']
  assert keys == ['x-goog-api-client']
  assert 'test-client' in request.headers['x-goog-api-client']
  assert 'google-genai-sdk/' in request.headers['x-goog-api-client']


def test_append_library_version_headers_merges_case_variants():
  """Case variants merge into one key, in order, and the merge is idempotent."""
  headers = {'User-Agent': 'first/1', 'user-agent': 'second/2'}
  api_client.append_library_version_headers(headers)
  assert [k for k in headers if k.lower() == 'user-agent'] == ['user-agent']
  user_agent = headers['user-agent']
  assert 'first/1 second/2' in user_agent
  assert 'google-genai-sdk/' in user_agent
  assert 'gl-python/' in user_agent

  api_client.append_library_version_headers(headers)
  assert headers['user-agent'] == user_agent


def test_append_library_version_headers_drops_repeated_variant_value():
  """A variant whose value repeats an earlier one is not joined twice."""
  headers = {'User-Agent': 'same/1', 'USER-AGENT': 'same/1'}
  api_client.append_library_version_headers(headers)
  assert [k for k in headers if k.lower() == 'user-agent'] == ['user-agent']
  assert headers['user-agent'].count('same/1') == 1


def test_title_case_user_agent_sent_once_on_wire():
  """The transport receives a single User-Agent header."""
  recorded = []

  def handler(request: httpx.Request) -> httpx.Response:
    recorded.append(request)
    return httpx.Response(200, json={'candidates': []})

  client = Client(
      api_key='test_api_key',
      http_options=types.HttpOptions(
          headers={'User-Agent': 'x/1'},
          httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
      ),
  )
  client.models.generate_content(model='gemini-2.5-flash', contents='hi')
  assert len(recorded) == 1
  user_agents = recorded[0].headers.get_list('user-agent')
  assert len(user_agents) == 1
  assert 'x/1' in user_agents[0]
