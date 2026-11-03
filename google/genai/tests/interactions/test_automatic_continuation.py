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

from ... import _interactions_continuation
from ... import client as client_lib
from ... import errors
from ... import types
from ..._gaos import interactions as gaos_interactions
from ..._gaos.lib import compat_errors
from ..._gaos.models import createinteraction as create_interaction_models
from ..._gaos.types import interactions as interaction_types
from ..._gaos.utils import eventstreaming

pytest_plugins = ("pytest_asyncio",)

# Until `continuation_token` is promoted to the public generated schema,
# `run_tests.sh --private` rewrites the `_gaos` imports above to
# `_gaos_private`. Use `pytestmark` rather than
# `pytest.skip(..., allow_module_level=True)` so pytest collects and skips tests
# cleanly (exit code 0) instead of failing with exit code 5 (no tests collected)
# under Blaze / TAP when `continuation_token` is absent from public types.
pytestmark = pytest.mark.skipif(
    "continuation_token" not in interaction_types.Interaction.model_fields,
    reason="continuation_token is not yet in the generated Interaction schema.",
)


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
          status="requires_continuation",
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
  # store defaults to on: the hop continues the stored hop that issued the
  # token instead of resending the input.
  assert second_req.body.previous_interaction_id == "int_123"
  assert second_req.body.input is None
  assert "input" not in second_req.body.model_dump()
  assert req.body.continuation_token is None
  assert req.body.input == "Hello"


def test_stream_automatic_continuation_close_on_second_hop():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _completed_event(
          status="requires_continuation",
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
          status="requires_continuation",
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
          status="requires_continuation",
          continuation_token="tok_1",
          output_tokens=50,
      ),
  ]
  hop2_events = [
      _created_event(),
      _text_delta_event("Hop 2 "),
      _completed_event(
          status="requires_continuation",
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
  for call in mock_create.call_args_list[1:]:
    assert call.kwargs["previous_interaction_id"] == "int_123"
    assert "input" not in call.kwargs


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


def test_unary_automatic_continuation_with_store_false_merges_hops():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_sf_1",
      status="requires_continuation",
      text="Stateless 1 ",
      continuation_token="tok_sf_1",
  )
  hop2 = _unary_hop(
      interaction_id="int_sf_2",
      status="completed",
      text="Stateless 2",
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, hop2],
  ) as mock_create:
    res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        store=False,
        automatic_continuation=True,
    )

  assert mock_create.call_count == 2
  assert mock_create.call_args_list[1].kwargs["store"] is False
  assert (
      mock_create.call_args_list[1].kwargs["continuation_token"] == "tok_sf_1"
  )
  # Nothing is stored, so the input is resent without previous_interaction_id.
  assert mock_create.call_args_list[1].kwargs["input"] == "Hello"
  assert "previous_interaction_id" not in mock_create.call_args_list[1].kwargs
  assert res.output_text == "Stateless 1 Stateless 2"
  assert res.continuation_ids == ["int_sf_1", "int_sf_2"]


