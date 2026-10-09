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

"""Tests for send_context_update in live.py."""

import json
from unittest import mock

import pytest
from websockets import client

from .. import pytest_helper
from ... import client as gl_client
from ... import live
from ... import types


def mock_api_client(vertexai=False):
  api_client = mock.MagicMock(spec=gl_client.BaseApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}
  api_client.vertexai = vertexai
  api_client._api_client = api_client
  return api_client


@pytest.fixture
def mock_websocket():
  websocket = mock.AsyncMock(spec=client.ClientConnection)
  websocket.send = mock.AsyncMock()
  websocket.recv = mock.AsyncMock(
      return_value='{"serverContent": {"turnComplete": true}}'
  )
  websocket.close = mock.AsyncMock()
  return websocket


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_context_update_system_instruction_str(
    mock_websocket, vertexai
):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  await session.send_context_update(
      system_instruction='You are a helpful assistant.'
  )

  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'contextUpdate' in sent_data
  assert 'systemInstruction' in sent_data['contextUpdate']
  parts = sent_data['contextUpdate']['systemInstruction']['parts']
  assert parts[0]['text'] == 'You are a helpful assistant.'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_context_update_clear_tools(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  await session.send_context_update(tools=[])

  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'contextUpdate' in sent_data
  assert 'tools' in sent_data['contextUpdate']
  assert sent_data['contextUpdate']['tools']['tools'] == []


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_context_update_with_function(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  def get_current_weather(location: str) -> str:
    """Gets the weather for a location."""
    return f'Sunny in {location}'

  await session.send_context_update(tools=[get_current_weather])

  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'contextUpdate' in sent_data
  tools = sent_data['contextUpdate']['tools']['tools']
  assert len(tools) == 1
  func_decl = tools[0]['functionDeclarations'][0]
  assert func_decl['name'] == 'get_current_weather'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_context_update_object(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  update = types.LiveClientContextUpdate(
      system_instruction=types.Content(
          parts=[types.Part.from_text(text='Custom prompt')]
      )
  )

  await session.send_context_update(context_update=update)

  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'contextUpdate' in sent_data
  parts = sent_data['contextUpdate']['systemInstruction']['parts']
  assert parts[0]['text'] == 'Custom prompt'


@pytest.mark.asyncio
async def test_send_context_update_validation_errors(mock_websocket):
  api_client = mock_api_client()
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  # Neither provided
  with pytest.raises(ValueError, match='At least one of'):
    await session.send_context_update()

  # Both context_update and kwargs provided
  with pytest.raises(ValueError, match='Cannot set both'):
    await session.send_context_update(
        system_instruction='Hello',
        context_update=types.LiveClientContextUpdate(),
    )
