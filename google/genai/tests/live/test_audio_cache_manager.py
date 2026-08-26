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

import time
from unittest.mock import AsyncMock, Mock

import pytest

from ... import types
from ...audio_cache_manager import AudioCacheManager


class DummyContext:

  def __init__(self, agent_name='test_agent'):
    self.app_name = 'test_app'
    self.user_id = 'test_user'
    self.session_id = 'test_session_123'
    self.invocation_id = 'inv_123'
    self.agent_name = agent_name
    self.input_realtime_cache = []
    self.output_realtime_cache = []
    self.artifact_service = None


@pytest.fixture
def manager():
  return AudioCacheManager()


def test_audio_cache_config_default_values():
  """Test default configuration values in AudioCacheConfig."""
  config = types.AudioCacheConfig()
  assert config.max_cache_size_bytes == 10 * 1024 * 1024  # 10MB
  assert config.max_cache_duration_seconds == 300.0  # 5 minutes
  assert config.auto_flush_threshold == 100


def test_audio_cache_config_custom_values():
  """Test custom configuration values in AudioCacheConfig."""
  config = types.AudioCacheConfig(
      max_cache_size_bytes=5 * 1024 * 1024,
      max_cache_duration_seconds=120.0,
      auto_flush_threshold=50,
  )
  assert config.max_cache_size_bytes == 5 * 1024 * 1024
  assert config.max_cache_duration_seconds == 120.0
  assert config.auto_flush_threshold == 50


@pytest.mark.asyncio
async def test_multiple_audio_caching(manager):
  """Test caching multiple input and output chunks."""
  context = DummyContext()
  for i in range(3):
    manager.cache_audio(
        context,
        types.Blob(data=f'in_{i}'.encode(), mime_type='audio/pcm'),
        'input',
    )
  for i in range(2):
    manager.cache_audio(
        context,
        types.Blob(data=f'out_{i}'.encode(), mime_type='audio/wav'),
        'output',
    )
  assert len(context.input_realtime_cache) == 3
  assert len(context.output_realtime_cache) == 2


@pytest.mark.asyncio
async def test_flush_caches_both(manager):
  """Test flushing both input and output caches."""
  context = DummyContext()
  mock_service = AsyncMock()
  mock_service.save_artifact.return_value = 0
  context.artifact_service = mock_service

  manager.cache_audio(
      context, types.Blob(data=b'input_data', mime_type='audio/pcm'), 'input'
  )
  manager.cache_audio(
      context, types.Blob(data=b'output_data', mime_type='audio/wav'), 'output'
  )

  events = await manager.flush_caches(context)
  assert len(events) == 2
  assert context.input_realtime_cache == []
  assert context.output_realtime_cache == []
  assert mock_service.save_artifact.call_count == 2


@pytest.mark.asyncio
async def test_flush_caches_selective(manager):
  """Test selectively flushing only input cache."""
  context = DummyContext()
  mock_service = AsyncMock()
  mock_service.save_artifact.return_value = 0
  context.artifact_service = mock_service

  manager.cache_audio(
      context, types.Blob(data=b'input_data', mime_type='audio/pcm'), 'input'
  )
  manager.cache_audio(
      context, types.Blob(data=b'output_data', mime_type='audio/wav'), 'output'
  )

  events = await manager.flush_caches(
      context, flush_user_audio=True, flush_model_audio=False
  )
  assert len(events) == 1
  assert context.input_realtime_cache == []
  assert len(context.output_realtime_cache) == 1
  assert mock_service.save_artifact.call_count == 1


@pytest.mark.asyncio
async def test_flush_empty_caches(manager):
  """Test flushing when caches are empty."""
  context = DummyContext()
  mock_service = AsyncMock()
  context.artifact_service = mock_service

  events = await manager.flush_caches(context)
  assert events == []
  mock_service.save_artifact.assert_not_called()


