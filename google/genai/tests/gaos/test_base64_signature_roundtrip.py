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
"""Round-trip and bytes-encoding tests for Base64EncodedString signature fields.

Covers Speakeasy PR #200 (raw bytes encoding on Base64EncodedString /
Base64FileInput fields), ensuring:
1. Response -> request round-trips preserve `signature` strings verbatim across
   model objects, `model_dump()`, `model_dump(mode="json")`, and
   `json.loads(model_dump_json())` (both sync and async).
2. Raw binary bytes (`base64.b64decode(sig)`) re-encode to the original base64
   string (sync and async).
3. ASCII base64 bytes (`sig.encode("ascii")`) are treated as raw bytes and
   base64-encoded (matching `bytes` = raw content across `Base64FileInput`
   fields; callers passing pre-encoded base64 must pass `str`).
4. The private `_EncodedBase64` `str` subclass preserves `model_dump()` output,
   equality, and subsequent round-trips without double-encoding.
"""

from __future__ import annotations

import base64
import copy
import json
from typing import Any

import pytest

# Import generated types through `_gaos` so `run_tests.sh --private` rewrites
# `_gaos` -> `_gaos_private` cleanly.
from ..._gaos.types import base64fileinput
from ..._gaos.types import interactions
from . import conftest

_MODEL = "gemini-3.5-flash"

_THOUGHT_SIG_RAW = b"\x80\xff\x01thought-signature\xfe\x00"
_THOUGHT_SIG = base64.b64encode(_THOUGHT_SIG_RAW).decode("ascii")

_SEARCH_CALL_SIG_RAW = b"\x90\xab\xcdsearch-call-signature\xef"
_SEARCH_CALL_SIG = base64.b64encode(_SEARCH_CALL_SIG_RAW).decode("ascii")

_SEARCH_RESULT_SIG_RAW = b"\x01\x02\xfesearch-result-signature\xff"
_SEARCH_RESULT_SIG = base64.b64encode(_SEARCH_RESULT_SIG_RAW).decode("ascii")

_RESPONSE_STEPS = [
    {
        "type": "thought",
        "signature": _THOUGHT_SIG,
        "summary": [{"type": "text", "text": "Checking weather."}],
    },
    {
        "type": "google_search_call",
        "id": "call_1",
        "arguments": {"queries": ["weather in paris"]},
        "signature": _SEARCH_CALL_SIG,
    },
    {
        "type": "google_search_result",
        "call_id": "call_1",
        "result": [{"title": "Paris Weather", "url": "https://example.com"}],
        "signature": _SEARCH_RESULT_SIG,
    },
    {
        "type": "model_output",
        "content": [{"type": "text", "text": "It is sunny in Paris."}],
    },
]

_EXPECTED_SIGNATURES = {
    "thought": _THOUGHT_SIG,
    "google_search_call": _SEARCH_CALL_SIG,
    "google_search_result": _SEARCH_RESULT_SIG,
}


def _interaction(**fields: Any) -> dict[str, Any]:
  return {
      "id": "v1_sig_roundtrip",
      "model": _MODEL,
      "status": "completed",
      "created": "2026-10-28T12:00:00Z",
      "updated": "2026-10-28T12:00:00Z",
      **fields,
  }


def _roundtrip_forms(
    interaction: interactions.Interaction,
) -> dict[str, Any]:
  assert interaction.steps is not None
  return {
      "model_objects": interaction.steps,
      "model_dump_steps": [s.model_dump() for s in interaction.steps],
      "model_dump_interaction": interaction.model_dump()["steps"],
      "model_dump_json_mode": [
          s.model_dump(mode="json") for s in interaction.steps
      ],
      "json_loads_model_dump_json": json.loads(interaction.model_dump_json())[
          "steps"
      ],
  }


def _assert_captured_signatures(sent_input: list[dict[str, Any]]) -> None:
  by_type = {step["type"]: step for step in sent_input}
  for step_type, expected_sig in _EXPECTED_SIGNATURES.items():
    assert by_type[step_type]["signature"] == expected_sig


@pytest.mark.parametrize(
    "form_name",
    [
        "model_objects",
        "model_dump_steps",
        "model_dump_interaction",
        "model_dump_json_mode",
        "json_loads_model_dump_json",
    ],
)
def test_signature_response_to_request_roundtrip_sync(
    mock_gaos_server: conftest.MockGaosServer,
    form_name: str,
) -> None:
  mock_gaos_server.responses.append(
      _interaction(steps=copy.deepcopy(_RESPONSE_STEPS))
  )
  first = mock_gaos_server.client.interactions.create(
      model=_MODEL, input="Weather in Paris?", store=False
  )
  history = _roundtrip_forms(first)[form_name]

  mock_gaos_server.responses.append(_interaction(steps=[]))
  mock_gaos_server.client.interactions.create(
      model=_MODEL, input=history, store=False
  )
  _assert_captured_signatures(mock_gaos_server.captured_bodies[-1]["input"])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "form_name",
    [
        "model_objects",
        "model_dump_steps",
        "model_dump_interaction",
        "model_dump_json_mode",
        "json_loads_model_dump_json",
    ],
)
async def test_signature_response_to_request_roundtrip_async(
    mock_gaos_server: conftest.MockGaosServer,
    form_name: str,
) -> None:
  mock_gaos_server.responses.append(
      _interaction(steps=copy.deepcopy(_RESPONSE_STEPS))
  )
  first = await mock_gaos_server.client.aio.interactions.create(
      model=_MODEL, input="Weather in Paris?", store=False
  )
  history = _roundtrip_forms(first)[form_name]

  mock_gaos_server.responses.append(_interaction(steps=[]))
  await mock_gaos_server.client.aio.interactions.create(
      model=_MODEL, input=history, store=False
  )
  _assert_captured_signatures(mock_gaos_server.captured_bodies[-1]["input"])


