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

import json
import os
import pydantic

import sys

from pydantic import BaseModel
from pydantic import ValidationError
import pytest
import typing
from typing import Any, Union

from .. import pytest_helper
from ... import errors
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


pytestmark = [
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
    ),
]
pytest_plugins = ('pytest_asyncio',)


MODEL_NAME = 'gemini-2.5-flash'


def get_weather(city: str) -> str:
  return f'The weather in {city} is sunny and 100 degrees.'


def get_stock_price(symbol: str) -> str:
  if symbol == 'GOOG':
    return '1000'
  else:
    return '100'


def square_integer(given_integer: int) -> int:
  return given_integer*given_integer


def divide_floats(numerator: float, denominator: float) -> float:
  """Divide two floats."""
  return numerator / denominator


def divide_integers(numerator: int, denominator: int) -> int:
  """Divide two integers."""
  return numerator // denominator


def power_disco_ball(power: bool) -> bool:
    """Powers the spinning disco ball."""
    print(f"Disco ball is {'spinning!' if power else 'stopped.'}")
    return True


def start_music(energetic: bool, loud: bool, bpm: int) -> str:
    """Play some music matching the specified parameters.

    Args:
      energetic: Whether the music is energetic or not.
      loud: Whether the music is loud or not.
      bpm: The beats per minute of the music.

    Returns: The name of the song being played.
    """
    print(f"Starting music! {energetic=} {loud=}, {bpm=}")
    return "Never gonna give you up."


def dim_lights(brightness: float) -> bool:
    """Dim the lights.

    Args:
      brightness: The brightness of the lights, 0.0 is off, 1.0 is full.
    """
    print(f"Lights are now set to {brightness:.0%}")
    return True


def test_text(client):
  chat = client.chats.create(model=MODEL_NAME)
  chat.send_message(
      'tell me a story in 100 words',
  )


def test_part(client):
  chat = client.chats.create(model=MODEL_NAME)
  chat.send_message(
      types.Part.from_text(text='tell me a story in 100 words'),
  )


def test_parts(client):
  chat = client.chats.create(model=MODEL_NAME)
  chat.send_message(
      [
          types.Part.from_text(text='tell me a US city'),
          types.Part.from_text(text='the city is in west coast'),
      ],
  )


def test_image(client, image_jpeg):
  chat = client.chats.create(model=MODEL_NAME)
  chat.send_message(
      [
          'what is the image about?',
          image_jpeg,
      ],
  )


def test_thinking_budget(client):
  """Tests that the thinking budget is respected and generates thoughts."""
  chat = client.chats.create(
      model=MODEL_NAME,
      config=types.ChatConfig(
          thinking_config=types.ThinkingConfig(
              include_thoughts=True,
              thinking_budget=10000,
          ),
      ),
  )
  response1 = chat.send_message(
      'what is the sum of natural numbers from 1 to 100?',
  )
  has_thought1 = False
  if response1.candidates:
    for candidate in response1.candidates:
      for part in candidate.content.parts:
        if part.thought:
          has_thought1 = True
          break
  assert has_thought1

  response2 = chat.send_message(
      'can you help me to understand the logic better?'
  )
  has_thought2 = False
  if response2.candidates:
    for candidate in response2.candidates:
      for part in candidate.content.parts:
        if part.thought:
          has_thought2 = True
          break
  assert has_thought2


def test_thinking_budget_stream(client):
  """Tests that the thinking budget is respected and generates thoughts."""
  chat = client.chats.create(
      model=MODEL_NAME,
      config=types.ChatConfig(
          thinking_config=types.ThinkingConfig(
              include_thoughts=True,
              thinking_budget=10000,
          ),
      ),
  )
  has_thought1 = False
  for chunk in chat.send_message_stream(
      'what is the sum of natural numbers from 1 to 100?',
  ):
    if chunk.candidates:
      for candidate in chunk.candidates:
        for part in candidate.content.parts:
          if part.thought:
            has_thought1 = True
            break
  assert has_thought1

  has_thought2 = False
  for chunk in chat.send_message_stream(
      'can you help me to understand the logic better?'
  ):
    if chunk.candidates:
      for candidate in chunk.candidates:
        for part in candidate.content.parts:
          if part.thought:
            has_thought2 = True
            break
  assert has_thought2


