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
import json
import os
from unittest import mock

import pytest
from websockets import client

from ... import client as gl_client
from ... import live
from ... import types
from .. import pytest_helper


IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.jpg')
)


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
async def test_send_media_blob_dict(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = {'data': bytes([0, 0, 0, 0, 0, 0]), 'mime_type': 'audio/pcm'}

  await session.send_realtime_input(media=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['mediaChunks'][0]['data'] == 'AAAAAAAA'
  assert pytest_helper.get_value_ignore_key_case(
      sent_data['realtime_input']['mediaChunks'][0], 'mime_type'
  ) == 'audio/pcm'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_media_blob(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  content = types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='audio/pcm')

  await session.send_realtime_input(media=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['mediaChunks'][0]['data'] == 'AAAAAAAA'
  assert pytest_helper.get_value_ignore_key_case(
      sent_data['realtime_input']['mediaChunks'][0], 'mime_type'
  ) == 'audio/pcm'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_media_image(mock_websocket, vertexai, image_jpeg):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  await session.send_realtime_input(media=image_jpeg)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert pytest_helper.get_value_ignore_key_case(
      sent_data['realtime_input']['mediaChunks'][0], 'mime_type'
  ) == 'image/jpeg'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.parametrize(
    'content',
    [
        {'data': bytes([0, 0, 0, 0, 0, 0]), 'mime_type': 'audio/pcm'},
        types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='audio/pcm'),
    ],
)
@pytest.mark.asyncio
async def test_send_audio(mock_websocket, vertexai, content):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  await session.send_realtime_input(audio=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['audio']['data'] == 'AAAAAAAA'
  assert pytest_helper.get_value_ignore_key_case(
      sent_data['realtime_input']['audio'], 'mime_type'
  ) == 'audio/pcm'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_bad_audio_blob(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)
  content = types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='image/png')

  with pytest.raises(ValueError, match='.*Unsupported mime type.*'):
    await session.send_realtime_input(audio=content)


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_bad_video_blob(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)
  content = types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='audio/pcm')

  with pytest.raises(ValueError, match='.*Unsupported mime type.*'):
    await session.send_realtime_input(video=content)


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_audio_stream_end(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  await session.send_realtime_input(audio_stream_end=True)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['audioStreamEnd'] == True


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.parametrize(
    'content',
    [
        {'data': bytes([0, 0, 0, 0, 0, 0]), 'mime_type': 'image/png'},
        types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='image/png'),
    ],
)
@pytest.mark.asyncio
async def test_send_video(mock_websocket, vertexai, content):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  await session.send_realtime_input(video=content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['video']['data'] == 'AAAAAAAA'
  assert pytest_helper.get_value_ignore_key_case(
      sent_data['realtime_input']['video'], 'mime_type'
  ) == 'image/png'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_video_image(mock_websocket, vertexai, image_jpeg):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  await session.send_realtime_input(video=image_jpeg)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert pytest_helper.get_value_ignore_key_case(
      sent_data['realtime_input']['video'], 'mime_type'
  ) == 'image/jpeg'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_text(mock_websocket, vertexai):
  api_client = mock_api_client(vertexai=vertexai)
  session = live.AsyncSession(api_client=api_client, websocket=mock_websocket)

  await session.send_realtime_input(text='Hello?')
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['text'] == 'Hello?'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.parametrize('activity', [{}, types.ActivityStart()])
@pytest.mark.asyncio
async def test_send_activity_start(mock_websocket, vertexai, activity):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  await session.send_realtime_input(activity_start=activity)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['activityStart'] == {}


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.parametrize('activity', [{}, types.ActivityEnd()])
@pytest.mark.asyncio
async def test_send_activity_end(mock_websocket, vertexai, activity):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  await session.send_realtime_input(activity_end=activity)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data

  assert sent_data['realtime_input']['activityEnd'] == {}


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_send_multiple_args(mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  with pytest.raises(ValueError, match='.*one argument.*'):
    await session.send_realtime_input(
        text='Hello?', activity_start=types.ActivityStart()
    )
