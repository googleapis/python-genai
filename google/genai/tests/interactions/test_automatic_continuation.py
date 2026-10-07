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

"""Tests for automatic_continuation in Interactions API."""

import json
import os
from typing import Any
from unittest import mock

import httpx
import pytest

from ... import client as client_lib
from ..._gaos import google_genai as gaos_google_genai
from ..._gaos import interactions as gaos_interactions
from ..._gaos.lib import compat_errors
from ..._gaos.models import createinteraction as create_interaction_models
from ..._gaos.types import interactions as interaction_types
from ..._gaos.utils import eventstreaming


pytest_plugins = ("pytest_asyncio",)


def _make_sync_stream(
    events: list[Any],
    exc: Exception | None = None,
) -> eventstreaming.Stream[Any]:
  stream = eventstreaming.Stream.__new__(eventstreaming.Stream)
  stream.response = mock.MagicMock(spec=httpx.Response)
  stream.client_ref = None
  stream._closed = False

  def _gen():
    try:
      for ev in events:
        yield ev
      if exc is not None:
        raise exc
    finally:
      stream.response.close()

  stream.generator = _gen()
  return stream


def _make_async_stream(
    events: list[Any],
    exc: Exception | None = None,
) -> eventstreaming.AsyncStream[Any]:
  stream = eventstreaming.AsyncStream.__new__(eventstreaming.AsyncStream)
  stream.response = mock.MagicMock(spec=httpx.Response)
  stream.response.aclose = mock.AsyncMock()
  stream.client_ref = None
  stream._closed = False

  async def _close():
    stream._closed = True
    await stream.response.aclose()

  stream.close = _close

  async def _agen():
    try:
      for ev in events:
        yield ev
      if exc is not None:
        raise exc
    finally:
      await stream.response.aclose()

  stream.generator = _agen()
  return stream


def _created_event(interaction_id: str = "int_123") -> dict[str, Any]:
  return {
      "event_type": "interaction.created",
      "interaction": {
          "id": interaction_id,
          "status": "in_progress",
      },
  }


def _text_delta_event(text: str, index: int = 0) -> dict[str, Any]:
  return {
      "event_type": "step.delta",
      "index": index,
      "delta": {"type": "text", "text": text},
  }


def _completed_event(
    *,
    status: str = "completed",
    continuation_token: str | None = None,
    output_tokens: int = 10,
    thought_tokens: int = 0,
    interaction_id: str = "int_123",
) -> dict[str, Any]:
  interaction: dict[str, Any] = {
      "id": interaction_id,
      "status": status,
      "usage": {
          "total_output_tokens": output_tokens,
          "total_thought_tokens": thought_tokens,
          "total_tokens": output_tokens + thought_tokens,
      },
  }
  if continuation_token is not None:
    interaction["continuation_token"] = continuation_token
  return {
      "event_type": "interaction.completed",
      "interaction": interaction,
  }


def test_stream_automatic_continuation_with_request_object():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Part 1 "),
      _completed_event(
          status="continuation_required",
          continuation_token="tok_req_1",
          output_tokens=20,
      ),
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("Part 2"),
      _completed_event(
          status="completed",
          output_tokens=20,
      ),
  ]

  req = create_interaction_models.CreateInteractionRequest(
      body=interaction_types.CreateModelInteraction(
          model="gemini-2.5-pro",
          input="Hello",
          stream=True,
      )
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(hop1_events),
          _make_sync_stream(hop2_events),
      ],
  ) as mock_create:
    stream = client.interactions.create(
        request=req,
        automatic_continuation=True,
    )
    received = list(stream)

  assert received == hop1_events + hop2_events
  assert mock_create.call_count == 2
  second_req = mock_create.call_args_list[1].kwargs["request"]
  assert second_req.body.continuation_token == "tok_req_1"
  assert req.body.continuation_token is None


