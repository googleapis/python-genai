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

from ... import _mcp_utils
from ... import types

try:
  from mcp import types as mcp_types
except ImportError as e:
  import sys

  if sys.version_info < (3, 10):
    raise ImportError(
        'MCP Tool requires Python 3.10 or above. Please upgrade your Python'
        ' version.'
    ) from e
  else:
    raise e


def test_empty_mcp_tools_list():
  """Test conversion of empty MCP tools list to Gemini tools list."""
  result = _mcp_utils.mcp_to_gemini_tools([])

  assert result == []


def test_unknown_field_conversion():
  """Test conversion of MCP tools with unknown fields to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'object',
              'properties': {},
              'unknown_field': 'unknownField',
              'unknown_object': {},
          },
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
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


def test_items_conversion():
  """Test conversion of MCP tools with items to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'array',
              'items': {
                  'type': 'object',
                  'properties': {
                      'key1': {
                          'type': 'string',
                      },
                      'key2': {
                          'type': 'number',
                      },
                  },
              },
          },
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='ARRAY',
                      items=types.Schema(
                          type='OBJECT',
                          properties={
                              'key1': types.Schema(type='STRING'),
                              'key2': types.Schema(type='NUMBER'),
                          },
                      ),
                  ),
              ),
          ],
      ),
  ]


def test_any_of_conversion():
  """Test conversion of MCP tools with any_of to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'object',
              'any_of': [
                  {
                      'type': 'string',
                  },
                  {
                      'type': 'number',
                  },
              ],
          },
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      any_of=[
                          types.Schema(type='STRING'),
                          types.Schema(type='NUMBER'),
                      ],
                  ),
              ),
          ],
      ),
  ]


def test_properties_conversion():
  """Test conversion of MCP tools with properties to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'object',
              'properties': {
                  'key1': {
                      'type': 'string',
                  },
                  'key2': {
                      'type': 'number',
                  },
              },
          },
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      properties={
                          'key1': types.Schema(type='STRING'),
                          'key2': types.Schema(type='NUMBER'),
                      },
                  ),
              ),
          ],
      ),
  ]