@pytest.mark.asyncio
async def test_async_unary_automatic_continuation_with_store_false_merges_hops():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_sf_1",
      status="requires_continuation",
      text="Stateless 1 ",
      continuation_token="tok_sf_1",
  )
  hop2 = _unary_hop(
      interaction_id="int_sf_2",
      status="completed",
      text="Stateless 2",
  )

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(side_effect=[hop1, hop2]),
  ) as mock_create:
    res = await client.aio.interactions.create(
        request={"body": {"model": "gemini-2.5-pro", "store": False}},
        automatic_continuation=True,
    )

  assert mock_create.call_count == 2
  second_req = mock_create.call_args_list[1].kwargs["request"]
  assert second_req["body"]["continuation_token"] == "tok_sf_1"
  assert res.output_text == "Stateless 1 Stateless 2"
  assert res.continuation_ids == ["int_sf_1", "int_sf_2"]


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
    interaction_id: str = "int_unary_123",
    continuation_token: str | None = None,
    input_tokens: int = 10,
    output_tokens: int = 20,
    thought_tokens: int = 0,
    created: str = "2026-01-01T00:00:00Z",
    updated: str = "2026-01-01T00:00:05Z",
) -> interaction_types.Interaction:
  """Builds a single hop response.

  Each continuation hop is its own interaction on the server, and only contains
  the output (and usage) generated during that hop.
  """
  return interaction_types.Interaction(
      id=interaction_id,
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
      interaction_id="int_req_1",
      status="requires_continuation",
      text="Part A ",
      continuation_token="tok_req_1",
      input_tokens=10,
      output_tokens=40,
      thought_tokens=5,
  )
  hop2 = _unary_hop(
      interaction_id="int_req_2",
      status="completed",
      text="Part B",
      continuation_token=None,
      input_tokens=50,
      output_tokens=30,
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
  # store defaults to on: the hop continues the stored hop that issued the
  # token instead of resending the input.
  assert second_req.body.previous_interaction_id == "int_req_1"
  assert second_req.body.input is None
  assert "input" not in second_req.body.model_dump()
  assert req.body.continuation_token is None
  assert req.body.input == "Hello"
  assert res.status == "completed"
  assert res.output_text == "Part A Part B"
  # Mental model 2: the result is the final hop, with the hops merged.
  assert res.id == "int_req_2"
  assert res.continuation_token is None
  assert res.continuation_ids == ["int_req_1", "int_req_2"]
  assert [s.content[0].text for s in res.steps] == ["Part A ", "Part B"]
  assert res.usage.total_input_tokens == 60
  assert res.usage.total_output_tokens == 70
  assert res.usage.total_thought_tokens == 5
  assert res.usage.total_tokens == 135
  assert res.usage.initial_input_tokens == 10


_RAW_REQUIRES_CONTINUATION_BODY = {
    "id": "int_raw_1",
    "status": "requires_continuation",
    "continuation_token": "dG9rX3Jhd18x",
    "previous_interaction_id": "int_turn_0",
    "steps": [
        {"type": "user_input", "content": [{"type": "text", "text": "Hello"}]},
        {"type": "model_output", "content": [{"type": "text", "text": "A"}]},
    ],
    "usage": {
        "total_input_tokens": 10,
        "total_output_tokens": 5,
        "total_tokens": 15,
    },
}


def _wire_client(
    handler, async_handler=None
) -> tuple[client_lib.Client, list[dict[str, Any]]]:
  """A client whose HTTP transport is `handler`; records request bodies."""
  bodies: list[dict[str, Any]] = []

  def _sync(request: httpx.Request) -> httpx.Response:
    bodies.append(json.loads(request.content.decode()))
    return handler(request)

  async def _async(request: httpx.Request) -> httpx.Response:
    bodies.append(json.loads(request.content.decode()))
    return (async_handler or handler)(request)

  client = client_lib.Client(
      api_key="test-key",
      http_options=types.HttpOptions(
          httpx_client=httpx.Client(transport=httpx.MockTransport(_sync)),
          httpx_async_client=httpx.AsyncClient(
              transport=httpx.MockTransport(_async)
          ),
      ),
  )
  return client, bodies


def _raw_json_response(_: httpx.Request) -> httpx.Response:
  return httpx.Response(
      200,
      headers={"content-type": "application/json"},
      text=json.dumps(_RAW_REQUIRES_CONTINUATION_BODY),
  )


def _assert_opt_out_passthrough(res: Any, bodies: list[dict[str, Any]]):
  # Exactly one request, sent as the caller wrote it: no continuation fields
  # added.
  assert len(bodies) == 1
  assert "generation_config" not in bodies[0]
  assert "continuation_token" not in bodies[0]
  assert bodies[0]["previous_interaction_id"] == "int_turn_0"
  assert bodies[0]["input"] == "Hello"
  # The response is the server body field-for-field (opted-out callers drive
  # continuation themselves, so continuation_token / status must survive).
  serialized = res.model_dump(mode="json", by_alias=True, exclude_none=True)
  for key, value in _RAW_REQUIRES_CONTINUATION_BODY.items():
    assert serialized.get(key) == value, key
  assert "continuation_ids" not in serialized
  assert res.continuation_ids is None
  assert res.continuation_token == "dG9rX3Jhd18x"
  assert res.status == "requires_continuation"


@pytest.mark.filterwarnings("ignore:Interaction stopped before completion")
def test_unary_automatic_continuation_disabled_with_request_object_is_passthrough():
  client, bodies = _wire_client(_raw_json_response)
  req = create_interaction_models.CreateInteractionRequest(
      body=interaction_types.CreateModelInteraction(
          model="gemini-2.5-pro",
          input="Hello",
          previous_interaction_id="int_turn_0",
      )
  )
  res = client.interactions.create(request=req, automatic_continuation=False)
  _assert_opt_out_passthrough(res, bodies)
  # The caller's request object is not mutated either.
  assert req.body.generation_config is None
  assert req.body.continuation_token is None


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore:Interaction stopped before completion")
async def test_async_unary_automatic_continuation_disabled_with_request_object_is_passthrough():
  client, bodies = _wire_client(_raw_json_response)
  req = create_interaction_models.CreateInteractionRequest(
      body=interaction_types.CreateModelInteraction(
          model="gemini-2.5-pro",
          input="Hello",
          previous_interaction_id="int_turn_0",
      )
  )
  res = await client.aio.interactions.create(
      request=req, automatic_continuation=False
  )
  _assert_opt_out_passthrough(res, bodies)
  assert req.body.generation_config is None
  assert req.body.continuation_token is None


def test_unary_automatic_continuation_merges_usage_by_modality():
  client = client_lib.Client(api_key="test-key")

  def _hop(interaction_id, status, token, text_tokens, image_tokens=None):
    by_modality = [
        interaction_types.ModalityTokens(modality="text", tokens=text_tokens)
    ]
    if image_tokens is not None:
      by_modality.append(
          interaction_types.ModalityTokens(
              modality="image", tokens=image_tokens
          )
      )
    return interaction_types.Interaction(
        id=interaction_id,
        status=status,
        continuation_token=token,
        steps=[],
        usage=interaction_types.Usage(
            total_output_tokens=sum(m.tokens for m in by_modality),
            output_tokens_by_modality=by_modality,
        ),
    )

  hop1 = _hop("int_m1", "requires_continuation", "tok_m1", 10, image_tokens=5)
  hop2 = _hop("int_m2", "completed", None, 7)

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, hop2],
  ):
    res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        automatic_continuation=True,
    )

  assert res.usage.total_output_tokens == 22
  assert {
      m.modality: m.tokens for m in res.usage.output_tokens_by_modality
  } == {"text": 17, "image": 5}
  # The hop responses are not mutated.
  assert hop1.usage.output_tokens_by_modality[0].tokens == 10


@pytest.mark.asyncio
async def test_async_unary_automatic_continuation_three_hops():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_a1",
      status="requires_continuation",
      text="Async 1 ",
      continuation_token="tok_1",
      output_tokens=50,
  )
  hop2 = _unary_hop(
      interaction_id="int_a2",
      status="requires_continuation",
      text="Async 2 ",
      continuation_token="tok_2",
      output_tokens=60,
  )
  hop3 = _unary_hop(
      interaction_id="int_a3",
      status="completed",
      text="Async 3",
      continuation_token=None,
      output_tokens=30,
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
  assert res.id == "int_a3"
  assert res.continuation_ids == ["int_a1", "int_a2", "int_a3"]
  assert len(res.steps) == 3
  assert res.usage.total_output_tokens == 140
  assert res.usage.total_input_tokens == 30
  assert res.usage.initial_input_tokens == 10


def test_unary_automatic_continuation_stops_when_token_missing_or_empty():
  client = client_lib.Client(api_key="test-key")
  hop_no_token = _unary_hop(
      status="requires_continuation",
      text="Continuation required without token",
      continuation_token=None,
  )
  hop_empty_token = _unary_hop(
      status="requires_continuation",
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
  assert res1.status == "requires_continuation"
  assert res1.output_text == "Continuation required without token"
  assert res2.status == "requires_continuation"
  assert res2.output_text == "Continuation required with empty token"
  assert res1.continuation_ids == ["int_unary_123"]
  assert res1.usage.total_output_tokens == 20


def test_unary_automatic_continuation_with_initial_user_continuation_token():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_resumed_1",
      status="requires_continuation",
      text="Resumed hop 1 ",
      continuation_token="tok_from_hop1",
  )
  hop2 = _unary_hop(
      interaction_id="int_resumed_2",
      status="completed",
      text="Resumed hop 2",
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
  assert res.continuation_ids == ["int_resumed_1", "int_resumed_2"]


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
          status="requires_continuation",
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


def test_stream_automatic_continuation_terminal_event_without_token_clears_checkpoint():
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
          status="requires_continuation",
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

  # The terminal interaction.completed event is authoritative: without a
  # token it clears the stale mid-hop checkpoint, so the stream stops (same
  # as unary) instead of resuming and re-generating already-received content.
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

  assert received == hop1_events
  assert mock_create.call_count == 1


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
              exc=httpx.RemoteProtocolError(
                  "disconnect with auto_continue=False"
              ),
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

  # 4. Repeated failure on the resumed hop before a new token (or any content)
  # is emitted -> retries the hop's own token up to the no-progress cap, then
  # raises ContinuationInterruptedError (the checkpoint token is resumable)
  # with the last disconnect as the cause.
  max_retries = (
      _interactions_continuation.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  )
  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(
              hop1_events_before_drop,
              exc=httpx.RemoteProtocolError("hop 1 disconnect"),
          ),
      ]
      + [
          _make_sync_stream(
              [_created_event()],
              exc=httpx.RemoteProtocolError("hop 2 disconnect before token"),
          )
          for _ in range(max_retries + 1)
      ],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Consecutive dead connection test",
        stream=True,
        automatic_continuation=True,
    )
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      _ = list(stream)
    assert isinstance(exc_info.value.__cause__, compat_errors.APIConnectionError)
    assert exc_info.value.continuation_token == "tok_checkpoint_2"
    assert exc_info.value.partial_interaction is None
    assert mock_create.call_count == max_retries + 2
    assert [
        c.kwargs["continuation_token"] for c in mock_create.call_args_list[1:]
    ] == ["tok_checkpoint_2"] * (max_retries + 1)

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
                _make_async_stream(hop1_events_before_drop, exc=disconnect_exc),
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