def test_stream_automatic_continuation_close_on_second_hop():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _completed_event(
          status="continuation_required",
          continuation_token="tok_hop1",
          output_tokens=10,
      ),
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("chunk 1"),
      _text_delta_event("chunk 2"),
      _completed_event(status="completed", output_tokens=10),
  ]
  hop1_stream = _make_sync_stream(hop1_events)
  hop2_stream = _make_sync_stream(hop2_events)

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1_stream, hop2_stream],
  ):
    with client.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        stream=True,
        automatic_continuation=True,
    ) as stream:
      # Consume hop 1 (2 events) + first event of hop 2
      _ = next(stream)
      _ = next(stream)
      _ = next(stream)
      # Exit context manager early on hop 2

  hop1_stream.response.close.assert_called()
  hop2_stream.response.close.assert_called()


@pytest.mark.asyncio
async def test_async_stream_automatic_continuation_close_on_second_hop():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _completed_event(
          status="continuation_required",
          continuation_token="tok_hop1",
          output_tokens=10,
      ),
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("chunk 1"),
      _text_delta_event("chunk 2"),
      _completed_event(status="completed", output_tokens=10),
  ]
  hop1_stream = _make_async_stream(hop1_events)
  hop2_stream = _make_async_stream(hop2_events)

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(side_effect=[hop1_stream, hop2_stream]),
  ):
    async with await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        stream=True,
        automatic_continuation=True,
    ) as stream:
      _ = await stream.__anext__()
      _ = await stream.__anext__()
      _ = await stream.__anext__()

  hop1_stream.response.aclose.assert_awaited()
  hop2_stream.response.aclose.assert_awaited()


@pytest.mark.asyncio
async def test_async_stream_automatic_continuation_three_hops():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Hop 1 "),
      _completed_event(
          status="continuation_required",
          continuation_token="tok_1",
          output_tokens=50,
      ),
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("Hop 2 "),
      _completed_event(
          status="continuation_required",
          continuation_token="tok_2",
          output_tokens=60,
      ),
  ]
  hop3_events = [
      _created_event(),
      _text_delta_event("Hop 3"),
      _completed_event(
          status="completed",
          output_tokens=30,
      ),
  ]

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[
              _make_async_stream(hop1_events),
              _make_async_stream(hop2_events),
              _make_async_stream(hop3_events),
          ]
      ),
  ) as mock_create:
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Write a long story",
        stream=True,
        automatic_continuation=True,
    )
    received = [ev async for ev in stream]

  assert received == hop1_events + hop2_events + hop3_events
  assert mock_create.call_count == 3
  assert "continuation_token" not in mock_create.call_args_list[0].kwargs
  assert mock_create.call_args_list[1].kwargs["continuation_token"] == "tok_1"
  assert mock_create.call_args_list[2].kwargs["continuation_token"] == "tok_2"


def test_automatic_continuation_false_with_background_raises_value_error():
  client = client_lib.Client(api_key="test-key")
  with pytest.raises(
      ValueError,
      match="automatic_continuation=False cannot be used with background=True",
  ):
    client.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        background=True,
        automatic_continuation=False,
    )

  with pytest.raises(
      ValueError,
      match="automatic_continuation=False cannot be used with background=True",
  ):
    client.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        background=True,
        stream=True,
        automatic_continuation=False,
    )

  with pytest.raises(
      ValueError,
      match="automatic_continuation=False cannot be used with background=True",
  ):
    client.interactions.create(
        request={"body": {"model": "gemini-2.5-pro", "background": True}},
        automatic_continuation=False,
    )


@pytest.mark.asyncio
async def test_async_automatic_continuation_false_with_background_raises_value_error():
  client = client_lib.Client(api_key="test-key")
  with pytest.raises(
      ValueError,
      match="automatic_continuation=False cannot be used with background=True",
  ):
    await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        background=True,
        automatic_continuation=False,
    )

  with pytest.raises(
      ValueError,
      match="automatic_continuation=False cannot be used with background=True",
  ):
    await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        background=True,
        stream=True,
        automatic_continuation=False,
    )


def test_automatic_continuation_true_with_store_false_unary_raises_value_error():
  client = client_lib.Client(api_key="test-key")
  with pytest.raises(
      ValueError,
      match=(
          "automatic_continuation=True cannot be used with store=False in unary"
          " mode"
      ),
  ):
    client.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        store=False,
        automatic_continuation=True,
    )

  with pytest.raises(
      ValueError,
      match=(
          "automatic_continuation=True cannot be used with store=False in unary"
          " mode"
      ),
  ):
    client.interactions.create(
        request={"body": {"model": "gemini-2.5-pro", "store": False}},
        automatic_continuation=True,
    )


