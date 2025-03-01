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
import os
from typing import AsyncIterator
from unittest import mock
from unittest.mock import AsyncMock

import PIL.Image
import pytest
from websockets import client

from ... import _api_client as api_client
from ... import Client
from ... import client as gl_client
from ... import live
from ... import types


IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.jpg')
)
image = PIL.Image.open(IMAGE_FILE_PATH)


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
async def test_send_text(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  await session.send_client_content(input='test')
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_content_dict(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = [{'parts': [{'text': 'test'}]}]

  await session.send_client_content(input=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data

  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_content(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  client_content = types.LiveClientContent(
      turns=[types.Content(parts=[types.Part(text='test')])], turn_complete=True
  )
  await session.send_client_content(input=client_content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'
  assert sent_data['client_content']['turn_complete'] == True


@pytest.mark.parametrize('vertexai', [False])
@pytest.mark.asyncio
async def test_send_file(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.File(
      uri='test_file.txt',
      mime_type='text/plain',
  )

  await session.send_client_content(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data

  assert (
      sent_data['client_content']['turns'][0]['parts'][0]['fileData'][
          'file_uri'
      ]
      == 'test_file.txt'
  )
  assert (
      sent_data['client_content']['turns'][0]['parts'][0]['fileData'][
          'mime_type'
      ]
      == 'text/plain'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_image(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = image

  await session.send_client_content(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert (
      sent_data['client_content']['turns'][0]['parts'][0]['inlineData'][
          'mime_type'
      ]
      == 'image/jpeg'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_blob_part(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.Part(
      inline_data=types.Blob(
          data=bytes([0, 0, 0, 0, 0, 0]), mime_type='audio/pcm'
      )
  )

  await session.send_client_content(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data

  assert (
      sent_data['client_content']['turns'][0]['parts'][0]['inlineData'][
          'mime_type'
      ]
      == 'audio/pcm'
  )
  assert (
      sent_data['client_content']['turns'][0]['parts'][0]['inlineData']['data']
      == 'AAAAAAAA'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_client_content_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = {'turns': [{'parts': [{'text': 'test'}]}]}

  await session.send_client_content(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_client_content_turn_complete(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = {'turn_complete': True}

  await session.send_client_content(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turn_complete'] == True


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_client_content_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.LiveClientContent(
      turns=[types.Content(parts=[types.Part(text='test')])], turn_complete=True
  )

  await session.send_client_content(input=input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turns'][0]['parts'][0]['text'] == 'test'
  assert sent_data['client_content']['turn_complete'] == True
