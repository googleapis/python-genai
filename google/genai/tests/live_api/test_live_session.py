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
#

"""API-mode integration tests for the live (bidirectional WebSocket) module.

These run only against the real backend. The live module opens a WebSocket and
never goes through BaseApiClient._request, so ReplayApiClient cannot record or
replay it -- see go/genai-sdk:integration-testing. In --mode=api the `client`
fixture yields a client that calls the real API and writes no replay, which is
exactly what these need.

They are deliberately not part of tests/shared: a live session is multi-step and
cannot be expressed as the request/response table that corpus is built on, and
emitting a _test_table.json for it would make the other SDKs' harnesses try to
execute a case they have no implementation for.
"""

import asyncio

import pytest

from .. import pytest_helper
from ... import types

pytestmark = pytest.mark.skipif(
    f"not ({pytest_helper.is_api_mode})",
    reason=(
        'Live tests open a real WebSocket to the backend; there is no replay'
        ' support for WebSocket traffic, so they only run in --mode=api.'
    ),
)

pytest_plugins = ('pytest_asyncio',)

# Live models are backend-specific: gemini-3.1-flash-live-preview is served only
# on the Gemini API, and gemini-live-2.5-flash-native-audio only on Vertex, and
# there only regionally -- see the location_override fixture in this package's
# conftest. Both are audio-native and reject a TEXT response modality outright
# ("The requested combination of response modalities (TEXT) is not supported by
# the model"), so these tests request AUDIO and turn on output transcription to
# get an assertable text signal.
LIVE_MODELS = {
    False: 'gemini-3.1-flash-live-preview',
    True: 'gemini-live-2.5-flash-native-audio',
}

# A live turn is an open-ended stream with no built-in deadline. Without this
# bound a wedged receive would hang the nightly rather than fail it.
_TURN_TIMEOUT_SECONDS = 90


def _base_config(**overrides) -> types.LiveConnectConfig:
  config = {
      'response_modalities': ['AUDIO'],
      'output_audio_transcription': types.AudioTranscriptionConfig(),
  }
  config.update(overrides)
  return types.LiveConnectConfig(**config)


class _Turn:
  """Everything a single model turn produced."""

  def __init__(self):
    self.audio_bytes = 0
    self.transcript = ''
    self.tool_calls = []


async def _receive_turn(session) -> _Turn:
  """Drains exactly one model turn, or the tool call that interrupts it."""
  turn = _Turn()
  transcript_parts = []

  async def _drain():
    async for message in session.receive():
      if message.tool_call and message.tool_call.function_calls:
        turn.tool_calls.extend(message.tool_call.function_calls)
        return
      server_content = message.server_content
      if not server_content:
        continue
      if (
          server_content.output_transcription
          and server_content.output_transcription.text
      ):
        transcript_parts.append(server_content.output_transcription.text)
      if server_content.model_turn:
        for part in server_content.model_turn.parts or []:
          if part.inline_data and part.inline_data.data:
            turn.audio_bytes += len(part.inline_data.data)
      if server_content.turn_complete:
        return

  await asyncio.wait_for(_drain(), timeout=_TURN_TIMEOUT_SECONDS)
  turn.transcript = ''.join(transcript_parts)
  return turn


def _skip_if_quota_exhausted(error: Exception) -> None:
  """Mirrors pytest_helper's api-mode 429 handling.

  A quota response still proves the SDK built the request, authenticated,
  reached the live endpoint and parsed the error, so it is not a regression.
  See go/genai-sdk:integration-testing section 4.4.
  """
  if getattr(error, 'code', None) == 429:
    pytest.skip(f'Resource exhausted (429). Skipping instead of failing: {error}')


async def _say(session, text: str) -> None:
  await session.send_client_content(
      turns=types.Content(role='user', parts=[types.Part(text=text)]),
      turn_complete=True,
  )