def test_google_cloud_storage_uri(client):
  chat = client.chats.create(model=MODEL_NAME)
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    chat.send_message(
        [
            'what is the image about?',
            types.Part.from_uri(
                file_uri=(
                    'gs://unified-genai-dev/imagen-inputs/google_small.png'
                ),
                mime_type='image/png',
            ),
        ],
    )


def test_uploaded_file_uri(client):
  chat = client.chats.create(model=MODEL_NAME)
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    chat.send_message(
        [
            'what is the image about?',
            types.Part.from_uri(
                file_uri='https://generativelanguage.googleapis.com/v1beta/files/az606f58k7zj',
                mime_type='image/png',
            ),
        ],
    )


def test_config_override(client):
  chat_config = types.ChatConfig(candidate_count=1)
  chat = client.chats.create(model=MODEL_NAME, config=chat_config)
  request_config = types.ChatConfig(candidate_count=2)
  request_config_response = chat.send_message(
      'tell me a story in 100 words',
      config=request_config)
  default_config_response = chat.send_message(
      'tell me a story in 100 words')

  assert len(request_config_response.candidates) == 2
  assert len(default_config_response.candidates) == 1


def test_history(client):
  history = [
      types.Content(
          role='user', parts=[types.Part.from_text(text='define a=5, b=10')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='Hello there! how can I help you?')],
      ),
  ]
  chat = client.chats.create(model=MODEL_NAME, history=history)
  chat.send_message('what is a + b?')

  assert len(chat.get_history()) > 2


def test_send_2_messages(client):
  chat = client.chats.create(model=MODEL_NAME)
  chat.send_message('write a python function to check if a year is a leap year')
  chat.send_message('write a unit test for the function')


def test_with_afc_multiple_remote_calls(client):

  house_fns = [power_disco_ball, start_music, dim_lights]
  config = types.ChatConfig(
      tools=house_fns,
      tool_config=types.ToolConfig(
          function_calling_config=types.FunctionCallingConfig(
              mode=types.FunctionCallingConfigMode.ANY,
          ),
      ),
      automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
          enable=True,
          maximum_remote_calls=3,
      ),
  )
  chat = client.chats.create(model='gemini-3.1-pro-preview', config=config)
  chat.send_message('Turn this place into a party!')
  curated_history = chat.get_history()

  assert len(curated_history) == 8
  assert curated_history[0].role == 'user'
  assert curated_history[0].parts[0].text == 'Turn this place into a party!'
  assert curated_history[1].role == 'model'
  assert len(curated_history[1].parts) == 3
  for part in curated_history[1].parts:
    assert part.function_call
  assert curated_history[2].role == 'user'
  assert len(curated_history[2].parts) == 3
  for part in curated_history[2].parts:
    assert part.function_response
  assert curated_history[3].role == 'model'
  assert len(curated_history[3].parts) == 3
  for part in curated_history[3].parts:
    assert part.function_call
  assert curated_history[4].role == 'user'
  assert len(curated_history[4].parts) == 3
  for part in curated_history[4].parts:
    assert part.function_response
  assert curated_history[5].role == 'model'
  assert len(curated_history[5].parts) == 3
  for part in curated_history[5].parts:
    assert part.function_call
  assert curated_history[6].role == 'user'
  assert len(curated_history[6].parts) == 3
  for part in curated_history[6].parts:
    assert part.function_response
  assert curated_history[7].role == 'model'
  assert len(curated_history[7].parts) == 3
  for part in curated_history[7].parts:
    assert part.function_call


