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
"""Serialization requirements for the generated Interactions models.

These tests describe how the generated models must behave, including the
behavior added in speakeasy-api/openapi-generation v2.955.0:

* speakeasy-api/openapi-generation#168: honour dump filters (`include`,
  `exclude`, `exclude_unset`, `exclude_defaults`) when `exclude_none=True`.
* speakeasy-api/openapi-generation#169: serialize unknown open-union variants
  as their raw payload.
* speakeasy-api/openapi-generation#170: pick the matching open union inside
  unions of open unions.
* speakeasy-api/openapi-generation#171: accept unknown discriminator values in
  request input when `preserveUnknownFields` is enabled.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import pydantic
import pytest

# Import the generated types and errors through `_gaos` rather than the public
# `interactions`/`_interactions` modules: `run_tests.sh --private` rewrites
# `_gaos` imports to `_gaos_private`, so the classes match the client under test.
from ..._gaos import utils as gaos_utils
from ..._gaos.lib import compat_errors as _interactions
from ..._gaos.types import interactions
from . import conftest


_MODEL = "gemini-3.5-flash"
_URI = "https://example.com/report.pdf"

_UNKNOWN_ANNOTATION = {"type": "future_annotation_kind", "score": 0.9}
_UNKNOWN_CONTENT = {"type": "future_content_kind", "payload": {"a": [1, None]}}
_UNKNOWN_STEP = {"type": "future_step_kind", "detail": "server-only"}

# A previous turn as the server returns it: one model output step whose text
# block carries an annotation type this SDK does not know, followed by a step
# with a content block type and a step type this SDK does not know.
_PREVIOUS_STEPS = [
    {
        "type": "model_output",
        "content": [{
            "type": "text",
            "text": "Hello there.",
            "annotations": [_UNKNOWN_ANNOTATION],
        }],
    },
    {"type": "model_output", "content": [_UNKNOWN_CONTENT]},
    _UNKNOWN_STEP,
]


def _interaction(**fields: Any) -> dict[str, Any]:
  return {
      "id": "v1_requirements",
      "model": _MODEL,
      "status": "completed",
      "created": "2026-10-28T12:00:00Z",
      "updated": "2026-10-28T12:00:00Z",
      **fields,
  }


def _previous_turn(
    server: conftest.MockGaosServer,
) -> interactions.Interaction:
  """Returns an Interaction parsed from a real SDK response."""
  server.responses.append(_interaction(steps=copy.deepcopy(_PREVIOUS_STEPS)))
  return server.client.interactions.create(model=_MODEL, input="Hi")


def _send_history(server: conftest.MockGaosServer, history: Any) -> Any:
  """Sends `history` back as the next turn's input; returns the sent input."""
  server.responses.append(_interaction(steps=[]))
  server.client.interactions.create(model=_MODEL, input=history, store=False)
  return server.captured_bodies[-1]["input"]


# ---------------------------------------------------------------------------
# Unknown open-union variants: serialization.
# ---------------------------------------------------------------------------


def test_unknown_variants_are_parsed_into_unknown_classes(
    mock_gaos_server: conftest.MockGaosServer,
):
  steps = _previous_turn(mock_gaos_server).steps

  annotation = steps[0].content[0].annotations[0]
  assert isinstance(annotation, interactions.UnknownAnnotation)
  assert annotation.raw == _UNKNOWN_ANNOTATION
  assert isinstance(steps[1].content[0], interactions.UnknownContent)
  assert steps[1].content[0].raw == _UNKNOWN_CONTENT
  assert isinstance(steps[2], interactions.UnknownStep)
  assert steps[2].raw == _UNKNOWN_STEP


def test_unknown_variants_to_dict_and_to_json_return_raw_payload(
    mock_gaos_server: conftest.MockGaosServer,
):
  interaction = _previous_turn(mock_gaos_server)

  assert interaction.to_dict()["steps"] == _PREVIOUS_STEPS
  assert json.loads(interaction.to_json())["steps"] == _PREVIOUS_STEPS


