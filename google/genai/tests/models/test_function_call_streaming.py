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

"""Tests for models.generate_content_stream() with stream_function_call_arguments enabled."""

import pytest
from ... import types
from unittest import mock
from .. import pytest_helper
from . import test_generate_content_tools

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
            }
        },
        'required': ['location', 'unit', 'country'],
    },
}]

generate_content_prompt = [
    types.Content(
        role='user',
        parts=[
            types.Part(
                text=(
                    'get the current weather in boston in celsius, the'
                    ' country should be US, the purpose is to know'
                    ' what to wear today?'
                )
            )
        ],
    ),
]
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
  with pytest.raises(ValueError) as e:
    for chunk in client.models.generate_content_stream(
        model='gemini-3-pro-preview',
        contents=generate_content_prompt,
        config=types.GenerateContentConfig(
            tools=[
                test_generate_content_tools.get_weather,
                test_generate_content_tools.get_stock_price,
            ],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    ):
      pass

  assert 'not compatible with automatic function calling (AFC)' in str(e.value)


def test_streaming_with_python_afc_disabled_false(client):
  """Tests streaming function calls with native python AFC without disabling AFC."""
  if not client.vertexai:
    return
  with pytest.raises(ValueError) as e:
    for chunk in client.models.generate_content_stream(
        model='gemini-3-pro-preview',
        contents=(
            'What is the price of GOOG? And what is the weather in Boston?'
        ),
        config=types.GenerateContentConfig(
            tools=[
                test_generate_content_tools.get_weather,
                test_generate_content_tools.get_stock_price,
            ],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
            ),
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    ):
      pass
  assert 'not compatible with automatic function calling (AFC)' in str(e.value)


def test_streaming_with_json_parameters_without_history(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""

  with pytest_helper.exception_if_mldev(client, ValueError):
    for chunk in client.models.generate_content_stream(
        model='gemini-3-pro-preview',
        contents=generate_content_prompt,
        config=types.GenerateContentConfig(
            tools=[{'function_declarations': json_function_declarations}],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    ):
      assert chunk is not None
      assert chunk.candidates is not None
      assert chunk.candidates[0].content is not None
      assert chunk.candidates[0].content.parts is not None


@pytest.mark.asyncio
async  def test_streaming_with_json_parameters_async(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""
  with pytest_helper.exception_if_mldev(client, ValueError):
    async for chunk in await client.aio.models.generate_content_stream(
        model='gemini-3-pro-preview',
        contents=generate_content_prompt,
        config=types.GenerateContentConfig(
            tools=[{'function_declarations': json_function_declarations}],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    ):
      assert chunk is not None
      assert chunk.candidates is not None
      assert chunk.candidates[0].content is not None
      assert chunk.candidates[0].content.parts is not None


def test_streaming_with_gemini_parameters_without_history(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""
  with pytest_helper.exception_if_mldev(client, ValueError):
    for chunk in client.models.generate_content_stream(
        model='gemini-3-pro-preview',
        contents=generate_content_prompt,
        config=types.GenerateContentConfig(
            tools=[{
                'function_declarations': gemini_function_declarations
            }],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    ):
      assert chunk is not None
      assert chunk.candidates is not None
      assert chunk.candidates[0].content is not None
      assert chunk.candidates[0].content.parts is not None

def test_streaming_with_gemini_parameters_with_response(client):
  """Tests streaming function calls with FunctionDeclaration withJSON parameters."""
  with pytest_helper.exception_if_mldev(client, ValueError):
    streaming_function_call_content = []
    for chunk in client.models.generate_content_stream(
        model='gemini-3-pro-preview',
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part(
                        text=(
                            'get the current weather in boston in celsius, the'
                            ' country should be US, the purpose is to know'
                            ' what to wear today?'
                        )
                    )
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            tools=[{
                'function_declarations': gemini_function_declarations
            }],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    ):
      streaming_function_call_content.append(chunk.candidates[0].content)

    streaming_function_call_content.append(
        types.Content(
            role='user',
            parts=[
                types.Part.from_function_response(
                    name='get_current_weather',
                    response={
                        'temperature': 21,
                        'unit': 'C',
                    },
                )
            ],
        ),
    )

    for chunk in client.models.generate_content_stream(
        model='gemini-3-pro-preview',
        contents=streaming_function_call_content,
        config=types.GenerateContentConfig(
            tools=[{'function_declarations': json_function_declarations}],
            tool_config=types.ToolConfig(
                function_calling_config={
                    'stream_function_call_arguments': True,
                }
            ),
        ),
    ):
      pass

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
        model='gemini-3-pro-preview',
        history=previous_generate_content_history,
        config=types.GenerateContentConfig(
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
        config=types.GenerateContentConfig(
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
