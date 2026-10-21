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
import io
import json
from typing import Any

import pytest

from ... import environments
from ... import interactions
from ..._gaos.google_genai import (
    AsyncGeminiNextGenEnvironmentFiles,
    GeminiNextGenEnvironmentFiles,
)
from ..._gaos.models.getenvironmentfiles import GetEnvironmentFilesRequest
from ..._gaos.types.environments.createenvironmentrequest import (
    CreateEnvironmentRequest,
)
from ..._gaos.types.environments.environmentfile import EnvironmentFile
from ..._gaos.types.environments.getenvironmentfilesresponse import (
    GetEnvironmentFilesResponse,
)
from . import conftest

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


def test_python_environments_lifecycle_routes_through_google_genai_client(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.default_response = ENVIRONMENT_BODY
  client = mock_gaos_server.client

  environment = client.environments.create(
      sources=[{
          "type": "inline",
          "content": "print('hello')",
          "target": "main.py",
      }]
  )
  forked_environment = client.environments.create(
      from_environment="environments/env_abc_1234",
  )
  client.environments.list()
  fetched = client.environments.get(id="env_abc_1234")
  client.environments.delete(id="env_abc_1234")

  assert environment.id == "env_abc_1234"
  assert forked_environment.id == "env_abc_1234"
  assert fetched.id == "env_abc_1234"
  assert mock_gaos_server.captured == [
      "POST /v1beta/environments",
      "POST /v1beta/environments",
      "GET /v1beta/environments",
      "GET /v1beta/environments/env_abc_1234",
      "DELETE /v1beta/environments/env_abc_1234",
  ]

  create_body = mock_gaos_server.captured_bodies[0]
  assert create_body["sources"][0]["content"] == "print('hello')"
  forked_body = mock_gaos_server.captured_bodies[1]
  assert forked_body["from_environment"] == "environments/env_abc_1234"


@pytest.mark.asyncio
async def test_python_environments_async_create_with_from_environment(
    mock_gaos_server: conftest.MockGaosServer,
):
  """Tests creating an environment asynchronously with from_environment."""
  mock_gaos_server.default_response = ENVIRONMENT_BODY
  client = mock_gaos_server.client

  forked_environment = await client.aio.environments.create(
      from_environment="environments/env_abc_1234",
  )
  assert forked_environment.id == "env_abc_1234"
  assert mock_gaos_server.captured == ["POST /v1beta/environments"]
  assert (
      mock_gaos_server.captured_bodies[0]["from_environment"]
      == "environments/env_abc_1234"
  )


def _scotty_file_handler(
    req: conftest.CapturedRequest,
    server: conftest.MockGaosServer,
) -> dict[str, Any] | conftest.RawHttpResponse:
  if req["method"] == "PUT":
    if (
        req["path"].startswith("/upload/")
        and "/environments/" in req["path"]
        and "/files/" in req["path"]
    ):
      return conftest.RawHttpResponse(
          headers={
              "x-goog-upload-url": (
                  f"{server.base_url}/scotty/upload/resumable_123"
              ),
              "x-goog-upload-status": "active",
          },
      )
    return conftest.RawHttpResponse(status=404)

  if req["method"] == "POST":
    if req["path"] == "/scotty/upload/resumable_123":
      data = req["body"]
      server.uploaded_bytes.append(data)
      file_response = {
          "file": {
              "name": "main.py",
              "sizeBytes": str(len(data)),
              "mimeType": "text/x-python",
          }
      }
      return conftest.RawHttpResponse(
          body=json.dumps(file_response).encode("utf-8"),
          headers={"x-goog-upload-status": "final"},
      )
    return conftest.RawHttpResponse(status=404)

  if req["method"] == "GET":
    if "?alt=media" in req["path"] or "&alt=media" in req["path"]:
      return conftest.RawHttpResponse(
          body=b"print('downloaded content')\n",
          content_type="application/octet-stream",
      )
    if "/files" in req["path"]:
      return ENVIRONMENT_FILES_PAYLOAD

  return conftest.RawHttpResponse(status=404)


def test_python_environments_file_upload_download(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _scotty_file_handler
  client = mock_gaos_server.make_client(
      headers={"X-Goog-Api-Client": "test"},
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

  # Test sync upload
  upload_res = client.environments.files.upload(
      environment="env_123",
      path="src/main.py",
      file=b"print('hello world')",
      mime_type="text/x-python",
      overwrite=True,
  )
  assert upload_res.files and len(upload_res.files) == 1
  assert upload_res.files[0].name == "main.py"
  assert mock_gaos_server.uploaded_bytes[0] == b"print('hello world')"

  # Verify handshake and chunk headers
  handshake = [
      r
      for r in mock_gaos_server.captured_requests
      if r["method"] == "PUT" and "/files/" in r["path"]
  ][0]
  assert handshake["method"] == "PUT"
  assert handshake["path"].startswith(
      "/upload/v1beta/environments/env_123/files/src/main.py"
  )
  assert "overwrite=true" in handshake["path"]
  assert handshake["headers"].get("x-goog-upload-protocol") == "resumable"
  assert handshake["headers"].get("x-goog-upload-command") == "start"
  assert handshake["headers"].get("x-goog-upload-header-content-length") == str(
      len(b"print('hello world')")
  )
  assert (
      handshake["headers"].get("x-goog-upload-header-content-type")
      == "text/x-python"
  )

  chunk_post = [
      r
      for r in mock_gaos_server.captured_requests
      if r["method"] == "POST" and r["path"] == "/scotty/upload/resumable_123"
  ][0]
  assert chunk_post["method"] == "POST"
  assert chunk_post["path"] == "/scotty/upload/resumable_123"
  assert chunk_post["headers"].get("x-goog-upload-command") == (
      "upload, finalize"
  )
  assert chunk_post["headers"].get("x-goog-upload-offset") == "0"
  assert chunk_post["body"] == b"print('hello world')"

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

  assert any("page_size=10" in call for call in mock_gaos_server.captured)
  assert any(
      "page_token=token_start" in call for call in mock_gaos_server.captured
  )
  assert any("recursive=true" in call for call in mock_gaos_server.captured)


@pytest.mark.asyncio
async def test_python_environments_async_file_upload_download(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.handler_fn = _scotty_file_handler
  client = mock_gaos_server.make_client(
      headers={"X-Goog-Api-Client": "test"},
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

  # Test async upload
  upload_res = await client.aio.environments.files.upload(
      environment="env_123",
      path="src/main.py",
      file=b"print('async hello world')",
      mime_type="text/x-python",
      overwrite=True,
  )
  assert upload_res.files and len(upload_res.files) == 1
  assert upload_res.files[0].name == "main.py"
  assert mock_gaos_server.uploaded_bytes[0] == b"print('async hello world')"

  # Verify async handshake and chunk headers
  handshake = [
      r
      for r in mock_gaos_server.captured_requests
      if r["method"] == "PUT" and "/files/" in r["path"]
  ][0]
  assert handshake["method"] == "PUT"
  assert handshake["path"].startswith(
      "/upload/v1beta/environments/env_123/files/src/main.py"
  )
  assert "overwrite=true" in handshake["path"]
  assert handshake["headers"].get("x-goog-upload-protocol") == "resumable"
  assert handshake["headers"].get("x-goog-upload-command") == "start"
  assert handshake["headers"].get("x-goog-upload-header-content-length") == str(
      len(b"print('async hello world')")
  )
  assert (
      handshake["headers"].get("x-goog-upload-header-content-type")
      == "text/x-python"
  )

  chunk_post = [
      r
      for r in mock_gaos_server.captured_requests
      if r["method"] == "POST" and r["path"] == "/scotty/upload/resumable_123"
  ][0]
  assert chunk_post["headers"].get("x-goog-upload-command") == (
      "upload, finalize"
  )
  assert chunk_post["headers"].get("x-goog-upload-offset") == "0"
  assert chunk_post["body"] == b"print('async hello world')"

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


def test_python_environments_upload_io_and_file_paths(
    mock_gaos_server: conftest.MockGaosServer,
    tmp_path,
):
  mock_gaos_server.handler_fn = _scotty_file_handler
  client = mock_gaos_server.client

  # 1. Test upload with io.BytesIO
  stream_data = b"content from BytesIO"
  io_stream = io.BytesIO(stream_data)
  upload_res = client.environments.files.upload(
      environment="env_123",
      path="stream.txt",
      file=io_stream,
      mime_type="text/plain",
  )
  assert upload_res.files and len(upload_res.files) == 1
  assert mock_gaos_server.uploaded_bytes[-1] == stream_data

  # 2. Test upload with file path as string
  tmp_file = tmp_path / "hello.py"
  tmp_file.write_text("print('from file path str')")
  upload_res_str = client.environments.files.upload(
      environment="env_123",
      path="hello.py",
      file=str(tmp_file),
  )
  assert upload_res_str.files and len(upload_res_str.files) == 1
  assert mock_gaos_server.uploaded_bytes[-1] == b"print('from file path str')"

  # 3. Test upload with pathlib.Path
  tmp_file_path = tmp_path / "hello_path.py"
  tmp_file_path.write_text("print('from pathlib.Path')")
  upload_res_path = client.environments.files.upload(
      environment="env_123",
      path="hello_path.py",
      file=tmp_file_path,
      extract=False,
      overwrite=True,
  )
  assert upload_res_path.files and len(upload_res_path.files) == 1
  assert mock_gaos_server.uploaded_bytes[-1] == b"print('from pathlib.Path')"

  # 4. Test upload with open file handle (io.IOBase)
  with open(str(tmp_file), "rb") as fh:
    upload_res_fh = client.environments.files.upload(
        environment="env_123",
        path="hello_fh.py",
        file=fh,
    )
    assert upload_res_fh.files and len(upload_res_fh.files) == 1
    assert mock_gaos_server.uploaded_bytes[-1] == b"print('from file path str')"


@pytest.mark.asyncio
async def test_python_environments_async_upload_io_and_file_paths(
    mock_gaos_server: conftest.MockGaosServer,
    tmp_path,
):
  mock_gaos_server.handler_fn = _scotty_file_handler
  client = mock_gaos_server.client

  # 1. Async test upload with io.BytesIO
  stream_data = b"async content from BytesIO"
  io_stream = io.BytesIO(stream_data)
  upload_res = await client.aio.environments.files.upload(
      environment="env_123",
      path="async_stream.txt",
      file=io_stream,
      mime_type="text/plain",
  )
  assert upload_res.files and len(upload_res.files) == 1
  assert mock_gaos_server.uploaded_bytes[-1] == stream_data

  # 2. Async test upload with file path as string
  tmp_file = tmp_path / "async_hello.py"
  tmp_file.write_text("print('async from file path str')")
  upload_res_str = await client.aio.environments.files.upload(
      environment="env_123",
      path="async_hello.py",
      file=str(tmp_file),
  )
  assert upload_res_str.files and len(upload_res_str.files) == 1
  assert (
      mock_gaos_server.uploaded_bytes[-1]
      == b"print('async from file path str')"
  )

  # 3. Async test upload with pathlib.Path
  tmp_file_path = tmp_path / "async_hello_path.py"
  tmp_file_path.write_text("print('async from pathlib.Path')")
  upload_res_path = await client.aio.environments.files.upload(
      environment="env_123",
      path="async_hello_path.py",
      file=tmp_file_path,
      overwrite=True,
  )
  assert upload_res_path.files and len(upload_res_path.files) == 1
  assert (
      mock_gaos_server.uploaded_bytes[-1] == b"print('async from pathlib.Path')"
  )

  # 4. Async test upload with open file handle (io.IOBase)
  with open(str(tmp_file), "rb") as fh:
    upload_res_fh = await client.aio.environments.files.upload(
        environment="env_123",
        path="async_hello_fh.py",
        file=fh,
    )
    assert upload_res_fh.files and len(upload_res_fh.files) == 1
    assert (
        mock_gaos_server.uploaded_bytes[-1]
        == b"print('async from file path str')"
    )


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

  create_req = CreateEnvironmentRequest(
      from_environment="environments/env_abc_1234",
  )
  assert create_req.from_environment == "environments/env_abc_1234"


def test_python_environments_dedicated_module_and_from_environment():
  """Tests dedicated environments module and from_environment creation."""
  assert hasattr(environments, "CreateEnvironmentRequest")
  assert hasattr(environments, "Environment")
  assert hasattr(environments, "EnvironmentListResponse")
  assert hasattr(environments, "EnvironmentFile")
  assert hasattr(environments, "GetEnvironmentFilesResponse")
  assert hasattr(environments, "EnvironmentStatus")
  assert hasattr(environments, "EnvironmentListParams")
  assert hasattr(environments, "EnvironmentDeleteResponse")

  # Test backward-compatible re-exports in interactions module
  assert hasattr(interactions, "Environment")
  assert hasattr(interactions, "CreateEnvironmentRequest")
  assert hasattr(interactions, "EnvironmentFile")

  req = environments.CreateEnvironmentRequest(
      from_environment="environments/env_abc_1234",
  )
  assert req.from_environment == "environments/env_abc_1234"

  req_dict = req.model_dump(exclude_unset=True, by_alias=True)
  assert req_dict == {"from_environment": "environments/env_abc_1234"}