@pytest.mark.parametrize(
    "dump",
    [
        lambda m: m.model_dump(),
        lambda m: m.model_dump(mode="json"),
        lambda m: m.model_dump(by_alias=True),
        lambda m: json.loads(m.model_dump_json()),
    ],
    ids=["python", "json", "by_alias", "model_dump_json"],
)
def test_unknown_variants_model_dump_returns_raw_payload(
    mock_gaos_server: conftest.MockGaosServer, dump
):
  interaction = _previous_turn(mock_gaos_server)

  assert dump(interaction)["steps"] == _PREVIOUS_STEPS
  assert dump(interaction.steps[2]) == _UNKNOWN_STEP


def test_previous_steps_sent_back_as_objects_use_raw_payload(
    mock_gaos_server: conftest.MockGaosServer,
):
  """Stateless multi-turn (`store=False`) with the parsed step objects."""
  steps = _previous_turn(mock_gaos_server).steps

  assert _send_history(mock_gaos_server, steps) == _PREVIOUS_STEPS


def test_request_body_never_contains_the_sdk_wrapper(
    mock_gaos_server: conftest.MockGaosServer,
):
  steps = _previous_turn(mock_gaos_server).steps

  sent = json.dumps(_send_history(mock_gaos_server, steps))
  assert '"UNKNOWN"' not in sent
  assert "is_unknown" not in sent


# ---------------------------------------------------------------------------
# Unknown open-union variants: request input built from stored history.
# With preserveUnknownFields, request input accepts unknown discriminator
# values (speakeasy-api/openapi-generation#171).
# `client.interactions.create` validates its arguments with `utils.unmarshal`,
# which passes no validation context, so this must hold without a context flag.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "store",
    [
        lambda m: m.to_dict()["steps"],
        lambda m: json.loads(m.to_json())["steps"],
        lambda m: m.model_dump(mode="json", by_alias=True)["steps"],
        # The documented stateless sample: history.append(step.model_dump()).
        lambda m: [step.model_dump() for step in m.steps],
    ],
    ids=["to_dict", "to_json", "model_dump_json_mode", "docs_step_model_dump"],
)
def test_previous_steps_sent_back_from_stored_dicts_use_raw_payload(
    mock_gaos_server: conftest.MockGaosServer, store
):
  """Stateless multi-turn with history persisted as JSON between requests."""
  stored = json.loads(json.dumps(store(_previous_turn(mock_gaos_server))))

  assert _send_history(mock_gaos_server, stored) == _PREVIOUS_STEPS


def test_request_models_accept_unknown_variants_without_context():
  """`Model(...)` and `model_validate` without context must accept them."""
  built = interactions.CreateModelInteraction(
      model=_MODEL, input=copy.deepcopy(_PREVIOUS_STEPS)
  )
  validated = interactions.CreateModelInteraction.model_validate(
      {"model": _MODEL, "input": copy.deepcopy(_PREVIOUS_STEPS)}
  )

  for request in (built, validated):
    body = json.loads(
        gaos_utils.marshal_json(request, interactions.CreateModelInteraction)
    )
    assert body["input"] == _PREVIOUS_STEPS


@pytest.mark.parametrize(
    "invalid_step",
    [
        {"type": "model_output", "content": [{"type": "text", "txt": "typo"}]},
        {"type": "model_output", "content": [{"type": "text", "text": 42}]},
    ],
    ids=["missing_required_field", "wrong_field_type"],
)
def test_known_variant_with_invalid_payload_still_raises(invalid_step):
  """Typos in known variants must fail locally, never be sent as unknown."""
  with pytest.raises(pydantic.ValidationError):
    interactions.CreateModelInteraction.model_validate(
        {"model": _MODEL, "input": [invalid_step]}
    )


_VALID_USER_INPUT = {
    "type": "user_input",
    "content": [{"type": "text", "text": "hi"}],
}

