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


"""Tests for live.py."""
import json
from typing import AsyncIterator
from unittest import mock
from unittest.mock import AsyncMock

import pytest
from websockets import client

from ... import _api_client as api_client
from ... import Client
from ... import client as gl_client
from ... import live
from ... import types


@pytest.fixture
def mock_api_client(vertexai=False):
  api_client = mock.MagicMock(spec=gl_client.ApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}  # Ensure headers exist
  api_client.vertexai = vertexai
  return api_client


@pytest.fixture
def mock_websocket():
  websocket = AsyncMock(spec=client.ClientConnection)
  websocket.send = AsyncMock()
  websocket.recv = AsyncMock(
      return_value='{"serverContent": {"turnComplete": true}}'
  )  # Default response
  websocket.close = AsyncMock()
  return websocket


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_function_response_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  input = {
      'name': 'get_current_weather',
      'response': {'temperature': 14.5, 'unit': 'C'},
      'id': 'some-id',
  }
  if vertexai:
    input.pop('id')

  await session.send(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data

  assert (
      sent_data['tool_response']['function_responses'][0]['name']
      == 'get_current_weather'
  )
  assert (
      sent_data['tool_response']['function_responses'][0]['response'][
          'temperature'
      ]
      == 14.5
  )
  assert (
      sent_data['tool_response']['function_responses'][0]['response']['unit']
      == 'C'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_function_response(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  if vertexai:
    maybe_id = {}
  else:
    maybe_id = {'id': 'some-id'}
  input = types.FunctionResponse(
      name='get_current_weather',
      response={'temperature': 14.5, 'unit': 'C'},
      **maybe_id
  )

  await session.send(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data

  assert (
      sent_data['tool_response']['function_responses'][0]['name']
      == 'get_current_weather'
  )
  assert (
      sent_data['tool_response']['function_responses'][0]['response'][
          'temperature'
      ]
      == 14.5
  )
  assert (
      sent_data['tool_response']['function_responses'][0]['response']['unit']
      == 'C'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_function_response_list(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  input1 = {
      'name': 'get_current_weather',
      'response': {'temperature': 14.5, 'unit': 'C'},
      'id': '1',
  }
  input2 = {
      'name': 'get_current_weather',
      'response': {'temperature': 99.9, 'unit': 'C'},
      'id': '2',
  }

  if vertexai:
    input1.pop('id')
    input2.pop('id')

  await session.send(input=[input1, input2])
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data

  assert len(sent_data['tool_response']['function_responses']) == 2
  assert (
      sent_data['tool_response']['function_responses'][0]['response'][
          'temperature'
      ]
      == 14.5
  )
  assert (
      sent_data['tool_response']['function_responses'][1]['response'][
          'temperature'
      ]
      == 99.9
  )
