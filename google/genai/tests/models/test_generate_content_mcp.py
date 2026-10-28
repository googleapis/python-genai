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

import asyncio
import sys
from typing import Any
from unittest import mock
import pytest
from ... import _transformers as t
from ... import errors
from ... import types
from ...models import AsyncModels
from .. import pytest_helper

try:
  from mcp import types as mcp_types
  from mcp import ClientSession as McpClientSession
except ImportError as e:
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


@pytest.mark.skip(
    reason='pydantic serialization inconsistant issue',
)
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
      model='gemini-3.5-flash',
      contents=t.t_contents('What is the weather in Boston?'),
      config=config,
  )
  assert 'sunny' in response.text.lower()

  response_2 = await client.aio.models.generate_content(
      model='gemini-3.5-flash',
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


class _LiveMcpClientSession(McpClientSession):
  """Holds an asyncio.Future, like a connected session, so deepcopy fails."""

  def __init__(self):
    self._read_stream = None
    self._write_stream = None
    self._pending_response = asyncio.get_running_loop().create_future()

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
            )
        ]
    )


def _live_session_config(session):
  return types.GenerateContentConfig(
      temperature=0,
      tools=[session],
      http_options=types.HttpOptions(headers={'x-custom-header': 'value'}),
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          disable=True
      ),
  )


def _assert_session_converted_and_config_unchanged(
    mock_generate, config, session
):
  """Checks the request got the session's tools and the config is intact."""
  mock_generate.assert_called_once()
  sent_tools = mock_generate.call_args.kwargs['config'].tools
  assert len(sent_tools) == 1
  assert [
      declaration.name for declaration in sent_tools[0].function_declarations
  ] == ['get_weather']
  assert len(config.tools) == 1
  assert config.tools[0] is session
  assert config.http_options.headers == {'x-custom-header': 'value'}


@pytest.mark.asyncio
async def test_mcp_session_in_config_object_async(client):
  """A live session in a GenerateContentConfig is converted, not deep-copied.

  The caller's config keeps its tools and headers.
  """
  session = _LiveMcpClientSession()
  config = _live_session_config(session)

  with mock.patch.object(
      AsyncModels,
      '_generate_content',
      return_value=types.GenerateContentResponse(),
  ) as mock_generate:
    await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents='What is the weather in Boston?',
        config=config,
    )

  _assert_session_converted_and_config_unchanged(mock_generate, config, session)


@pytest.mark.asyncio
async def test_mcp_session_in_config_object_stream_async(client):
  """The streaming variant also converts a live session without deep-copying.

  The caller's config keeps its tools and headers.
  """
  session = _LiveMcpClientSession()
  config = _live_session_config(session)

  async def mock_stream():
    yield types.GenerateContentResponse()

  with mock.patch.object(
      AsyncModels, '_generate_content_stream', side_effect=[mock_stream()]
  ) as mock_generate_stream:
    response = await client.aio.models.generate_content_stream(
        model='gemini-2.5-flash',
        contents='What is the weather in Boston?',
        config=config,
    )
    async for _ in response:
      pass

  _assert_session_converted_and_config_unchanged(
      mock_generate_stream, config, session
  )