@pytest.mark.asyncio
async def test_with_afc_multiple_remote_calls_async(client):

  house_fns = [power_disco_ball, start_music, dim_lights]
  config = types.ChatConfig(
      tools=house_fns,
      tool_config=types.ToolConfig(
          function_calling_config=types.FunctionCallingConfig(
              mode=types.FunctionCallingConfigMode.ANY,
          ),
      ),
      automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
          enable=True,
          maximum_remote_calls=3,
      ),
  )
  chat = client.aio.chats.create(model='gemini-3.1-pro-preview', config=config)
  await chat.send_message('Turn this place into a party!')
  curated_history = chat.get_history()

  assert len(curated_history) == 8
  assert curated_history[0].role == 'user'
  assert curated_history[0].parts[0].text == 'Turn this place into a party!'
  assert curated_history[1].role == 'model'
  assert len(curated_history[1].parts) == 3
  for part in curated_history[1].parts:
    assert part.function_call
  assert curated_history[2].role == 'user'
  assert len(curated_history[2].parts) == 3
  for part in curated_history[2].parts:
    assert part.function_response
  assert curated_history[3].role == 'model'
  assert len(curated_history[3].parts) == 3
  for part in curated_history[3].parts:
    assert part.function_call
  assert curated_history[4].role == 'user'
  assert len(curated_history[4].parts) == 3
  for part in curated_history[4].parts:
    assert part.function_response
  assert curated_history[5].role == 'model'
  assert len(curated_history[5].parts) == 3
  for part in curated_history[5].parts:
    assert part.function_call
  assert curated_history[6].role == 'user'
  assert len(curated_history[6].parts) == 3
  for part in curated_history[6].parts:
    assert part.function_response
  assert curated_history[7].role == 'model'
  assert len(curated_history[7].parts) == 3
  for part in curated_history[7].parts:
    assert part.function_call


def test_with_afc_disabled(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[square_integer],
      ),
  )
  chat.send_message(
      'Do the square of 3.',
  )
  chat_history = chat.get_history()

  assert len(chat_history) == 2
  assert chat_history[0].role == 'user'
  assert chat_history[0].parts[0].text == 'Do the square of 3.'

  assert chat_history[1].role == 'model'
  assert chat_history[1].parts[0].function_call.name == 'square_integer'
  assert chat_history[1].parts[0].function_call.args == {
      'given_integer': 3,
  }


@pytest.mark.asyncio
async def test_with_afc_disabled_async(client):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[square_integer],
      ),
  )
  await chat.send_message(
      'Do the square of 3.',
  )
  chat_history = chat.get_history()

  assert len(chat_history) == 2
  assert chat_history[0].role == 'user'
  assert chat_history[0].parts[0].text == 'Do the square of 3.'

  assert chat_history[1].role == 'model'
  assert chat_history[1].parts[0].function_call.name == 'square_integer'
  assert chat_history[1].parts[0].function_call.args == {
      'given_integer': 3,
  }


def test_stream_text(client):
  chat = client.chats.create(model=MODEL_NAME)
  chunks = 0
  for chunk in chat.send_message_stream(
      'tell me a story in 100 words',
  ):
    chunks += 1

  assert chunks > 1


def test_stream_part(client):
  chat = client.chats.create(model=MODEL_NAME)
  chunks = 0
  for chunk in chat.send_message_stream(
      types.Part.from_text(text='tell me a story in 100 words'),
  ):
    chunks += 1

  assert chunks > 1


def test_stream_parts(client):
  chat = client.chats.create(model=MODEL_NAME)
  chunks = 0
  for chunk in chat.send_message_stream(
      [
          types.Part.from_text(text='tell me a story in 100 words'),
          types.Part.from_text(text='the story is about a car'),
      ],
  ):
    chunks += 1

  assert chunks > 2


def test_stream_config_override(client):
  chat_config = types.ChatConfig(response_mime_type='text/plain')
  chat = client.chats.create(model=MODEL_NAME, config=chat_config)
  request_config = types.ChatConfig(response_mime_type='application/json')
  request_config_text = ''
  for chunk in chat.send_message_stream(
      'tell me a story in 100 words', config=request_config
  ):
    request_config_text += chunk.text
  default_config_text = ''
  for chunk in chat.send_message_stream('tell me a story in 100 words'):
    default_config_text += chunk.text

  assert json.loads(request_config_text)
  with pytest.raises(json.JSONDecodeError):
    json.loads(default_config_text)


def test_stream_function_calling(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[square_integer],
      ),
  )
  for chunk in chat.send_message_stream(
      'do the square of 3',
  ):
    pass
  for chunk in chat.send_message_stream(
      'do the square of 4',
  ):
    pass
  chat_history = chat.get_history()

  assert len(chat_history) == 6
  assert chat_history[0].role == 'user'
  assert chat_history[0].parts[0].text == 'do the square of 3'
  assert chat_history[1].role == 'model'
  assert chat_history[1].parts[0].function_call.name == 'square_integer'
  assert chat_history[1].parts[0].function_call.args == {
      'given_integer': 3,
  }
  assert chat_history[2].role == 'model'
  assert chat_history[2].parts[0].text == ''
  assert chat_history[3].role == 'user'
  assert chat_history[3].parts[0].text == 'do the square of 4'
  assert chat_history[4].role == 'model'
  assert chat_history[4].parts[0].function_call.name == 'square_integer'
  assert chat_history[4].parts[0].function_call.args == {
      'given_integer': 4,
  }
  assert chat_history[5].role == 'model'
  assert chat_history[5].parts[0].text == ''


