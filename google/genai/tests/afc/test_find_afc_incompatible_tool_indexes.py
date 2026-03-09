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


"""Tests for find_afc_incompatible_tool_indexes."""

from typing import Any
import pytest
from ... import types
from ..._extra_utils import find_afc_incompatible_tool_indexes

try:
  from mcp import types as mcp_types
  from mcp import ClientSession as McpClientSession
  from ..._adapters import McpToGenAiToolAdapter
except ImportError as e:
  import sys

  if sys.version_info < (3, 10):
    raise ImportError(
        'MCP Tool requires Python 3.10 or above. Please upgrade your Python'
        ' version.'
    ) from e
  else:
    raise e


def get_weather_tool(city: str) -> str:
  """Get the weather in a city."""
  return f'The weather in {city} is sunny and 100 degrees.'


class MockMcpClientSession(McpClientSession):

  def __init__(self):
    self._read_stream = None
    self._write_stream = None

  async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
    return mcp_types.CallToolResult(
        content=[mcp_types.TextContent(type='text', text='1.01')]
    )

mcp_to_genai_tool_adapter = McpToGenAiToolAdapter(
    session=MockMcpClientSession(),
    list_tools_result=mcp_types.ListToolsResult(tools=[]),
)


def test_no_config_returns_empty_list():
    """Verifies that an empty list is returned if the input config is None.
    """
    result = find_afc_incompatible_tool_indexes(config=None)
    assert result == []

def test_config_with_no_tools_returns_empty_list():
    """Verifies an empty list is returned if the config has no 'tools' attribute.
    """
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig()
    )
    assert result == []

def test_empty_tools_list_returns_empty_list():
    """Verifies that an empty list is returned if the 'tools' list is empty."""
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig(tools=[])
    )

    assert result == []

def test_all_compatible_tools_returns_empty_list_with_empty_fd():
    """Verifies that an empty list is returned when all tools are compatible.

    A tool is compatible if it's not a `types.Tool` or if its
    `function_declarations` attribute is empty or None from config.
    """
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                ),
                types.Tool(retrieval=types.Retrieval()),
                types.Tool(google_search=types.GoogleSearch()),
                types.Tool(code_execution=types.ToolCodeExecution()),
                types.Tool(google_maps=types.GoogleMaps()),
                types.Tool(url_context=types.UrlContext()),
                types.Tool(computer_use=types.ComputerUse()),
                types.Tool(code_execution=types.ToolCodeExecution()),
                types.Tool(function_declarations=[]),
                mcp_types.Tool(
                    name='get_weather',
                    description='Get the weather in a city.',
                    inputSchema={
                        'type': 'object',
                        'properties': {'location': {'type': 'string'}},
                    },
                ),
                get_weather_tool,
                mcp_to_genai_tool_adapter,
            ]
        )
    )

    assert result == []

def test_all_compatible_tools_returns_empty_list_with_none_fd():
    """Verifies that an empty list is returned when all tools are compatible.

    A tool is compatible if it's not a `types.Tool` or if its
    `function_declarations` attribute is empty or None from config.
    """
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                ),
                types.Tool(retrieval=types.Retrieval()),
                types.Tool(google_search=types.GoogleSearch()),
                types.Tool(code_execution=types.ToolCodeExecution()),
                types.Tool(google_maps=types.GoogleMaps()),
                types.Tool(url_context=types.UrlContext()),
                types.Tool(computer_use=types.ComputerUse()),
                types.Tool(code_execution=types.ToolCodeExecution()),
                types.Tool(function_declarations=None),
                mcp_types.Tool(
                    name='get_weather',
                    description='Get the weather in a city.',
                    inputSchema={
                        'type': 'object',
                        'properties': {'location': {'type': 'string'}},
                    },
                ),
                get_weather_tool,
                mcp_to_genai_tool_adapter,
            ]
        )
    )

    assert result == []

def test_all_compatible_tools_returns_empty_list():
    """Verifies that an empty list is returned when all tools are compatible.

    A tool is compatible if it's not a `types.Tool` or if its
    `function_declarations` attribute is empty or None from config.
    """
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                ),
                types.Tool(retrieval=types.Retrieval()),
                types.Tool(google_search=types.GoogleSearch()),
                types.Tool(code_execution=types.ToolCodeExecution()),
                types.Tool(google_maps=types.GoogleMaps()),
                types.Tool(url_context=types.UrlContext()),
                types.Tool(computer_use=types.ComputerUse()),
                types.Tool(code_execution=types.ToolCodeExecution()),
                types.Tool(function_declarations=[]),
                mcp_types.Tool(
                    name='get_weather',
                    description='Get the weather in a city.',
                    inputSchema={
                        'type': 'object',
                        'properties': {'location': {'type': 'string'}},
                    },
                ),
                get_weather_tool,
                mcp_to_genai_tool_adapter,
            ]
        )
    )

    assert result == []

def test_single_incompatible_tool():
    """Verifies that the correct index is returned for a single incompatible
    tool.
    """
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                ),
                types.Tool(retrieval=types.Retrieval()),
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(name='test_function')
                    ]
                ),
                get_weather_tool,
                mcp_to_genai_tool_adapter,
            ]
        )
    )
    assert result == [2]


def test_multiple_incompatible_tools():
    """Verifies correct indexes are returned for multiple incompatible tools."""
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                ),
                types.Tool(retrieval=types.Retrieval()),
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(name='test_function')
                    ]
                ),
                types.Tool(computer_use=types.ComputerUse()),
                types.Tool(code_execution=types.ToolCodeExecution()),
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(name='test_function_2')
                    ]
                ),
                get_weather_tool,
                mcp_to_genai_tool_adapter,
            ]
        )
    )
    assert result == [2, 5]

def test_mcp_tool_incompatible():
    """Verifies correct indexes are returned for multiple incompatible tools."""
    result = find_afc_incompatible_tool_indexes(
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search_retrieval=types.GoogleSearchRetrieval()
                ),
                types.Tool(retrieval=types.Retrieval()),
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(name='test_function')
                    ]
                ),
                types.Tool(code_execution=types.ToolCodeExecution()),

                get_weather_tool,
                mcp_to_genai_tool_adapter,
                types.Tool(
                    mcp_servers=[types.McpServer(name='test_mcp_server')]
                ),
            ]
        )
    )
    assert result == [2, 6]