@pytest.mark.asyncio
async def test_async_automatic_continuation_true_with_store_false_unary_raises_value_error():
  client = client_lib.Client(api_key="test-key")
  with pytest.raises(
      ValueError,
      match=(
          "automatic_continuation=True cannot be used with store=False in unary"
          " mode"
      ),
  ):
    await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        store=False,
        automatic_continuation=True,
    )

  with pytest.raises(
      ValueError,
      match=(
          "automatic_continuation=True cannot be used with store=False in unary"
          " mode"
      ),
  ):
    await client.aio.interactions.create(
        request={"body": {"model": "gemini-2.5-pro", "store": False}},
        automatic_continuation=True,
    )


def test_output_text_skips_thought_steps_but_stops_at_tool_steps():
  client = client_lib.Client(api_key="test-key")
  interaction = interaction_types.Interaction(
      id="int_tool_thought",
      status="completed",
      steps=[
          interaction_types.ThoughtStep(type="thought", signature="sig_0"),
          interaction_types.ModelOutputStep(
              type="model_output",
              content=[
                  interaction_types.TextContent(
                      type="text", text="Pre-tool chatter. "
                  )
              ],
          ),
          interaction_types.FunctionCallStep(
              type="function_call",
              id="call_1",
              name="search",
              arguments={"q": "test"},
          ),
          interaction_types.FunctionResultStep(
              type="function_result",
              call_id="call_1",
              result="found",
          ),
          interaction_types.ThoughtStep(type="thought", signature="sig_1"),
          interaction_types.ModelOutputStep(
              type="model_output",
              content=[
                  interaction_types.TextContent(
                      type="text", text="Post-tool hop 1. "
                  )
              ],
          ),
          interaction_types.ThoughtStep(type="thought", signature="sig_2"),
          interaction_types.ModelOutputStep(
              type="model_output",
              content=[
                  interaction_types.TextContent(
                      type="text", text="Post-tool hop 2."
                  )
              ],
          ),
      ],
  )
  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      return_value=interaction,
  ):
    res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Search and summarize",
    )
  assert res.output_text == "Post-tool hop 1. Post-tool hop 2."


def _unary_hop(
    *,
    status: str,
    text: str,
    continuation_token: str | None = None,
    input_tokens: int = 10,
    output_tokens: int = 20,
    thought_tokens: int = 0,
    created: str = "2026-01-01T00:00:00Z",
    updated: str = "2026-01-01T00:00:05Z",
) -> interaction_types.Interaction:
  return interaction_types.Interaction(
      id="int_unary_123",
      status=status,
      continuation_token=continuation_token,
      created=created,
      updated=updated,
      steps=[
          interaction_types.ModelOutputStep(
              type="model_output",
              content=[interaction_types.TextContent(type="text", text=text)],
          )
      ],
      usage=interaction_types.Usage(
          total_input_tokens=input_tokens,
          total_output_tokens=output_tokens,
          total_thought_tokens=thought_tokens,
          total_tokens=input_tokens + output_tokens + thought_tokens,
      ),
  )


def test_unary_automatic_continuation_with_request_object():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      status="continuation_required",
      text="Part A ",
      continuation_token="tok_req_1",
      output_tokens=40,
  )
  hop2 = _unary_hop(
      status="completed",
      text="Part A Part B",
      continuation_token=None,
      output_tokens=70,
  )

  req = create_interaction_models.CreateInteractionRequest(
      body=interaction_types.CreateModelInteraction(
          model="gemini-2.5-pro",
          input="Hello",
      )
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, hop2],
  ) as mock_create:
    res = client.interactions.create(
        request=req,
        automatic_continuation=True,
    )

  assert mock_create.call_count == 2
  second_req = mock_create.call_args_list[1].kwargs["request"]
  assert second_req.body.continuation_token == "tok_req_1"
  assert req.body.continuation_token is None
  assert res.status == "completed"
  assert res.output_text == "Part A Part B"


