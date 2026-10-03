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

import re
import pytest
from ... import _extra_utils
from ... import types
from ..._adapters import McpToGenAiToolAdapter

try:
  from mcp import types as mcp_types
  from mcp import ClientSession as McpClientSession
except ImportError as e:
  import sys

  if sys.version_info < (3, 10):
    raise ImportError(
        'MCP Tool requires Python 3.10 or above. Please upgrade your Python'
        ' version.'
    ) from e
  else:
    raise e


def test_parse_empty_config_dict():
  """Test conversion of empty GenerateContentConfigDict to parsed config."""
  config = {}
  parsed_config = _extra_utils.parse_config_for_mcp_usage(config)
  assert parsed_config == None


def test_parse_empty_config_object():
  """Test conversion of empty GenerateContentConfig to parsed config."""
  config = types.GenerateContentConfig()
  parsed_config = _extra_utils.parse_config_for_mcp_usage(config)
  assert config is not parsed_config  # config is not modified


def test_parse_config_object_with_tools():
  """Test conversion of GenerateContentConfig with tools to parsed config."""

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None

    async def list_tools(self):
      return mcp_types.ListToolsResult(
          tools=[
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              ),
              mcp_types.Tool(
                  name='get_weather_2',
                  description='Different tool to get the weather.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              ),
          ]
      )

  mock_session_instance = MockMcpClientSession()
  config = types.GenerateContentConfig(tools=[mock_session_instance])
  parsed_config = _extra_utils.parse_config_for_mcp_usage(config)
  assert config.http_options is None
  assert config is not parsed_config  # config is not modified
  assert re.match(
      r'mcp_used/\d+\.\d+\.\d+',
      parsed_config.http_options.headers['x-goog-api-client'],
  )


def test_parse_config_object_with_tools_and_existing_headers():
  """Test conversion of GenerateContentConfig with tools and existing headers to parsed config."""

  config = types.GenerateContentConfig(
      tools=[
          mcp_types.Tool(
              name='get_weather',
              description='Get the weather in a city.',
              inputSchema={
                  'type': 'object',
                  'properties': {'location': {'type': 'string'}},
              },
          ),
          mcp_types.Tool(
              name='get_weather_2',
              description='Different tool to get the weather.',
              inputSchema={
                  'type': 'object',
                  'properties': {'location': {'type': 'string'}},
              },
          ),
      ],
      http_options=types.HttpOptions(
          headers={
              'x-goog-api-client': 'google-genai-sdk/1.0.0 gl-python/1.0.0'
          }
      ),
  )
  parsed_config = _extra_utils.parse_config_for_mcp_usage(config)
  assert not re.match(
      r'mcp_used/\d+\.\d+\.\d+',
      config.http_options.headers['x-goog-api-client'],
  )
  assert config is not parsed_config  # config is not modified
  assert re.match(
      r'google-genai-sdk/1.0.0 gl-python/1.0.0 mcp_used/\d+\.\d+\.\d+',
      parsed_config.http_options.headers['x-goog-api-client'],
  )