def _status_update_event(continuation_token: str) -> dict[str, Any]:
  return {
      "event_type": "interaction.status_update",
      "status": "in_progress",
      "continuation_token": continuation_token,
  }


def test_stream_automatic_continuation_drop_before_checkpoint_retries_hop_token():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Part 1 "),
      _completed_event(
          status="requires_continuation",
          continuation_token="tok_hop1",
      ),
  ]
  # Hop 2 drops before its first checkpoint, and before yielding any output
  # (output since the last checkpoint can't be replayed without duplicating
  # it; see the conformance spec).
  hop2_events_before_drop = [
      _created_event(),
  ]
  hop2_retry_events = [
      _created_event(),
      _text_delta_event("Part 2"),
      _completed_event(status="completed"),
  ]

  for disconnect_exc in (
      httpx.RemoteProtocolError("peer closed connection"),
      None,
  ):
    with mock.patch.object(
        gaos_interactions.Interactions,
        "create",
        side_effect=[
            _make_sync_stream(hop1_events),
            _make_sync_stream(hop2_events_before_drop, exc=disconnect_exc),
            _make_sync_stream(hop2_retry_events),
        ],
    ) as mock_create:
      stream = client.interactions.create(
          model="gemini-2.5-pro",
          input="Drop before checkpoint test",
          stream=True,
          automatic_continuation=True,
      )
      received = list(stream)

    assert received == hop1_events + hop2_events_before_drop + hop2_retry_events
    assert mock_create.call_count == 3
    assert "continuation_token" not in mock_create.call_args_list[0].kwargs
    assert mock_create.call_args_list[1].kwargs["continuation_token"] == (
        "tok_hop1"
    )
    assert mock_create.call_args_list[2].kwargs["continuation_token"] == (
        "tok_hop1"
    )


def test_stream_automatic_continuation_drop_before_checkpoint_retries_caller_token():
  client = client_lib.Client(api_key="test-key")
  events_before_drop = [_created_event()]
  retry_events = [
      _created_event(),
      _text_delta_event("done"),
      _completed_event(status="completed"),
  ]

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(
              events_before_drop,
              exc=httpx.RemoteProtocolError("peer closed connection"),
          ),
          _make_sync_stream(retry_events),
      ],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Caller token drop test",
        stream=True,
        continuation_token="tok_caller",
        automatic_continuation=True,
    )
    received = list(stream)

  assert received == events_before_drop + retry_events
  assert mock_create.call_count == 2
  assert [
      c.kwargs["continuation_token"] for c in mock_create.call_args_list
  ] == ["tok_caller", "tok_caller"]


def test_stream_automatic_continuation_checkpoint_progress_resets_reconnect_cap():
  client = client_lib.Client(api_key="test-key")
  max_retries = (
      _interactions_continuation.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  )
  num_drops = max_retries + 2
  dropping_streams = [
      _make_sync_stream(
          [_created_event(), _status_update_event(f"tok_ckpt_{i}")],
          exc=httpx.RemoteProtocolError(f"drop {i}"),
      )
      for i in range(num_drops)
  ]
  final_events = [_created_event(), _completed_event(status="completed")]

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=dropping_streams + [_make_sync_stream(final_events)],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Progress resets cap test",
        stream=True,
        automatic_continuation=True,
    )
    received = list(stream)

  assert received[-len(final_events) :] == final_events
  assert mock_create.call_count == num_drops + 1
  assert [
      c.kwargs["continuation_token"] for c in mock_create.call_args_list[1:]
  ] == [f"tok_ckpt_{i}" for i in range(num_drops)]


@pytest.mark.asyncio
async def test_async_stream_automatic_continuation_drop_before_checkpoint_retries_hop_token():
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _completed_event(
          status="requires_continuation",
          continuation_token="async_tok_hop1",
      ),
  ]
  hop2_events_before_drop = [_created_event()]
  hop2_retry_events = [
      _created_event(),
      _text_delta_event("Part 2"),
      _completed_event(status="completed"),
  ]

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[
              _make_async_stream(hop1_events),
              _make_async_stream(
                  hop2_events_before_drop,
                  exc=httpx.RemoteProtocolError("async peer closed"),
              ),
              _make_async_stream(hop2_retry_events),
          ]
      ),
  ) as mock_create:
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Async drop before checkpoint test",
        stream=True,
        automatic_continuation=True,
    )
    received = [ev async for ev in stream]

  assert received == hop1_events + hop2_events_before_drop + hop2_retry_events
  assert mock_create.call_count == 3
  assert [
      c.kwargs["continuation_token"] for c in mock_create.call_args_list[1:]
  ] == ["async_tok_hop1", "async_tok_hop1"]