@pytest.mark.asyncio
async def test_async_unary_automatic_continuation_three_hops():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      status="continuation_required",
      text="Async 1 ",
      continuation_token="tok_1",
      output_tokens=50,
  )
  hop2 = _unary_hop(
      status="continuation_required",
      text="Async 1 Async 2 ",
      continuation_token="tok_2",
      output_tokens=110,
  )
  hop3 = _unary_hop(
      status="completed",
      text="Async 1 Async 2 Async 3",
      continuation_token=None,
      output_tokens=140,
  )

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(side_effect=[hop1, hop2, hop3]),
  ) as mock_create:
    res = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Write a long story",
        automatic_continuation=True,
    )

  assert mock_create.call_count == 3
  assert "continuation_token" not in mock_create.call_args_list[0].kwargs
  assert mock_create.call_args_list[1].kwargs["continuation_token"] == "tok_1"
  assert mock_create.call_args_list[2].kwargs["continuation_token"] == "tok_2"
  assert res.status == "completed"
  assert res.output_text == "Async 1 Async 2 Async 3"


def test_unary_automatic_continuation_stops_when_token_missing_or_empty():
  client = client_lib.Client(api_key="test-key")
  hop_no_token = _unary_hop(
      status="continuation_required",
      text="Continuation required without token",
      continuation_token=None,
  )
  hop_empty_token = _unary_hop(
      status="continuation_required",
      text="Continuation required with empty token",
      continuation_token="",
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop_no_token, hop_empty_token],
  ) as mock_create:
    res1 = client.interactions.create(
        model="gemini-2.5-pro",
        input="Test 1",
        automatic_continuation=True,
    )
    res2 = client.interactions.create(
        model="gemini-2.5-pro",
        input="Test 2",
        automatic_continuation=True,
    )

  assert mock_create.call_count == 2
  assert res1.status == "continuation_required"
  assert res1.output_text == "Continuation required without token"
  assert res2.status == "continuation_required"
  assert res2.output_text == "Continuation required with empty token"


def test_unary_automatic_continuation_with_initial_user_continuation_token():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      status="continuation_required",
      text="Resumed hop 1 ",
      continuation_token="tok_from_hop1",
  )
  hop2 = _unary_hop(
      status="completed",
      text="Resumed hop 1 Resumed hop 2",
      continuation_token=None,
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, hop2],
  ) as mock_create:
    res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Resume",
        continuation_token="user_initial_tok",
        automatic_continuation=True,
    )

  assert mock_create.call_count == 2
  assert (
      mock_create.call_args_list[0].kwargs["continuation_token"]
      == "user_initial_tok"
  )
  assert (
      mock_create.call_args_list[1].kwargs["continuation_token"]
      == "tok_from_hop1"
  )
  assert res.status == "completed"
  assert res.output_text == "Resumed hop 1 Resumed hop 2"


def test_stream_automatic_continuation_stops_on_requires_action_or_missing_token():
  client = client_lib.Client(api_key="test-key")
  requires_action_events = [
      _created_event(),
      _text_delta_event("Calling tool..."),
      _completed_event(
          status="requires_action",
          continuation_token="tok_should_not_continue",
          output_tokens=20,
      ),
  ]
  missing_token_events = [
      _created_event(),
      _text_delta_event("Partial..."),
      _completed_event(
          status="continuation_required",
          continuation_token=None,
          output_tokens=20,
      ),
  ]

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(requires_action_events),
          _make_sync_stream(missing_token_events),
      ],
  ) as mock_create:
    stream1 = client.interactions.create(
        model="gemini-2.5-pro",
        input="Tool call",
        stream=True,
        automatic_continuation=True,
    )
    events1 = list(stream1)

    stream2 = client.interactions.create(
        model="gemini-2.5-pro",
        input="Missing token",
        stream=True,
        automatic_continuation=True,
    )
    events2 = list(stream2)

  assert mock_create.call_count == 2
  assert events1 == requires_action_events
  assert events2 == missing_token_events


def test_stream_automatic_continuation_uses_checkpoint_token_from_status_update():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Chunk 1 "),
      {
          "event_type": "interaction.status_update",
          "status": "in_progress",
          "continuation_token": "tok_checkpoint_1",
      },
      _completed_event(
          status="continuation_required",
          continuation_token=None,
          output_tokens=40,
      ),
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("Chunk 2"),
      _completed_event(
          status="completed",
          continuation_token=None,
          output_tokens=20,
      ),
  ]

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(hop1_events),
          _make_sync_stream(hop2_events),
      ],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Checkpoint test",
        stream=True,
        automatic_continuation=True,
    )
    received = list(stream)

  assert received == hop1_events + hop2_events
  assert mock_create.call_count == 2
  assert (
      mock_create.call_args_list[1].kwargs["continuation_token"]
      == "tok_checkpoint_1"
  )


