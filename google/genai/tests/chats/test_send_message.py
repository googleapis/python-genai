# Copyright 2024 Google LLC
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


import os

import PIL.Image
from pydantic import BaseModel, ValidationError
import pytest

from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper


IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.jpg')
)
image = PIL.Image.open(IMAGE_FILE_PATH)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)
pytest_plugins = ('pytest_asyncio',)


def divide_intergers_with_customized_math_rule(
    numerator: int, denominator: int
) -> int:
  """Divides two integers with customized math rule."""
  return numerator // denominator + 1


def square_integer(given_integer: int) -> int:
  return given_integer*given_integer


def test_text(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chat.send_message(
      'tell me a story in 100 words',
  )


def test_part(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chat.send_message(
      types.Part.from_text('tell me a story in 100 words'),
  )


def test_parts(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chat.send_message(
      [
          types.Part.from_text('tell me a US city'),
          types.Part.from_text('the city is in west coast'),
      ],
  )


def test_image(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chat.send_message(
      [
          'what is the image about?',
          image,
      ],
  )


def test_google_cloud_storage_uri(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    chat.send_message(
        [
            'what is the image about?',
            types.Part.from_uri(
                'gs://unified-genai-dev/imagen-inputs/google_small.png',
                'image/png',
            ),
        ],
    )


def test_uploaded_file_uri(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    chat.send_message(
        [
            'what is the image about?',
            types.Part.from_uri(
                'https://generativelanguage.googleapis.com/v1beta/files/9w04rxmcgsp8',
                'image/png',
            ),
        ],
    )


def test_history(client):
  history = [
      types.Content(
          role='model',
          parts=[types.Part.from_text('Hello there! how can I help you?')],
      ),
      types.Content(
          role='user', parts=[types.Part.from_text('define a=5, b=10')]
      ),
  ]
  chat = client.chats.create(model='gemini-1.5-flash', history=history)
  chat.send_message('what is a + b?')


def test_send_2_messages(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chat.send_message('write a python function to check if a year is a leap year')
  chat.send_message('write a unit test for the function')


def test_with_afc_history(client):
  chat = client.chats.create(
      model='gemini-1.5-flash',
      config={'tools': [divide_intergers_with_customized_math_rule]},
  )
  _ = chat.send_message('what is the result of 100/2?')
  chat_history = chat._curated_history

  assert len(chat_history) == 4
  assert chat_history[0].role == 'user'
  assert chat_history[0].parts[0].text == 'what is the result of 100/2?'

  assert chat_history[1].role == 'model'
  assert (
      chat_history[1].parts[0].function_call.name
      == 'divide_intergers_with_customized_math_rule'
  )
  assert chat_history[1].parts[0].function_call.args == {
      'numerator': 100,
      'denominator': 2,
  }

  assert chat_history[2].role == 'user'
  assert (
      chat_history[2].parts[0].function_response.name
      == 'divide_intergers_with_customized_math_rule'
  )
  assert chat_history[2].parts[0].function_response.response == {'result': 51}

  assert chat_history[3].role == 'model'
  assert '51' in chat_history[3].parts[0].text


def test_with_afc_disabled(client):
  chat = client.chats.create(
      model='gemini-1.5-flash',
      config={
          'tools': [square_integer],
          'automatic_function_calling': {'disable': True},
      },
  )
  chat.send_message(
      'Do the square of 3.',
  )
  chat_history = chat._curated_history

  assert len(chat_history) == 2
  assert chat_history[0].role == 'user'
  assert chat_history[0].parts[0].text == 'Do the square of 3.'

  assert chat_history[1].role == 'model'
  assert chat_history[1].parts[0].function_call.name == 'square_integer'
  assert chat_history[1].parts[0].function_call.args == {
      'given_integer': 3,
  }


@pytest.mark.asyncio
async def test_with_afc_history_async(client):
  chat = client.aio.chats.create(
      model='gemini-1.5-flash',
      config={'tools': [divide_intergers_with_customized_math_rule]},
  )
  _ = await chat.send_message('what is the result of 100/2?')
  chat_history = chat._curated_history

  assert len(chat_history) == 4
  assert chat_history[0].role == 'user'
  assert chat_history[0].parts[0].text == 'what is the result of 100/2?'

  assert chat_history[1].role == 'model'
  assert (
      chat_history[1].parts[0].function_call.name
      == 'divide_intergers_with_customized_math_rule'
  )
  assert chat_history[1].parts[0].function_call.args == {
      'numerator': 100,
      'denominator': 2,
  }

  assert chat_history[2].role == 'user'
  assert (
      chat_history[2].parts[0].function_response.name
      == 'divide_intergers_with_customized_math_rule'
  )
  assert chat_history[2].parts[0].function_response.response == {'result': 51}

  assert chat_history[3].role == 'model'
  assert '51' in chat_history[3].parts[0].text


@pytest.mark.asyncio
async def test_with_afc_disabled_async(client):
  chat = client.aio.chats.create(
      model='gemini-1.5-flash',
      config={
          'tools': [square_integer],
          'automatic_function_calling': {'disable': True},
      },
  )
  await chat.send_message(
      'Do the square of 3.',
  )
  chat_history = chat._curated_history

  assert len(chat_history) == 2
  assert chat_history[0].role == 'user'
  assert chat_history[0].parts[0].text == 'Do the square of 3.'

  assert chat_history[1].role == 'model'
  assert chat_history[1].parts[0].function_call.name == 'square_integer'
  assert chat_history[1].parts[0].function_call.args == {
      'given_integer': 3,
  }


def test_stream_text(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chunks = 0
  for chunk in chat.send_message_stream(
      'tell me a story in 100 words',
  ):
    chunks += 1

  assert chunks > 2


def test_stream_part(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chunks = 0
  for chunk in chat.send_message_stream(
      types.Part.from_text('tell me a story in 100 words'),
  ):
    chunks += 1

  assert chunks > 2


def test_stream_parts(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  chunks = 0
  for chunk in chat.send_message_stream(
      [
          types.Part.from_text('tell me a story in 100 words'),
          types.Part.from_text('the story is about a car'),
      ],
  ):
    chunks += 1

  assert chunks > 2


def test_stream_function_calling(client):
  chat = client.chats.create(
      model='gemini-2.0-flash-exp',
      config={'tools': [divide_intergers_with_customized_math_rule]},
  )
  for chunk in chat.send_message_stream(
      'what is the result of 100/2?',
  ):
    pass
  for chunk in chat.send_message_stream(
      'what is the result of 50/2?',
  ):
    pass


def test_stream_send_2_messages(client):
  chat = client.chats.create(model='gemini-1.5-flash')
  for chunk in chat.send_message_stream(
      'write a python function to check if a year is a leap year'
  ):
    pass

  for chunk in chat.send_message_stream('write a unit test for the function'):
    pass


@pytest.mark.asyncio
async def test_async_text(client):
  chat = client.aio.chats.create(model='gemini-1.5-flash')
  await chat.send_message('tell me a story in 100 words')


@pytest.mark.asyncio
async def test_async_part(client):
  chat = client.aio.chats.create(model='gemini-1.5-flash')
  await chat.send_message(types.Part.from_text('tell me a story in 100 words'))


@pytest.mark.asyncio
async def test_async_parts(client):
  chat = client.aio.chats.create(model='gemini-1.5-flash')
  await chat.send_message(
      [
          types.Part.from_text('tell me a US city'),
          types.Part.from_text('the city is in west coast'),
      ],
  )


@pytest.mark.asyncio
async def test_async_history(client):
  history = [
      types.Content(
          role='model',
          parts=[types.Part.from_text('Hello there! how can I help you?')],
      ),
      types.Content(
          role='user', parts=[types.Part.from_text('define a=5, b=10')]
      ),
  ]
  chat = client.aio.chats.create(model='gemini-1.5-flash', history=history)
  await chat.send_message('what is a + b?')


@pytest.mark.asyncio
async def test_async_stream_text(client):
  chat = client.aio.chats.create(model='gemini-1.5-flash')
  chunks = 0
  async for chunk in chat.send_message_stream('tell me a story in 100 words'):
    chunks += 1

  assert chunks > 2


@pytest.mark.asyncio
async def test_async_stream_part(client):
  chat = client.aio.chats.create(model='gemini-1.5-flash')
  chunks = 0
  async for chunk in chat.send_message_stream(
      types.Part.from_text('tell me a story in 100 words')
  ):
    chunks += 1

  assert chunks > 2


@pytest.mark.asyncio
async def test_async_stream_parts(client):
  chat = client.aio.chats.create(model='gemini-1.5-flash')
  chunks = 0
  async for chunk in chat.send_message_stream(
      [
          types.Part.from_text('tell me a story in 100 words'),
          types.Part.from_text('the story is about a car'),
      ],
  ):
    chunks += 1

  assert chunks > 2


@pytest.mark.asyncio
async def test_async_stream_function_calling(client):
  chat = client.aio.chats.create(
      model='gemini-2.0-flash-exp',
      config={'tools': [divide_intergers_with_customized_math_rule]},
  )
  async for chunk in chat.send_message_stream('what is the result of 100/2?'):
    pass
  async for chunk in chat.send_message_stream('what is the result of 50/2?'):
    pass


@pytest.mark.asyncio
async def test_async_stream_send_2_messages(client):
  chat = client.aio.chats.create(model='gemini-1.5-flash')
  async for chunk in chat.send_message_stream(
      'write a python function to check if a year is a leap year'
  ):
    pass
  async for chunk in chat.send_message_stream(
      'write a unit test for the function'
  ):
    pass