@pytest.mark.asyncio
async def test_async_stream_automatic_continuation_reconnect_cap_raises():
  client = client_lib.Client(api_key="test-key")
  max_retries = (
      _interactions_continuation.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  )

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[
              _make_async_stream(
                  [_created_event()],
                  exc=httpx.RemoteProtocolError(f"async drop {i}"),
              )
              for i in range(max_retries + 1)
          ]
      ),
  ) as mock_create:
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Async reconnect cap test",
        stream=True,
        continuation_token="async_tok_caller",
        automatic_continuation=True,
    )
    with pytest.raises(compat_errors.APIConnectionError):
      _ = [ev async for ev in stream]

  assert mock_create.call_count == max_retries + 1
  assert [
      c.kwargs["continuation_token"] for c in mock_create.call_args_list
  ] == ["async_tok_caller"] * (max_retries + 1)


def test_stream_continuation_state_machine_resets_hop_fields_and_tracks_owner():
  state = _interactions_continuation.StreamContinuation(
      connection_error_type=compat_errors.APIConnectionError,
  )

  # Hop 1: initial hop emits content, then a checkpoint token, then drops before
  # any post-checkpoint content.
  assert state.start_hop(stream_opened=True) == (None, None)
  state.observe(_created_event(interaction_id="hop_1"))
  state.observe(_text_delta_event("hello"))
  state.observe(_status_update_event("tok_ckpt_1"))
  assert state.end_hop(httpx.RemoteProtocolError("drop 1")) is True

  # Hop 2: start_hop replaces the per-hop record cleanly, seeded with hop 1's
  # checkpoint token and hop_1 as owner; pre-stream non-connection errors raise
  # immediately, wrapped as ContinuationInterruptedError since hop 1's
  # checkpoint token is resumable.
  assert state.start_hop(stream_opened=False) == ("tok_ckpt_1", "hop_1")
  with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
    state.end_hop(RuntimeError("429"))
  assert isinstance(exc_info.value.__cause__, RuntimeError)
  assert exc_info.value.continuation_token == "tok_ckpt_1"
  assert exc_info.value.interaction_id == "hop_1"
  assert exc_info.value.continuation_ids == ["hop_1"]
  assert exc_info.value.partial_interaction is None

  # Pre-stream connection error retries up to MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  # while preserving ("tok_ckpt_1", "hop_1") as the resume target.
  conn_err = compat_errors.APIConnectionError(
      request=httpx.Request("POST", "https://example.com/interactions")
  )
  state = _interactions_continuation.StreamContinuation(
      connection_error_type=compat_errors.APIConnectionError,
  )
  state.start_hop(stream_opened=True)
  state.observe(_created_event(interaction_id="hop_1"))
  state.observe(_status_update_event("tok_ckpt_1"))
  assert state.end_hop() is True

  for _ in range(
      _interactions_continuation.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  ):
    assert state.start_hop(stream_opened=False) == ("tok_ckpt_1", "hop_1")
    assert state.end_hop(conn_err) is True

  assert state.start_hop(stream_opened=False) == ("tok_ckpt_1", "hop_1")
  with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
    state.end_hop(conn_err)
  assert exc_info.value.__cause__ is conn_err
  assert exc_info.value.continuation_token == "tok_ckpt_1"
  assert exc_info.value.interaction_id == "hop_1"

  # No server-issued token (only the caller's own): the error is raised as-is.
  state = _interactions_continuation.StreamContinuation(
      initial_continuation_token="tok_caller",
      connection_error_type=compat_errors.APIConnectionError,
  )
  for _ in range(
      _interactions_continuation.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  ):
    assert state.start_hop(stream_opened=False) == ("tok_caller", None)
    assert state.end_hop(conn_err) is True
  assert state.start_hop(stream_opened=False) == ("tok_caller", None)
  with pytest.raises(compat_errors.APIConnectionError):
    state.end_hop(conn_err)


def test_stream_continuation_state_machine_stops_on_unchanged_token():
  state = _interactions_continuation.StreamContinuation(
      initial_continuation_token="tok_same",
      connection_error_type=compat_errors.APIConnectionError,
  )
  assert state.start_hop(stream_opened=True) == ("tok_same", None)
  state.observe(_created_event(interaction_id="hop_1"))
  state.observe(
      _completed_event(
          interaction_id="hop_1",
          status="requires_continuation",
          continuation_token="tok_same",
      )
  )
  assert state.end_hop() is False


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

  def _json_response(
      status_code: int, payload: dict[str, Any]
  ) -> httpx.Response:
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
          "status": "requires_continuation",
          "continuation_token": "tok_retry_1",
          "steps": [{
              "type": "model_output",
              "content": [{"type": "text", "text": "Hop 1 "}],
          }],
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
          "id": "int_retry_2",
          "status": "completed",
          "steps": [{
              "type": "model_output",
              "content": [{"type": "text", "text": "Hop 2"}],
          }],
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
  assert res.id == "int_retry_2"
  assert res.continuation_ids == ["int_retry_1", "int_retry_2"]
  assert res.usage.total_output_tokens == 60


def test_unary_later_hop_failure_raises_continuation_interrupted_error():
  """A hop-3 failure keeps hops 1-2 merged on ContinuationInterruptedError."""
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_err_1",
      status="requires_continuation",
      text="Part 1 ",
      continuation_token="tok_err_1",
  )
  hop2 = _unary_hop(
      interaction_id="int_err_2",
      status="requires_continuation",
      text="Part 2 ",
      continuation_token="tok_err_2",
  )
  cause = compat_errors.APIConnectionError(
      request=httpx.Request("POST", "https://example.com/interactions")
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, hop2, cause],
  ) as mock_create:
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      client.interactions.create(model="gemini-2.5-pro", input="Essay")

  assert mock_create.call_count == 3
  err = exc_info.value
  assert err.__cause__ is cause
  assert err.continuation_token == "tok_err_2"
  assert err.interaction_id == "int_err_2"
  assert err.continuation_ids == ["int_err_1", "int_err_2"]
  partial = err.partial_interaction
  assert partial.id == "int_err_2"
  assert partial.status == "requires_continuation"
  assert partial.continuation_token == "tok_err_2"
  assert partial.output_text == "Part 1 Part 2 "
  assert partial.continuation_ids == ["int_err_1", "int_err_2"]

  # A first-hop failure has nothing to keep: the error is raised as-is.
  with mock.patch.object(
      gaos_interactions.Interactions, "create", side_effect=[cause]
  ):
    with pytest.raises(compat_errors.APIConnectionError):
      client.interactions.create(model="gemini-2.5-pro", input="Essay")


