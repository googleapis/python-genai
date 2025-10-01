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


from ... import _api_client
from ... import types


def test_patch_http_options_with_copies_all_fields():
  patch_options = types.HttpOptions(
      base_url='https://fake-url.com/',
      api_version='v1',
      headers={'X-Custom-Header': 'custom_value'},
      timeout=10000,
      client_args={'http2': True},
      async_client_args={'http1': True},
      extra_body={'key': 'value'},
      retry_options=types.HttpRetryOptions(attempts=10),
  )
  options = types.HttpOptions()
  patched = _api_client.patch_http_options(options, patch_options)
  http_options_keys = types.HttpOptions.model_fields.keys()

  for key in http_options_keys:
    assert hasattr(patched, key) and getattr(patched, key) is not None
  assert patched.base_url == 'https://fake-url.com/'
  assert patched.api_version == 'v1'
  assert patched.headers['X-Custom-Header'] == 'custom_value'
  assert patched.timeout == 10000
  assert patched.retry_options.attempts == 10
  assert patched.client_args['http2']
  assert patched.async_client_args['http1']


def test_patch_http_options_merges_headers():
  original_options = types.HttpOptions(
      headers={
          'X-Custom-Header': 'different_value',
          'X-different-header': 'different_value',
      }
  )
  patch_options = types.HttpOptions(
      base_url='https://fake-url.com/',
      api_version='v1',
      headers={'X-Custom-Header': 'custom_value'},
      timeout=10000,
  )
  patched = _api_client.patch_http_options(original_options, patch_options)
  # If the header is present in both the original and patch options, the patch
  # options value should be used
  assert patched.headers['X-Custom-Header'] == 'custom_value'

  assert patched.headers['X-different-header'] == 'different_value'


def test_patch_http_options_appends_version_headers():
  original_options = types.HttpOptions(
      headers={
          'X-Custom-Header': 'different_value',
          'X-different-header': 'different_value',
      }
  )
  patch_options = types.HttpOptions(
      base_url='https://fake-url.com/',
      api_version='v1',
      headers={'X-Custom-Header': 'custom_value'},
      timeout=10000,
  )
  patched = _api_client.patch_http_options(original_options, patch_options)
  assert 'user-agent' in patched.headers
  assert 'x-goog-api-client' in patched.headers


def test_update_headers_appends_headers_for_reserved_keys():
  client_options = types.HttpOptions(
      headers={
          'user-agent': 'client_user_agent',
          'x-goog-api-client': 'client_x_goog_api_client',
      }
  )
  config_options = types.HttpOptions(
      headers={
          'user-agent': 'config_user_agent',
          'x-goog-api-client': 'config_x_goog_api_client',
      }
  )
  updated_headers = _api_client._update_headers_with_append_keys(
      client_options,
      config_options,
  )
  assert updated_headers['user-agent'] == 'client_user_agent, config_user_agent'
  assert (
      updated_headers['x-goog-api-client']
      == 'client_x_goog_api_client, config_x_goog_api_client'
  )


def test_update_headers_behavior_for_non_reserved_keys():
  client_options = types.HttpOptions(
      headers={
          'user-agent': 'client_user_agent',
          'x-goog-api-client': 'client_x_goog_api_client',
          'custom-header': 'client_custom_header',
          'custom-header-2': 'client_custom_header_2',
      }
  )
  config_options = types.HttpOptions(
      headers={
          'user-agent': 'config_user_agent',
          'x-goog-api-client': 'config_x_goog_api_client',
          'custom-header': 'config_custom_header',
          'custom-header-3': 'config_custom_header_3',
      }
  )
  updated_headers = _api_client._update_headers_with_append_keys(
      client_options,
      config_options,
  )
  assert updated_headers['user-agent'] == 'client_user_agent, config_user_agent'
  assert (
      updated_headers['x-goog-api-client']
      == 'client_x_goog_api_client, config_x_goog_api_client'
  )
  assert updated_headers['custom-header'] == 'config_custom_header'
  assert updated_headers['custom-header-2'] == 'client_custom_header_2'
  assert updated_headers['custom-header-3'] == 'config_custom_header_3'


def test_update_headers_behavior_for_missing_input():
  client_options = types.HttpOptions(
      headers={
          'user-agent': 'client_user_agent',
          'x-goog-api-client': 'client_x_goog_api_client',
          'custom-header': 'client_custom_header',
          'custom-header-2': 'client_custom_header_2',
      }
  )
  config_options = types.HttpOptions(
      headers={
          'user-agent': 'config_user_agent',
          'x-goog-api-client': 'config_x_goog_api_client',
          'custom-header': 'config_custom_header',
          'custom-header-3': 'config_custom_header_3',
      }
  )
  # No original headers, no config options, result should be
  # empty
  update_headers_1 = _api_client._update_headers_with_append_keys(
      None, None
  )
  assert update_headers_1 == {}

  # No original headers, config options,result should be
  # config headers
  update_headers_2 = _api_client._update_headers_with_append_keys(
      None, config_options
  )
  assert update_headers_2 == config_options.headers

  # Original headers, no config options, no reserved keys, result should be
  # original headers
  update_headers_3 = _api_client._update_headers_with_append_keys(
      client_options, None
  )
  assert update_headers_3 == client_options.headers



def test_setting_timeout_populates_server_timeout_header():
  api_client = _api_client.BaseApiClient(
      vertexai=False,
      api_key='test_api_key',
      http_options=types.HttpOptions(timeout=10000),
  )
  request = api_client._build_request(
      http_method='POST',
      path='sample/path',
      request_dict={},
  )
  assert 'X-Server-Timeout' in request.headers
  assert request.headers['X-Server-Timeout'] == '10'


def test_timeout_rounded_to_nearest_second():
  api_client = _api_client.BaseApiClient(
      vertexai=False,
      api_key='test_api_key',
  )
  http_options = types.HttpOptions(timeout=7300)
  request = api_client._build_request(
      http_method='POST',
      path='sample/path',
      request_dict={},
      http_options=http_options,
  )
  assert request.headers['X-Server-Timeout'] == '8'


def test_server_timeout_not_overwritten():
  api_client = _api_client.BaseApiClient(
      vertexai=False,
      api_key='test_api_key',
  )
  http_options = types.HttpOptions(
      headers={'X-Server-Timeout': '3'},
      timeout=11000)
  request = api_client._build_request(
      http_method='POST',
      path='sample/path',
      request_dict={},
      http_options=http_options,
  )
  assert request.headers['X-Server-Timeout'] == '3'


def test_server_timeout_not_set_by_default():
  api_client = _api_client.BaseApiClient(
      vertexai=False,
      api_key='test_api_key',
  )
  request = api_client._build_request(
      http_method='POST',
      path='sample/path',
      request_dict={},
  )
  assert not 'X-Server-Timeout' in request.headers


def test_retry_options_not_set_by_default():
  options = types.HttpOptions()
  assert options.retry_options is None
