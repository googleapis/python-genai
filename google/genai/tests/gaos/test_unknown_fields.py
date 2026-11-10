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
"""Unknown-field round-trip tests for the Interactions API in the Python SDK.

The generated models preserve fields that are not declared in the SDK schema
(`preserveUnknownFields`). These tests pin down two consequences:

* Unknown request fields are forwarded to the API instead of being silently
  dropped, so the API can reject unsupported options (for example
  `transcription_config.diarization`, see
  https://github.com/googleapis/python-genai/issues/3162) and the caller gets
  an error instead of a silently degraded response.
* Unknown response fields survive parsing and serialization at every nesting
  level, including streamed events and responses merged by automatic
  continuation.
* In stateless multi-turn conversations (`store=False`), the previous turn's
  steps are sent back exactly as the server returned them, unknown fields
  included, whether the caller keeps the SDK objects or stores them as dicts.
"""

from __future__ import annotations

import base64
import copy
import json
from typing import Any

import pytest

# Import the generated types and errors through `_gaos` rather than the public
# `interactions`/`_interactions` modules: `run_tests.sh --private` rewrites
# `_gaos` imports to `_gaos_private`, so the classes match the client under test.
from ..._gaos.lib import compat_errors as _interactions
from ..._gaos.types import interactions
from . import conftest

_TRANSCRIBE_MODEL = "gemini-3.5-transcribe"
_AUDIO_INPUT = [{
    "type": "audio",
    "data": base64.b64encode(b"fake-wav-bytes").decode("ascii"),
    "mime_type": "audio/wav",
}]

_UNKNOWN_DIARIZATION_ERROR = {
    "error": {
        "code": 400,
        "message": (
            'Invalid JSON payload received. Unknown name "diarization" at'
            " 'generation_config.transcription_config': Cannot find field."
        ),
        "status": "INVALID_ARGUMENT",
    }
}

_INTERACTION_BODY = {
    "id": "v1_unknown_fields",
    "model": _TRANSCRIBE_MODEL,
    "status": "completed",
    "created": "2026-10-28T12:00:00Z",
    "updated": "2026-10-28T12:00:00Z",
    "future_top_level_field": {"nested": [1, 2, 3]},
    "steps": [{
        "type": "model_output",
        "future_step_field": "step-extra",
        "content": [{
            "type": "text",
            "text": "Hello there.",
            "future_content_field": True,
            "annotations": [{
                "type": "speech_metadata",
                "speaker": "spk_1",
                "start_index": 0,
                "end_index": 12,
                "future_annotation_field": 0.97,
            }],
        }],
    }],
}


def _transcription_config(sent_bodies: list[dict[str, Any]]) -> dict[str, Any]:
  assert len(sent_bodies) == 1
  return sent_bodies[0]["generation_config"]["transcription_config"]


def _bad_request(
    unused_req: conftest.CapturedRequest,
    unused_server: conftest.MockGaosServer,
) -> conftest.RawHttpResponse:
  return conftest.RawHttpResponse(
      body=json.dumps(_UNKNOWN_DIARIZATION_ERROR).encode("utf-8"), status=400
  )


def test_unknown_transcription_option_is_forwarded_and_rejection_surfaces(
    mock_gaos_server: conftest.MockGaosServer,
):
  """GH-3162: `diarization=True` must not be silently dropped by the SDK."""
  mock_gaos_server.handler_fn = _bad_request

  with pytest.raises(_interactions.BadRequestError) as exc_info:
    mock_gaos_server.client.interactions.create(
        model=_TRANSCRIBE_MODEL,
        input=_AUDIO_INPUT,
        generation_config={
            "transcription_config": {
                "mode": {"type": "verbatim"},
                "timestamp_granularities": ["word"],
                "diarization": True,
            }
        },
    )

  assert exc_info.value.status_code == 400
  assert "diarization" in str(exc_info.value)
  config = _transcription_config(mock_gaos_server.captured_bodies)
  assert config["diarization"] is True
  assert config["mode"] == {"type": "verbatim"}
  assert config["timestamp_granularities"] == ["word"]


def test_supported_diarization_mode_is_sent(
    mock_gaos_server: conftest.MockGaosServer,
):
  """Positive control: the supported `diarization_mode` field is sent as-is."""
  mock_gaos_server.default_response = _INTERACTION_BODY

  mock_gaos_server.client.interactions.create(
      model=_TRANSCRIBE_MODEL,
      input=_AUDIO_INPUT,
      generation_config={
          "transcription_config": {
              "mode": {"type": "verbatim"},
              "diarization_mode": "speaker",
          }
      },
  )

  config = _transcription_config(mock_gaos_server.captured_bodies)
  assert config == {"mode": {"type": "verbatim"}, "diarization_mode": "speaker"}