@pytest.mark.asyncio
async def test_async_unary_later_hop_failure_raises_continuation_interrupted_error():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_aerr_1",
      status="requires_continuation",
      text="Part 1 ",
      continuation_token="tok_aerr_1",
  )
  cause = compat_errors.APIConnectionError(
      request=httpx.Request("POST", "https://example.com/interactions")
  )

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(side_effect=[hop1, cause]),
  ):
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      await client.aio.interactions.create(
          model="gemini-2.5-pro", input="Essay"
      )

  err = exc_info.value
  assert err.__cause__ is cause
  assert err.continuation_token == "tok_aerr_1"
  assert err.interaction_id == "int_aerr_1"
  assert err.continuation_ids == ["int_aerr_1"]
  assert err.partial_interaction.output_text == "Part 1 "
  assert err.partial_interaction.status == "requires_continuation"


def test_default_automatic_continuation_leaves_max_output_tokens_unset_unary():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_def_1",
      status="requires_continuation",
      text="Part 1 ",
      continuation_token="tok_def_1",
  )
  hop2 = _unary_hop(
      interaction_id="int_def_2",
      status="completed",
      text="Part 2",
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, hop2],
  ) as mock_create:
    res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Write a long essay",
    )

  assert res.status == "completed"
  assert res.output_text == "Part 1 Part 2"
  assert res.continuation_ids == ["int_def_1", "int_def_2"]
  assert mock_create.call_count == 2
  assert "generation_config" not in mock_create.call_args_list[0].kwargs
  assert "generation_config" not in mock_create.call_args_list[1].kwargs


def test_generation_config_preserved_and_not_mutated_without_max_output_tokens():
  client = client_lib.Client(api_key="test-key")
  hop = _unary_hop(interaction_id="int_cfg_1", status="completed", text="Done")

  caller_dict_cfg = {"seed": 42}
  caller_model_cfg = interaction_types.GenerationConfig(seed=99)
  caller_req = create_interaction_models.CreateInteractionRequest(
      body=interaction_types.CreateModelInteraction(
          model="gemini-2.5-pro",
          input="Request object test",
          generation_config=caller_model_cfg,
      )
  )

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop, hop, hop],
  ) as mock_create:
    client.interactions.create(
        model="gemini-2.5-pro",
        input="Dict config test",
        generation_config=caller_dict_cfg,
    )
    client.interactions.create(
        model="gemini-2.5-pro",
        input="Model config test",
        generation_config=caller_model_cfg,
    )
    client.interactions.create(request=caller_req)

  assert caller_dict_cfg == {"seed": 42}
  assert caller_model_cfg.max_output_tokens is None
  assert caller_req.body.generation_config.max_output_tokens is None

  assert mock_create.call_args_list[0].kwargs["generation_config"] == {
      "seed": 42,
  }
  sent_model_cfg = mock_create.call_args_list[1].kwargs["generation_config"]
  assert sent_model_cfg.seed == 99
  assert sent_model_cfg.max_output_tokens is None
  sent_req = mock_create.call_args_list[2].kwargs["request"]
  assert sent_req.body.generation_config.seed == 99
  assert sent_req.body.generation_config.max_output_tokens is None


@pytest.mark.asyncio
async def test_async_max_output_tokens_left_unset_unless_explicitly_provided():
  client = client_lib.Client(api_key="test-key")
  hop = _unary_hop(
      interaction_id="int_async_1", status="completed", text="Done"
  )
  bg_hop = interaction_types.Interaction(id="int_bg_1", status="in_progress")
  stream_events = [
      _created_event(interaction_id="int_s_1"),
      _text_delta_event("Chunk"),
      _completed_event(interaction_id="int_s_1", status="completed"),
  ]

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[
              hop,
              hop,
              hop,
              bg_hop,
              hop,
              _make_async_stream(stream_events),
          ]
      ),
  ) as mock_create:
    # 1. Default async unary -> leaves generation_config unset
    await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Default async",
    )
    # 2. Explicit generation_config.max_output_tokens -> preserved
    await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Explicit budget",
        generation_config={"max_output_tokens": 2048},
    )
    # 3. agent interaction -> unset
    await client.aio.interactions.create(
        agent="deep-research-pro-preview-12-2025",
        input="Agent run",
    )
    # 4. background=True -> unset
    bg_res = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Background",
        background=True,
    )
    # 5. automatic_continuation=False -> unset
    await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Disabled",
        automatic_continuation=False,
    )
    # 6. stream=True -> unset
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Streaming",
        stream=True,
    )
    _ = [ev async for ev in stream]

  assert bg_res.status == "in_progress"
  assert bg_res.continuation_ids is None
  assert "generation_config" not in mock_create.call_args_list[0].kwargs
  assert mock_create.call_args_list[1].kwargs["generation_config"] == {
      "max_output_tokens": 2048
  }
  assert "generation_config" not in mock_create.call_args_list[2].kwargs
  assert "generation_config" not in mock_create.call_args_list[3].kwargs
  assert "generation_config" not in mock_create.call_args_list[4].kwargs
  assert "generation_config" not in mock_create.call_args_list[5].kwargs


def test_unary_incomplete_with_continuation_token_emits_warning_once(
    monkeypatch,
):
  monkeypatch.setattr(
      _interactions_continuation, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      status="requires_continuation",
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
        match="status='requires_continuation'.*automatic_continuation=True",
    ):
      res = client.interactions.create(
          model="gemini-2.5-pro",
          input="Write a long story",
          automatic_continuation=False,
      )

    import warnings as std_warnings

    with std_warnings.catch_warnings(record=True) as recorded:
      std_warnings.simplefilter("always")
      res2 = client.interactions.create(
          model="gemini-2.5-pro",
          input="Write another long story",
          automatic_continuation=False,
      )

  assert res.status == "requires_continuation"
  assert res.continuation_token == "tok_warn_1"
  assert res2.status == "requires_continuation"
  incomplete_warnings = [
      w for w in recorded if "status='requires_continuation'" in str(w.message)
  ]
  assert not incomplete_warnings


