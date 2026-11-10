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

"""Tests that GAOS resources use the client's API version."""

from typing import Any

import pytest

from ... import _api_client
from ... import Client
from ... import types
from . import conftest


def _make_client(
    server: conftest.MockGaosServer, **http_options: Any
) -> Client:
  return Client(
      api_key="test-key",
      vertexai=False,
      http_options=types.HttpOptions(base_url=server.base_url, **http_options),
  )


def _list_resources(client: Client) -> None:
  client.agents.list()
  client.triggers.list()
  client.environments.list()
  client.credentials.list()
  client.webhooks.list()
  client.voices.list()


def _expected_paths(api_version: str) -> list[str]:
  return [
      f"GET /{api_version}/agents",
      f"GET /{api_version}/triggers",
      f"GET /{api_version}/environments",
      f"GET /{api_version}/credentials",
      f"GET /{api_version}/webhooks",
      f"GET /{api_version}/voices",
  ]


def test_resources_use_default_api_version(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  client = _make_client(mock_gaos_server)

  _list_resources(client)
  client.interactions.delete(id="abc")

  version = _api_client.GOOGLE_AI_API_DEFAULT_VERSION
  assert mock_gaos_server.captured == _expected_paths(version) + [
      f"DELETE /{version}/interactions/abc"
  ]


def test_http_options_api_version_is_respected(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  client = _make_client(mock_gaos_server, api_version="v1alpha")

  _list_resources(client)

  assert mock_gaos_server.captured == _expected_paths("v1alpha")


def test_env_var_api_version_is_respected(
    mock_gaos_server: conftest.MockGaosServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setenv("GOOGLE_GENAI_API_VERSION", "v1alpha")
  client = _make_client(mock_gaos_server)

  _list_resources(client)

  assert mock_gaos_server.captured == _expected_paths("v1alpha")


def test_empty_env_var_api_version_is_ignored(
    mock_gaos_server: conftest.MockGaosServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setenv("GOOGLE_GENAI_API_VERSION", "")
  client = _make_client(mock_gaos_server)

  _list_resources(client)

  assert mock_gaos_server.captured == _expected_paths(
      _api_client.GOOGLE_AI_API_DEFAULT_VERSION
  )


def test_environment_file_download_uses_client_api_version(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.handler_fn = lambda req, _: conftest.RawHttpResponse(
      body=b"content", content_type="application/octet-stream"
  )
  client = _make_client(mock_gaos_server, api_version="v1alpha")

  downloaded = client.environments.files.download(
      environment="env_123", path="src/main.py"
  )

  assert downloaded == b"content"
  assert mock_gaos_server.captured == [
      "GET /v1alpha/environments/env_123/files/src/main.py?alt=media"
  ]