def test_stream_send_2_messages(client):
  chat = client.chats.create(model=MODEL_NAME)
  for chunk in chat.send_message_stream(
      'write a python function to check if a year is a leap year'
  ):
    pass

  for chunk in chat.send_message_stream('write a unit test for the function'):
    pass


@pytest.mark.asyncio
async def test_async_text(client):
  chat = client.aio.chats.create(model=MODEL_NAME)
  await chat.send_message('tell me a story in 100 words')


@pytest.mark.asyncio
async def test_async_part(client):
  chat = client.aio.chats.create(model=MODEL_NAME)
  await chat.send_message(types.Part.from_text(text='tell me a story in 100 words'))


@pytest.mark.asyncio
async def test_async_parts(client):
  chat = client.aio.chats.create(model=MODEL_NAME)
  await chat.send_message(
      [
          types.Part.from_text(text='tell me a US city'),
          types.Part.from_text(text='the city is in west coast'),
      ],
  )


@pytest.mark.asyncio
async def test_async_config_override(client):
  chat_config = types.ChatConfig(candidate_count=1)
  chat = client.aio.chats.create(model=MODEL_NAME, config=chat_config)
  request_config = types.ChatConfig(candidate_count=2)
  request_config_response = await chat.send_message(
      'tell me a story in 100 words',
      config=request_config)
  default_config_response = await chat.send_message(
      'tell me a story in 100 words')

  assert len(request_config_response.candidates) == 2
  assert len(default_config_response.candidates) == 1


@pytest.mark.asyncio
async def test_async_history(client):
  history = [
       types.Content(
          role='user', parts=[types.Part.from_text(text='define a=5, b=10')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='Hello there! how can I help you?')],
      ),
  ]
  chat = client.aio.chats.create(model=MODEL_NAME, history=history)
  await chat.send_message('what is a + b?')

  assert len(chat.get_history()) > 2


@pytest.mark.asyncio
async def test_async_stream_text(client):
  chat = client.aio.chats.create(model=MODEL_NAME)
  chunks = 0
  async for chunk in await chat.send_message_stream('tell me a story in 100 words'):
    chunks += 1

  assert chunks > 1


@pytest.mark.asyncio
async def test_async_stream_part(client):
  chat = client.aio.chats.create(model=MODEL_NAME)
  chunks = 0
  async for chunk in await chat.send_message_stream(
      types.Part.from_text(text='tell me a story in 100 words')
  ):
    chunks += 1

  assert chunks > 1


@pytest.mark.asyncio
async def test_async_stream_parts(client):
  chat = client.aio.chats.create(model=MODEL_NAME)
  chunks = 0
  async for chunk in await chat.send_message_stream(
      [
          types.Part.from_text(text='tell me a story in 100 words'),
          types.Part.from_text(text='the story is about a car'),
      ],
  ):
    chunks += 1

  assert chunks > 1


@pytest.mark.asyncio
async def test_async_stream_config_override(client):
  chat_config = types.ChatConfig(response_mime_type='text/plain')
  chat = client.aio.chats.create(model=MODEL_NAME, config=chat_config)
  request_config = types.ChatConfig(response_mime_type='application/json')
  request_config_text = ''
  async for chunk in await chat.send_message_stream(
      'tell me a story in 100 words', config=request_config
  ):
    request_config_text += chunk.text
  default_config_text = ''

  async for chunk in await chat.send_message_stream('tell me family friendly story in 100 words'):
    default_config_text += chunk.text

  assert json.loads(request_config_text)
  with pytest_helper.exception_if_mldev(client, json.JSONDecodeError):
    json.loads(default_config_text)


@pytest.mark.asyncio
async def test_async_stream_send_2_messages(client):
  chat = client.aio.chats.create(model=MODEL_NAME)
  async for chunk in await chat.send_message_stream(
      'write a python function to check if a year is a leap year'
  ):
    pass
  async for chunk in await chat.send_message_stream(
      'write a unit test for the function'
  ):
    pass