def test_stream_automatic_continuation_resumes_on_dead_connection_with_last_token():
  client = client_lib.Client(api_key="test-key")
  hop1_events_before_drop = [
      _created_event(),
      _text_delta_event("Chunk 1 "),
      {
          "event_type": "interaction.status_update",
          "status": "in_progress",
          "continuation_token": "tok_checkpoint_1",
      },
      _text_delta_event("Chunk 2 "),
      {
          "event_type": "interaction.status_update",
          "status": "in_progress",
          "continuation_token": "tok_checkpoint_2",
      },
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("Chunk 3"),
      _completed_event(
          status="completed",
          continuation_token=None,
          output_tokens=30,
      ),
  ]

  # 1. Dead connection mid-stream (transport error or premature EOF) after
  # checkpoint tokens -> reconnects and sends the last continuation_token.
  for disconnect_exc in (
      httpx.RemoteProtocolError("peer closed connection"),
      httpx.ReadTimeout("stream read timed out"),
      None,
  ):
    with mock.patch.object(
        gaos_interactions.Interactions,
        "create",
        side_effect=[
            _make_sync_stream(hop1_events_before_drop, exc=disconnect_exc),
            _make_sync_stream(hop2_events),
        ],
    ) as mock_create:
      stream = client.interactions.create(
          model="gemini-2.5-pro",
          input="Dead connection resume test",
          stream=True,
          automatic_continuation=True,
      )
      received = list(stream)

    assert received == hop1_events_before_drop + hop2_events
    assert mock_create.call_count == 2
    assert "continuation_token" not in mock_create.call_args_list[0].kwargs
    assert (
        mock_create.call_args_list[1].kwargs["continuation_token"]
        == "tok_checkpoint_2"
    )

  # 2. Dead connection before any continuation_token in the hop -> raises error.
  events_without_token = [
      _created_event(),
      _text_delta_event("Early chunk"),
  ]
  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(
              events_without_token,
              exc=httpx.RemoteProtocolError("early disconnect"),
          ),
      ],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Early dead connection test",
        stream=True,
        automatic_continuation=True,
    )
    with pytest.raises(compat_errors.APIConnectionError):
      _ = list(stream)
    assert mock_create.call_count == 1

  # 3. Dead connection when automatic_continuation=False -> raises even if
  # checkpoint token was received.
  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(
              hop1_events_before_drop,
              exc=httpx.RemoteProtocolError("disconnect with auto_continue=False"),
          ),
      ],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="No auto-continue dead connection test",
        stream=True,
        automatic_continuation=False,
    )
    with pytest.raises(compat_errors.APIConnectionError):
      _ = list(stream)
    assert mock_create.call_count == 1

  # 4. Consecutive failure on resumed hop before a new token is emitted ->
  # raises without infinite looping.
  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(
              hop1_events_before_drop,
              exc=httpx.RemoteProtocolError("hop 1 disconnect"),
          ),
          _make_sync_stream(
              events_without_token,
              exc=httpx.RemoteProtocolError("hop 2 disconnect before token"),
          ),
      ],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Consecutive dead connection test",
        stream=True,
        automatic_continuation=True,
    )
    with pytest.raises(compat_errors.APIConnectionError):
      _ = list(stream)
    assert mock_create.call_count == 2

  # 5. Server SSE error event after a checkpoint token -> stops cleanly without
  # reconnecting.
  events_with_sse_error = hop1_events_before_drop + [
      {
          "event_type": "error",
          "error": {"code": "resource_exhausted", "message": "quota exceeded"},
      },
  ]
  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[_make_sync_stream(events_with_sse_error)],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="SSE error event after checkpoint",
        stream=True,
        automatic_continuation=True,
    )
    received = list(stream)
    assert received == events_with_sse_error
    assert mock_create.call_count == 1