def test_unknown_document_content_field_is_forwarded(
    mock_gaos_server: conftest.MockGaosServer,
):
  """Content fields missing from the SDK schema reach the API unchanged."""
  mock_gaos_server.default_response = _INTERACTION_BODY

  mock_gaos_server.client.interactions.create(
      model="gemini-3.5-flash",
      input=[
          {
              "type": "document",
              "uri": "https://example.com/report.pdf",
              "mime_type": "application/pdf",
              "resolution": "low",
          },
          {"type": "text", "text": "Summarize this document."},
      ],
  )

  (body,) = mock_gaos_server.captured_bodies
  # The SDK wraps bare content lists into a single `user_input` step.
  assert body["input"][0]["content"][0] == {
      "type": "document",
      "uri": "https://example.com/report.pdf",
      "mime_type": "application/pdf",
      "resolution": "low",
  }


def test_unknown_response_fields_survive_parsing_and_serialization(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.default_response = _INTERACTION_BODY

  interaction = mock_gaos_server.client.interactions.create(
      model=_TRANSCRIBE_MODEL, input=_AUDIO_INPUT
  )

  assert isinstance(interaction, interactions.Interaction)
  step = interaction.steps[0]
  content = step.content[0]
  annotation = content.annotations[0]
  assert isinstance(annotation, interactions.SpeechAnnotation)
  assert annotation.speaker == "spk_1"

  # Unknown fields are accessible as attributes at every nesting level.
  assert interaction.future_top_level_field == {"nested": [1, 2, 3]}
  assert step.future_step_field == "step-extra"
  assert content.future_content_field is True
  assert annotation.future_annotation_field == 0.97

  # ...and survive every serialization entry point.
  for dumped in (
      interaction.model_dump(mode="json", exclude_none=True),
      json.loads(interaction.model_dump_json(exclude_none=True)),
      interaction.to_dict(),
      json.loads(interaction.to_json()),
  ):
    # `output_text` is an SDK convenience property, and `continuation_ids` is
    # added by automatic continuation; neither is part of the payload.
    dumped.pop("output_text", None)
    assert dumped.pop("continuation_ids", None) in (None, [interaction.id])
    assert dumped == _INTERACTION_BODY


# ---------------------------------------------------------------------------
# Stateless multi-turn: the previous turn is sent back as the next input.
# ---------------------------------------------------------------------------

_CHAT_MODEL = "gemini-3.5-flash"

# A previous turn as the server returns it: unknown fields on known steps,
# content blocks and annotations, followed by a step type the SDK does not
# know.
_PREVIOUS_STEPS = [
    {
        "type": "user_input",
        "future_step_field": {"origin": "client"},
        "content": [{"type": "text", "text": "Hi", "future_content_field": 1}],
    },
    {
        "type": "model_output",
        "future_step_field": "step-extra",
        "content": [{
            "type": "text",
            "text": "Hello there.",
            "future_content_field": True,
            "annotations": [{
                "type": "speech_metadata",
                "speaker": "spk_1",
                "start_index": 0,
                "end_index": 12,
                "future_annotation_field": 0.97,
            }],
        }],
    },
    {"type": "future_step_kind", "detail": "server-only"},
]

# The caller's next message, with unknown fields of its own.
_NEXT_TURN = {
    "type": "user_input",
    "future_step_field": "next",
    "content": [{"type": "text", "text": "And then?", "future_content_field": 2}],
}


def _chat_interaction(
    steps: list[dict[str, Any]], **fields: Any
) -> dict[str, Any]:
  return {
      "id": "v1_multi_turn",
      "model": _CHAT_MODEL,
      "status": "completed",
      "created": "2026-10-28T12:00:00Z",
      "updated": "2026-10-28T12:00:00Z",
      "future_top_level_field": {"turn": 1},
      "steps": copy.deepcopy(steps),
      **fields,
  }


_HISTORY_FORMS = pytest.mark.parametrize(
    "to_history",
    [
        lambda steps: list(steps),
        lambda steps: [step.to_dict() for step in steps],
        lambda steps: [step.model_dump() for step in steps],
        lambda steps: json.loads(
            json.dumps([step.model_dump(mode="json") for step in steps])
        ),
    ],
    ids=["objects", "to_dict", "model_dump", "stored_json"],
)


@_HISTORY_FORMS
def test_multi_turn_history_keeps_unknown_fields(
    mock_gaos_server: conftest.MockGaosServer, to_history
):
  """Turn 2 sends turn 1's steps back unchanged, plus a new user message."""
  mock_gaos_server.responses.append(_chat_interaction(_PREVIOUS_STEPS))
  mock_gaos_server.responses.append(_chat_interaction([]))

  first = mock_gaos_server.client.interactions.create(
      model=_CHAT_MODEL, input="Hi", store=False
  )
  mock_gaos_server.client.interactions.create(
      model=_CHAT_MODEL,
      input=[*to_history(first.steps), copy.deepcopy(_NEXT_TURN)],
      store=False,
  )

  sent = mock_gaos_server.captured_bodies[-1]["input"]
  assert sent == [*_PREVIOUS_STEPS, _NEXT_TURN]


@pytest.mark.asyncio
async def test_async_multi_turn_history_keeps_unknown_fields(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.responses.append(_chat_interaction(_PREVIOUS_STEPS))
  mock_gaos_server.responses.append(_chat_interaction([]))
  client = mock_gaos_server.client.aio

  first = await client.interactions.create(
      model=_CHAT_MODEL, input="Hi", store=False
  )
  await client.interactions.create(
      model=_CHAT_MODEL,
      input=[*first.steps, copy.deepcopy(_NEXT_TURN)],
      store=False,
  )

  sent = mock_gaos_server.captured_bodies[-1]["input"]
  assert sent == [*_PREVIOUS_STEPS, _NEXT_TURN]


def test_streamed_events_keep_unknown_fields_and_feed_the_next_turn(
    mock_gaos_server: conftest.MockGaosServer,
):
  """Streamed events round-trip; the completed interaction seeds turn 2."""
  events = [
      {
          "event_type": "interaction.created",
          "interaction": {
              "id": "v1_multi_turn",
              "status": "in_progress",
              "future_event_field": 1,
          },
      },
      {
          "event_type": "step.start",
          "index": 1,
          "step": {
              "type": "model_output",
              "future_step_field": "step-extra",
              "content": [],
          },
          "future_event_field": 2,
      },
      {
          "event_type": "step.delta",
          "index": 1,
          "delta": {"type": "text", "text": "Hello", "future_delta_field": 3},
      },
      {"event_type": "future.event_kind", "payload": {"a": 1}},
      {
          "event_type": "interaction.completed",
          "interaction": _chat_interaction(_PREVIOUS_STEPS),
      },
  ]
  mock_gaos_server.stream_payload = "".join(
      f"event: {event['event_type']}\ndata: {json.dumps(event)}\n\n"
      for event in events
  )

  received = list(
      mock_gaos_server.client.interactions.create(
          model=_CHAT_MODEL, input="Hi", stream=True, store=False
      )
  )

  assert [
      event.model_dump(mode="json", by_alias=True, exclude_none=True)
      for event in received
  ] == events

  mock_gaos_server.default_response = _chat_interaction([])
  mock_gaos_server.client.interactions.create(
      model=_CHAT_MODEL,
      input=[*received[-1].interaction.steps, copy.deepcopy(_NEXT_TURN)],
      store=False,
  )
  sent = mock_gaos_server.captured_bodies[-1]["input"]
  assert sent == [*_PREVIOUS_STEPS, _NEXT_TURN]


def test_automatic_continuation_keeps_unknown_fields_from_every_hop(
    mock_gaos_server: conftest.MockGaosServer,
):
  """Merging continuation hops keeps each hop's unknown fields and steps."""
  second_hop_steps = [
      {
          "type": "model_output",
          "future_step_field": "hop-2",
          "content": [
              {"type": "text", "text": "More.", "future_content_field": 3}
          ],
      },
      {"type": "future_step_kind", "detail": "hop-2"},
  ]
  mock_gaos_server.responses.append(
      _chat_interaction(
          _PREVIOUS_STEPS,
          id="v1_hop_1",
          status="requires_continuation",
          continuation_token="dG9rX2hvcF8x",
      )
  )
  mock_gaos_server.responses.append(
      _chat_interaction(
          second_hop_steps,
          id="v1_hop_2",
          future_top_level_field={"turn": 2},
      )
  )

  merged = mock_gaos_server.client.interactions.create(
      model=_CHAT_MODEL, input="Hi", automatic_continuation=True
  )

  assert len(mock_gaos_server.captured_bodies) == 2
  dumped = merged.to_dict()
  assert dumped["steps"] == [*_PREVIOUS_STEPS, *second_hop_steps]
  # Top-level fields describe the final hop.
  assert dumped["future_top_level_field"] == {"turn": 2}