def test_mcp_tools(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config = types.ChatConfig(
          tools=[
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              )
          ],
      ),
  )
  response = chat.send_message('What is the weather in Boston?')
  response = chat.send_message('What is the weather in San Francisco?')


def test_mcp_tools_stream(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config = types.ChatConfig(
          tools=[
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              )
          ],
      ),
  )
  for chunk in chat.send_message_stream(
    'What is the weather in Boston?'
  ):
    pass
  for chunk in chat.send_message_stream(
    'What is the weather in San Francisco?'
  ):
    pass


@pytest.mark.asyncio
async def test_async_mcp_tools(client):
  chat = client.aio.chats.create(
        model='gemini-3.1-pro-preview',
        config=types.ChatConfig(
          tools=[
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              )
          ],
      ),
    )
  await chat.send_message('What is the weather in Boston?');
  await chat.send_message('What is the weather in San Francisco?');


@pytest.mark.asyncio
async def test_async_mcp_tools_stream(client):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              mcp_types.Tool(
                  name='get_weather',
                  description='Get the weather in a city.',
                  inputSchema={
                      'type': 'object',
                      'properties': {'location': {'type': 'string'}},
                  },
              )
          ],
      ),
  )

  async for chunk in await chat.send_message_stream(
    'What is the weather in Boston?'
  ):
    pass
  async for chunk in await chat.send_message_stream(
    'What is the weather in San Francisco?'
  ):
    pass


def test_server_side_mcp_tools(client):
   with pytest_helper.exception_if_vertex(client, ValueError):
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.ChatConfig(
            tools=[
                {
                    'mcp_servers': [
                        {
                            'name': 'weather_server',
                            'streamable_http_transport': {
                                'url': (
                                    'https://gemini-api-demos.uc.r.appspot.com/mcp'
                                ),
                                'headers': {
                                    'AUTHORIZATION': 'Bearer github_pat_XXXX',
                                },
                                'timeout': '10s',
                            },
                        },
                    ],
                },
            ],
        ),
    )
    response = chat.send_message('What is the weather in Boston on 02/02/2026?')
    response = chat.send_message(
        'What is the weather in San Francisco on 02/02/2026?'
    )


def test_server_side_mcp_tools_stream(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.ChatConfig(
            tools=[
                {
                    'mcp_servers': [
                        {
                            'name': 'weather_server',
                            'streamable_http_transport': {
                                'url': (
                                    'https://gemini-api-demos.uc.r.appspot.com/mcp'
                                ),
                                'headers': {
                                    'AUTHORIZATION': 'Bearer github_pat_XXXX',
                                },
                                'timeout': '10s',
                            },
                        },
                    ],
                },
            ],
        ),
    )
    for chunk in chat.send_message_stream(
        'What is the weather in Boston on 02/02/2026?'
    ):
      pass
    for chunk in chat.send_message_stream(
        'What is the weather in San Francisco on 02/02/2026?'
    ):
      pass


@pytest.mark.asyncio
async def test_async_server_side_mcp_tools(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    chat = client.aio.chats.create(
        model='gemini-2.5-flash',
        config=types.ChatConfig(
            tools=[
                {
                    'mcp_servers': [
                        {
                            'name': 'weather_server',
                            'streamable_http_transport': {
                                'url': (
                                    'https://gemini-api-demos.uc.r.appspot.com/mcp'
                                ),
                                'headers': {
                                    'AUTHORIZATION': 'Bearer github_pat_XXXX',
                                },
                                'timeout': '10s',
                            },
                        },
                    ],
                },
            ],
        ),
    )
    await chat.send_message('What is the weather in Boston on 02/02/2026?')
    await chat.send_message(
        'What is the weather in San Francisco on 02/02/2026?'
    )


def test_function_tool_afc(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  chat.send_message('What is the weather in Boston?')
  history = chat.get_history()
  assert len(history) == 4
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}
  assert history[2].role == 'user'
  assert history[2].parts[0].function_response.name == 'get_weather'
  assert history[3].role == 'model'
  assert 'sunny' in history[3].parts[0].text.lower()


def test_function_tool_multi_turn_afc(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
              get_stock_price,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  chat.send_message('What is the weather in Boston?')
  history = chat.get_history()
  assert len(history) == 4
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}
  assert history[2].role == 'user'
  assert history[2].parts[0].function_response.name == 'get_weather'
  assert history[3].role == 'model'
  assert 'sunny' in history[3].parts[0].text.lower()

  chat.send_message('What is the stock price of symbol GOOG?')
  history = chat.get_history()
  assert len(history) == 8
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}
  assert history[2].role == 'user'
  assert history[2].parts[0].function_response.name == 'get_weather'
  assert history[3].role == 'model'
  assert 'sunny' in history[3].parts[0].text.lower()
  assert history[4].role == 'user'
  assert history[4].parts[0].text == 'What is the stock price of symbol GOOG?'
  assert history[5].role == 'model'
  assert history[5].parts[0].function_call.name == 'get_stock_price'
  assert history[5].parts[0].function_call.args == {'symbol': 'GOOG'}
  assert history[6].role == 'user'
  assert history[6].parts[0].function_response.name == 'get_stock_price'
  assert history[7].role == 'model'
  assert '1000' in history[7].parts[0].text