@pytest.mark.asyncio
async def test_async_stream_automatic_continuation_resumes_on_dead_connection_with_last_token():
  client = client_lib.Client(api_key="test-key")
  hop1_events_before_drop = [
      _created_event(),
      _text_delta_event("Async Chunk 1 "),
      {
          "event_type": "interaction.status_update",
          "status": "in_progress",
          "continuation_token": "async_tok_ckpt_1",
      },
      _text_delta_event("Async Chunk 2 "),
      {
          "event_type": "interaction.status_update",
          "status": "in_progress",
          "continuation_token": "async_tok_ckpt_2",
      },
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("Async Chunk 3"),
      _completed_event(
          status="completed",
          continuation_token=None,
          output_tokens=30,
      ),
  ]

  for disconnect_exc in (
      httpx.RemoteProtocolError("async peer closed connection"),
      httpx.ReadTimeout("async stream read timed out"),
      None,
  ):
    with mock.patch.object(
        gaos_interactions.AsyncInteractions,
        "create",
        new=mock.AsyncMock(
            side_effect=[
                _make_async_stream(
                    hop1_events_before_drop, exc=disconnect_exc
                ),
                _make_async_stream(hop2_events),
            ]
        ),
    ) as mock_create:
      stream = await client.aio.interactions.create(
          model="gemini-2.5-pro",
          input="Async dead connection resume test",
          stream=True,
          automatic_continuation=True,
      )
      received = [ev async for ev in stream]

    assert received == hop1_events_before_drop + hop2_events
    assert mock_create.call_count == 2
    assert "continuation_token" not in mock_create.call_args_list[0].kwargs
    assert (
        mock_create.call_args_list[1].kwargs["continuation_token"]
        == "async_tok_ckpt_2"
    )

  events_without_token = [
      _created_event(),
      _text_delta_event("Early async chunk"),
  ]
  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[
              _make_async_stream(
                  events_without_token,
                  exc=httpx.RemoteProtocolError("early async disconnect"),
              ),
          ]
      ),
  ) as mock_create:
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Early async dead connection test",
        stream=True,
        automatic_continuation=True,
    )
    with pytest.raises(compat_errors.APIConnectionError):
      _ = [ev async for ev in stream]
    assert mock_create.call_count == 1

  events_with_sse_error = hop1_events_before_drop + [
      {
          "event_type": "error",
          "error": {"code": "resource_exhausted", "message": "quota exceeded"},
      },
  ]
  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[_make_async_stream(events_with_sse_error)]
      ),
  ) as mock_create:
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Async SSE error event after checkpoint",
        stream=True,
        automatic_continuation=True,
    )
    received = [ev async for ev in stream]
    assert received == events_with_sse_error
    assert mock_create.call_count == 1


def test_unary_automatic_continuation_transient_retry_on_hop2():
  client = client_lib.Client(
      api_key="test-key",
      http_options={
          "retry_options": {
              "attempts": 2,
              "initial_delay": 0.001,
              "max_delay": 0.002,
          }
      },
  )

  def _json_response(status_code: int, payload: dict[str, Any]) -> httpx.Response:
    req = httpx.Request(
        "POST",
        "https://generativelanguage.googleapis.com/v1beta/interactions",
    )
    return httpx.Response(
        status_code=status_code,
        headers={"content-type": "application/json"},
        content=json.dumps(payload).encode("utf-8"),
        request=req,
    )

  hop1_ok = _json_response(
      200,
      {
          "id": "int_retry_1",
          "status": "continuation_required",
          "continuation_token": "tok_retry_1",
          "steps": [
              {
                  "type": "model_output",
                  "content": [{"type": "text", "text": "Hop 1 "}],
              }
          ],
          "usage": {"total_output_tokens": 20},
      },
  )
  hop2_err_503 = _json_response(
      503,
      {"error": {"message": "Service unavailable", "code": 503}},
  )
  hop2_ok = _json_response(
      200,
      {
          "id": "int_retry_1",
          "status": "completed",
          "steps": [
              {
                  "type": "model_output",
                  "content": [{"type": "text", "text": "Hop 1 Hop 2"}],
              }
          ],
          "usage": {"total_output_tokens": 40},
      },
  )

  # Hop 1 succeeds on attempt 1.
  # Hop 2 fails once with 503 then retries Hop 2 with tok_retry_1 without
  # re-running Hop 1.
  with mock.patch.object(
      client._api_client._httpx_client,
      "send",
      side_effect=[hop1_ok, hop2_err_503, hop2_ok],
  ) as mock_send:
    res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Retry test",
        automatic_continuation=True,
    )

  assert mock_send.call_count == 3
  req0_body = json.loads(mock_send.call_args_list[0].args[0].content)
  req1_body = json.loads(mock_send.call_args_list[1].args[0].content)
  req2_body = json.loads(mock_send.call_args_list[2].args[0].content)
  assert "continuation_token" not in req0_body
  assert req1_body.get("continuation_token") == "tok_retry_1"
  assert req2_body.get("continuation_token") == "tok_retry_1"
  assert res.status == "completed"
  assert res.output_text == "Hop 1 Hop 2"


