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

import json
from unittest import mock

import httpx
import pytest

from ... import client as client_lib
from ..._gaos import google_genai as gaos_google_genai
from ..._gaos.types import basemodel as gaos_basemodel
from ..._gaos.types.interactions import documentcontent as gaos_documentcontent
from ..._gaos.types.interactions import dynamicagentconfig as gaos_dynamicagentconfig
from ..._gaos.types.interactions import generationconfig as gaos_generationconfig
from ..._gaos.types.interactions import interaction as gaos_interaction
from ..._gaos.utils import serializers as gaos_serializers


pytest_plugins = ("pytest_asyncio",)


def test_client_timeout():
  with mock.patch.object(
      gaos_google_genai, "GenAI", spec_set=True
  ) as mock_genai:
    mock_client = mock.Mock()
    mock_genai.return_value = mock_client

    client = client_lib.Client(
        api_key="placeholder",
        http_options={"api_version": "v1alpha", "timeout": 5000},
    )

    # Trigger client build
    _ = client.interactions.with_raw_response

    mock_genai.assert_called_once_with(
        security=mock.ANY,
        api_version=mock.ANY,
        user_project=mock.ANY,
        server_url=mock.ANY,
        client=mock.ANY,
        timeout_ms=5000,
        retry_config=mock.ANY,
    )


@pytest.mark.asyncio
async def test_async_client_timeout():
  with mock.patch.object(
      gaos_google_genai, "AsyncGenAI", spec_set=True
  ) as mock_async_genai:
    mock_client = mock.Mock()
    mock_async_genai.return_value = mock_client

    client = client_lib.Client(
        api_key="placeholder",
        http_options={"api_version": "v1alpha", "timeout": 5000},
    )

    # Trigger client build
    _ = client.aio.interactions.with_raw_response

    mock_async_genai.assert_called_once_with(
        security=mock.ANY,
        api_version=mock.ANY,
        user_project=mock.ANY,
        server_url=mock.ANY,
        async_client=mock.ANY,
        timeout_ms=5000,
        retry_config=mock.ANY,
    )


def test_client_vertex_default_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha"},
  )
  sdk_client = client.interactions.sdk_configuration.client
  assert sdk_client is not None
  # Default on Vertex should match GenAI default (timeout=None, no 5s timeout)
  assert sdk_client.timeout == httpx.Timeout(None)
  assert sdk_client.timeout != httpx.Timeout(5.0)


def test_client_vertex_explicit_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha", "timeout": 12000},
  )
  interactions_client = client.interactions
  assert interactions_client.sdk_configuration.timeout_ms == 12000


@pytest.mark.asyncio
async def test_async_client_vertex_default_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha"},
  )
  async_sdk_client = client.aio.interactions.sdk_configuration.async_client
  assert async_sdk_client is not None
  assert async_sdk_client.timeout == httpx.Timeout(None)
  assert async_sdk_client.timeout != httpx.Timeout(5.0)


@pytest.mark.asyncio
async def test_async_client_vertex_explicit_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha", "timeout": 15000},
  )
  async_interactions_client = client.aio.interactions
  assert async_interactions_client.sdk_configuration.timeout_ms == 15000


def test_client_genai_default_timeout():
  client = client_lib.Client(
      api_key="placeholder",
      http_options={"api_version": "v1alpha"},
  )
  sdk_client = client.interactions.sdk_configuration.client
  assert sdk_client is not None
  assert sdk_client.timeout == httpx.Timeout(None)
  assert sdk_client.timeout != httpx.Timeout(5.0)


@pytest.mark.asyncio
async def test_async_client_genai_default_timeout():
  client = client_lib.Client(
      api_key="placeholder",
      http_options={"api_version": "v1alpha"},
  )
  async_sdk_client = client.aio.interactions.sdk_configuration.async_client
  assert async_sdk_client is not None
  assert async_sdk_client.timeout == httpx.Timeout(None)
  assert async_sdk_client.timeout != httpx.Timeout(5.0)