def test_unary_incomplete_when_caller_passes_continuation_token_does_not_warn(
    monkeypatch, recwarn
):
  monkeypatch.setattr(
      _interactions_continuation, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop2 = _unary_hop(
      status="requires_continuation",
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
        automatic_continuation=False,
    )

  assert res.status == "requires_continuation"
  incomplete_warnings = [
      w
      for w in recwarn.list
      if "status='requires_continuation'" in str(w.message)
  ]
  assert not incomplete_warnings


def test_stream_incomplete_with_continuation_token_emits_warning_once(
    monkeypatch,
):
  monkeypatch.setattr(
      _interactions_continuation, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Stream partial"),
      _completed_event(
          status="requires_continuation",
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
        automatic_continuation=False,
    )
    with pytest.warns(
        UserWarning,
        match="status='requires_continuation'.*automatic_continuation=True",
    ):
      received = list(stream)

    import warnings as std_warnings

    stream2 = client.interactions.create(
        model="gemini-2.5-pro",
        input="Stream warning test 2",
        stream=True,
        automatic_continuation=False,
    )
    with std_warnings.catch_warnings(record=True) as recorded:
      std_warnings.simplefilter("always")
      received2 = list(stream2)

  assert received == hop1_events
  assert received2 == hop1_events
  incomplete_warnings = [
      w for w in recorded if "status='requires_continuation'" in str(w.message)
  ]
  assert not incomplete_warnings


@pytest.mark.asyncio
async def test_async_stream_incomplete_with_continuation_token_emits_warning(
    monkeypatch,
):
  monkeypatch.setattr(
      _interactions_continuation, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  hop1_events = [
      _created_event(),
      _text_delta_event("Async stream partial"),
      _completed_event(
          status="requires_continuation",
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
        automatic_continuation=False,
    )
    with pytest.warns(
        UserWarning,
        match="status='requires_continuation'.*automatic_continuation=True",
    ):
      received = [ev async for ev in stream]

  assert received == hop1_events


class _FakeClock:
  """A manual monotonic clock for deadline tests."""

  def __init__(self, now: float = 1000.0):
    self.now = now

  def __call__(self) -> float:
    return self.now

  def advance(self, seconds: float) -> None:
    self.now += seconds


def test_call_deadline_bounds_numeric_timeout_only():
  clock = _FakeClock()
  deadline = _interactions_continuation.CallDeadline(10, clock=clock)
  assert deadline.hop_timeout() == 10
  clock.advance(4)
  assert deadline.remaining() == pytest.approx(6)
  assert deadline.hop_timeout() == pytest.approx(6)
  assert not deadline.expired()
  deadline.check()
  clock.advance(7)
  assert deadline.expired()
  assert deadline.hop_timeout() == 0
  with pytest.raises(_interactions_continuation.ContinuationTimeoutError):
    deadline.check()

  # None, httpx.Timeout, and enabled=False pass timeout through unchanged and
  # never expire (opt-out / background / agent calls stay pure passthroughs).
  for per_hop in (None, httpx.Timeout(10.0)):
    deadline = _interactions_continuation.CallDeadline(per_hop, clock=clock)
    clock.advance(1_000_000)
    assert deadline.remaining() is None
    assert not deadline.expired()
    assert deadline.hop_timeout() is per_hop
    deadline.check()
  disabled = _interactions_continuation.CallDeadline(
      60, enabled=False, clock=clock
  )
  clock.advance(1_000_000)
  assert disabled.remaining() is None
  assert disabled.hop_timeout() == 60
  disabled.check()

  # ContinuationTimeoutError mid-hop right after a checkpoint (no content yet)
  # fails immediately instead of triggering a reconnect attempt.
  state = _interactions_continuation.StreamContinuation(
      connection_error_type=compat_errors.APIConnectionError,
  )
  state.start_hop(stream_opened=True)
  state.observe(_created_event(interaction_id="hop_1"))
  state.observe(_status_update_event("tok_ckpt_1"))
  with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
    state.end_hop(_interactions_continuation.ContinuationTimeoutError("expired"))
  assert exc_info.value.continuation_token == "tok_ckpt_1"
  assert exc_info.value.interaction_id == "hop_1"


def test_unary_timeout_bounds_whole_call_and_passes_remaining_per_hop():
  client = client_lib.Client(api_key="test-key")
  clock = _FakeClock()
  hops = [
      _unary_hop(
          interaction_id="int_t1",
          status="requires_continuation",
          text="A ",
          continuation_token="tok_t1",
      ),
      _unary_hop(
          interaction_id="int_t2",
          status="requires_continuation",
          text="B ",
          continuation_token="tok_t2",
      ),
      _unary_hop(interaction_id="int_t3", status="completed", text="C"),
  ]

  def _create(**kwargs):
    del kwargs
    clock.advance(10)  # each hop takes 10s
    return hops.pop(0)

  with mock.patch.object(
      _interactions_continuation.time, "monotonic", clock
  ), mock.patch.object(
      gaos_interactions.Interactions, "create", side_effect=_create
  ) as mock_create:
    res = client.interactions.create(
        model="gemini-2.5-pro", input="Hello", timeout=60
    )

  assert res.status == "completed"
  assert res.continuation_ids == ["int_t1", "int_t2", "int_t3"]
  # Each hop is sent with the time left on the call, not the full timeout.
  assert [c.kwargs["timeout"] for c in mock_create.call_args_list] == [
      pytest.approx(60),
      pytest.approx(50),
      pytest.approx(40),
  ]


def test_unary_timeout_expiry_raises_interrupted_with_partial_result():
  client = client_lib.Client(api_key="test-key")
  clock = _FakeClock()
  hops = [
      _unary_hop(
          interaction_id="int_t1",
          status="requires_continuation",
          text="A ",
          continuation_token="tok_t1",
          output_tokens=40,
      ),
      _unary_hop(
          interaction_id="int_t2",
          status="requires_continuation",
          text="B ",
          continuation_token="tok_t2",
          output_tokens=30,
      ),
  ]

  def _create(**kwargs):
    del kwargs
    clock.advance(10)
    return hops.pop(0)

  with mock.patch.object(
      _interactions_continuation.time, "monotonic", clock
  ), mock.patch.object(
      gaos_interactions.Interactions, "create", side_effect=_create
  ) as mock_create:
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      client.interactions.create(
          model="gemini-2.5-pro", input="Hello", timeout=15
      )

  # Hop 1 (10s) left 5s for hop 2, which used it up; hop 3 never started.
  assert mock_create.call_count == 2
  assert mock_create.call_args_list[1].kwargs["timeout"] == pytest.approx(5)
  err = exc_info.value
  assert isinstance(err.__cause__, TimeoutError)
  assert isinstance(
      err.__cause__, _interactions_continuation.ContinuationTimeoutError
  )
  assert err.continuation_token == "tok_t2"
  assert err.interaction_id == "int_t2"
  assert err.continuation_ids == ["int_t1", "int_t2"]
  assert err.partial_interaction.status == "requires_continuation"
  assert err.partial_interaction.output_text == "A B "
  assert err.partial_interaction.usage.total_output_tokens == 70


@pytest.mark.asyncio
async def test_async_unary_timeout_expiry_raises_interrupted():
  client = client_lib.Client(api_key="test-key")
  clock = _FakeClock()
  hops = [
      _unary_hop(
          interaction_id="int_at1",
          status="requires_continuation",
          text="A ",
          continuation_token="tok_at1",
      ),
      _unary_hop(
          interaction_id="int_at2",
          status="requires_continuation",
          text="B ",
          continuation_token="tok_at2",
      ),
  ]

  async def _create(**kwargs):
    del kwargs
    clock.advance(10)
    return hops.pop(0)

  with mock.patch.object(
      _interactions_continuation.time, "monotonic", clock
  ), mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(side_effect=_create),
  ) as mock_create:
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      await client.aio.interactions.create(
          model="gemini-2.5-pro", input="Hello", timeout=15
      )

  assert mock_create.call_count == 2
  assert [c.kwargs["timeout"] for c in mock_create.call_args_list] == [
      pytest.approx(15),
      pytest.approx(5),
  ]
  assert isinstance(exc_info.value.__cause__, TimeoutError)
  assert exc_info.value.continuation_token == "tok_at2"
  assert exc_info.value.partial_interaction.output_text == "A B "


def test_unary_httpx_timeout_object_applies_per_hop():
  client = client_lib.Client(api_key="test-key")
  clock = _FakeClock()
  per_hop = httpx.Timeout(10.0)
  hops = [
      _unary_hop(
          interaction_id="int_h1",
          status="requires_continuation",
          text="A ",
          continuation_token="tok_h1",
      ),
      _unary_hop(interaction_id="int_h2", status="completed", text="B"),
  ]

  def _create(**kwargs):
    del kwargs
    clock.advance(1_000)
    return hops.pop(0)

  with mock.patch.object(
      _interactions_continuation.time, "monotonic", clock
  ), mock.patch.object(
      gaos_interactions.Interactions, "create", side_effect=_create
  ) as mock_create:
    res = client.interactions.create(
        model="gemini-2.5-pro", input="Hello", timeout=per_hop
    )

  assert res.status == "completed"
  assert [c.kwargs["timeout"] for c in mock_create.call_args_list] == [
      per_hop,
      per_hop,
  ]


def test_stream_timeout_expiry_between_hops_raises_interrupted():
  client = client_lib.Client(api_key="test-key")
  clock = _FakeClock()
  hop1_events = [
      _created_event(interaction_id="int_s1"),
      _text_delta_event("Part 1 "),
      _completed_event(
          status="requires_continuation",
          continuation_token="tok_s1",
          interaction_id="int_s1",
      ),
  ]

  def _hop1():
    yield hop1_events[0]
    yield hop1_events[1]
    clock.advance(20)  # hop 1 outlives the 15s budget
    yield hop1_events[2]

  with mock.patch.object(
      _interactions_continuation.time, "monotonic", clock
  ), mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[_make_sync_stream(_hop1())],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro", input="Hello", stream=True, timeout=15
    )
    received = []
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      for event in stream:
        received.append(event)

  # Hop 1's events were all yielded; hop 2 never started.
  assert received == hop1_events
  assert mock_create.call_count == 1
  assert isinstance(exc_info.value.__cause__, TimeoutError)
  assert exc_info.value.continuation_token == "tok_s1"
  assert exc_info.value.interaction_id == "int_s1"
  assert exc_info.value.partial_interaction is None


def test_stream_timeout_expiry_mid_hop_raises_interrupted_with_checkpoint():
  client = client_lib.Client(api_key="test-key")
  clock = _FakeClock()
  hop1_events = [
      _created_event(interaction_id="int_m1"),
      _text_delta_event("Part 1 "),
      _completed_event(
          status="requires_continuation",
          continuation_token="tok_m1",
          interaction_id="int_m1",
      ),
  ]

  def _hop2_events():
    yield _created_event(interaction_id="int_m2")
    yield _text_delta_event("Part 2a ")
    clock.advance(100)  # the deadline passes while waiting for the next event
    yield _text_delta_event("Part 2b ")
    yield _completed_event(status="completed", interaction_id="int_m2")

  with mock.patch.object(
      _interactions_continuation.time, "monotonic", clock
  ), mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(hop1_events),
          _make_sync_stream(_hop2_events()),
      ],
  ) as mock_create:
    stream = client.interactions.create(
        model="gemini-2.5-pro", input="Hello", stream=True, timeout=60
    )
    received = []
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      for event in stream:
        received.append(event)

  # The event that arrived as the deadline passed is still delivered; the
  # stream stops before waiting for the next one.
  assert [ev["event_type"] for ev in received] == [
      "interaction.created",
      "step.delta",
      "interaction.completed",
      "interaction.created",
      "step.delta",
      "step.delta",
  ]
  assert mock_create.call_count == 2
  assert isinstance(exc_info.value.__cause__, TimeoutError)
  # Hop 2 produced output after hop 1's token, so resuming from tok_m1
  # re-generates "Part 2a " (documented on ContinuationInterruptedError).
  assert exc_info.value.continuation_token == "tok_m1"
  assert exc_info.value.interaction_id == "int_m1"
  assert exc_info.value.continuation_ids == ["int_m1", "int_m2"]