@pytest.mark.parametrize(
    "bytes_factory",
    [
        lambda raw: raw,
        bytearray,
        memoryview,
    ],
    ids=["bytes", "bytearray", "memoryview"],
)
def test_signature_raw_bytes_reencodes_to_original_string_sync(
    mock_gaos_server: conftest.MockGaosServer,
    bytes_factory: Any,
) -> None:
  steps = [
      interactions.ThoughtStep(
          signature=bytes_factory(base64.b64decode(_THOUGHT_SIG))
      ),
      interactions.GoogleSearchCallStep(
          id="call_1",
          arguments=interactions.GoogleSearchCallArguments(queries=["paris"]),
          signature=bytes_factory(base64.b64decode(_SEARCH_CALL_SIG)),
      ),
      {
          "type": "google_search_result",
          "call_id": "call_1",
          "result": [{"title": "Paris", "url": "https://example.com"}],
          "signature": bytes_factory(base64.b64decode(_SEARCH_RESULT_SIG)),
      },
  ]
  mock_gaos_server.responses.append(_interaction(steps=[]))
  mock_gaos_server.client.interactions.create(
      model=_MODEL, input=steps, store=False
  )
  _assert_captured_signatures(mock_gaos_server.captured_bodies[-1]["input"])


@pytest.mark.asyncio
async def test_signature_raw_bytes_reencodes_to_original_string_async(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  steps = [
      interactions.ThoughtStep(signature=base64.b64decode(_THOUGHT_SIG)),
      interactions.GoogleSearchCallStep(
          id="call_1",
          arguments=interactions.GoogleSearchCallArguments(queries=["paris"]),
          signature=base64.b64decode(_SEARCH_CALL_SIG),
      ),
      {
          "type": "google_search_result",
          "call_id": "call_1",
          "result": [{"title": "Paris", "url": "https://example.com"}],
          "signature": base64.b64decode(_SEARCH_RESULT_SIG),
      },
  ]
  mock_gaos_server.responses.append(_interaction(steps=[]))
  await mock_gaos_server.client.aio.interactions.create(
      model=_MODEL, input=steps, store=False
  )
  _assert_captured_signatures(mock_gaos_server.captured_bodies[-1]["input"])


def test_ascii_base64_bytes_are_treated_as_raw_bytes(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  """Pins that all bytes inputs (including ASCII base64 bytes) are encoded.

  Callers passing an already base64-encoded signature must pass `str`, not
  `bytes`; passing `sig.encode("ascii")` treats those bytes as raw binary
  content and base64-encodes them, matching `Base64FileInput` semantics.
  """
  ascii_bytes = _THOUGHT_SIG.encode("ascii")
  expected_encoded = base64.b64encode(ascii_bytes).decode("ascii")

  step = interactions.ThoughtStep(signature=ascii_bytes)
  assert step.signature == expected_encoded
  assert step.signature != _THOUGHT_SIG

  mock_gaos_server.responses.append(_interaction(steps=[]))
  mock_gaos_server.client.interactions.create(
      model=_MODEL,
      input=[{"type": "thought", "signature": ascii_bytes}],
      store=False,
  )
  sent_step = mock_gaos_server.captured_bodies[-1]["input"][0]
  assert sent_step["signature"] == expected_encoded


def test_encoded_base64_subclass_preserves_equality_dump_and_roundtrip(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  thought = interactions.ThoughtStep(signature=_THOUGHT_SIG_RAW)
  search_call = interactions.GoogleSearchCallStep(
      id="call_1",
      arguments=interactions.GoogleSearchCallArguments(queries=["paris"]),
      signature=_SEARCH_CALL_SIG_RAW,
  )

  # encode_base64_file_input returns _EncodedBase64 for raw bytes, and
  # Pydantic's str validator normalizes it back to an exact plain str so the
  # private subclass never leaks onto the model or into model_dump().
  encoded_raw = base64fileinput.encode_base64_file_input(_THOUGHT_SIG_RAW)
  assert isinstance(encoded_raw, base64fileinput._EncodedBase64)
  assert encoded_raw == _THOUGHT_SIG

  assert type(thought.signature) is str
  assert type(thought.model_dump()["signature"]) is str
  assert thought.signature == _THOUGHT_SIG
  assert _THOUGHT_SIG == thought.signature
  assert hash(thought.signature) == hash(_THOUGHT_SIG)

  # Comparing against a model constructed from str succeeds.
  thought_from_str = interactions.ThoughtStep(signature=_THOUGHT_SIG)
  assert thought == thought_from_str
  assert thought.model_dump() == thought_from_str.model_dump()
  assert thought.model_dump(mode="json") == thought_from_str.model_dump(
      mode="json"
  )
  assert json.loads(thought.model_dump_json()) == json.loads(
      thought_from_str.model_dump_json()
  )

  # Re-sending dumped forms of bytes-constructed models must NOT double-encode.
  for payload in (
      [thought, search_call],
      [thought.model_dump(), search_call.model_dump()],
      [thought.model_dump(mode="json"), search_call.model_dump(mode="json")],
      [
          json.loads(thought.model_dump_json()),
          json.loads(search_call.model_dump_json()),
      ],
  ):
    mock_gaos_server.responses.append(_interaction(steps=[]))
    mock_gaos_server.client.interactions.create(
        model=_MODEL, input=payload, store=False
    )
    sent = mock_gaos_server.captured_bodies[-1]["input"]
    assert sent[0]["signature"] == _THOUGHT_SIG
    assert sent[1]["signature"] == _SEARCH_CALL_SIG
