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

"""Tests for copy_generate_content_config (issue #2669)."""

import _asyncio
from types import SimpleNamespace
from unittest import mock

import pytest

from ... import _extra_utils
from ... import _transformers as t
from ... import models as models_module
from ... import types

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


def _mock_async_models():
  api_client = SimpleNamespace(vertexai=False)
  return models_module.AsyncModels(api_client)


class _UnpickleableMcpClientSession(McpClientSession):

  def __init__(self):
    self._read_stream = None
    self._write_stream = None
    self._future = _asyncio.Future()

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
        ]
    )


def test_copy_none_and_empty_dict():
  assert _extra_utils.copy_generate_content_config(None) is None
  assert _extra_utils.copy_generate_content_config({}) is None


def test_copy_preserves_unpickleable_mcp_session():
  """Deep copy must not pickle MCP sessions that hold asyncio.Future."""

  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None
      self._future = _asyncio.Future()

  session = MockMcpClientSession()
  config = types.GenerateContentConfig(
      temperature=0.5,
      tools=[session],
  )

  with pytest.raises(TypeError, match='pickle'):
    config.model_copy(deep=True)

  copied = _extra_utils.copy_generate_content_config(config)
  assert copied is not config
  assert copied.temperature == 0.5
  assert copied.tools is not None
  assert len(copied.tools) == 1
  assert copied.tools[0] is session
  # Caller config is unchanged.
  assert config.tools is not None
  assert config.tools[0] is session


def test_copy_from_dict_keeps_tool_identity():
  class MockMcpClientSession(McpClientSession):

    def __init__(self):
      self._read_stream = None
      self._write_stream = None
      self._future = _asyncio.Future()

  session = MockMcpClientSession()
  config = {
      'temperature': 0.25,
      'tools': [session],
  }
  copied = _extra_utils.copy_generate_content_config(config)
  assert copied is not None
  assert copied.temperature == 0.25
  assert copied.tools is not None
  assert copied.tools[0] is session


def test_copy_deep_copies_other_nested_fields():
  config = types.GenerateContentConfig(
      http_options=types.HttpOptions(headers={'x-test': '1'}),
  )
  copied = _extra_utils.copy_generate_content_config(config)
  assert copied is not None
  assert copied.http_options is not None
  assert copied.http_options is not config.http_options
  assert copied.http_options.headers is not None
  assert config.http_options is not None
  assert config.http_options.headers is not None
  assert copied.http_options.headers is not config.http_options.headers
  copied.http_options.headers['x-test'] = '2'
  assert config.http_options.headers['x-test'] == '1'


@pytest.mark.asyncio
async def test_async_generate_content_accepts_unpickleable_mcp_config_object():
  """Regression for #2669 on AsyncModels.generate_content."""
  async_models = _mock_async_models()

  async def fake_generate_content(self, *, model, contents, config):
    del self, model, contents, config
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role='model',
                    parts=[types.Part(text='sunny')],
                )
            )
        ]
    )

  with mock.patch.object(
      models_module.AsyncModels,
      '_generate_content',
      fake_generate_content,
  ):
    response = await async_models.generate_content(
        model='gemini-2.5-flash',
        contents=t.t_contents('What is the weather in Boston?'),
        config=types.GenerateContentConfig(
            tools=[_UnpickleableMcpClientSession()]
        ),
    )
  assert response.text == 'sunny'


@pytest.mark.asyncio
async def test_async_generate_content_stream_accepts_unpickleable_mcp_config_object():
  """Regression for #2669 on AsyncModels.generate_content_stream."""
  async_models = _mock_async_models()

  async def fake_generate_content_stream(self, *, model, contents, config):
    del self, model, contents, config

    async def _gen():
      yield types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='sunny')],
                  )
              )
          ]
      )

    return _gen()

  with mock.patch.object(
      models_module.AsyncModels,
      '_generate_content_stream',
      fake_generate_content_stream,
  ):
    stream = await async_models.generate_content_stream(
        model='gemini-2.5-flash',
        contents=t.t_contents('What is the weather in Boston?'),
        config=types.GenerateContentConfig(
            tools=[_UnpickleableMcpClientSession()]
        ),
    )
    chunks = [chunk async for chunk in stream]
  assert chunks
  assert chunks[0].text == 'sunny'
