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

from typing import Any
import pytest
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper

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

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
)


# Cannot be included in test_table because MCP integration is only supported
# in the Python SDK.
@pytest.mark.asyncio
async def test_mcp_tools_async(client):
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents=t.t_contents('What is the weather in Boston?'),
      config={
          'tools': [
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              )
          ],
      },
  )
  assert response.function_calls == [
      types.FunctionCall(
          name='get_weather',
          args={'location': 'Boston'},
      )
  ]


@pytest.mark.asyncio
async def test_mcp_tools_with_custom_headers_async(client):
  config = {
      'http_options': {
          'headers': {
              'x-goog-api-client': 'google-genai-sdk/1.0.0 gl-python/1.0.0',
          },
      },
      'tools': [
          mcp_types.Tool(
              name='get_weather',
              description='Get the weather in a city.',
              inputSchema={
                  'type': 'object',
                  'properties': {'location': {'type': 'string'}},
              },
          )
      ],
  }
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents=t.t_contents('What is the weather in Boston?'),
      config=config,
  )
  assert response.function_calls == [
      types.FunctionCall(
          name='get_weather',
          args={'location': 'Boston'},
      )
  ]
  # Assert config is not modified.
  assert config['http_options']['headers'] == {
      'x-goog-api-client': 'google-genai-sdk/1.0.0 gl-python/1.0.0'
  }


@pytest.mark.asyncio
async def test_mcp_tools_subsequent_calls_async(client):
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
                  name='add_numbers',
                  description='Add two numbers together.',
                  inputSchema={
                      'type': 'object',
                      'properties': {
                          'a': {'type': 'number'},
                          'b': {'type': 'number'},
                      },
                  },
              ),
          ]
      )

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ):
      if name == 'get_weather':
        return mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type='text', text='Sunny')]
        )
      else:
        return mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type='text', text='100')]
        )

  config = {
      'tools': [MockMcpClientSession()],
  }

  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents=t.t_contents('What is the weather in Boston?'),
      config=config,
  )
  assert 'sunny' in response.text.lower()

  response_2 = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents=t.t_contents('What is 50 + 50?'),
      config=config,
  )
  assert '100' in response_2.text


@pytest.mark.asyncio
async def test_mcp_tools_duplicate_tool_name_raises_error(client):
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
                  name='get_weather',
                  description='Different tool to get the weather.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              ),
          ]
      )

  with pytest.raises(ValueError):
    await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents=t.t_contents('What is the weather in Boston?'),
        config={
            'tools': [MockMcpClientSession()],
        },
    )


def test_mcp_tools_synchronous_call(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=t.t_contents('What is the weather in Boston?'),
      config={
          'tools': [
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              )
          ]
      },
  )
  assert response.function_calls == [
      types.FunctionCall(
          name='get_weather',
          args={'location': 'Boston'},
      )
  ]


def test_mcp_session_synchronous_call_raises_error(client):
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
                  name='get_weather',
                  description='Different tool to get the weather.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              ),
          ]
      )

  with pytest.raises(errors.UnsupportedFunctionError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=t.t_contents('What is the weather in Boston?'),
        config={
            'tools': [MockMcpClientSession()],
        },
    )


def test_mcp_tools_synchronous_stream_call(client):
  response = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents=t.t_contents('What is the weather in Boston?'),
      config={
          'tools': [
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              )
          ]
      },
  )
  for chunk in response:
    assert chunk.function_calls == [
        types.FunctionCall(
            name='get_weather',
            args={'location': 'Boston'},
        )
    ]


def test_mcp_session_synchronous_stream_call_raises_error(client):
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
                  name='get_weather',
                  description='Different tool to get the weather.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              ),
          ]
      )

  response = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents=t.t_contents('What is the weather in Boston?'),
      config={
          'tools': [MockMcpClientSession()],
      },
  )

  with pytest.raises(errors.UnsupportedFunctionError):
    for chunk in response:
      pass
