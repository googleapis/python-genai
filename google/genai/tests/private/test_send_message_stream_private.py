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

"""Tests for private send_message_stream."""

import pytest

from .. import pytest_helper
from ..models import test_generate_content_tools


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


def test_send_message_stream_function_tool_afc_disabled(client):
  chat = client.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
      },
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


def test_send_message_stream_function_tool_afc_enabled(client):
  chat = client.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
          'automatic_function_calling': {'enable': True},
      },
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


def test_send_message_stream_function_tool_afc_enabled_multi_turn(client):
  chat = client.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'enable': True},
      },
  )
  for chunk in chat.send_message_stream('What is the weather in Boston?'):
    pass
  history = chat.get_history()

  if client.vertexai:
    assert len(history) == 7
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
    assert '100' in history[5].parts[0].text
    assert history[6].role == 'model'
    assert history[6].parts[0].text == ''
  else:
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

  if client.vertexai:
    assert len(history) == 14
    assert history[7].role == 'user'
    assert history[8].role == 'model'
    assert history[8].parts[0].function_call.name == 'get_stock_price'
    assert history[9].role == 'model'
    assert history[9].parts[0].text == ''
    assert history[10].role == 'user'
    assert history[10].parts[0].function_response.name == 'get_stock_price'
    assert history[11].role == 'model'
    assert 'GOOG' in history[11].parts[0].text
    assert history[12].role == 'model'
    assert '1000' in history[12].parts[0].text
    assert history[13].role == 'model'
    assert history[13].parts[0].text == ''
  else:
    assert len(history) == 13
    assert history[6].role == 'user'
    assert history[7].role == 'model'
    assert history[7].parts[0].function_call.name == 'get_stock_price'
    assert history[8].role == 'model'
    assert history[8].parts[0].text == ''
    assert history[9].role == 'user'
    assert history[9].parts[0].function_response.name == 'get_stock_price'
    assert history[10].role == 'model'
    assert 'GOOG' in history[10].parts[0].text
    assert history[11].role == 'model'
    assert '1000' in history[11].parts[0].text
    assert history[12].role == 'model'
    assert history[12].parts[0].text == ''


@pytest.mark.asyncio
async def test_async_send_message_stream_function_tool_afc_disabled(client):
  chat = client.aio.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
      },
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
async def test_async_send_message_stream_function_tool_afc_enabled(client):
  chat = client.aio.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather],
          'automatic_function_calling': {'enable': True},
      },
  )
  async for chunk in await chat.send_message_stream(
      'What is the weather in Boston?'
  ):
    pass
  history = chat.get_history()
  if client.vertexai:
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
  else:
    assert len(history) == 7
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
    assert 'degrees' in history[5].parts[0].text
    assert history[6].role == 'model'
    assert history[6].parts[0].text == ''


@pytest.mark.asyncio
async def test_async_send_message_stream_function_tool_afc_enabled_multi_turn(
    client,
):
  chat = client.aio.chats.create(
      model=MODEL_NAME,
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'enable': True},
      },
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