@pytest.mark.parametrize('use_vertex', [False, True])
@pytest.mark.asyncio
async def test_text_input(client, use_vertex):
  """A single text turn produces audio output and a matching transcription."""
  try:
    async with client.aio.live.connect(
        model=LIVE_MODELS[use_vertex], config=_base_config()
    ) as session:
      await _say(session, 'Say hello.')
      turn = await _receive_turn(session)

      assert turn.audio_bytes > 0, 'expected audio output from the model'
      assert turn.transcript.strip(), 'expected an output transcription'
  except Exception as e:  # pylint: disable=broad-except
    _skip_if_quota_exhausted(e)
    raise


@pytest.mark.parametrize('use_vertex', [False, True])
@pytest.mark.asyncio
async def test_multi_turn(client, use_vertex):
  """A second turn in the same session can see the first turn's context."""
  try:
    async with client.aio.live.connect(
        model=LIVE_MODELS[use_vertex], config=_base_config()
    ) as session:
      await _say(session, 'Remember the number 42. Just acknowledge it.')
      first = await _receive_turn(session)
      assert first.transcript.strip(), 'expected a response to the first turn'

      await _say(session, 'What number did I ask you to remember?')
      second = await _receive_turn(session)

      assert second.audio_bytes > 0, 'expected audio output on the second turn'
      assert '42' in second.transcript, (
          'the second turn should recall context from the first; transcript was'
          f' {second.transcript!r}'
      )
  except Exception as e:  # pylint: disable=broad-except
    _skip_if_quota_exhausted(e)
    raise


@pytest.mark.parametrize('use_vertex', [False, True])
@pytest.mark.asyncio
async def test_function_calling(client, use_vertex):
  """The model requests a declared tool, and the session accepts its result."""
  turn_on_the_lights = types.FunctionDeclaration(
      name='turn_on_the_lights',
      description='Turns the lights on in the room.',
      parameters=types.Schema(type=types.Type.OBJECT, properties={}),
  )
  config = _base_config(
      tools=[types.Tool(function_declarations=[turn_on_the_lights])]
  )

  try:
    async with client.aio.live.connect(
        model=LIVE_MODELS[use_vertex], config=config
    ) as session:
      await _say(session, 'Please turn on the lights.')
      turn = await _receive_turn(session)

      assert turn.tool_calls, 'expected the model to request the tool'
      call = turn.tool_calls[0]
      assert call.name == 'turn_on_the_lights'
      assert call.id, 'a Gemini API tool call must carry an id'

      await session.send_tool_response(
          function_responses=[
              types.FunctionResponse(
                  id=call.id, name=call.name, response={'result': 'ok'}
              )
          ]
      )
      follow_up = await _receive_turn(session)
      if not use_vertex:
        # Vertex accepts the tool result and completes the turn, but emits an
        # empty transcription and no audio for it, so only the Gemini API can be
        # asserted on content here. Confirmed at the raw protocol level: the
        # follow-up carries outputTranscription with empty text, then
        # generationComplete and turnComplete.
        assert follow_up.transcript.strip(), (
            'expected the model to respond after the tool result'
        )
  except Exception as e:  # pylint: disable=broad-except
    _skip_if_quota_exhausted(e)
    raise


@pytest.mark.parametrize('use_vertex', [False])
@pytest.mark.asyncio
async def test_send_tool_response_without_id_raises(client, use_vertex):
  """The Gemini API backend requires an id on every FunctionResponse.

  Gemini API only: live.py:409 puts this validation in the non-vertexai branch
  of send_tool_response, so Vertex accepts an id-less FunctionResponse.
  """
  try:
    async with client.aio.live.connect(
        model=LIVE_MODELS[use_vertex], config=_base_config()
    ) as session:
      with pytest.raises(ValueError, match='must have an `id` field'):
        await session.send_tool_response(
            function_responses=[
                types.FunctionResponse(
                    name='turn_on_the_lights', response={'result': 'ok'}
                )
            ]
        )
  except Exception as e:  # pylint: disable=broad-except
    _skip_if_quota_exhausted(e)
    raise