def test_multi_turn_afc_enabled_FC_FR_parts(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
              get_stock_price,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
      history=[
          types.Content(
              role='user',
              parts=[types.Part(text='What is the weather in Boston?')],
          ),
          types.Content(
              role='model',
              parts=[
                  types.Part(
                      function_call=types.FunctionCall(
                          name='get_weather',
                          args={'city': 'Boston'},
                      ),
                  ),
                  types.Part(
                      function_response=types.FunctionResponse(
                          name='get_weather',
                          response={'weather': 'sunny and 80 degrees'},
                      ),
                  ),
                  types.Part(text='The weather is sunny.'),
              ],
          ),
      ]
  )
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    chat.send_message('What is the stock price of symbol GOOG?')


@pytest.mark.asyncio
async def test_async_function_tool_afc_disabled(client):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
          ],
      ),
  )
  await chat.send_message('What is the weather in Boston?')
  history = chat.get_history()
  assert len(history) == 2
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert len(history[1].parts) == 1
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}


@pytest.mark.asyncio
async def test_async_function_tool_afc_enabled(client):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  await chat.send_message('What is the weather in Boston?')
  history = chat.get_history()
  assert len(history) == 4
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}
  assert history[2].role == 'user'
  assert history[2].parts[0].function_response.name == 'get_weather'
  assert history[3].role == 'model'
  assert 'sunny' in history[3].parts[0].text.lower()


@pytest.mark.asyncio
async def test_async_function_tool_afc_enabled_multi_turn(client):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
              get_stock_price,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  await chat.send_message('What is the weather in Boston?')
  history = chat.get_history()
  assert len(history) == 4
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}
  assert history[2].role == 'user'
  assert history[2].parts[0].function_response.name == 'get_weather'
  assert history[3].role == 'model'
  assert 'sunny' in history[3].parts[0].text.lower()

  await chat.send_message('What is the stock price of symbol GOOG?')
  history = chat.get_history()
  assert len(history) == 8
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}
  assert history[2].role == 'user'
  assert history[2].parts[0].function_response.name == 'get_weather'
  assert history[3].role == 'model'
  assert 'sunny' in history[3].parts[0].text.lower()
  assert history[4].role == 'user'
  assert history[4].parts[0].text == 'What is the stock price of symbol GOOG?'
  assert history[5].role == 'model'
  assert history[5].parts[0].function_call.name == 'get_stock_price'
  assert history[5].parts[0].function_call.args == {'symbol': 'GOOG'}
  assert history[6].role == 'user'
  assert history[6].parts[0].function_response.name == 'get_stock_price'
  assert history[7].role == 'model'
  assert '1000' in history[7].parts[0].text


def test_stream_function_tool_afc_disabled(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
          ],
      ),
  )
  for chunk in chat.send_message_stream('What is the weather in Boston?'):
    pass
  history = chat.get_history()
  assert len(history) == 3
  assert history[0].role == 'user'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[2].role == 'model'
  assert history[2].parts[0].text == ''


