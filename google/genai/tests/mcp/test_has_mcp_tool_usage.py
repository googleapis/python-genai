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

import typing
from typing import Any

from ... import _mcp_utils
from ... import types

if typing.TYPE_CHECKING:
  from mcp.types import Tool as McpTool
  from mcp import ClientSession as McpClientSession
else:
  McpTool: typing.Type = Any
  McpClientSession: typing.Type = Any
  try:
    from mcp.types import Tool as McpTool
    from mcp import ClientSession as McpClientSession
  except ImportError:
    McpTool = None
    McpClientSession = None


def test_mcp_tools():
  """Test whether the list of tools contains any MCP tools."""
  if McpTool is None:
    return
  mcp_tools = [
      McpTool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'OBJECT',
              'properties': {
                  'key1': {'type': 'STRING'},
                  'key2': {'type': 'NUMBER'},
              },
          },
      ),
  ]
  assert _mcp_utils.has_mcp_tool_usage(mcp_tools)


def test_mcp_client_session():
  """Test whether the list of tools contains any MCP tools."""

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None

  mcp_tools = [
      MockMcpClientSession(),
  ]
  assert _mcp_utils.has_mcp_tool_usage(mcp_tools)


def test_no_mcp_tools():
  if McpClientSession is None:
    return
  """Test whether the list of tools contains any MCP tools."""
  gemini_tools = [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      properties={},
                  ),
              ),
          ],
      ),
  ]
  assert not _mcp_utils.has_mcp_tool_usage(gemini_tools)