@pytest.mark.filterwarnings("error")
def test_unrecognized_model_serialization():
  from ..._gaos.types.interactions.createmodelinteraction import CreateModelInteraction
  # This shouldn't raise a Pydantic serialization error due to UnrecognizedStr
  obj = CreateModelInteraction(model="gemini-3.5-flash", input="hello")
  dumped = obj.model_dump()
  assert dumped["model"] == "gemini-3.5-flash"


@pytest.mark.filterwarnings("error")
def test_unrecognized_model_request_serialization():
  from ..._gaos.models.createinteraction import CreateInteractionRequest
  from ..._gaos.types.interactions.createmodelinteraction import CreateModelInteraction
  body = CreateModelInteraction(model="gemini-3.5-flash", input="hello")
  req = CreateInteractionRequest(body=body)
  dumped = req.model_dump()
  assert dumped["body"]["model"] == "gemini-3.5-flash"


def test_allowlist_entry_with_dict_transform():
  from ..._gaos.types.interactions.allowlistentry import AllowlistEntry

  # Should construct successfully with a single dict
  entry = AllowlistEntry(
      domain="github.com", transform={"Authorization": "Bearer TOKEN"}
  )
  assert entry.domain == "github.com"
  assert entry.transform == {"Authorization": "Bearer TOKEN"}

  # Serialization should preserve it as a dict
  dumped = entry.model_dump()
  assert dumped["transform"] == {"Authorization": "Bearer TOKEN"}


def test_allowlist_entry_with_list_transform():
  from ..._gaos.types.interactions.allowlistentry import AllowlistEntry

  # Should construct successfully with a list of dicts
  entry = AllowlistEntry(
      domain="github.com", transform=[{"Authorization": "Bearer TOKEN"}]
  )
  assert entry.domain == "github.com"
  assert entry.transform == [{"Authorization": "Bearer TOKEN"}]

  # Serialization should preserve it as a list
  dumped = entry.model_dump()
  assert dumped["transform"] == [{"Authorization": "Bearer TOKEN"}]


def test_interaction_model_construct():
  """Tests Interaction.model_construct binding and legacy lyria coercion."""
  interaction = gaos_interaction.Interaction.model_construct(id="x")
  assert isinstance(interaction, gaos_interaction.Interaction)
  assert interaction.id == "x"

  lyria_interaction = gaos_interaction.Interaction.model_construct(
      id="y",
      model="lyria-3-pro-preview",
      outputs=[{"type": "audio", "data": "abc"}],
  )
  assert isinstance(lyria_interaction, gaos_interaction.Interaction)
  assert lyria_interaction.id == "y"
  assert lyria_interaction.steps == [
      {"type": "model_output", "content": [{"type": "audio", "data": "abc"}]}
  ]


def test_interaction_lenient_parsing():
  """Tests lenient response parsing when required fields are omitted."""
  # Payload missing required `status` field falls back to
  # _construct_model_lenient, which calls Interaction.model_construct(...).
  parsed = gaos_serializers.construct_unvalidated(
      {"id": "x"}, gaos_interaction.Interaction
  )
  assert isinstance(parsed, gaos_interaction.Interaction)
  assert parsed.id == "x"


def test_interactions_default_timeout():
  from ... import _interactions

  assert _interactions.DEFAULT_TIMEOUT == httpx.Timeout(
      timeout=None, connect=5.0
  )


def _thought(signature):
  return {
      "type": "thought",
      "signature": signature,
      "summary": [{"type": "text", "text": f"summary {signature}"}],
  }


def _text(value):
  return {"type": "model_output", "content": [{"type": "text", "text": value}]}


_FUNCTION_CALL = {
    "type": "function_call",
    "id": "call_1",
    "name": "get_weather",
    "arguments": {"city": "Mountain View"},
}
_FUNCTION_RESULT = {
    "type": "function_result",
    "call_id": "call_1",
    "name": "get_weather",
    "result": "Sunny",
}