def test_unary_incomplete_with_continuation_token_emits_warning_once(
    monkeypatch,
):
  monkeypatch.setattr(
      gaos_google_genai, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      status="continuation_required",
      text="Partial output",
      continuation_token="tok_warn_1",
      output_tokens=100,
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, hop1],
  ):
    with pytest.warns(
        UserWarning,
        match="status='continuation_required'.*automatic_continuation=True",
    ):
      res = client.interactions.create(
          model="gemini-2.5-pro",
          input="Write a long story",
      )

    import warnings as std_warnings

    with std_warnings.catch_warnings(record=True) as recorded:
      std_warnings.simplefilter("always")
      res2 = client.interactions.create(
          model="gemini-2.5-pro",
          input="Write another long story",
      )

  assert res.status == "continuation_required"
  assert res.continuation_token == "tok_warn_1"
  assert res2.status == "continuation_required"
  incomplete_warnings = [
      w for w in recorded if "status='continuation_required'" in str(w.message)
  ]
  assert not incomplete_warnings


def test_unary_incomplete_when_caller_passes_continuation_token_does_not_warn(
    monkeypatch, recwarn
):
  monkeypatch.setattr(
      gaos_google_genai, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop2 = _unary_hop(
      status="continuation_required",
      text="Manual hop 2 still incomplete",
      continuation_token="tok_manual_2",
      output_tokens=100,
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop2],
  ):
    res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Write a long story",
        continuation_token="tok_manual_1",
    )

  assert res.status == "continuation_required"
  incomplete_warnings = [
      w
      for w in recwarn.list
      if "status='continuation_required'" in str(w.message)
  ]
  assert not incomplete_warnings


def test_stream_incomplete_with_continuation_token_emits_warning_once(
    monkeypatch,
):
  monkeypatch.setattr(
      gaos_google_genai, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Stream partial"),
      _completed_event(
          status="continuation_required",
          continuation_token="tok_stream_warn_1",
          output_tokens=50,
      ),
  ]

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(hop1_events),
          _make_sync_stream(hop1_events),
      ],
  ):
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Stream warning test",
        stream=True,
    )
    with pytest.warns(
        UserWarning,
        match="status='continuation_required'.*automatic_continuation=True",
    ):
      received = list(stream)

    import warnings as std_warnings

    stream2 = client.interactions.create(
        model="gemini-2.5-pro",
        input="Stream warning test 2",
        stream=True,
    )
    with std_warnings.catch_warnings(record=True) as recorded:
      std_warnings.simplefilter("always")
      received2 = list(stream2)

  assert received == hop1_events
  assert received2 == hop1_events
  incomplete_warnings = [
      w for w in recorded if "status='continuation_required'" in str(w.message)
  ]
  assert not incomplete_warnings


@pytest.mark.asyncio
async def test_async_stream_incomplete_with_continuation_token_emits_warning(
    monkeypatch,
):
  monkeypatch.setattr(
      gaos_google_genai, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Async stream partial"),
      _completed_event(
          status="continuation_required",
          continuation_token="tok_async_stream_warn_1",
          output_tokens=50,
      ),
  ]

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(side_effect=[_make_async_stream(hop1_events)]),
  ):
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Async stream warning test",
        stream=True,
    )
    with pytest.warns(
        UserWarning,
        match="status='continuation_required'.*automatic_continuation=True",
    ):
      received = [ev async for ev in stream]

  assert received == hop1_events
