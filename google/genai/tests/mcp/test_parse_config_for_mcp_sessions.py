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

import _asyncio
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


@pytest.mark.asyncio
async def test_parse_empty_config_dict():
  """Test conversion of empty GenerateContentConfigDict to parsed config."""
  config = {}
  parsed_config, mcp_to_genai_tool_adapters = (
      await _extra_utils.parse_config_for_mcp_sessions(config)
  )
  assert parsed_config == None
  assert not mcp_to_genai_tool_adapters


@pytest.mark.asyncio
async def test_parse_empty_config_object():
  """Test conversion of empty GenerateContentConfig to parsed config."""
  config = types.GenerateContentConfig()
  parsed_config, mcp_to_genai_tool_adapters = (
      await _extra_utils.parse_config_for_mcp_sessions(config)
  )
  assert config is not parsed_config  # config is not modified
  assert not mcp_to_genai_tool_adapters


@pytest.mark.asyncio
async def test_parse_config_object_with_tools():
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
  parsed_config, mcp_to_genai_tool_adapters = (
      await _extra_utils.parse_config_for_mcp_sessions(config)
  )
  assert len(config.tools) == 1
  assert config.tools[0] is mock_session_instance
  assert config is not parsed_config  # config is not modified
  assert len(mcp_to_genai_tool_adapters) == 2
  assert mcp_to_genai_tool_adapters.keys() == {
      'get_weather',
      'get_weather_2',
  }
  assert isinstance(
      mcp_to_genai_tool_adapters['get_weather'], McpToGenAiToolAdapter
  )
  assert isinstance(
      mcp_to_genai_tool_adapters['get_weather_2'], McpToGenAiToolAdapter
  )


@pytest.mark.asyncio
async def test_parse_config_object_with_tools_complex_type():
  """Test conversion of GenerateContentConfig with tools to parsed config."""

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None
      self._future = _asyncio.Future()  # This object cannot be pickled.

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
  parsed_config, mcp_to_genai_tool_adapters = (
      await _extra_utils.parse_config_for_mcp_sessions(config)
  )
  assert len(config.tools) == 1
  assert config.tools[0] is mock_session_instance
  assert config is not parsed_config  # config is not modified
  assert len(mcp_to_genai_tool_adapters) == 2
  assert mcp_to_genai_tool_adapters.keys() == {
      'get_weather',
      'get_weather_2',
  }
  assert isinstance(
      mcp_to_genai_tool_adapters['get_weather'], McpToGenAiToolAdapter
  )
  assert isinstance(
      mcp_to_genai_tool_adapters['get_weather_2'], McpToGenAiToolAdapter
  )


@pytest.mark.asyncio
async def test_parse_config_object_with_non_mcp_tools():
  """Test conversion of GenerateContentConfig with regular tools to parsed config."""

  config = types.GenerateContentConfig(
      tools=[
          types.Tool(
              function_declarations=[
                  {'name': 'tool-1', 'description': 'tool-1-description'}
              ]
          ),
          types.Tool(
              function_declarations=[
                  {'name': 'tool-2', 'description': 'tool-2-description'}
              ]
          ),
      ]
  )
  parsed_config, mcp_to_genai_tool_adapters = (
      await _extra_utils.parse_config_for_mcp_sessions(config)
  )
  assert len(config.tools) == 2
  assert config is not parsed_config  # config is not modified
  assert mcp_to_genai_tool_adapters == {}
  assert parsed_config.tools == [
      types.Tool(
          function_declarations=[
              {'name': 'tool-1', 'description': 'tool-1-description'}
          ]
      ),
      types.Tool(
          function_declarations=[
              {'name': 'tool-2', 'description': 'tool-2-description'}
          ]
      ),
  ]
