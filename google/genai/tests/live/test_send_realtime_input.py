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
async def test_send_blob_dict(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = {'data': bytes([0, 0, 0, 0, 0, 0]), 'mimeType': 'audio/pcm'}

  await session.send_realtime_input(input=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['media_chunks'][0]['data'] == 'AAAAAAAA'
  assert (
      sent_data['realtime_input']['media_chunks'][0]['mime_type'] == 'audio/pcm'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_blob(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='audio/pcm')

  await session.send_realtime_input(input=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['media_chunks'][0]['data'] == 'AAAAAAAA'
  assert (
      sent_data['realtime_input']['media_chunks'][0]['mime_type'] == 'audio/pcm'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_image(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  await session.send_realtime_input(input=image)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert (
      sent_data['realtime_input']['media_chunks'][0]['mime_type']
      == 'image/jpeg'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_blob_list(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = [
      types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='image/jpeg'),
      {'data': bytes([0, 0, 0, 0, 0, 0]), 'mimeType': 'image/jpeg'},
      image,
  ]

  await session.send_realtime_input(input=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert len(sent_data['realtime_input']['media_chunks']) == 3
  assert (
      sent_data['realtime_input']['media_chunks'][0]['mime_type']
      == 'image/jpeg'
  )
  assert (
      sent_data['realtime_input']['media_chunks'][1]['mime_type']
      == 'image/jpeg'
  )
  assert (
      sent_data['realtime_input']['media_chunks'][2]['mime_type']
      == 'image/jpeg'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_realtime_input_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = {
      'media_chunks': [
          {'data': bytes([0, 0, 0, 0, 0, 0]), 'mimeType': 'audio/pcm'}
      ]
  }

  await session.send_realtime_input(input=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['media_chunks'][0]['data'] == 'AAAAAAAA'
  assert (
      sent_data['realtime_input']['media_chunks'][0]['mime_type'] == 'audio/pcm'
  )


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_realtime_input(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = types.LiveClientRealtimeInput(
      media_chunks=[
          types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='audio/pcm')
      ]
  )

  await session.send_realtime_input(input=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['media_chunks'][0]['data'] == 'AAAAAAAA'
  assert (
      sent_data['realtime_input']['media_chunks'][0]['mime_type'] == 'audio/pcm'
  )
