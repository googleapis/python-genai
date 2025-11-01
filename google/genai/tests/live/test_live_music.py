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


"""Tests for live_music.py."""
import contextlib
import json
from typing import AsyncIterator
from unittest import mock
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch
import warnings

from google.oauth2.credentials import Credentials
import pytest
from websockets import client

from ... import _api_client as api_client
from ... import _common
from ... import Client
from ... import client as gl_client
from ... import live
from ... import live_music
from ... import types
from .. import pytest_helper
try:
    import aiohttp
    AIOHTTP_NOT_INSTALLED = False
except ImportError:
    AIOHTTP_NOT_INSTALLED = True
    aiohttp = mock.MagicMock()


requires_aiohttp = pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason="aiohttp is not installed, skipping test."
)


def mock_api_client(vertexai=False, credentials=None):
  api_client = mock.MagicMock(spec=gl_client.BaseApiClient)
  if not vertexai:
    api_client.api_key = 'TEST_API_KEY'
    api_client.location = None
    api_client.project = None
  else:
    api_client.api_key = None
    api_client.location = 'us-central1'
    api_client.project = 'test_project'

  api_client._host = lambda: 'test_host'
  api_client._credentials = credentials
  api_client._http_options = types.HttpOptions.model_validate(
      {'headers': {}}
  )  # Ensure headers exist
  api_client.vertexai = vertexai
  api_client._api_client = api_client
  return api_client


@pytest.fixture
def mock_websocket():
  websocket = AsyncMock(spec=client.ClientConnection)
  websocket.send = AsyncMock()
  websocket.recv = AsyncMock(
      return_value=b"""{
  "serverContent": {
    "audioChunks": [
      {
        "data": "Z2VsYmFuYW5h",
        "mimeType": "audio/l16;rate=48000;channels=2",
        "sourceMetadata": {
          "clientContent": {
            "weightedPrompts": [
              {
                "text": "Jazz",
                "weight": 1
              }
            ]
          },
          "musicGenerationConfig": {
            "seed": -957124937,
            "bpm": 140,
            "scale": "A_FLAT_MAJOR_F_MINOR"
          }
        }
      }
    ]
  }
}"""
  )  # Default response
  websocket.close = AsyncMock()
  return websocket


async def get_connect_message(api_client, model):
  mock_ws = AsyncMock()
  mock_ws.send = AsyncMock()
  mock_ws.recv = AsyncMock(return_value=b'some response')

  mock_google_auth_default = Mock(return_value=(None, None))
  mock_creds = Mock(token='test_token')
  mock_google_auth_default.return_value = (mock_creds, None)

  @contextlib.asynccontextmanager
  async def mock_connect(uri, additional_headers=None):
    yield mock_ws

  @patch('google.auth.default', new=mock_google_auth_default)
  @patch.object(live_music, 'connect', new=mock_connect)
  async def _test_connect():
    live_module = live.AsyncLive(api_client)
    async with live_module.music.connect(
        model=model,
    ):
      pass

    mock_ws.send.assert_called_once()
    return json.loads(mock_ws.send.call_args[0][0])

  return await _test_connect()


def test_mldev_from_env(monkeypatch):
  api_key = 'google_api_key'
  monkeypatch.setenv('GOOGLE_API_KEY', api_key)

  client = Client()

  assert not client.aio.live.music._api_client.vertexai
  assert client.aio.live.music._api_client.api_key == api_key
  assert isinstance(client.aio.live._api_client, api_client.BaseApiClient)


@requires_aiohttp
def test_vertex_from_env(monkeypatch):
  project_id = 'fake_project_id'
  location = 'fake-location'
  monkeypatch.setenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')
  monkeypatch.setenv('GOOGLE_CLOUD_PROJECT', project_id)
  monkeypatch.setenv('GOOGLE_CLOUD_LOCATION', location)

  client = Client()

  assert client.aio.live.music._api_client.vertexai
  assert client.aio.live.music._api_client.project == project_id
  assert isinstance(client.aio.live._api_client, api_client.BaseApiClient)


