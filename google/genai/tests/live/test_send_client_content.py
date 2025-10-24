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
import base64
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
  api_client._http_options = {'headers': {}}  # Ensure headers exist
  api_client.vertexai = vertexai
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
async def test_send_content_dict(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = [{'parts': [{'text': 'test'}]}]

  await session.send_client_content(turns=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data

  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'

@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_content_dict_list(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = [{'parts': [{'text': 'test'}]}]

  await session.send_client_content(turns=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data

  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'

@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_content_content(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = types.Content.model_validate({'parts': [{'text': 'test'}]})

  await session.send_client_content(turns=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data

  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_content_with_blob(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = types.Content.model_validate(
      {'parts': [{'inline_data': {'data': b'test'}}]}
  )

  await session.send_client_content(turns=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data

  assert pytest_helper.get_value_ignore_key_case(
      sent_data['client_content']['turns'][0]['parts'][0], 'inline_data') == {
          'data': base64.b64encode(b'test').decode()
      }


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_client_content_turn_complete_false(
    mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  await session.send_client_content(turn_complete=False)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turnComplete'] == False


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_client_content_empty(
    mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  await session.send_client_content()
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turnComplete'] == True
