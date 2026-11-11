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
"""Unit tests for Decisions API in the public Python SDK."""

from __future__ import annotations

from typing import Any

import pytest

from ... import decisions
from . import conftest

DECISION_RESPONSE_BODY = {
    "answers": {
        "q1": {
            "type": "noul",
            "noul": 0.95,
            "confidence": 0.95,
        }
    }
}


def _decisions_handler(
    unused_req: conftest.CapturedRequest,
    unused_server: conftest.MockGaosServer,
) -> dict[str, Any]:
  return DECISION_RESPONSE_BODY


def test_python_decisions_create_routes_through_google_genai_client(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _decisions_handler
  client = mock_gaos_server.client

  response = client.decisions.create(
      model="decisions-prerelease",
      input="User prompt context",
      questions={
          "q1": {
              "type": "noul",
              "instructions": "Does the user want a summary?",
          }
      },
  )
  assert response.answers is not None
  assert "q1" in response.answers
  answer = response.answers["q1"]
  assert answer.type == "noul"
  assert answer.noul == 0.95
  assert answer.confidence == 0.95

  assert mock_gaos_server.captured == [
      "POST /v1beta/decisions",
  ]
  assert mock_gaos_server.captured_bodies[0] == {
      "model": "decisions-prerelease",
      "input": "User prompt context",
      "questions": {
          "q1": {
              "type": "noul",
              "instructions": "Does the user want a summary?",
          }
      },
  }


@pytest.mark.asyncio
async def test_python_decisions_async_create(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _decisions_handler
  client = mock_gaos_server.client

  response = await client.aio.decisions.create(
      model="decisions-prerelease",
      input="User prompt context",
      questions={
          "q1": {
              "type": "noul",
              "instructions": "Does the user want a summary?",
          }
      },
  )
  assert response.answers is not None
  assert "q1" in response.answers
  answer = response.answers["q1"]
  assert answer.type == "noul"
  assert answer.noul == 0.95
  assert answer.confidence == 0.95
  assert mock_gaos_server.captured == [
      "POST /v1beta/decisions",
  ]


def test_python_decisions_with_raw_response(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _decisions_handler
  client = mock_gaos_server.client

  raw_res = client.decisions.with_raw_response.create(
      model="decisions-prerelease",
      input="User prompt context",
      questions={
          "q1": {
              "type": "noul",
              "instructions": "Does the user want a summary?",
          }
      },
  )
  parsed = raw_res.parse()
  assert parsed.answers is not None
  assert parsed.answers["q1"].type == "noul"


def test_python_decisions_types_and_empty_criteria():
  # b/577987982: The public SDK types ChoiceQuestion.criteria values as `str`.
  # An empty string means "no description" (the server ignores blank
  # descriptions), so it must pass request validation.
  question = decisions.ChoiceQuestion(
      type="choice",
      instructions="Pick action.",
      criteria={"refund": "", "replace": "Ship a new unit."},
  )
  assert question.type == "choice"
  assert question.criteria == {
      "refund": "",
      "replace": "Ship a new unit.",
  }