def test_stream_function_tool_afc_enabled(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  for chunk in chat.send_message_stream('What is the weather in Boston?'):
    pass
  history = chat.get_history()
  assert len(history) == 6
  assert history[0].role == 'user'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[2].role == 'model'
  assert history[2].parts[0].text == ''
  assert history[3].role == 'user'
  assert history[3].parts[0].function_response.name == 'get_weather'
  assert history[4].role == 'model'
  assert 'Boston' in history[4].parts[0].text
  assert history[5].role == 'model'
  assert history[5].parts[0].text == ''


def test_stream_function_tool_afc_enabled_multi_turn(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
              get_stock_price,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  for chunk in chat.send_message_stream('What is the weather in Boston?'):
    pass
  history = chat.get_history()

  assert len(history) == 6
  assert history[0].role == 'user'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[2].role == 'model'
  assert history[2].parts[0].text == ''
  assert history[3].role == 'user'
  assert history[3].parts[0].function_response.name == 'get_weather'
  assert history[4].role == 'model'
  assert 'Boston' in history[4].parts[0].text
  assert history[5].role == 'model'

  for chunk in chat.send_message_stream('What is the stock price of symbol GOOG?'):
    pass
  history = chat.get_history()

  assert len(history) == 13
  assert history[6].role == 'user'
  assert history[7].role == 'model'
  assert history[7].parts[0].function_call.name == 'get_stock_price'
  assert history[8].role == 'model'
  assert history[8].parts[0].text == ''
  assert history[9].role == 'user'
  assert history[9].parts[0].function_response.name == 'get_stock_price'
  assert history[10].role == 'model'
  assert 'stock' in history[10].parts[0].text
  assert history[11].role == 'model'
  assert '1000' in history[11].parts[0].text
  assert history[12].role == 'model'
  assert history[12].parts[0].text == ''


@pytest.mark.asyncio
async def test_async_stream_function_tool_afc_disabled(client):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
          ],
      ),
  )
  async for chunk in await chat.send_message_stream(
      'What is the weather in Boston?'
  ):
    pass
  history = chat.get_history()
  assert len(history) == 3
  assert history[0].role == 'user'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[2].role == 'model'
  assert history[2].parts[0].text == ''


@pytest.mark.asyncio
async def test_async_stream_function_tool_afc_enabled(client):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  async for _ in await chat.send_message_stream(
      'What is the weather in Boston?'
  ):
    pass

  history = chat.get_history()
  assert len(history) == 6
  assert history[0].role == 'user'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[2].role == 'model'
  assert history[2].parts[0].text == ''
  assert history[3].role == 'user'
  assert history[3].parts[0].function_response.name == 'get_weather'
  assert history[4].role == 'model'
  assert 'Boston' in history[4].parts[0].text
  assert history[5].parts[0].text == ''


@pytest.mark.asyncio
async def test_async_stream_function_tool_afc_enabled_multi_turn(
    client,
):
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather,
              get_stock_price,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  async for _ in await chat.send_message_stream(
      'What is the weather in Boston?'
  ):
    pass
  history = chat.get_history()

  assert len(history) == 6
  assert history[0].role == 'user'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[2].role == 'model'
  assert history[2].parts[0].text == ''
  assert history[3].role == 'user'
  assert history[3].parts[0].function_response.name == 'get_weather'
  assert history[4].role == 'model'
  assert 'Boston' in history[4].parts[0].text
  assert history[5].role == 'model'
  assert history[5].parts[0].text == ''

  async for _ in await chat.send_message_stream(
      'What is the stock price of symbol GOOG?'
  ):
    pass
  history = chat.get_history()

  assert len(history) == 13
  assert history[6].role == 'user'
  assert history[7].role == 'model'
  assert history[7].parts[0].function_call.name == 'get_stock_price'
  assert history[8].role == 'model'
  assert history[8].parts[0].text == ''
  assert history[9].role == 'user'
  assert history[9].parts[0].function_response.name == 'get_stock_price'
  assert history[10].role == 'model'
  assert 'stock' in history[10].parts[0].text
  assert history[11].role == 'model'
  assert '1000' in history[11].parts[0].text
  assert history[12].role == 'model'
  assert history[12].parts[0].text == ''


def test_union_type_afc(client):

  def add_numbers(
      a: Union[int, float], b: Union[int, float]
  ) -> Union[int, float]:
    """add two numbers."""

    return a + b

  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              add_numbers,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  chat.send_message('add 1 and 2.5')
  history = chat.get_history()
  assert len(history) == 4
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'add 1 and 2.5'
  assert history[1].role == 'model'
  assert history[1].parts[0].function_call.name == 'add_numbers'
  assert history[2].role == 'user'
  assert history[2].parts[0].function_response.name == 'add_numbers'
  assert history[3].role == 'model'
  assert '3.5' in history[3].parts[0].text


