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
"""Lifecycle tests for Credentials API."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest

from ... import Client
from ..._gaos.models.getcredential import GetCredentialRequest
from ..._gaos.models.listcredentials import ListCredentialsRequest
from ..._gaos.types.credentials.credential import Credential
from ..._gaos.types.credentials.credentiallistresponse import (
    CredentialListResponse,
)
from ..._gaos.types.credentials.environmentvariableconfig import (
    EnvironmentVariableConfig,
)
from ..._gaos.types.credentials.environmentvariableupdateconfig import (
    EnvironmentVariableUpdateConfig,
)
from ..._gaos.types.credentials.httpbearerconfig import HTTPBearerConfig
from ..._gaos.types.credentials.httpbearerupdateconfig import (
    HTTPBearerUpdateConfig,
)
from ..._gaos.types.credentials.oauth2config import OAuth2Config
from ..._gaos.types.credentials.oauth2updateconfig import OAuth2UpdateConfig

CREDENTIAL_BODY = {
    "id": "cred_bearer_123",
    "status": "active",
    "type": "bearer_token",
    "create_time": "2026-07-22T15:18:38Z",
    "update_time": "2026-07-22T15:18:38Z",
}

CREDENTIAL_LIST_BODY = {
    "credentials": [
        CREDENTIAL_BODY,
        {
            "id": "cred_env_123",
            "status": "active",
            "type": "environment_variable",
            "create_time": "2026-07-22T15:18:38Z",
            "update_time": "2026-07-22T15:18:38Z",
        },
        {
            "id": "cred_oauth_123",
            "status": "active",
            "type": "oauth2",
            "create_time": "2026-07-22T15:18:38Z",
            "update_time": "2026-07-22T15:18:38Z",
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
        self.path == "/v1beta/credentials"
        or self.path.startswith("/v1beta/credentials?")
    ):
      payload = json.dumps(CREDENTIAL_LIST_BODY).encode()
    else:
      payload = json.dumps(CREDENTIAL_BODY).encode()

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


def test_python_credentials_lifecycle_routes_through_google_genai_client(
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

    # 1. Create Bearer Token Credential with header_name and prefix
    bearer_cred = client.credentials.create(
        id="cred_bearer_123",
        token="test-bearer-token",
        header_name="X-Custom-Auth",
        prefix="Token",
        type="bearer_token",
    )
    assert bearer_cred.id == "cred_bearer_123"

    # 2. Create Environment Variable Credential with injection_location and trusted_domains
    env_cred = client.credentials.create(
        id="cred_env_123",
        value="super-secret-key",
        injection_location=["header", "query"],
        trusted_domains=["api.example.com", "service.example.org"],
        type="environment_variable",
    )
    assert env_cred.id == "cred_bearer_123"

    # 3. Create OAuth2 Credential with scopes
    oauth_cred = client.credentials.create(
        id="cred_oauth_123",
        client_id="test-client-id",
        client_secret="test-client-secret",
        refresh_token="test-refresh-token",
        token_url="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
        type="oauth2",
    )
    assert oauth_cred.id == "cred_bearer_123"

    # 4. List credentials
    list_res = client.credentials.list()
    assert list_res.credentials is not None
    assert len(list_res.credentials) == 3

    # 5. Get credential
    fetched = client.credentials.get(id="cred_bearer_123")
    assert fetched.id == "cred_bearer_123"

    # 6. Update Bearer Token Credential
    client.credentials.update(
        id="cred_bearer_123",
        token="updated-bearer-token",
        header_name="Authorization",
        prefix="Bearer",
        type="bearer_token",
    )

    # 7. Update Environment Variable Credential
    client.credentials.update(
        id="cred_env_123",
        value="updated-secret",
        injection_location="header",
        trusted_domains=["api.example.com"],
        type="environment_variable",
    )

    # 8. Update OAuth2 Credential
    client.credentials.update(
        id="cred_oauth_123",
        client_secret="updated-secret",
        scopes=["scope1", "scope2"],
        type="oauth2",
    )

    # 9. Delete credential
    client.credentials.delete(id="cred_bearer_123")

    assert captured == [
        "POST /v1beta/credentials",
        "POST /v1beta/credentials",
        "POST /v1beta/credentials",
        "GET /v1beta/credentials",
        "GET /v1beta/credentials/cred_bearer_123",
        "PATCH /v1beta/credentials/cred_bearer_123",
        "PATCH /v1beta/credentials/cred_env_123",
        "PATCH /v1beta/credentials/cred_oauth_123",
        "DELETE /v1beta/credentials/cred_bearer_123",
    ]

    # Verify captured bodies
    assert captured_bodies[0] == {
        "id": "cred_bearer_123",
        "token": "test-bearer-token",
        "header_name": "X-Custom-Auth",
        "prefix": "Token",
        "type": "bearer_token",
    }
    assert captured_bodies[1] == {
        "id": "cred_env_123",
        "value": "super-secret-key",
        "injection_location": ["header", "query"],
        "trusted_domains": ["api.example.com", "service.example.org"],
        "type": "environment_variable",
    }
    assert captured_bodies[2] == {
        "id": "cred_oauth_123",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
        "type": "oauth2",
    }

  finally:
    server.shutdown()
    thread.join()
    server.server_close()


@pytest.mark.asyncio
async def test_python_credentials_async_lifecycle(monkeypatch):
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

    credential = await client.aio.credentials.create(
        id="cred_env_123",
        value="super-secret-key",
        injection_location=["header", "query"],
        trusted_domains=["api.example.com"],
        type="environment_variable",
    )
    list_res = await client.aio.credentials.list()
    fetched = await client.aio.credentials.get(id="cred_env_123")
    updated = await client.aio.credentials.update(
        id="cred_env_123",
        value="updated-secret",
        injection_location="header",
        type="environment_variable",
    )
    await client.aio.credentials.delete(id="cred_env_123")

    assert credential.id == "cred_bearer_123"
    assert fetched.id == "cred_bearer_123"
    assert updated.id == "cred_bearer_123"
    assert list_res.credentials is not None
    assert len(list_res.credentials) == 3
    assert captured == [
        "POST /v1beta/credentials",
        "GET /v1beta/credentials",
        "GET /v1beta/credentials/cred_env_123",
        "PATCH /v1beta/credentials/cred_env_123",
        "DELETE /v1beta/credentials/cred_env_123",
    ]

  finally:
    server.shutdown()
    thread.join()
    server.server_close()


def test_python_credentials_with_raw_response(monkeypatch):
  monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
  captured: list[str] = []
  handler = type("Handler", (_RecordingHandler,), {
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

    raw_res = client.credentials.with_raw_response.list()
    parsed = raw_res.parse()
    assert parsed.credentials is not None
    assert len(parsed.credentials) == 3
    assert parsed.credentials[0].id == "cred_bearer_123"

  finally:
    server.shutdown()
    thread.join()
    server.server_close()


def test_python_credentials_types_and_models():
  cred = Credential(
      id="cred_123",
      status="active",
      type="bearer_token",
      create_time="2026-07-22T15:18:38Z",
      update_time="2026-07-22T15:18:38Z",
  )
  assert cred.id == "cred_123"
  assert cred.status == "active"
  assert cred.type == "bearer_token"
  assert cred.create_time is not None
  assert cred.update_time is not None

  list_resp = CredentialListResponse(
      credentials=[cred],
      next_page_token="next_tok",
  )
  assert list_resp.credentials is not None
  assert len(list_resp.credentials) == 1
  assert list_resp.next_page_token == "next_tok"

  # HTTP Bearer Config
  bearer = HTTPBearerConfig(
      id="cred_bearer",
      token="secret-token",
      header_name="X-Auth",
      prefix="Bearer",
  )
  assert bearer.id == "cred_bearer"
  assert bearer.token == "secret-token"
  assert bearer.header_name == "X-Auth"
  assert bearer.prefix == "Bearer"
  assert bearer.type == "bearer_token"

  bearer_update = HTTPBearerUpdateConfig(
      token="new-token",
      header_name="Authorization",
      prefix="Token",
  )
  assert bearer_update.token == "new-token"
  assert bearer_update.header_name == "Authorization"
  assert bearer_update.prefix == "Token"
  assert bearer_update.type == "bearer_token"

  # OAuth2 Config
  oauth = OAuth2Config(
      id="cred_oauth",
      client_id="cid",
      client_secret="csecret",
      refresh_token="rtoken",
      token_url="https://example.com/token",
      scopes=["https://www.googleapis.com/auth/cloud-platform"],
  )
  assert oauth.id == "cred_oauth"
  assert oauth.client_id == "cid"
  assert oauth.client_secret == "csecret"
  assert oauth.refresh_token == "rtoken"
  assert oauth.token_url == "https://example.com/token"
  assert oauth.scopes == ["https://www.googleapis.com/auth/cloud-platform"]
  assert oauth.type == "oauth2"

  oauth_update = OAuth2UpdateConfig(
      client_secret="new-secret",
      scopes=["scope1", "scope2"],
  )
  assert oauth_update.client_secret == "new-secret"
  assert oauth_update.scopes == ["scope1", "scope2"]
  assert oauth_update.type == "oauth2"

  # Environment Variable Config with single and multiple injection locations
  env_var = EnvironmentVariableConfig(
      id="cred_env",
      value="secret-key",
      injection_location=["header", "query"],
      trusted_domains=["api.example.com"],
  )
  assert env_var.id == "cred_env"
  assert env_var.value == "secret-key"
  assert env_var.injection_location == ["header", "query"]
  assert env_var.trusted_domains == ["api.example.com"]
  assert env_var.type == "environment_variable"

  env_var_single = EnvironmentVariableConfig(
      id="cred_env_2",
      value="secret-key",
      injection_location="header",
  )
  assert env_var_single.injection_location == "header"

  env_var_update = EnvironmentVariableUpdateConfig(
      value="updated-key",
      injection_location="query",
      trusted_domains=["new.example.com"],
  )
  assert env_var_update.value == "updated-key"
  assert env_var_update.injection_location == "query"
  assert env_var_update.trusted_domains == ["new.example.com"]
  assert env_var_update.type == "environment_variable"

  # Request models
  req = GetCredentialRequest(
      id="cred_123",
      api_version="v1beta",
  )
  assert req.id == "cred_123"
  assert req.api_version == "v1beta"

  list_req = ListCredentialsRequest(
      page_size=10,
      page_token="tok",
      api_version="v1beta",
  )
  assert list_req.page_size == 10
  assert list_req.page_token == "tok"
  assert list_req.api_version == "v1beta"
