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

"""Tests for chats.send_message_stream() with stream_function_call_arguments enabled."""

import pytest
from ... import types
from unittest import mock
from .. import pytest_helper
from . import test_send_message


json_function_declarations = [{
    'name': 'get_current_weather',
    'description': 'Get the current weather in a city',
    'parameters_json_schema': {
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'The location to get the weather for',
            },
            'country': {
                'anyOf': [
                    {
                        'type': 'string',
                        'description': 'The country to get the weather for',
                    },
                    {
                        'type': 'null',
                    },
                ],
                'description': 'The country to get the weather for',
            },
            'unit': {
                'type': 'string',
                'enum': ['C', 'F'],
            },
            'purpose': {
                'type': 'string',
                'description': 'Discribes the purpose of asking the weather',
            }
        },
        'required': ['location', 'unit', 'country'],
    },
}]

gemini_function_declarations = [{
    'name': 'get_current_weather',
    'description': 'Get the current weather in a city',
    'parameters': {
        'type': 'OBJECT',
        'properties': {
            'location': {
                'type': 'STRING',
                'description': 'The location to get the weather for',
            },
            'country': {
                'type': 'STRING',
                'description': 'The country to get the weather for',
                'nullable': True,
            },
            'unit': {
                'type': 'STRING',
                'enum': ['C', 'F'],
                'description': 'The unit to return the weather in',
            },
            'purpose': {
                'type': 'STRING',
                'description': 'Discribes the purpose of asking the weather',
            },
        },
        'required': ['location', 'unit', 'country'],
    },
}]

generate_content_prompt = (
    'get the current weather in boston in celsius, the country should be US,'
    ' the purpose is to know what to wear today?'
)
previous_generate_content_history = [
    types.Content(
        role='user',
        parts=[
            types.Part(
                text=(
                    ' get the current weather in boston in celsius, the country'
                    ' is U.S., the purpose is to'
                    ' know what to wear today.'
                )
            )
        ],
    ),
    types.Content(
        role='model',
        parts=[
            types.Part(
                function_call=types.FunctionCall(
                    name='get_current_weather',
                    will_continue=True,
                )
            )
        ],
    ),
    types.Content(
        role='model',
        parts=[
            types.Part(
                function_call=types.FunctionCall(
                    name='get_current_weather',
                    partial_args=[
                        types.PartialArg(
                            json_path='$.country',
                            null_value="NULL_VALUE",
                        )
                    ],
                    will_continue=False,
                )
            )
        ],
    )
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content_stream',
)


def test_streaming_with_python_native_no_afc_config(client):
  """Tests streaming function calls with native python AFC without disabling AFC."""
  if not client.vertexai:
    return
  chat = client.chats.create(
      model='gemini-3-pro-preview',
      config=types.ChatConfig(
          tools=[
              test_send_message.get_weather,
              test_send_message.get_stock_price,
          ],
      ),
  )
  for _ in chat.send_message_stream(
      generate_content_prompt,
  ):
    pass
  history = chat.get_history()
  assert len(history) == 2
  assert history[0].role == 'user'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'



def test_streaming_with_python_afc_enabled(client):
  """Tests streaming function calls with native python AFC without disabling AFC."""
  if not client.vertexai:
    return
  with pytest.raises(ValueError) as e:
    chat = client.chats.create(
        model='gemini-3-pro-preview',
        config=types.ChatConfig(
            tools=[
                test_send_message.get_weather,
                test_send_message.get_stock_price,
            ],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
            automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                enable=True,
            ),
        ),
    )
    for _ in chat.send_message_stream(
        'What is the price of GOOG? And what is the weather in Boston?'
    ):
      pass
  assert 'not compatible with automatic function calling (AFC)' in str(e.value)


