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

"""Replay tests for private chats.send_message()."""

import pytest

from .. import pytest_helper
from ...errors import ClientError
from ..models import test_generate_content_tools
from ...types import Content
from ...types import FunctionCall
from ...types import FunctionResponse
from ...types import Part


pytestmark = [
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
    ),
    pytest.mark.skipif(
        "not config.getoption('--private')",
        reason="This test file is only intended for the private SDK",
    ),
]


MODEL_NAME = 'gemini-3.1-pro-preview'
get_weather = test_generate_content_tools.get_weather
get_stock_price = test_generate_content_tools.get_stock_price


def test_send_message_function_tool_afc_disabled(client):
  chat = client.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
      },
  )
  chat.send_message('What is the weather in Boston?')
  history = chat.get_history()
  assert len(history) == 2
  assert history[0].role == 'user'
  assert history[0].parts[0].text == 'What is the weather in Boston?'
  assert history[1].role == 'model'
  assert len(history[1].parts) == 1
  assert history[1].parts[0].function_call.name == 'get_weather'
  assert history[1].parts[0].function_call.args == {'city': 'Boston'}


def test_send_message_function_tool_afc_enabled(client):
  chat = client.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
          'automatic_function_calling': {'enable': True},
      },
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


def test_send_message_function_tool_afc_enabled_multi_turn(client):
  chat = client.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'enable': True},
      },
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


def test_send_message_multi_turn_afc_enabled_FC_FR_parts(client):
  chat = client.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'enable': True},
      },
      history=[
          Content(
              role='user',
              parts=[Part(text='What is the weather in Boston?')],
          ),
          Content(
              role='model',
              parts=[
                  Part(
                      function_call=FunctionCall(
                          name='get_weather',
                          args={'city': 'Boston'},
                      ),
                  ),
                  Part(
                      function_response=FunctionResponse(
                          name='get_weather',
                          response={'weather': 'sunny and 80 degrees'},
                      ),
                  ),
                  Part(text='The weather is sunny.'),
              ],
          ),
      ]
  )
  with pytest_helper.exception_if_vertex(client, ClientError):
    chat.send_message('What is the stock price of symbol GOOG?')


@pytest.mark.asyncio
async def test_async_send_message_function_tool_afc_disabled(client):
  chat = client.aio.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
      },
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
async def test_async_send_message_function_tool_afc_enabled(client):
  chat = client.aio.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
          'automatic_function_calling': {'enable': True},
      },
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
async def test_async_send_message_function_tool_afc_enabled_multi_turn(client):
  chat = client.aio.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'enable': True},
      },
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
