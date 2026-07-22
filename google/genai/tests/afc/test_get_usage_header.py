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

"""Unit tests for _extra_utils.get_usage_header."""

from ... import types
from ... import version as public_version
from ..._extra_utils import get_usage_header


def test_get_usage_header_none_config():
  config = get_usage_header(None)
  expected_header = f'google-genai-sdk/{public_version.__version__}+afc'
  assert config.http_options.headers['user-agent'] == expected_header
  assert config.http_options.headers['x-goog-api-client'] == expected_header


def test_get_usage_header_dict_config():
  config = get_usage_header({'temperature': 0.5}, usage='afc')
  expected_header = f'google-genai-sdk/{public_version.__version__}+afc'
  assert config.temperature == 0.5
  assert config.http_options.headers['user-agent'] == expected_header
  assert config.http_options.headers['x-goog-api-client'] == expected_header


def test_get_usage_header_custom_usage():
  config = get_usage_header(None, usage='chat')
  expected_header = f'google-genai-sdk/{public_version.__version__}+chat'
  assert config.http_options.headers['user-agent'] == expected_header
  assert config.http_options.headers['x-goog-api-client'] == expected_header


def test_get_usage_header_with_existing_sdk_headers():
  initial_headers = {
      'user-agent': (
          f'google-genai-sdk/{public_version.__version__} gl-python/3.12'
      ),
      'x-goog-api-client': (
          f'google-genai-sdk/{public_version.__version__} gl-python/3.12'
      ),
  }
  config = types.GenerateContentConfig(
      http_options=types.HttpOptions(headers=initial_headers)
  )
  config = get_usage_header(config, usage='afc')
  expected_header = (
      f'google-genai-sdk/{public_version.__version__}+afc gl-python/3.12'
  )
  assert config.http_options.headers['user-agent'] == expected_header
  assert config.http_options.headers['x-goog-api-client'] == expected_header


def test_get_usage_header_idempotent_no_duplicate_usage():
  config = get_usage_header(None, usage='afc')
  config = get_usage_header(config, usage='afc')
  expected_header = f'google-genai-sdk/{public_version.__version__}+afc'
  assert config.http_options.headers['user-agent'] == expected_header
  assert config.http_options.headers['x-goog-api-client'] == expected_header


def test_get_usage_header_multiple_usages_no_duplicate():
  config = get_usage_header(None, usage='chat')
  config = get_usage_header(config, usage='afc')
  # Call again with chat and afc to ensure no duplicate entries are appended
  config = get_usage_header(config, usage='chat')
  config = get_usage_header(config, usage='afc')

  user_agent = config.http_options.headers['user-agent']
  x_goog_api_client = config.http_options.headers['x-goog-api-client']

  assert '+chat' in user_agent
  assert '+afc' in user_agent
  assert user_agent.count('+chat') == 1
  assert user_agent.count('+afc') == 1

  assert '+chat' in x_goog_api_client
  assert '+afc' in x_goog_api_client
  assert x_goog_api_client.count('+chat') == 1
  assert x_goog_api_client.count('+afc') == 1


def test_get_usage_header_with_custom_user_agent():
  initial_headers = {
      'user-agent': 'custom-agent/1.0',
      'x-goog-api-client': 'custom-agent/1.0',
  }
  config = types.GenerateContentConfig(
      http_options=types.HttpOptions(headers=initial_headers)
  )
  config = get_usage_header(config, usage='afc')
  # Call again to ensure idempotency
  config = get_usage_header(config, usage='afc')

  expected_usage = f'google-genai-sdk/{public_version.__version__}+afc'
  assert 'custom-agent/1.0' in config.http_options.headers['user-agent']
  assert expected_usage in config.http_options.headers['user-agent']
  assert config.http_options.headers['user-agent'].count('+afc') == 1


def test_get_usage_header_preserves_other_http_options():
  config = types.GenerateContentConfig(
      http_options=types.HttpOptions(
          api_version='v1alpha',
          headers={'custom-header': 'value'},
      )
  )
  config = get_usage_header(config, usage='afc')
  assert config.http_options.api_version == 'v1alpha'
  assert config.http_options.headers['custom-header'] == 'value'
  assert '+afc' in config.http_options.headers['user-agent']
  assert '+afc' in config.http_options.headers['x-goog-api-client']
