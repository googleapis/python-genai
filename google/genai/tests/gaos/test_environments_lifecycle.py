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

import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest

from ... import Client
from ..._gaos.google_genai import (
    AsyncGeminiNextGenEnvironmentFiles,
    GeminiNextGenEnvironmentFiles,
)
from ..._gaos.models.getenvironmentfiles import GetEnvironmentFilesRequest
from ..._gaos.types.environments.environmentfile import EnvironmentFile
from ..._gaos.types.environments.getenvironmentfilesresponse import (
    GetEnvironmentFilesResponse,
)

ENVIRONMENT_BODY = {
    "id": "env_abc_1234",
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

ENVIRONMENT_FILES_PAYLOAD = {
    "files": [
        {
            "name": "main.py",
            "path": "workspace/src/main.py",
            "type": "file",
            "size_bytes": "128",
            "mime_type": "text/x-python",
            "created": "2026-07-22T15:18:38Z",
            "modified": "2026-07-22T15:18:38Z",
        }
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
        sources=[
            {
                "type": "inline",
                "content": "print('hello')",
                "target": "main.py",
            }
        ]
    )
    client.environments.list()
    fetched = client.environments.get(id="env_abc_1234")
    client.environments.delete(id="env_abc_1234")

    assert environment.id == "env_abc_1234"
    assert fetched.id == "env_abc_1234"
    assert captured == [
        "POST /v1beta/environments",
        "GET /v1beta/environments",
        "GET /v1beta/environments/env_abc_1234",
        "DELETE /v1beta/environments/env_abc_1234",
    ]

    create_body = captured_bodies[0]
    assert create_body["sources"][0]["content"] == "print('hello')"

  finally:
    server.shutdown()
    thread.join()
    server.server_close()


class _ScottyDownloadHandler(BaseHTTPRequestHandler):
  captured: list[str] = []

  def do_GET(self) -> None:
    self.captured.append(f"GET {self.path}")
    if "?alt=media" in self.path or "&alt=media" in self.path:
      payload = b"print('downloaded content')\n"
      self.send_response(200)
      self.send_header("content-type", "application/octet-stream")
      self.send_header("content-length", str(len(payload)))
      self.end_headers()
      self.wfile.write(payload)
      return
    elif "/files" in self.path:
      payload = json.dumps(ENVIRONMENT_FILES_PAYLOAD).encode()
      self.send_response(200)
      self.send_header("content-type", "application/json")
      self.send_header("content-length", str(len(payload)))
      self.end_headers()
      self.wfile.write(payload)
      return

    self.send_response(404)
    self.end_headers()

  def log_message(self, *args) -> None:
    pass


def test_python_environments_files_list_and_download(monkeypatch):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  handler = type("Handler", (_ScottyDownloadHandler,), {
      "captured": captured,
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
            "headers": {"X-Goog-Api-Client": "test"},
        },
    )

    # Test sync files.list basic
    files_res = client.environments.files.list(
        environment="env_123",
        path="src/main.py",
    )
    assert len(files_res.files) == 1
    assert files_res.files[0].name == "main.py"
    assert files_res.files[0].path == "workspace/src/main.py"
    assert files_res.files[0].type == "file"
    assert files_res.files[0].size_bytes == 128
    assert files_res.next_page_token == "token_next_123"

    # Test sync files.list with pagination and recursive options
    files_res_paginated = client.environments.files.list(
        environment="env_123",
        path="src",
        page_size=10,
        page_token="token_start",
        recursive=True,
    )
    assert len(files_res_paginated.files) == 1

    # Test sync files.download
    downloaded = client.environments.files.download(
        environment="env_123",
        path="src/main.py",
    )
    assert downloaded == b"print('downloaded content')\n"

    # Test sync files.download with full resource name and leading slash
    downloaded_full = client.environments.files.download(
        environment="environments/env_123",
        path="/src/main.py",
    )
    assert downloaded_full == b"print('downloaded content')\n"

    # Test with_raw_response on environments.files
    raw_files_res = client.environments.with_raw_response.files.list(
        environment="env_123",
        path="src/main.py",
    )
    parsed = raw_files_res.parse()
    assert len(parsed.files) == 1
    assert parsed.files[0].name == "main.py"

    assert any("page_size=10" in call for call in captured)
    assert any("page_token=token_start" in call for call in captured)
    assert any("recursive=true" in call for call in captured)

  finally:
    server.shutdown()
    thread.join()
    server.server_close()


@pytest.mark.asyncio
async def test_python_environments_async_files_list_and_download(monkeypatch):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  handler = type("Handler", (_ScottyDownloadHandler,), {
      "captured": captured,
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

    # Test async files.list basic
    files_res = await client.aio.environments.files.list(
        environment="env_123",
        path="src/main.py",
    )
    assert len(files_res.files) == 1
    assert files_res.files[0].name == "main.py"
    assert files_res.files[0].path == "workspace/src/main.py"
    assert files_res.files[0].type == "file"
    assert files_res.files[0].size_bytes == 128

    # Test async files.list with pagination and recursive options
    files_res_paginated = await client.aio.environments.files.list(
        environment="env_123",
        path="src",
        page_size=10,
        page_token="token_start",
        recursive=True,
    )
    assert len(files_res_paginated.files) == 1

    # Test async files.download
    downloaded = await client.aio.environments.files.download(
        environment="env_123",
        path="src/main.py",
    )
    assert downloaded == b"print('downloaded content')\n"

    # Test async files.download with full resource name and leading slash
    downloaded_full = await client.aio.environments.files.download(
        environment="environments/env_123",
        path="/src/main.py",
    )
    assert downloaded_full == b"print('downloaded content')\n"

    # Test async with_raw_response on environments.files
    raw_files_res = await client.aio.environments.with_raw_response.files.list(
        environment="env_123",
        path="src/main.py",
    )
    parsed = await raw_files_res.parse()
    assert len(parsed.files) == 1
    assert parsed.files[0].name == "main.py"

  finally:
    server.shutdown()
    thread.join()
    server.server_close()


def test_python_environments_files_download_missing_api_client():
  files_obj = GeminiNextGenEnvironmentFiles(sdk_config=object(), api_client=None)
  with pytest.raises(
      AttributeError,
      match="api_client is required to download files.",
  ):
    files_obj.download(environment="env_123", path="src/main.py")

  async_files_obj = AsyncGeminiNextGenEnvironmentFiles(sdk_config=object(), api_client=None)

  with pytest.raises(
      AttributeError,
      match="api_client is required to download files.",
  ):
    asyncio.run(async_files_obj.download(environment="env_123", path="src/main.py"))


def test_python_environments_types_and_models():
  file_obj = EnvironmentFile(
      created="2026-07-22T15:18:38Z",
      mime_type="text/x-python",
      modified="2026-07-22T15:18:38Z",
      name="main.py",
      path="workspace/src/main.py",
      size_bytes=128,
      type="file",
  )
  assert file_obj.name == "main.py"
  assert file_obj.path == "workspace/src/main.py"
  assert file_obj.type == "file"
  assert file_obj.size_bytes == 128
  assert file_obj.mime_type == "text/x-python"
  assert file_obj.created is not None
  assert file_obj.modified is not None

  response = GetEnvironmentFilesResponse(
      files=[file_obj],
      next_page_token="next_tok",
  )
  assert len(response.files) == 1
  assert response.next_page_token == "next_tok"

  req = GetEnvironmentFilesRequest(
      environment="env_123",
      path="src/main.py",
      page_size=20,
      page_token="tok",
      recursive=True,
      api_version="v1beta",
  )
  assert req.environment == "env_123"
  assert req.path == "src/main.py"
  assert req.page_size == 20
  assert req.page_token == "tok"
  assert req.recursive is True
  assert req.api_version == "v1beta"




