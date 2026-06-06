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

"""Tests for get_function_map."""

import typing
from typing import Any
import pytest
from ..._extra_utils import get_function_map
from ...errors import UnsupportedFunctionError
from ...types import GenerateContentConfig

_is_mcp_imported = False
if typing.TYPE_CHECKING:
  from mcp import types as mcp_types
  from mcp import ClientSession as McpClientSession
  from ..._adapters import McpToGenAiToolAdapter

  _is_mcp_imported = True
else:
  McpClientSession: typing.Type = Any
  McpToGenAiToolAdapter: typing.Type = Any
  try:
    from mcp import types as mcp_types
    from mcp import ClientSession as McpClientSession
    from ..._adapters import McpToGenAiToolAdapter

    _is_mcp_imported = True
  except ImportError:
    McpClientSession = None
    McpToGenAiToolAdapter = None


def test_coroutine_function():
  async def func_under_test():
    pass

  config = GenerateContentConfig(tools=[func_under_test])

  with pytest.raises(UnsupportedFunctionError):
    get_function_map(config)


def test_empty_config():
  config = {}

  assert get_function_map(config) == {}


def test_empty_tools():
  config = GenerateContentConfig(top_p=0.5)

  assert get_function_map(config) == {}


def test_valid_function():
  def func_under_test():
    pass

  config = GenerateContentConfig(tools=[func_under_test])

  assert get_function_map(config) == {'func_under_test': func_under_test}


def test_mcp_tool_raises_error():
  if not _is_mcp_imported:
    return

  session = McpClientSession(read_stream=None, write_stream=None)
  config = GenerateContentConfig(tools=[session])
  mcp_to_genai_tool_adapters = {'tool': McpToGenAiToolAdapter(session, [])}
  with pytest.raises(UnsupportedFunctionError):
    get_function_map(
        config, mcp_to_genai_tool_adapters, is_caller_method_async=False
    )


@pytest.mark.asyncio
async def test_mcp_tool():
  if not _is_mcp_imported:
    return

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None

    async def list_tools(self):
      return mcp_types.ListToolsResult(
          tools=[
              mcp_types.Tool(
                  name='tool',
                  description='tool-description',
                  inputSchema={
                      'type': 'OBJECT',
                      'properties': {
                          'key1': {
                              'type': 'STRING',
                          },
                          'key2': {
                              'type': 'NUMBER',
                          },
                      },
                  },
              )
          ]
      )

  session = MockMcpClientSession()
  config = GenerateContentConfig(tools=[session])
  mcp_to_genai_tool_adapters = {
      'tool': McpToGenAiToolAdapter(session, [await session.list_tools()]),
  }
  result = get_function_map(
      config, mcp_to_genai_tool_adapters, is_caller_method_async=True
  )
  assert isinstance(result['tool'], McpToGenAiToolAdapter)


@pytest.mark.asyncio
async def test_duplicate_mcp_tool_raises_error():
  if not _is_mcp_imported:
    return

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None

    async def list_tools(self):
      return mcp_types.ListToolsResult(
          tools=[
              mcp_types.Tool(
                  name='tool',
                  description='tool-description',
                  inputSchema={
                      'type': 'OBJECT',
                      'properties': {
                          'key1': {
                              'type': 'STRING',
                          },
                          'key2': {
                              'type': 'NUMBER',
                          },
                      },
                  },
              )
          ]
      )

  def tool():
    pass

  session = MockMcpClientSession()
  config = GenerateContentConfig(tools=[tool, session])
  mcp_to_genai_tool_adapters = {
      'tool': McpToGenAiToolAdapter(session, [await session.list_tools()]),
  }
  with pytest.raises(ValueError):
    get_function_map(
        config, mcp_to_genai_tool_adapters, is_caller_method_async=True
    )