# `input` is Union[Content, List[Step], List[Content], str]. A value whose
# `type` is known to one of these members must validate as that member: it must
# never be accepted as another member's unknown variant. These shapes have no
# single owning member (mixed lists, a step outside a list), which is where a
# union-of-open-unions dispatch can skip its checks.
_MALFORMED_INPUTS = [
    pytest.param(
        [{"type": "user_input", "content": "not-a-list"}],
        id="invalid_known_step",
    ),
    pytest.param([{"type": "text", "text": 3}], id="invalid_known_content"),
    pytest.param(
        [
            {"type": "user_input", "content": "not-a-list"},
            {"type": "text", "text": "hi"},
        ],
        id="mixed_invalid_step_and_valid_content",
    ),
    pytest.param(
        [_VALID_USER_INPUT, {"type": "text", "text": 3}],
        id="mixed_valid_step_and_invalid_content",
    ),
    pytest.param(
        [_VALID_USER_INPUT, {"type": "text", "text": "hi"}],
        id="mixed_valid_step_and_valid_content",
    ),
    pytest.param(_VALID_USER_INPUT, id="single_step_outside_list"),
]


@pytest.mark.parametrize("malformed", _MALFORMED_INPUTS)
def test_malformed_input_shapes_still_raise(malformed):
  with pytest.raises(pydantic.ValidationError):
    interactions.CreateModelInteraction.model_validate(
        {"model": _MODEL, "input": copy.deepcopy(malformed)}
    )


@pytest.mark.parametrize("malformed", _MALFORMED_INPUTS)
def test_malformed_input_shapes_are_not_sent(
    mock_gaos_server: conftest.MockGaosServer, malformed
):
  mock_gaos_server.default_response = _interaction(steps=[])

  with pytest.raises(Exception):
    mock_gaos_server.client.interactions.create(
        model=_MODEL, input=copy.deepcopy(malformed)
    )
  assert not mock_gaos_server.captured_bodies


# ---------------------------------------------------------------------------
# Dump filters combined with exclude_none=True.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("build", "kwargs", "expected"),
    [
        (
            lambda: interactions.DocumentContent(
                uri=_URI, mime_type="application/pdf"
            ),
            {"include": {"uri"}},
            {"uri": _URI},
        ),
        (
            lambda: interactions.DocumentContent(
                uri=_URI, mime_type="application/pdf"
            ),
            {"exclude": {"type"}},
            {"uri": _URI, "mime_type": "application/pdf"},
        ),
        (
            lambda: interactions.TextContent(text="secret"),
            {"exclude": {"text"}},
            {"type": "text"},
        ),
        (
            lambda: interactions.TextContent(text="hi"),
            {"exclude_defaults": True},
            {"text": "hi"},
        ),
        (
            lambda: interactions.ModelOutputStep(
                content=[interactions.TextContent(text="secret")]
            ),
            {"exclude": {"content": {"__all__": {"text"}}}},
            {"type": "model_output", "content": [{"type": "text"}]},
        ),
    ],
    ids=[
        "include",
        "exclude_const",
        "exclude_required",
        "exclude_defaults",
        "nested_exclude",
    ],
)
def test_dump_filters_are_honoured_with_exclude_none(build, kwargs, expected):
  assert build().model_dump(exclude_none=True, **kwargs) == expected


@pytest.mark.parametrize(
    ("build", "kwargs", "expected"),
    [
        (
            lambda: interactions.DocumentContent(uri=_URI),
            {"include": {"uri"}},
            {"uri": _URI},
        ),
        (
            lambda: interactions.TextContent(text="secret"),
            {"exclude": {"text"}},
            {"type": "text"},
        ),
    ],
    ids=["include", "exclude_required"],
)
def test_dump_filters_are_honoured_without_exclude_none(
    build, kwargs, expected
):
  assert build().model_dump(**kwargs) == expected


def test_plain_exclude_none_dump_round_trips():
  original = interactions.ModelOutputStep(
      content=[
          interactions.TextContent(text="hi"),
          interactions.DocumentContent(uri=_URI),
      ]
  )

  dumped = original.model_dump(by_alias=True, exclude_none=True)

  assert dumped == {
      "type": "model_output",
      "content": [
          {"type": "text", "text": "hi"},
          {"type": "document", "uri": _URI},
      ],
  }
  assert interactions.ModelOutputStep.model_validate(dumped) == original


