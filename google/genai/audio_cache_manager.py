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

from __future__ import annotations

import logging
import time
from typing import Any, Optional
import uuid

from pydantic import Field

from . import _common
from . import types

logger = logging.getLogger(__name__)


def _require_audio_data(blob: Optional[types.Blob]) -> bytes:
  if blob is None:
    raise ValueError('Audio blob cannot be None.')
  data = blob.data
  if not isinstance(data, bytes):
    raise ValueError('Audio blobs must contain byte data.')
  return data


def require_agent_name(context: Any) -> str:
  if hasattr(context, 'agent_name') and context.agent_name:
    return str(context.agent_name)
  if (
      hasattr(context, 'agent')
      and hasattr(context.agent, 'name')
      and context.agent.name
  ):
    return str(context.agent.name)
  return 'agent'


class Event(_common.BaseModel):
  """Representation of an event occurring in a session."""

  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  invocation_id: Optional[str] = None
  author: str = 'user'
  content: Optional[types.Content] = None
  timestamp: float = Field(default_factory=time.time)


class AudioCacheManager:
  """Manages audio caching and flushing for live streaming flows."""

  def __init__(self, config: Optional[types.AudioCacheConfig] = None) -> None:
    """Initialize the audio cache manager.

    Args:
      config: Configuration for audio caching behavior.
    """
    self.config = config or types.AudioCacheConfig()

  def cache_audio(
      self,
      invocation_context: Any,
      audio_blob: types.Blob,
      cache_type: str,
  ) -> None:
    """Cache incoming user or outgoing model audio data.

    Args:
      invocation_context: The current invocation context.
      audio_blob: The audio data to cache.
      cache_type: Type of audio to cache, either 'input' or 'output'.

    Raises:
      ValueError: If cache_type is not 'input' or 'output'.
    """
    audio_data = _require_audio_data(audio_blob)
    if cache_type == 'input':
      if getattr(invocation_context, 'input_realtime_cache', None) is None:
        invocation_context.input_realtime_cache = []
      cache = invocation_context.input_realtime_cache
      role = 'user'
    elif cache_type == 'output':
      if getattr(invocation_context, 'output_realtime_cache', None) is None:
        invocation_context.output_realtime_cache = []
      cache = invocation_context.output_realtime_cache
      role = 'model'
    else:
      raise ValueError("cache_type must be either 'input' or 'output'")

    audio_entry = types.RealtimeCacheEntry(
        role=role, data=audio_blob, timestamp=time.time()
    )
    cache.append(audio_entry)

    logger.debug(
        'Cached %s audio chunk: %d bytes, cache size: %d',
        cache_type,
        len(audio_data),
        len(cache),
    )

  async def flush_caches(
      self,
      invocation_context: Any,
      flush_user_audio: bool = True,
      flush_model_audio: bool = True,
  ) -> list[Event]:
    """Flush audio caches to artifact services.

    Args:
      invocation_context: The invocation context containing audio caches.
      flush_user_audio: Whether to flush the input (user) audio cache.
      flush_model_audio: Whether to flush the output (model) audio cache.

    Returns:
      A list of Event objects created from the flushed caches.
    """
    flushed_events: list[Event] = []
    if flush_user_audio and getattr(
        invocation_context, 'input_realtime_cache', None
    ):
      audio_event = await self._flush_cache_to_services(
          invocation_context,
          invocation_context.input_realtime_cache,
          'input_audio',
      )
      if audio_event:
        flushed_events.append(audio_event)
        invocation_context.input_realtime_cache = []

    if flush_model_audio and getattr(
        invocation_context, 'output_realtime_cache', None
    ):
      logger.debug('Flushed output audio cache')
      audio_event = await self._flush_cache_to_services(
          invocation_context,
          invocation_context.output_realtime_cache,
          'output_audio',
      )
      if audio_event:
        flushed_events.append(audio_event)
        invocation_context.output_realtime_cache = []

    return flushed_events

  async def _flush_cache_to_services(
      self,
      invocation_context: Any,
      audio_cache: list[types.RealtimeCacheEntry],
      cache_type: str,
  ) -> Optional[Event]:
    """Flush a list of audio cache entries to artifact services.

    Args:
      invocation_context: The invocation context.
      audio_cache: The audio cache to flush.
      cache_type: Type identifier for the cache ('input_audio' or
        'output_audio').

    Returns:
      The created Event if the cache was successfully flushed, None otherwise.
    """
    if (
        not getattr(invocation_context, 'artifact_service', None)
        or not audio_cache
    ):
      logger.debug('Skipping cache flush: no artifact service or empty cache')
      return None

    try:
      first_entry = audio_cache[0]
      first_blob = first_entry.data
      mime_type = (first_blob.mime_type if first_blob else None) or 'audio/pcm'
      if 'rate=' not in mime_type:
        if cache_type == 'output_audio':
          mime_type = f'{mime_type};rate=24000'
        elif cache_type == 'input_audio':
          mime_type = f'{mime_type};rate=16000'

      combined_audio_data = b''.join(
          (entry.data.data if entry.data and entry.data.data else b'')
          for entry in audio_cache
      )

      # Generate filename with timestamp from first audio chunk (when recording started)
      first_ts = (
          first_entry.timestamp
          if first_entry.timestamp is not None
          else time.time()
      )
      timestamp = int(first_ts * 1000)  # milliseconds
      filename = f"live_audio_storage_{cache_type}_{timestamp}.{mime_type.split('/')[-1]}"

      # Save to artifact service
      combined_audio_part = types.Part(
          inline_data=types.Blob(data=combined_audio_data, mime_type=mime_type)
      )

      app_name = getattr(invocation_context, 'app_name', 'app')
      user_id = getattr(invocation_context, 'user_id', 'user')
      session_id = getattr(
          getattr(invocation_context, 'session', None), 'id', None
      ) or getattr(invocation_context, 'session_id', 'default_session')

      revision_id = await invocation_context.artifact_service.save_artifact(
          app_name=app_name,
          user_id=user_id,
          session_id=session_id,
          filename=filename,
          artifact=combined_audio_part,
      )

      artifact_ref = f'artifact://{app_name}/{user_id}/{session_id}/_live/{filename}#{revision_id}'

      author = (
          require_agent_name(invocation_context)
          if audio_cache[0].role == 'model'
          else (audio_cache[0].role or 'user')
      )
      audio_event = Event(
          invocation_id=getattr(invocation_context, 'invocation_id', None),
          author=author,
          content=types.Content(
              role=audio_cache[0].role,
              parts=[
                  types.Part(
                      file_data=types.FileData(
                          file_uri=artifact_ref, mime_type=mime_type
                      )
                  )
              ],
          ),
          timestamp=audio_cache[0].timestamp or time.time(),
      )

      logger.debug(
          'Successfully flushed %s cache: %d chunks, %d bytes, saved as %s',
          cache_type,
          len(audio_cache),
          len(combined_audio_data),
          filename,
      )

      if hasattr(invocation_context, 'events') and isinstance(
          invocation_context.events, list
      ):
        invocation_context.events.append(audio_event)
      session_obj = getattr(invocation_context, 'session', None)
      if (
          session_obj
          and hasattr(session_obj, 'events')
          and isinstance(session_obj.events, list)
      ):
        session_obj.events.append(audio_event)

      return audio_event

    except Exception as e:
      logger.error('Failed to flush %s cache: %s', cache_type, e)
      return None

  def get_cache_stats(self, invocation_context: Any) -> dict[str, int]:
    """Get statistics about current cache state.

    Args:
      invocation_context: The invocation context.

    Returns:
      Dictionary containing cache statistics.
    """
    input_chunks = (
        getattr(invocation_context, 'input_realtime_cache', None) or []
    )
    output_chunks = (
        getattr(invocation_context, 'output_realtime_cache', None) or []
    )

    input_count = len(input_chunks)
    output_count = len(output_chunks)

    input_bytes = sum(
        len(_require_audio_data(entry.data)) for entry in input_chunks
    )
    output_bytes = sum(
        len(_require_audio_data(entry.data)) for entry in output_chunks
    )

    return {
        'input_chunks': input_count,
        'output_chunks': output_count,
        'input_bytes': input_bytes,
        'output_bytes': output_bytes,
        'total_chunks': input_count + output_count,
        'total_bytes': input_bytes + output_bytes,
    }