@pytest.mark.asyncio
async def test_mcp_sync_call_async_afc(client):
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

  config = types.ChatConfig(
      tools=[
          MockMcpClientSession(),
      ],
      automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
          enable=True
      ),
  )
  chat = client.aio.chats.create(
      model='gemini-3.1-pro-preview',
      config=config,
  )

  response = await chat.send_message(
      'What is the weather in Boston?'
  )
  assert 'sunny' in response.text.lower()

  response_2 = await chat.send_message(
      'What is 50 + 50?'
  )
  assert '100' in response_2.text


def test_afc_float_without_decimal(client):
  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              divide_floats,
              divide_integers,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  response = chat.send_message('what is the result of 10.0/2?')
  assert '5.0' in response.text


def test_afc_pydantic_model(client):
  class CityObject(pydantic.BaseModel):
    city_name: str

  def get_weather_pydantic_model(
      city_object: CityObject, is_winter: bool
  ) -> str:
    if is_winter:
      return f'The weather in {city_object.city_name} is cold and 10 degrees.'
    else:
      return f'The weather in {city_object.city_name} is warm and 25 degrees.'

  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather_pydantic_model,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  response = chat.send_message(
      'it is winter now, what is the weather in Boston?'
  )
  assert 'cold' in response.text and 'Boston' in response.text


def test_afc_pydantic_model_list_type(client):
  class CityObject(pydantic.BaseModel):
    city_name: str

  def get_weather_from_list_of_cities(
      city_object_list: list[CityObject],
      is_winter: bool,
  ) -> str:
    result = ''
    if is_winter:
      for city_object in city_object_list:
        result += (
            f'The weather in {city_object.city_name} is cold and 10 degrees.\n'
        )
    else:
      for city_object in city_object_list:
        result += (
            f'The weather in {city_object.city_name} is warm and 100 degrees.\n'
        )
    return result

  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_weather_from_list_of_cities,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  response = chat.send_message(
      'it is winter now, what is the weather in Boston and New York?'
  )
  assert 'cold' in response.text
  assert 'Boston' in response.text
  assert 'New York' in response.text


@pytest.mark.skip(
    'kokoro pydantic version is too low, can unskip after increasing the'
    ' pydantic version to 2.13.4 in requirements.txt later'
)
def test_afc_pydantic_model_union_type(client):

  class AnimalObject(pydantic.BaseModel):
    name: str
    age: int
    species: str

  class PlantObject(pydantic.BaseModel):
    name: str
    height: float
    color: str

  def get_information(
      object_of_interest: Union[AnimalObject, PlantObject],
  ) -> str:
    if isinstance(object_of_interest, AnimalObject):
      return (
          f'The animal is of {object_of_interest.species} species and is named'
          f' {object_of_interest.name} is {object_of_interest.age} years old'
      )
    elif isinstance(object_of_interest, PlantObject):
      return (
          f'The plant is named {object_of_interest.name} and is'
          f' {object_of_interest.height} meters tall and is'
          f' {object_of_interest.color} color'
      )
    else:
      return 'The animal is not supported'

  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              get_information,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )
  response = chat.send_message(
      'I have a one year old cat named Sundae, can you get the'
      ' information of the cat for me?'
  )
  assert 'Sundae' in response.text
  assert 'cat' in response.text


def test_afc_with_coroutine_function(client):

  async def divide_integers_async(a: int, b: int) -> int:
    return a // b

  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              divide_integers_async,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )

  with pytest.raises(errors.UnsupportedFunctionError):
    chat.send_message('Divide 1000 by 2.')


def test_class_method_afc(client):

  class FunctionHolder:
    NAME = 'FunctionHolder'
    def is_a_duck(self, number: int) -> str:
      return self.NAME + 'says isOdd: ' + str(number % 2 == 1)
    def is_a_rabbit(self, number: int) -> str:
      return self.NAME + 'says isEven: ' + str(number % 2 == 0)

  function_holder = FunctionHolder()

  chat = client.chats.create(
      model='gemini-3.1-pro-preview',
      config=types.ChatConfig(
          tools=[
              function_holder.is_a_duck,
              function_holder.is_a_rabbit,
          ],
          automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
              enable=True
          ),
      ),
  )

  response = chat.send_message(
      'Print the vertatim output of is_a_duck and is_a_rabbit for the number'
      ' of 100'
  )

  assert 'functionholder' in response.text.lower()