@pytest.mark.asyncio
async def test_async_stream_timeout_expiry_between_hops_raises_interrupted():
  client = client_lib.Client(api_key="test-key")
  clock = _FakeClock()
  hop1_events = [
      _created_event(interaction_id="int_as1"),
      _text_delta_event("Part 1 "),
      _completed_event(
          status="requires_continuation",
          continuation_token="tok_as1",
          interaction_id="int_as1",
      ),
  ]

  def _hop1():
    yield hop1_events[0]
    yield hop1_events[1]
    clock.advance(20)
    yield hop1_events[2]

  with mock.patch.object(
      _interactions_continuation.time, "monotonic", clock
  ), mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(side_effect=[_make_async_stream(_hop1())]),
  ) as mock_create:
    stream = await client.aio.interactions.create(
        model="gemini-2.5-pro", input="Hello", stream=True, timeout=15
    )
    received = []
    with pytest.raises(errors.ContinuationInterruptedError) as exc_info:
      async for event in stream:
        received.append(event)

  assert received == hop1_events
  assert mock_create.call_count == 1
  assert isinstance(exc_info.value.__cause__, TimeoutError)
  assert exc_info.value.continuation_token == "tok_as1"


@pytest.mark.asyncio
async def test_background_and_agent_requires_continuation_do_not_warn(
    monkeypatch, recwarn
):
  monkeypatch.setattr(
      _interactions_continuation, "_incomplete_continuation_warned", False
  )
  client = client_lib.Client(api_key="test-key")
  incomplete_hop = _unary_hop(
      interaction_id="int_skip_warn",
      status="requires_continuation",
      text="Server-managed partial",
      continuation_token="tok_skip_warn",
      output_tokens=25,
  )
  incomplete_events = [
      _created_event(interaction_id="int_skip_stream"),
      _text_delta_event("Server-managed stream partial"),
      _completed_event(
          interaction_id="int_skip_stream",
          status="requires_continuation",
          continuation_token="tok_skip_stream",
          output_tokens=25,
      ),
  ]

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          incomplete_hop,
          incomplete_hop,
          _make_sync_stream(incomplete_events),
      ],
  ), mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[
              incomplete_hop,
              _make_async_stream(incomplete_events),
          ]
      ),
  ):
    bg_res = client.interactions.create(
        model="gemini-2.5-pro",
        input="Background task",
        background=True,
    )
    agent_res = client.interactions.create(
        agent="deep-research-pro-preview-12-2025",
        input="Agent task",
    )
    bg_stream = list(
        client.interactions.create(
            model="gemini-2.5-pro",
            input="Background stream",
            background=True,
            stream=True,
        )
    )
    async_agent_res = await client.aio.interactions.create(
        agent="deep-research-pro-preview-12-2025",
        input="Async agent task",
    )
    async_agent_stream = [
        ev
        async for ev in await client.aio.interactions.create(
            agent="deep-research-pro-preview-12-2025",
            input="Async agent stream",
            stream=True,
        )
    ]

  assert bg_res.status == "requires_continuation"
  assert agent_res.status == "requires_continuation"
  assert len(bg_stream) == 3
  assert async_agent_res.status == "requires_continuation"
  assert len(async_agent_stream) == 3
  incomplete_warnings = [
      w
      for w in recwarn.list
      if "status='requires_continuation'" in str(w.message)
  ]
  assert not incomplete_warnings


