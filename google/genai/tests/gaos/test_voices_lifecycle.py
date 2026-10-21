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
"""Lifecycle tests for Voices API in the public Python SDK."""

from __future__ import annotations

from typing import Any

import pytest

from ... import voices
from . import conftest

VOICE_BODY = {
    "id": "voice_abc123",
    "display_name": "Warm Narrator",
    "type": "prompted",
    "gender": "female",
    "language_code": "en-US",
    "prompted": {
        "input": "A warm, friendly narrator voice.",
    },
}

VOICE_LIST_BODY = {
    "voices": [
        VOICE_BODY,
        {
            "id": "Puck",
            "display_name": "Puck",
            "type": "prebuilt",
            "gender": "male",
            "language_code": "en-US",
        },
    ],
    "next_page_token": "token_next_123",
}


def _voices_handler(
    req: conftest.CapturedRequest,
    unused_server: conftest.MockGaosServer,
) -> dict[str, Any]:
  if req["method"] == "GET" and (
      req["path"] == "/v1beta/voices"
      or req["path"].startswith("/v1beta/voices?")
  ):
    return VOICE_LIST_BODY
  if req["method"] == "DELETE":
    return {}
  return VOICE_BODY


def test_python_voices_lifecycle_routes_through_google_genai_client(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _voices_handler
  client = mock_gaos_server.client

  # 1. Create prompted voice
  created = client.voices.create(
      store=True,
      voice={
          "type": "prompted",
          "display_name": "Warm Narrator",
          "gender": "female",
          "language_code": "en-US",
          "prompted": {
              "input": "A warm, friendly narrator voice.",
          },
      },
  )
  assert created.id == "voice_abc123"
  assert created.display_name == "Warm Narrator"

  # 2. List voices
  list_res = client.voices.list(language_code=["en-US"])
  assert list_res.voices is not None
  assert len(list_res.voices) == 2
  assert list_res.next_page_token == "token_next_123"

  # 3. Get voice
  fetched = client.voices.get(id="voice_abc123")
  assert fetched.id == "voice_abc123"

  # 4. Delete voice
  client.voices.delete(id="voice_abc123")

  assert mock_gaos_server.captured == [
      "POST /v1beta/voices",
      "GET /v1beta/voices?language_code=en-US",
      "GET /v1beta/voices/voice_abc123",
      "DELETE /v1beta/voices/voice_abc123",
  ]
  assert mock_gaos_server.captured_bodies[0] == {
      "store": True,
      "voice": {
          "type": "prompted",
          "display_name": "Warm Narrator",
          "gender": "female",
          "language_code": "en-US",
          "prompted": {
              "input": "A warm, friendly narrator voice.",
          },
      },
  }


@pytest.mark.asyncio
async def test_python_voices_async_lifecycle(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _voices_handler
  client = mock_gaos_server.client

  created = await client.aio.voices.create(
      store=True,
      voice={
          "type": "prompted",
          "display_name": "Warm Narrator",
          "prompted": {
              "input": "A warm, friendly narrator voice.",
          },
      },
  )
  list_res = await client.aio.voices.list()
  fetched = await client.aio.voices.get(id="voice_abc123")
  await client.aio.voices.delete(id="voice_abc123")

  assert created.id == "voice_abc123"
  assert fetched.id == "voice_abc123"
  assert list_res.voices is not None
  assert len(list_res.voices) == 2
  assert mock_gaos_server.captured == [
      "POST /v1beta/voices",
      "GET /v1beta/voices",
      "GET /v1beta/voices/voice_abc123",
      "DELETE /v1beta/voices/voice_abc123",
  ]


def test_python_voices_with_raw_response(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _voices_handler
  client = mock_gaos_server.client

  raw_res = client.voices.with_raw_response.list()
  parsed = raw_res.parse()
  assert parsed.voices is not None
  assert len(parsed.voices) == 2
  assert parsed.voices[0].id == "voice_abc123"


def test_python_voices_types_and_models():
  voice = voices.Voice(
      id="voice_abc123",
      display_name="Warm Narrator",
      type="prompted",
      prompted={"input": "Warm voice"},
  )
  assert voice.id == "voice_abc123"
  assert voice.type == "prompted"
  assert voice.prompted is not None
  assert voice.prompted.input == "Warm voice"

  list_resp = voices.VoiceListResponse(
      voices=[voice],
      next_page_token="next_tok",
  )
  assert list_resp.voices is not None
  assert len(list_resp.voices) == 1
  assert list_resp.next_page_token == "next_tok"