def test_request_body_omits_optional_fields_set_to_none():
  body = gaos_utils.marshal_json(
      interactions.DocumentContent(uri=_URI, mime_type=None),
      interactions.DocumentContent,
  )
  assert json.loads(body) == {"type": "document", "uri": _URI}


# ---------------------------------------------------------------------------
# Unions of open unions: InteractionsInput.
# ---------------------------------------------------------------------------


def _parsed_input(server: conftest.MockGaosServer, value: Any) -> Any:
  server.responses.append(_interaction(input=value))
  return server.client.interactions.create(model=_MODEL, input="Hi").input


def test_response_input_steps_parse_as_steps(
    mock_gaos_server: conftest.MockGaosServer,
):
  value = _parsed_input(
      mock_gaos_server,
      [
          {"type": "user_input", "content": [{"type": "text", "text": "hi"}]},
          {"type": "model_output", "content": [{"type": "text", "text": "yo"}]},
      ],
  )
  assert [type(v) for v in value] == [
      interactions.UserInputStep,
      interactions.ModelOutputStep,
  ]


def test_response_input_single_content_parses_as_content(
    mock_gaos_server: conftest.MockGaosServer,
):
  value = _parsed_input(mock_gaos_server, {"type": "text", "text": "hi"})
  assert isinstance(value, interactions.TextContent)


def test_response_input_content_list_parses_as_content(
    mock_gaos_server: conftest.MockGaosServer,
):
  value = _parsed_input(
      mock_gaos_server,
      [{"type": "text", "text": "hi"}, {"type": "document", "uri": _URI}],
  )
  assert [type(v) for v in value] == [
      interactions.TextContent,
      interactions.DocumentContent,
  ]


def test_response_input_content_list_with_unknown_block_stays_content(
    mock_gaos_server: conftest.MockGaosServer,
):
  value = _parsed_input(
      mock_gaos_server,
      [{"type": "text", "text": "hi"}, copy.deepcopy(_UNKNOWN_CONTENT)],
  )
  assert [type(v) for v in value] == [
      interactions.TextContent,
      interactions.UnknownContent,
  ]


def test_request_content_list_is_sent_as_content(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.default_response = _interaction(steps=[])

  mock_gaos_server.client.interactions.create(
      model=_MODEL, input=[{"type": "text", "text": "hi"}]
  )

  (body,) = mock_gaos_server.captured_bodies
  assert body["input"][0]["content"] == [{"type": "text", "text": "hi"}]


# ---------------------------------------------------------------------------
# Unknown fields set to None (documented behavior, no generator change)
# ---------------------------------------------------------------------------


def test_unknown_field_set_to_none_is_sent_as_null():
  body = gaos_utils.marshal_json(
      interactions.DocumentContent(uri=_URI, resolution=None),
      interactions.DocumentContent,
  )
  assert json.loads(body) == {
      "type": "document",
      "uri": _URI,
      "resolution": None,
  }


def test_api_rejection_of_unknown_field_surfaces_as_bad_request(
    mock_gaos_server: conftest.MockGaosServer,
):
  """An unknown value the API rejects surfaces as a BadRequestError."""

  def reject(
      unused_req: conftest.CapturedRequest,
      unused_server: conftest.MockGaosServer,
  ) -> conftest.RawHttpResponse:
    return conftest.RawHttpResponse(
        body=json.dumps({
            "error": {
                "code": 400,
                "message": "Unknown name \"resolution\".",
                "status": "INVALID_ARGUMENT",
            }
        }).encode("utf-8"),
        status=400,
    )

  mock_gaos_server.handler_fn = reject
  with pytest.raises(_interactions.BadRequestError):
    mock_gaos_server.client.interactions.create(
        model=_MODEL,
        input=[{"type": "document", "uri": _URI, "resolution": None}],
    )
  assert mock_gaos_server.captured_bodies[-1]["input"][0]["content"][0] == {
      "type": "document",
      "uri": _URI,
      "resolution": None,
  }
