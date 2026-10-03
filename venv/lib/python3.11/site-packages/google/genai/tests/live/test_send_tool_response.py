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


"""Tests for live.py."""

import contextlib
import json
from unittest import mock

import pytest
from websockets import client

from .. import pytest_helper
from ... import client as gl_client
from ... import live
from ... import types


def exception_if_mldev(vertexai, exception_type: type[Exception]):
  if vertexai:
    return contextlib.nullcontext()
  else:
    return pytest.raises(exception_type)


def mock_api_client(vertexai=False):
  api_client = mock.MagicMock(spec=gl_client.BaseApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}  # Ensure headers exist
  api_client.vertexai = vertexai
  api_client._api_client = api_client
  return api_client


@pytest.fixture
def mock_websocket():
  websocket = mock.AsyncMock(spec=client.ClientConnection)
  websocket.send = mock.AsyncMock()
  websocket.recv = mock.AsyncMock(
      return_value='{"serverContent": {"turnComplete": true}}'
  )  # Default response
  websocket.close = mock.AsyncMock()
  return websocket


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_function_response_dict(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(
      api_client=api_client, websocket=mock_websocket
  )

  input = {
      'name': 'get_current_weather',
      'response': {'temperature': 14.5, 'unit': 'C'},
  }

  if not vertexai:
    input['id'] = 'some-id'

  await session.send_tool_response(function_responses=input)

  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data

  assert (
      sent_data['tool_response']['functionResponses'][0]['name']
      == 'get_current_weather'
  )
  assert (
      sent_data['tool_response']['functionResponses'][0]['response'][
          'temperature'
      ]
      == 14.5
  )
  assert (
      sent_data['tool_response']['functionResponses'][0]['response']['unit']
      == 'C'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_function_response(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  input = types.FunctionResponse(
      name='get_current_weather',
      response={
          'temperature': 14.5,
          'unit': 'C',
          'user_name': 'test_user_name',
          'userEmail': 'test_user_email',
      },
  )
  if not vertexai:
    input.id = 'some-id'

  await session.send_tool_response(function_responses=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data

  assert (
      sent_data['tool_response']['functionResponses'][0]['name']
      == 'get_current_weather'
  )
  assert (
      sent_data['tool_response']['functionResponses'][0]['response']
      == input.response
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_function_response_scheduling(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  input = types.FunctionResponse(
      name='get_current_weather',
      response={'temperature': 14.5, 'unit': 'C'},
      will_continue=True,
      scheduling=types.FunctionResponseScheduling.SILENT,
  )
  if not vertexai:
    input.id = 'some-id'

  await session.send_tool_response(function_responses=input)

  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data

  assert pytest_helper.get_value_ignore_key_case(
      sent_data['tool_response']['functionResponses'][0], 'will_continue'
  )
  assert (
      sent_data['tool_response']['functionResponses'][0]['scheduling']
      == 'SILENT'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_function_response_list(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  input1 = {
      'name': 'get_current_weather',
      'response': {'temperature': 14.5, 'unit': 'C'},
  }
  input2 = {
      'name': 'get_current_weather',
      'response': {'temperature': 99.9, 'unit': 'C'},
  }

  if not vertexai:
    input1['id'] = '1'
    input2['id'] = '2'

  await session.send_tool_response(function_responses=[input1, input2])
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data

  assert len(sent_data['tool_response']['functionResponses']) == 2
  assert (
      sent_data['tool_response']['functionResponses'][0]['response'][
          'temperature'
      ]
      == 14.5
  )
  assert (
      sent_data['tool_response']['functionResponses'][1]['response'][
          'temperature'
      ]
      == 99.9
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_missing_id(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(
      api_client=api_client, websocket=mock_websocket
  )

  input1 = {
      'name': 'get_current_weather',
      'response': {'temperature': 14.5, 'unit': 'C'},
      'id': '1',
  }
  input2 = {
      'name': 'get_current_weather',
      'response': {'temperature': 99.9, 'unit': 'C'},
  }

  if not vertexai:
    with pytest.raises(ValueError, match=".*must have.*"):
      await session.send_tool_response(function_responses=[input1, input2])
