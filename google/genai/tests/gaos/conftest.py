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

"""Shared mock HTTP server fixture for GAOS SDK unit tests."""

from collections.abc import Callable, Iterator
import dataclasses
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import Any, TypedDict, cast

import pytest

from ... import Client
from ... import types

_ENV_VARS_TO_CLEAR = (
    "GOOGLE_GENAI_USE_VERTEXAI",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
)


class CapturedRequest(TypedDict):
  """Metadata recorded for each incoming HTTP request."""

  method: str
  path: str
  headers: dict[str, str]
  body: bytes


@dataclasses.dataclass
class RawHttpResponse:
  """Custom non-JSON or header-customised HTTP response."""

  body: bytes = b""
  status: int = 200
  content_type: str = "application/json"
  headers: dict[str, str] = dataclasses.field(default_factory=dict)


HandlerFn = Callable[
    [CapturedRequest, "MockGaosServer"],
    dict[str, Any] | RawHttpResponse | None,
]


@dataclasses.dataclass
class MockGaosServer:
  """Per-test mock HTTP server state and pre-configured GenAI Client."""

  base_url: str
  client: Client
  captured: list[str] = dataclasses.field(default_factory=list)
  captured_bodies: list[dict[str, Any]] = dataclasses.field(
      default_factory=list
  )
  captured_requests: list[CapturedRequest] = dataclasses.field(
      default_factory=list
  )
  uploaded_bytes: list[bytes] = dataclasses.field(default_factory=list)
  responses: list[dict[str, Any]] = dataclasses.field(default_factory=list)
  default_response: dict[str, Any] = dataclasses.field(default_factory=dict)
  stream_payload: str = ""
  handler_fn: HandlerFn | None = None

  def make_client(
      self,
      *,
      headers: dict[str, str] | None = None,
  ) -> Client:
    """Creates a new Client pointing at this mock server."""
    http_options = (
        types.HttpOptions(base_url=self.base_url, headers=headers)
        if headers is not None
        else types.HttpOptions(base_url=self.base_url)
    )
    return Client(
        api_key="test-key",
        vertexai=False,
        http_options=http_options,
    )


class _GaosHTTPServer(ThreadingHTTPServer):
  """ThreadingHTTPServer bound to a per-test MockGaosServer state."""

  state: MockGaosServer


class _GaosRequestHandler(BaseHTTPRequestHandler):
  """HTTP request handler that delegates state to its owning _GaosHTTPServer."""

  @property
  def _state(self) -> MockGaosServer:
    return cast(_GaosHTTPServer, self.server).state

  def _send_json(self, body_dict: dict[str, Any], status: int = 200) -> None:
    body = json.dumps(body_dict).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def _send_raw(self, response: RawHttpResponse) -> None:
    self.send_response(response.status)
    self.send_header("Content-Type", response.content_type)
    for key, value in response.headers.items():
      self.send_header(key, value)
    self.send_header("Content-Length", str(len(response.body)))
    self.end_headers()
    self.wfile.write(response.body)

  def _handle_request(self) -> None:
    state = self._state
    content_length = int(self.headers.get("Content-Length", "0"))
    raw_body = self.rfile.read(content_length) if content_length > 0 else b""

    state.captured.append(f"{self.command} {self.path}")
    request_record: CapturedRequest = {
        "method": self.command,
        "path": self.path,
        "headers": {k.lower(): v for k, v in self.headers.items()},
        "body": raw_body,
    }
    state.captured_requests.append(request_record)

    if self.command in ("POST", "PATCH", "PUT") and raw_body:
      try:
        state.captured_bodies.append(json.loads(raw_body.decode("utf-8")))
      except (UnicodeDecodeError, json.JSONDecodeError):
        pass

    if "text/event-stream" in self.headers.get("Accept", "") and (
        state.stream_payload
    ):
      self._send_raw(
          RawHttpResponse(
              body=state.stream_payload.encode("utf-8"),
              content_type="text/event-stream",
          )
      )
      return

    if state.handler_fn is not None:
      custom_result = state.handler_fn(request_record, state)
      if isinstance(custom_result, RawHttpResponse):
        self._send_raw(custom_result)
        return
      if custom_result is not None:
        self._send_json(custom_result)
        return

    body_dict = (
        state.responses.pop(0) if state.responses else state.default_response
    )
    self._send_json(body_dict)

  def do_GET(self) -> None:  # pylint: disable=invalid-name
    self._handle_request()

  def do_POST(self) -> None:  # pylint: disable=invalid-name
    self._handle_request()

  def do_PATCH(self) -> None:  # pylint: disable=invalid-name
    self._handle_request()

  def do_PUT(self) -> None:  # pylint: disable=invalid-name
    self._handle_request()

  def do_DELETE(self) -> None:  # pylint: disable=invalid-name
    self._handle_request()

  def log_message(self, format: str, *args: Any) -> None:  # pylint: disable=redefined-builtin
    return


@pytest.fixture
def mock_gaos_server(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[MockGaosServer]:
  """Starts an isolated local HTTP server and yields a MockGaosServer state."""
  for env_var in _ENV_VARS_TO_CLEAR:
    monkeypatch.delenv(env_var, raising=False)

  server = _GaosHTTPServer(("127.0.0.1", 0), _GaosRequestHandler)
  port = server.server_address[1]
  base_url = f"http://127.0.0.1:{port}"
  client = Client(
      api_key="test-key",
      vertexai=False,
      http_options=types.HttpOptions(base_url=base_url),
  )
  state = MockGaosServer(base_url=base_url, client=client)
  server.state = state

  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  try:
    yield state
  finally:
    server.shutdown()
    thread.join()
    server.server_close()
