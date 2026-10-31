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

"""Tests that v1beta-only GAOS resources are pinned to v1beta by default."""

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


def _list_v1beta_only_resources(client: Client) -> None:
  client.agents.list()
  client.triggers.list()
  client.environments.list()
  client.credentials.list()
  client.webhooks.list()
  client.voices.list()


async def _async_list_v1beta_only_resources(client: Client) -> None:
  await client.aio.agents.list()
  await client.aio.triggers.list()
  await client.aio.environments.list()
  await client.aio.credentials.list()
  await client.aio.webhooks.list()
  await client.aio.voices.list()


def _expected_paths(api_version: str) -> list[str]:
  return [
      f"GET /{api_version}/agents",
      f"GET /{api_version}/triggers",
      f"GET /{api_version}/environments",
      f"GET /{api_version}/credentials",
      f"GET /{api_version}/webhooks",
      f"GET /{api_version}/voices",
  ]


@pytest.fixture
def default_v1(monkeypatch: pytest.MonkeyPatch) -> None:
  """Simulates the exported SDK, where the default API version is v1."""
  monkeypatch.delenv("GOOGLE_GENAI_API_VERSION", raising=False)
  monkeypatch.setattr(_api_client, "GOOGLE_AI_API_DEFAULT_VERSION", "v1")
  public_api_client = getattr(_api_client, "public_api_client", None)
  if public_api_client is not None:
    monkeypatch.setattr(
        public_api_client, "GOOGLE_AI_API_DEFAULT_VERSION", "v1"
    )


@pytest.mark.usefixtures("default_v1")
def test_v1beta_only_resources_pinned_when_default_is_v1(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  client = _make_client(mock_gaos_server)
  assert client._api_client._http_options.api_version == "v1"

  _list_v1beta_only_resources(client)

  assert mock_gaos_server.captured == _expected_paths("v1beta")


@pytest.mark.asyncio
@pytest.mark.usefixtures("default_v1")
async def test_async_v1beta_only_resources_pinned_when_default_is_v1(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  client = _make_client(mock_gaos_server)
  assert client._api_client._http_options.api_version == "v1"

  await _async_list_v1beta_only_resources(client)

  assert mock_gaos_server.captured == _expected_paths("v1beta")


@pytest.mark.usefixtures("default_v1")
def test_explicit_http_options_api_version_is_respected(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  client = _make_client(mock_gaos_server, api_version="v1alpha")

  _list_v1beta_only_resources(client)

  assert mock_gaos_server.captured == _expected_paths("v1alpha")


@pytest.mark.usefixtures("default_v1")
def test_explicit_v1_is_respected(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  client = _make_client(mock_gaos_server, api_version="v1")

  _list_v1beta_only_resources(client)

  assert mock_gaos_server.captured == _expected_paths("v1")


@pytest.mark.usefixtures("default_v1")
def test_env_var_api_version_is_respected(
    mock_gaos_server: conftest.MockGaosServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setenv("GOOGLE_GENAI_API_VERSION", "v1alpha")
  client = _make_client(mock_gaos_server)

  _list_v1beta_only_resources(client)

  assert mock_gaos_server.captured == _expected_paths("v1alpha")


@pytest.mark.usefixtures("default_v1")
def test_environment_file_download_pinned_when_default_is_v1(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.handler_fn = lambda req, _: conftest.RawHttpResponse(
      body=b"content", content_type="application/octet-stream"
  )
  client = _make_client(mock_gaos_server)

  downloaded = client.environments.files.download(
      environment="env_123", path="src/main.py"
  )

  assert downloaded == b"content"
  assert mock_gaos_server.captured == [
      "GET /v1beta/environments/env_123/files/src/main.py?alt=media"
  ]


@pytest.mark.usefixtures("default_v1")
def test_environment_file_download_per_request_api_version_is_respected(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.handler_fn = lambda req, _: conftest.RawHttpResponse(
      body=b"content", content_type="application/octet-stream"
  )
  client = _make_client(mock_gaos_server)

  client.environments.files.download(
      environment="env_123",
      path="src/main.py",
      http_options={"api_version": "v1alpha"},
  )

  assert mock_gaos_server.captured == [
      "GET /v1alpha/environments/env_123/files/src/main.py?alt=media"
  ]
