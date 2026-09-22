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

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest

from ... import Client
from ... import voices

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


class _RecordingHandler(BaseHTTPRequestHandler):
  captured: list[str] = []
  captured_bodies: list[dict] = []

  def _record_and_respond(self) -> None:
    self.captured.append(f"{self.command} {self.path}")
    if self.command in ("POST", "PATCH", "PUT"):
      content_length = int(self.headers.get("Content-Length", 0))
      if content_length > 0:
        body = self.rfile.read(content_length)
        self.captured_bodies.append(json.loads(body.decode("utf-8")))

    if self.command == "GET" and (
        self.path == "/v1beta/voices"
        or self.path.startswith("/v1beta/voices?")
    ):
      payload = json.dumps(VOICE_LIST_BODY).encode()
    elif self.command == "DELETE":
      payload = json.dumps({}).encode()
    else:
      payload = json.dumps(VOICE_BODY).encode()

    self.send_response(200)
    self.send_header("content-type", "application/json")
    self.send_header("content-length", str(len(payload)))
    self.end_headers()
    self.wfile.write(payload)

  do_GET = _record_and_respond
  do_POST = _record_and_respond
  do_DELETE = _record_and_respond

  def log_message(self, *args) -> None:
    pass


def test_python_voices_lifecycle_routes_through_google_genai_client(
    monkeypatch,
):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  captured_bodies: list[dict] = []
  handler = type(
      "Handler",
      (_RecordingHandler,),
      {
          "captured": captured,
          "captured_bodies": captured_bodies,
      },
  )
  server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  try:
    client = Client(
        api_key="test-api-key",
        http_options={
            "api_version": "v1beta",
            "base_url": f"http://127.0.0.1:{server.server_port}",
        },
    )

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

    assert captured == [
        "POST /v1beta/voices",
        "GET /v1beta/voices?language_code=en-US",
        "GET /v1beta/voices/voice_abc123",
        "DELETE /v1beta/voices/voice_abc123",
    ]
    assert captured_bodies[0] == {
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
  finally:
    server.shutdown()
    thread.join()
    server.server_close()


@pytest.mark.asyncio
async def test_python_voices_async_lifecycle(monkeypatch):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  captured_bodies: list[dict] = []
  handler = type(
      "Handler",
      (_RecordingHandler,),
      {
          "captured": captured,
          "captured_bodies": captured_bodies,
      },
  )
  server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  try:
    client = Client(
        api_key="test-api-key",
        http_options={
            "api_version": "v1beta",
            "base_url": f"http://127.0.0.1:{server.server_port}",
        },
    )

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
    assert captured == [
        "POST /v1beta/voices",
        "GET /v1beta/voices",
        "GET /v1beta/voices/voice_abc123",
        "DELETE /v1beta/voices/voice_abc123",
    ]
  finally:
    server.shutdown()
    thread.join()
    server.server_close()


def test_python_voices_with_raw_response(monkeypatch):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  handler = type(
      "Handler",
      (_RecordingHandler,),
      {
          "captured": captured,
      },
  )
  server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  try:
    client = Client(
        api_key="test-api-key",
        http_options={
            "api_version": "v1beta",
            "base_url": f"http://127.0.0.1:{server.server_port}",
        },
    )

    raw_res = client.voices.with_raw_response.list()
    parsed = raw_res.parse()
    assert parsed.voices is not None
    assert len(parsed.voices) == 2
    assert parsed.voices[0].id == "voice_abc123"
  finally:
    server.shutdown()
    thread.join()
    server.server_close()


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
