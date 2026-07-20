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
"""Lifecycle tests for Environments API."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest

from ... import Client

ENVIRONMENT_BODY = {
    "id": "environments/env_abc",
    "status": "active",
    "created": "2026-07-22T15:18:38Z",
    "updated": "2026-07-22T15:18:38Z",
    "sources": [
        {
            "type": "INLINE",
            "content": "print('hello')",
            "target": "main.py",
        }
    ],
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
    payload = json.dumps(ENVIRONMENT_BODY).encode()
    self.send_response(200)
    self.send_header("content-type", "application/json")
    self.send_header("content-length", str(len(payload)))
    self.end_headers()
    self.wfile.write(payload)

  do_GET = _record_and_respond
  do_POST = _record_and_respond
  do_PATCH = _record_and_respond
  do_DELETE = _record_and_respond

  def log_message(self, *args) -> None:
    pass


def test_python_environments_lifecycle_routes_through_google_genai_client(
    monkeypatch,
):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  captured_bodies: list[dict] = []
  handler = type("Handler", (_RecordingHandler,), {
      "captured": captured,
      "captured_bodies": captured_bodies,
  })
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

    environment = client.environments.create(
        environment={
            "sources": [
                {
                    "type": "INLINE",
                    "content": "print('hello')",
                    "target": "main.py",
                }
            ]
        }
    )
    client.environments.list()
    fetched = client.environments.get(id="env_abc")
    client.environments.delete(id="env_abc")

    assert environment.id == "environments/env_abc"
    assert fetched.id == "environments/env_abc"
    assert captured == [
        "POST /v1beta/environments",
        "GET /v1beta/environments",
        "GET /v1beta/environments/env_abc",
        "DELETE /v1beta/environments/env_abc",
    ]

    create_body = captured_bodies[0]
    assert create_body["sources"][0]["content"] == "print('hello')"

  finally:
    server.shutdown()
    thread.join()
    server.server_close()