def test_streaming_with_json_parameters_without_history(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""

  with pytest_helper.exception_if_mldev(client, ValueError):
    chat = client.chats.create(
        model='gemini-3.1-pro-preview',
        config=types.ChatConfig(
            tools=[{'function_declarations': json_function_declarations}],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    )
    for chunk in chat.send_message_stream(
        generate_content_prompt,
    ):
      assert chunk is not None
      assert chunk.candidates is not None
      assert chunk.candidates[0].content is not None
      assert chunk.candidates[0].content.parts is not None


@pytest.mark.asyncio
async  def test_streaming_with_json_parameters_async(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""
  with pytest_helper.exception_if_mldev(client, ValueError):
    chat = client.aio.chats.create(
        model='gemini-3.1-pro-preview',
        config=types.ChatConfig(
            tools=[{'function_declarations': json_function_declarations}],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    )
    async for chunk in await chat.send_message_stream(
        generate_content_prompt,
    ):
      assert chunk is not None
      assert chunk.candidates is not None
      assert chunk.candidates[0].content is not None
      assert chunk.candidates[0].content.parts is not None


def test_streaming_with_gemini_parameters_without_history(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""
  with pytest_helper.exception_if_mldev(client, ValueError):
    chat = client.chats.create(
        model='gemini-3.1-pro-preview',
        config=types.ChatConfig(
            tools=[{
                'function_declarations': gemini_function_declarations
            }],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    )
    for chunk in chat.send_message_stream(
        generate_content_prompt,
    ):
      assert chunk is not None
      assert chunk.candidates is not None
      assert chunk.candidates[0].content is not None
      assert chunk.candidates[0].content.parts is not None


def test_chat_streaming_with_json_parameters_with_history(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""
  with pytest_helper.exception_if_mldev(client, ValueError):
    test_parts = [
        types.Part(
            text=(
                'get the current weather in boston in celsius, the'
                ' country should be US, the purpose is to know'
                ' what to wear today?'
            )
        ),
        types.Part.from_function_response(
            name='get_current_weather',
            response={
                'temperature': 21,
                'unit': 'C',
            },
        ),
        types.Part(
            text=(
                'get the current weather in new brunswick in celsius, the'
                ' country should be US, the purpose is to know'
                ' what to prepare an event today?'
            )
        ),
        types.Part.from_function_response(
            name='get_current_weather',
            response={
                'temperature': 21,
                'unit': 'C',
            },
        ),
    ]
    chat = client.chats.create(
        model='gemini-3.1-pro-preview',
        history=previous_generate_content_history,
        config=types.ChatConfig(
            tools=[{
                'function_declarations': gemini_function_declarations
            }],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    )
    for message in test_parts:
      result = chat.send_message_stream(message)
      for chunk in result:
        assert chunk is not None
        assert chunk.candidates is not None
        assert chunk.candidates[0].content is not None
        assert chunk.candidates[0].content.parts is not None

    assert chat.get_history() is not None


@pytest.mark.asyncio
async def test_chat_streaming_with_json_parameters_with_history_async(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""
  test_parts = [
      types.Part(
          text=(
              'get the current weather in boston in celsius, the'
              ' country should be US, the purpose is to know'
              ' what to wear today?'
          )
      ),
      types.Part.from_function_response(
          name='get_current_weather',
          response={
              'temperature': 21,
              'unit': 'C',
          },
      ),
      types.Part(
          text=(
              'get the current weather in new brunswick in celsius, the'
              ' country should be US, the purpose is to know'
              ' what to prepare an event today?'
          )
      ),
      types.Part.from_function_response(
          name='get_current_weather',
          response={
              'temperature': 21,
              'unit': 'C',
          },
      ),
  ]
  with pytest_helper.exception_if_mldev(client, ValueError):
    chat = client.aio.chats.create(
        model='gemini-3-pro-preview',
        history=previous_generate_content_history,
        config=types.ChatConfig(
            tools=[{'function_declarations': gemini_function_declarations}],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    )
    for message in test_parts:
      async for chunk in await chat.send_message_stream(message):
        assert chunk is not None
        assert chunk.candidates is not None
        assert chunk.candidates[0].content is not None
        assert chunk.candidates[0].content.parts is not None