@pytest.mark.asyncio
async def test_store_false_interrupted_sets_interaction_id_none():
  client = client_lib.Client(api_key="test-key")
  hop1 = _unary_hop(
      interaction_id="int_unstored_1",
      status="requires_continuation",
      text="Part 1 ",
      continuation_token="tok_unstored_1",
      output_tokens=10,
  )
  hop1_events = [
      _created_event(interaction_id="int_unstored_s1"),
      _text_delta_event("Stream Part 1 "),
      _completed_event(
          interaction_id="int_unstored_s1",
          status="requires_continuation",
          continuation_token="tok_unstored_s1",
      ),
  ]

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[hop1, RuntimeError("boom unary")],
  ):
    with pytest.raises(errors.ContinuationInterruptedError) as unary_exc:
      client.interactions.create(
          model="gemini-2.5-pro",
          input="Hello",
          store=False,
      )
  assert unary_exc.value.continuation_token == "tok_unstored_1"
  assert unary_exc.value.interaction_id is None

  with mock.patch.object(
      gaos_interactions.Interactions,
      "create",
      side_effect=[
          _make_sync_stream(hop1_events),
          RuntimeError("boom sync stream"),
      ],
  ):
    stream = client.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        store=False,
        stream=True,
    )
    with pytest.raises(errors.ContinuationInterruptedError) as stream_exc:
      list(stream)
  assert stream_exc.value.continuation_token == "tok_unstored_s1"
  assert stream_exc.value.interaction_id is None

  with mock.patch.object(
      gaos_interactions.AsyncInteractions,
      "create",
      new=mock.AsyncMock(
          side_effect=[
              _make_async_stream(hop1_events),
              RuntimeError("boom async stream"),
          ]
      ),
  ):
    astream = await client.aio.interactions.create(
        model="gemini-2.5-pro",
        input="Hello",
        store=False,
        stream=True,
    )
    with pytest.raises(errors.ContinuationInterruptedError) as astream_exc:
      _ = [ev async for ev in astream]
  assert astream_exc.value.continuation_token == "tok_unstored_s1"
  assert astream_exc.value.interaction_id is None


def test_merge_usages_does_not_leak_later_hop_initial_input_tokens():
  hop1_missing_input = interaction_types.Interaction(
      id="int_u1",
      status="requires_continuation",
      continuation_token="tok_u1",
      steps=[],
      usage=interaction_types.Usage(total_output_tokens=20),
  )
  hop2 = interaction_types.Interaction(
      id="int_u2",
      status="completed",
      steps=[],
      usage=interaction_types.Usage(
          initial_input_tokens=500,
          total_input_tokens=500,
          total_output_tokens=30,
      ),
  )
  merged = _interactions_continuation.merge_unary_hops(
      [hop1_missing_input, hop2]
  )
  assert merged.usage.initial_input_tokens is None
  assert merged.usage.total_input_tokens == 500
  assert merged.usage.total_output_tokens == 50

  hop1_no_usage = interaction_types.Interaction(
      id="int_u1_none",
      status="requires_continuation",
      continuation_token="tok_u1",
      steps=[],
      usage=None,
  )
  merged_no_usage = _interactions_continuation.merge_unary_hops(
      [hop1_no_usage, hop2]
  )
  assert merged_no_usage.usage.initial_input_tokens is None
  assert merged_no_usage.usage.total_output_tokens == 30