@pytest.mark.parametrize(
    "steps,expected",
    [
        pytest.param(
            [
                _thought("a"),
                _text("First part. "),
                _thought("b"),
                _text("Second part. "),
                {"type": "model_output"},
                _text("Third part."),
                _thought("c"),
            ],
            "First part. Second part. Third part.",
            id="long_decode_multi_step",
        ),
        pytest.param(
            [
                _text("Before tool call. "),
                _FUNCTION_CALL,
                _FUNCTION_RESULT,
                _thought("a"),
                _text("Final part 1. "),
                _thought("b"),
                _text("Final part 2."),
                {**_FUNCTION_CALL, "id": "call_trailing"},
            ],
            "Final part 1. Final part 2.",
            id="tool_boundary",
        ),
        pytest.param(
            [
                _text("Previous turn. "),
                {
                    "type": "user_input",
                    "content": [{"type": "text", "text": "Next question"}],
                },
                _thought("a"),
                _text("A"),
                _thought("b"),
                _text("B"),
            ],
            "AB",
            id="user_input_boundary",
        ),
        pytest.param(
            [
                {
                    "type": "model_output",
                    "content": [
                        {"type": "text", "text": "X"},
                        {
                            "type": "image",
                            "data": "aW1hZ2U=",
                            "mime_type": "image/png",
                        },
                    ],
                },
                _thought("a"),
                _text("Y"),
            ],
            "Y",
            id="non_text_barrier",
        ),
    ],
)
def test_output_text_across_steps(steps, expected):
  payload = {"id": "v1_123", "status": "completed", "steps": steps}

  interaction = gaos_interaction.Interaction.model_validate(payload)
  assert interaction.output_text == expected

  wrapped = gaos_google_genai._add_output_properties_if_interaction(payload)  # pylint: disable=protected-access
  assert wrapped["output_text"] == expected


def test_extra_fields_preserved_in_model_serialization():
  nested = gaos_generationconfig.GenerationConfig(
      temperature=0.25,
      inner_extra="kept",
  )
  doc = gaos_documentcontent.DocumentContent(
      type="document",
      data="aGVsbG8=",
      mime_type="application/pdf",
      resolution="low",
      null_extra=None,
      unset_extra=gaos_basemodel.UNSET,
      nested_extra=nested,
  )

  marshaled = json.loads(
      gaos_serializers.marshal_json(doc, gaos_documentcontent.DocumentContent)
  )
  assert marshaled == {
      "type": "document",
      "data": "aGVsbG8=",
      "mime_type": "application/pdf",
      "resolution": "low",
      "nested_extra": {"temperature": 0.25, "inner_extra": "kept"},
  }

  assert doc.model_dump(mode="json", exclude_none=True) == marshaled
  assert doc.model_dump(mode="json") == {**marshaled, "null_extra": None}
  assert doc.model_dump(include={"type"}) == {"type": "document"}
  assert "resolution" not in doc.model_dump(exclude={"resolution"})
  assert doc.to_dict(mode="json", exclude_none=True) == marshaled

  constructed = gaos_documentcontent.DocumentContent.model_construct(
      type="document",
      data="aGVsbG8=",
      resolution="low",
  )
  assert constructed.to_dict() == {
      "type": "document",
      "data": "aGVsbG8=",
      "resolution": "low",
  }


def test_interactions_create_preserves_nested_extra_fields_on_wire():
  captured_requests: list[httpx.Request] = []

  def fake_send(
      unused_self: httpx.Client, request: httpx.Request, **unused_kwargs
  ) -> httpx.Response:
    captured_requests.append(request)
    return httpx.Response(
        200,
        json={"id": "v1_123", "status": "completed", "steps": []},
        headers={"content-type": "application/json"},
        request=request,
    )

  client = client_lib.Client(api_key="placeholder")
  with mock.patch.object(httpx.Client, "send", autospec=True, side_effect=fake_send):
    client.interactions.create(
        model="gemini-2.5-flash",
        input=[
            {
                "type": "document",
                "data": "aGVsbG8=",
                "mime_type": "application/pdf",
                "resolution": "low",
            }
        ],
        generation_config={"temperature": 0.5, "extra_knob": 42},
    )

  assert len(captured_requests) == 1
  payload = json.loads(captured_requests[0].content)
  assert payload == {
      "model": "gemini-2.5-flash",
      "input": [
          {
              "type": "user_input",
              "content": [
                  {
                      "type": "document",
                      "data": "aGVsbG8=",
                      "mime_type": "application/pdf",
                      "resolution": "low",
                  }
              ],
          }
      ],
      "generation_config": {"temperature": 0.5, "extra_knob": 42},
  }