@pytest.mark.asyncio
async def test_flush_without_artifact_service(manager):
  """Test flushing when no artifact service is available."""
  context = DummyContext()
  context.artifact_service = None

  manager.cache_audio(
      context, types.Blob(data=b'input_data', mime_type='audio/pcm'), 'input'
  )
  events = await manager.flush_caches(context)
  assert events == []
  assert len(context.input_realtime_cache) == 1


def test_get_cache_stats_empty(manager):
  """Test getting statistics for empty caches."""
  context = DummyContext()
  stats = manager.get_cache_stats(context)
  expected = {
      'input_chunks': 0,
      'output_chunks': 0,
      'input_bytes': 0,
      'output_bytes': 0,
      'total_chunks': 0,
      'total_bytes': 0,
  }
  assert stats == expected


@pytest.mark.asyncio
async def test_get_cache_stats_with_data(manager):
  """Test getting statistics for caches with data."""
  context = DummyContext()

  input_blob1 = types.Blob(data=b'12345', mime_type='audio/pcm')  # 5 bytes
  input_blob2 = types.Blob(
      data=b'1234567890', mime_type='audio/pcm'
  )  # 10 bytes
  output_blob = types.Blob(data=b'abc', mime_type='audio/wav')  # 3 bytes

  manager.cache_audio(context, input_blob1, 'input')
  manager.cache_audio(context, input_blob2, 'input')
  manager.cache_audio(context, output_blob, 'output')

  stats = manager.get_cache_stats(context)
  expected = {
      'input_chunks': 2,
      'output_chunks': 1,
      'input_bytes': 15,  # 5 + 10
      'output_bytes': 3,
      'total_chunks': 3,
      'total_bytes': 18,  # 15 + 3
  }
  assert stats == expected


@pytest.mark.asyncio
async def test_error_handling_in_flush(manager):
  """Test error handling during cache flush operations."""
  context = DummyContext()
  mock_artifact_service = AsyncMock()
  mock_artifact_service.save_artifact.side_effect = Exception(
      'Artifact service error'
  )
  context.artifact_service = mock_artifact_service

  audio_blob = types.Blob(data=b'test_data', mime_type='audio/pcm')
  manager.cache_audio(context, audio_blob, 'input')

  # Flush should not raise exception but should retain cache
  events = await manager.flush_caches(context)
  assert events == []
  assert len(context.input_realtime_cache) == 1


@pytest.mark.asyncio
async def test_filename_uses_first_chunk_timestamp(manager):
  """Test that the filename timestamp comes from the first audio chunk, not flush time."""
  context = DummyContext()
  mock_artifact_service = AsyncMock()
  mock_artifact_service.save_artifact.return_value = 789
  context.artifact_service = mock_artifact_service

  first_timestamp = 1234567890.123
  second_timestamp = 1234567891.456

  first_entry = types.RealtimeCacheEntry(
      role='user',
      data=types.Blob(data=b'first_chunk', mime_type='audio/pcm'),
      timestamp=first_timestamp,
  )
  second_entry = types.RealtimeCacheEntry(
      role='user',
      data=types.Blob(data=b'second_chunk', mime_type='audio/pcm'),
      timestamp=second_timestamp,
  )

  context.input_realtime_cache.extend([first_entry, second_entry])
  time.sleep(0.01)

  events = await manager.flush_caches(context)
  assert len(events) == 1
  mock_artifact_service.save_artifact.assert_called_once()
  call_args = mock_artifact_service.save_artifact.call_args
  filename = call_args.kwargs['filename']

  expected_timestamp_ms = int(first_timestamp * 1000)
  assert (
      filename
      == f'live_audio_storage_input_audio_{expected_timestamp_ms}.pcm;rate=16000'
  )


