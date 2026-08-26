# Copyright 2026 Google LLC
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

import base64
import json
from unittest.mock import AsyncMock, Mock

import pytest

from ... import types
from ...audio_cache_manager import AudioCacheManager
from ...file_artifact_service import FileArtifactService
from ...live import AsyncSession


def test_live_connect_config_save_live_blob_defaults():
  """Test default value is False."""
  config = types.LiveConnectConfig()
  assert config.save_live_blob is False


def test_live_connect_config_save_live_blob_explicit_true():
  """Test setting save_live_blob to True."""
  config = types.LiveConnectConfig(save_live_blob=True)
  assert config.save_live_blob is True


def test_dict_initialization_with_save_live_blob():
  """Test dictionary initialization sets save_live_blob."""
  config = types.LiveConnectConfig(**{"save_live_blob": True})
  assert config.save_live_blob is True


@pytest.mark.asyncio
async def test_async_session_records_input_and_output_audio(tmp_path):
  """Test AsyncSession with save_live_blob=True records input chunks and output chunks and flushes on turn_complete."""
  mock_ws = AsyncMock()
  mock_api_client = Mock()
  mock_api_client.vertexai = False

  artifact_service = FileArtifactService(base_dir=tmp_path)
  cache_manager = AudioCacheManager()

  session = AsyncSession(
      api_client=mock_api_client,
      websocket=mock_ws,
      session_id="test_live_session",
      save_live_blob=True,
      artifact_service=artifact_service,
      audio_cache_manager=cache_manager,
      app_name="test_app",
      user_id="test_user",
      agent_name="gemini_agent",
  )

  assert session.save_live_blob is True

  # 1. User sends input audio chunk
  input_data = b"user_input_audio_bytes_16k"
  await session.send_realtime_input(
      media=types.Blob(data=input_data, mime_type="audio/pcm;rate=16000")
  )

  # Check that input audio was cached in volatile memory
  assert len(session.input_realtime_cache) == 1
  assert session.input_realtime_cache[0].role == "user"
  assert session.input_realtime_cache[0].data.data == input_data

  # 2. Server sends model output audio chunks followed by turn_complete
  output_data_1 = b"model_audio_part_1"
  output_data_2 = b"model_audio_part_2"

  mock_server_message_1 = {
      "serverContent": {
          "modelTurn": {
              "parts": [{
                  "inlineData": {
                      "mimeType": "audio/pcm",
                      "data": base64.b64encode(output_data_1).decode("utf-8"),
                  }
              }]
          }
      }
  }

  mock_server_message_2 = {
      "serverContent": {
          "modelTurn": {
              "parts": [{
                  "inlineData": {
                      "mimeType": "audio/pcm",
                      "data": base64.b64encode(output_data_2).decode("utf-8"),
                  }
              }]
          },
          "turnComplete": True,
      }
  }

  mock_ws.recv.side_effect = [
      json.dumps(mock_server_message_1),
      json.dumps(mock_server_message_2),
  ]

  # Receive turn
  received_messages = []
  async for msg in session.receive():
    received_messages.append(msg)

  assert len(received_messages) == 2

  # Since turnComplete was received, caches should be flushed and cleared
  assert len(session.input_realtime_cache) == 0
  assert len(session.output_realtime_cache) == 0

  # Check that artifacts were written to disk
  artifacts_dir = (
      tmp_path
      / "users"
      / "test_user"
      / "sessions"
      / "test_live_session"
      / "artifacts"
  )
  saved_input_files = list(
      artifacts_dir.glob("live_audio_storage_input_audio_*")
  )
  saved_output_files = list(
      artifacts_dir.glob("live_audio_storage_output_audio_*")
  )

  assert len(saved_input_files) == 1
  assert len(saved_output_files) == 1

  # Verify combined output audio payload on disk (version 0)
  output_artifact_dir = saved_output_files[0]
  saved_output_payload = (
      output_artifact_dir / "versions" / "0" / output_artifact_dir.name
  ).read_bytes()
  assert saved_output_payload == output_data_1 + output_data_2


@pytest.mark.asyncio
async def test_async_session_flush_on_interrupted(tmp_path):
  """Test that interruption flushes model output audio while keeping input intact."""
  mock_ws = AsyncMock()
  mock_api_client = Mock()
  mock_api_client.vertexai = False

  artifact_service = FileArtifactService(base_dir=tmp_path)
  cache_manager = AudioCacheManager()

  session = AsyncSession(
      api_client=mock_api_client,
      websocket=mock_ws,
      session_id="test_session_interrupted",
      save_live_blob=True,
      artifact_service=artifact_service,
      audio_cache_manager=cache_manager,
      app_name="app",
      user_id="user",
      agent_name="agent",
  )

  # User caches input audio manually
  cache_manager.cache_audio(
      session, types.Blob(data=b"user_audio", mime_type="audio/pcm"), "input"
  )
  # Model caches output audio
  cache_manager.cache_audio(
      session, types.Blob(data=b"model_audio", mime_type="audio/pcm"), "output"
  )

  assert len(session.input_realtime_cache) == 1
  assert len(session.output_realtime_cache) == 1

  mock_server_message = {
      "serverContent": {
          "interrupted": True,
      }
  }
  mock_ws.recv.return_value = json.dumps(mock_server_message)

  msg = await session._receive()
  assert msg.server_content.interrupted is True

  # Output should be flushed, input should be preserved
  assert len(session.output_realtime_cache) == 0
  assert len(session.input_realtime_cache) == 1