@pytest.mark.asyncio
async def test_async_interactions_create_preserves_nested_extra_fields_on_wire():
  captured_requests: list[httpx.Request] = []

  async def fake_send(
      unused_self: httpx.AsyncClient, request: httpx.Request, **unused_kwargs
  ) -> httpx.Response:
    captured_requests.append(request)
    return httpx.Response(
        200,
        json={"id": "v1_123", "status": "completed", "steps": []},
        headers={"content-type": "application/json"},
        request=request,
    )

  client = client_lib.Client(api_key="placeholder")
  with mock.patch.object(
      httpx.AsyncClient, "send", autospec=True, side_effect=fake_send
  ):
    await client.aio.interactions.create(
        model="gemini-2.5-flash",
        input=[
            {
                "type": "document",
                "data": "aGVsbG8=",
                "mime_type": "application/pdf",
                "resolution": "low",
            }
        ],
        generation_config={"temperature": 0.5, "extra_knob": 42},
    )

  assert len(captured_requests) == 1
  payload = json.loads(captured_requests[0].content)
  assert payload == {
      "model": "gemini-2.5-flash",
      "input": [
          {
              "type": "user_input",
              "content": [
                  {
                      "type": "document",
                      "data": "aGVsbG8=",
                      "mime_type": "application/pdf",
                      "resolution": "low",
                  }
              ],
          }
      ],
      "generation_config": {"temperature": 0.5, "extra_knob": 42},
  }


def test_dynamic_agent_config_extra_fields_preserved():
  cfg = gaos_dynamicagentconfig.DynamicAgentConfig(
      type="dynamic",
      custom_flag=True,
  )
  assert json.loads(
      gaos_serializers.marshal_json(
          cfg, gaos_dynamicagentconfig.DynamicAgentConfig
      )
  ) == {"type": "dynamic", "custom_flag": True}

  cfg2 = gaos_dynamicagentconfig.DynamicAgentConfig()
  cfg2.additional_properties = {"via_setter": "value"}
  assert cfg2.to_dict() == {"via_setter": "value"}
  assert json.loads(
      gaos_serializers.marshal_json(
          cfg2, gaos_dynamicagentconfig.DynamicAgentConfig
      )
  ) == {"type": "dynamic", "via_setter": "value"}


def test_response_unmarshal_preserves_unknown_fields():
  raw_json = json.dumps({
      "id": "v1_999",
      "status": "completed",
      "future_top_level": "abc",
      "steps": [
          {
              "type": "model_output",
              "future_step_field": 7,
              "content": [
                  {
                      "type": "document",
                      "data": "aGVsbG8=",
                      "mime_type": "application/pdf",
                      "resolution": "low",
                  }
              ],
          }
      ],
  })

  parsed = gaos_serializers.unmarshal_json(raw_json, gaos_interaction.Interaction)
  dumped = parsed.to_dict(mode="json", exclude_none=True)
  assert dumped["future_top_level"] == "abc"
  assert dumped["steps"][0]["future_step_field"] == 7
  assert dumped["steps"][0]["content"][0]["resolution"] == "low"

  # Also verify lenient fallback when required `status` is omitted.
  lenient = gaos_serializers.construct_unvalidated(
      {
          "id": "v1_lenient",
          "future_top_level": "xyz",
          "steps": [
              {
                  "type": "model_output",
                  "future_step_field": 9,
                  "content": [{"type": "document", "resolution": "high"}],
              }
          ],
      },
      gaos_interaction.Interaction,
  )
  lenient_dumped = lenient.to_dict(mode="json", exclude_none=True)
  assert lenient_dumped["future_top_level"] == "xyz"
  assert lenient_dumped["steps"][0]["future_step_field"] == 9
  assert lenient_dumped["steps"][0]["content"][0]["resolution"] == "high"
