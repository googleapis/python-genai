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
"""Lifecycle tests for Triggers API."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

from ... import Client

TRIGGER_BODY = {
    "id": "projects/my-project/locations/my-location/triggers/svc_abc",
    "schedule": "0 0 * * *",
    "time_zone": "UTC",
    "interaction": {
        "agent": "projects/my-project/locations/my-location/agents/my-agent",
        "input": "test-input",
        "environment": {
            "type": "remote",
            "network": {
                "allowlist": [
                    {
                        "domain": "api.github.com",
                        "transform": {
                            "Authorization": (
                                "Bearer"
                                " ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                            )
                        },
                    },
                    {"domain": "github.com"},
                ]
            },
        },
    },
}


class _RecordingHandler(BaseHTTPRequestHandler):
  captured: list[str] = []

  def _record_and_respond(self) -> None:
    self.captured.append(f"{self.command} {self.path}")
    payload = json.dumps(TRIGGER_BODY).encode()
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


def test_python_triggers_lifecycle_routes_through_google_genai_client(
    monkeypatch,
):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  handler = type("Handler", (_RecordingHandler,), {"captured": captured})
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

    trigger = client.triggers.create(
        interaction={
            "agent": (
                "projects/my-project/locations/my-location/agents/my-agent"
            ),
            "input": "test-input",
            "environment": {
                "type": "remote",
                "network": {
                    "allowlist": [
                        {
                            "domain": "api.github.com",
                            "transform": {
                                "Authorization": (
                                    "Bearer"
                                    " ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                )
                            },
                        },
                        {"domain": "github.com"},
                    ]
                },
            },
        },
        schedule="0 0 * * *",
        time_zone="UTC",
    )
    client.triggers.list(filter_="some-filter", page_size=10)
    fetched = client.triggers.get(id="svc_abc")
    client.triggers.update(
        id="svc_abc",
        display_name="updated-name",
        status="paused",
    )
    client.triggers.delete(id="svc_abc")
    client.triggers.run(trigger_id="svc_abc")
    client.triggers.list_executions(trigger_id="svc_abc", page_size=5)

    assert trigger.schedule == "0 0 * * *"
    assert fetched.schedule == "0 0 * * *"
    assert captured == [
        "POST /v1beta/triggers",
        "GET /v1beta/triggers?filter=some-filter&page_size=10",
        "GET /v1beta/triggers/svc_abc",
        "PATCH /v1beta/triggers/svc_abc",
        "DELETE /v1beta/triggers/svc_abc",
        "POST /v1beta/triggers/svc_abc/executions",
        "GET /v1beta/triggers/svc_abc/executions?page_size=5",
    ]
  finally:
    server.shutdown()
    thread.join()
    server.server_close()