def test_websocket_base_url():
  base_url = 'https://test.com'
  api_client = gl_client.BaseApiClient(
      api_key='google_api_key',
      http_options={'base_url': base_url},
  )
  assert api_client._websocket_base_url() == 'wss://test.com'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_weighted_prompts(
    mock_websocket, vertexai
):
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  if vertexai:
    with pytest.raises(NotImplementedError):
      await session.set_weighted_prompts(prompts=[types.WeightedPrompt(text='Jazz', weight=1)])
    return
  await session.set_weighted_prompts(prompts=[types.WeightedPrompt(text='Jazz', weight=1)])
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'clientContent' in sent_data
  assert sent_data['clientContent']['weightedPrompts'][0]['text'] == 'Jazz'
  assert sent_data['clientContent']['weightedPrompts'][0]['weight'] == 1


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_config(
    mock_websocket, vertexai
):
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  if vertexai:
    with pytest.raises(NotImplementedError):
      await session.set_music_generation_config(
          config=types.LiveMusicGenerationConfig(
              bpm=140,
              music_generation_mode=types.MusicGenerationMode.VOCALIZATION,
          )
      )
    return
  await session.set_music_generation_config(
      config=types.LiveMusicGenerationConfig(
          bpm=140,
          music_generation_mode=types.MusicGenerationMode.VOCALIZATION,
      )
  )
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'musicGenerationConfig' in sent_data
  assert sent_data['musicGenerationConfig']['bpm'] == 140


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_control_signal_play(
    mock_websocket, vertexai
):
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  if vertexai:
    with pytest.raises(NotImplementedError):
      await session.play()
    return
  await session.play()
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'playbackControl' in sent_data
  assert 'PLAY' in sent_data['playbackControl']


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_control_signal_pause(
    mock_websocket, vertexai
):
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  if vertexai:
    with pytest.raises(NotImplementedError):
      await session.pause()
    return
  await session.pause()
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'playbackControl' in sent_data
  assert 'PAUSE' in sent_data['playbackControl']


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_control_signal_stop(
    mock_websocket, vertexai
):
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  if vertexai:
    with pytest.raises(NotImplementedError):
      await session.stop()
    return
  await session.stop()
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'playbackControl' in sent_data
  assert 'STOP' in sent_data['playbackControl']


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_control_signal_reset_context(
    mock_websocket, vertexai
):
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  if vertexai:
    with pytest.raises(NotImplementedError):
      await session.reset_context()
    return
  await session.reset_context()
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'playbackControl' in sent_data
  assert 'RESET_CONTEXT' in sent_data['playbackControl']


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_receive( mock_websocket, vertexai):
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  if vertexai:
    with pytest.raises(NotImplementedError):
      async for _ in session.receive():
        pass
    return
  async for response in session.receive():
    assert isinstance(response, types.LiveMusicServerMessage)
    audio_chunk = response.server_content.audio_chunks[0]
    # Data contains decoded b64 audio
    assert audio_chunk.data == b'gelbanana'
    assert audio_chunk.mime_type == 'audio/l16;rate=48000;channels=2'
    assert audio_chunk.source_metadata.client_content.weighted_prompts[0].text == 'Jazz'
    assert audio_chunk.source_metadata.client_content.weighted_prompts[0].weight == 1
    assert audio_chunk.source_metadata.music_generation_config.bpm == 140
    break


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_receive_error(
     mock_websocket, vertexai
):
  mock_websocket.recv = AsyncMock(return_value='invalid json')
  session = live_music.AsyncMusicSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  with pytest.raises(ValueError):
    await session.receive().__anext__()


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_close( mock_websocket, vertexai):
  session = live_music.AsyncMusicSession(
      mock_api_client(vertexai=vertexai), mock_websocket
  )
  await session.close()
  mock_websocket.close.assert_called_once()


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_setup_to_api(vertexai):
  if vertexai:
    with pytest.raises(NotImplementedError):
      await get_connect_message(
          mock_api_client(vertexai=vertexai),
          model='test_model'
      )
    return
  result = await get_connect_message(
      mock_api_client(vertexai=vertexai),
      model='test_model'
  )
  expected_result = {'setup': {}}
  if vertexai:
    # Vertex is not supported yet
    assert False
  else:
    expected_result['setup']['model'] = 'models/test_model'
  assert result == expected_result