@pytest.mark.asyncio
async def test_flush_event_author_for_user_audio(manager):
  """Test that flushed user audio events have 'user' as author."""
  context = DummyContext()
  mock_artifact_service = AsyncMock()
  mock_artifact_service.save_artifact.return_value = 123
  context.artifact_service = mock_artifact_service

  input_blob = types.Blob(data=b'user_audio_data', mime_type='audio/pcm')
  manager.cache_audio(context, input_blob, 'input')

  events = await manager.flush_caches(
      context, flush_user_audio=True, flush_model_audio=False
  )
  assert len(events) == 1
  assert events[0].author == 'user'
  assert events[0].content.role == 'user'


@pytest.mark.asyncio
async def test_flush_event_author_for_model_audio(manager):
  """Test that flushed model audio events have agent name as author, not 'model'."""
  context = DummyContext(agent_name='my_test_agent')
  mock_artifact_service = AsyncMock()
  mock_artifact_service.save_artifact.return_value = 123
  context.artifact_service = mock_artifact_service

  output_blob = types.Blob(data=b'model_audio_data', mime_type='audio/wav')
  manager.cache_audio(context, output_blob, 'output')

  events = await manager.flush_caches(
      context, flush_user_audio=False, flush_model_audio=True
  )
  assert len(events) == 1
  assert events[0].author == 'my_test_agent'
  assert events[0].content.role == 'model'


def test_invalid_cache_type(manager):
  """Test caching with invalid cache type raises ValueError."""
  context = DummyContext()
  blob = types.Blob(data=b'test', mime_type='audio/pcm')
  with pytest.raises(
      ValueError, match="cache_type must be either 'input' or 'output'"
  ):
    manager.cache_audio(context, blob, 'invalid_type')


def test_non_bytes_audio_data_raises(manager):
  """Test caching non-bytes audio data raises ValueError."""
  context = DummyContext()
  blob = types.Blob(data=None, mime_type='audio/pcm')
  with pytest.raises(ValueError, match='Audio blobs must contain byte data.'):
    manager.cache_audio(context, blob, 'input')


@pytest.mark.asyncio
async def test_output_audio_mime_type_defaults_to_24000_rate(manager):
  """Test that flushed model output audio defaults to rate=24000 if not specified."""
  context = DummyContext(agent_name='gemini_agent')
  mock_artifact_service = AsyncMock()
  mock_artifact_service.save_artifact.return_value = 1
  context.artifact_service = mock_artifact_service

  output_blob = types.Blob(data=b'model_audio_pcm_bytes', mime_type='audio/pcm')
  manager.cache_audio(context, output_blob, 'output')

  events = await manager.flush_caches(
      context, flush_user_audio=False, flush_model_audio=True
  )
  assert len(events) == 1
  mock_artifact_service.save_artifact.assert_called_once()
  saved_artifact = mock_artifact_service.save_artifact.call_args.kwargs[
      'artifact'
  ]
  assert saved_artifact.inline_data.mime_type == 'audio/pcm;rate=24000'
  assert (
      events[0].content.parts[0].file_data.mime_type == 'audio/pcm;rate=24000'
  )


@pytest.mark.asyncio
async def test_input_audio_mime_type_defaults_to_16000_rate(manager):
  """Test that flushed user input audio defaults to rate=16000 if not specified."""
  context = DummyContext()
  mock_artifact_service = AsyncMock()
  mock_artifact_service.save_artifact.return_value = 1
  context.artifact_service = mock_artifact_service

  input_blob = types.Blob(data=b'user_audio_pcm_bytes', mime_type='audio/pcm')
  manager.cache_audio(context, input_blob, 'input')

  events = await manager.flush_caches(
      context, flush_user_audio=True, flush_model_audio=False
  )
  assert len(events) == 1
  mock_artifact_service.save_artifact.assert_called_once()
  saved_artifact = mock_artifact_service.save_artifact.call_args.kwargs[
      'artifact'
  ]
  assert saved_artifact.inline_data.mime_type == 'audio/pcm;rate=16000'
  assert (
      events[0].content.parts[0].file_data.mime_type == 'audio/pcm;rate=16000'
  )
