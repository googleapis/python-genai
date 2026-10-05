# Copyright 2025 Google LLC
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

from unittest import mock

import httpx
import pytest

from ..._gaos import google_genai as gaos_google_genai
from ... import client as client_lib


pytest_plugins = ("pytest_asyncio",)


def test_client_timeout():
  with mock.patch.object(
      gaos_google_genai, "GenAI", spec_set=True
  ) as mock_genai:
    mock_client = mock.Mock()
    mock_genai.return_value = mock_client

    client = client_lib.Client(
        api_key="placeholder",
        http_options={"api_version": "v1alpha", "timeout": 5000},
    )

    # Trigger client build
    _ = client.interactions.with_raw_response

    mock_genai.assert_called_once_with(
        security=mock.ANY,
        api_version=mock.ANY,
        user_project=mock.ANY,
        server_url=mock.ANY,
        client=mock.ANY,
        timeout_ms=5000,
        retry_config=mock.ANY,
    )


@pytest.mark.asyncio
async def test_async_client_timeout():
  with mock.patch.object(
      gaos_google_genai, "AsyncGenAI", spec_set=True
  ) as mock_async_genai:
    mock_client = mock.Mock()
    mock_async_genai.return_value = mock_client

    client = client_lib.Client(
        api_key="placeholder",
        http_options={"api_version": "v1alpha", "timeout": 5000},
    )

    # Trigger client build
    _ = client.aio.interactions.with_raw_response

    mock_async_genai.assert_called_once_with(
        security=mock.ANY,
        api_version=mock.ANY,
        user_project=mock.ANY,
        server_url=mock.ANY,
        async_client=mock.ANY,
        timeout_ms=5000,
        retry_config=mock.ANY,
    )


def test_client_vertex_default_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha"},
  )
  sdk_client = client.interactions.sdk_configuration.client
  assert sdk_client is not None
  # Default on Vertex should match GenAI default (timeout=None, no 5s timeout)
  assert sdk_client.timeout == httpx.Timeout(None)
  assert sdk_client.timeout != httpx.Timeout(5.0)


def test_client_vertex_explicit_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha", "timeout": 12000},
  )
  interactions_client = client.interactions
  assert interactions_client.sdk_configuration.timeout_ms == 12000


@pytest.mark.asyncio
async def test_async_client_vertex_default_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha"},
  )
  async_sdk_client = client.aio.interactions.sdk_configuration.async_client
  assert async_sdk_client is not None
  assert async_sdk_client.timeout == httpx.Timeout(None)
  assert async_sdk_client.timeout != httpx.Timeout(5.0)


@pytest.mark.asyncio
async def test_async_client_vertex_explicit_timeout():
  client = client_lib.Client(
      vertexai=True,
      project="test-project",
      location="us-central1",
      http_options={"api_version": "v1alpha", "timeout": 15000},
  )
  async_interactions_client = client.aio.interactions
  assert async_interactions_client.sdk_configuration.timeout_ms == 15000


def test_client_genai_default_timeout():
  client = client_lib.Client(
      api_key="placeholder",
      http_options={"api_version": "v1alpha"},
  )
  sdk_client = client.interactions.sdk_configuration.client
  assert sdk_client is not None
  assert sdk_client.timeout == httpx.Timeout(None)
  assert sdk_client.timeout != httpx.Timeout(5.0)


@pytest.mark.asyncio
async def test_async_client_genai_default_timeout():
  client = client_lib.Client(
      api_key="placeholder",
      http_options={"api_version": "v1alpha"},
  )
  async_sdk_client = client.aio.interactions.sdk_configuration.async_client
  assert async_sdk_client is not None
  assert async_sdk_client.timeout == httpx.Timeout(None)
  assert async_sdk_client.timeout != httpx.Timeout(5.0)



@pytest.mark.filterwarnings("error")
def test_unrecognized_model_serialization():
  from ..._gaos.types.interactions.createmodelinteraction import CreateModelInteraction
  # This shouldn't raise a Pydantic serialization error due to UnrecognizedStr
  obj = CreateModelInteraction(model="gemini-3.5-flash", input="hello")
  dumped = obj.model_dump()
  assert dumped["model"] == "gemini-3.5-flash"


@pytest.mark.filterwarnings("error")
def test_unrecognized_model_request_serialization():
  from ..._gaos.models.createinteraction import CreateInteractionRequest
  from ..._gaos.types.interactions.createmodelinteraction import CreateModelInteraction
  body = CreateModelInteraction(model="gemini-3.5-flash", input="hello")
  req = CreateInteractionRequest(body=body)
  dumped = req.model_dump()
  assert dumped["body"]["model"] == "gemini-3.5-flash"


def test_allowlist_entry_with_dict_transform():
  from ..._gaos.types.interactions.allowlistentry import AllowlistEntry

  # Should construct successfully with a single dict
  entry = AllowlistEntry(
      domain="github.com", transform={"Authorization": "Bearer TOKEN"}
  )
  assert entry.domain == "github.com"
  assert entry.transform == {"Authorization": "Bearer TOKEN"}

  # Serialization should preserve it as a dict
  dumped = entry.model_dump()
  assert dumped["transform"] == {"Authorization": "Bearer TOKEN"}


def test_allowlist_entry_with_list_transform():
  from ..._gaos.types.interactions.allowlistentry import AllowlistEntry

  # Should construct successfully with a list of dicts
  entry = AllowlistEntry(
      domain="github.com", transform=[{"Authorization": "Bearer TOKEN"}]
  )
  assert entry.domain == "github.com"
  assert entry.transform == [{"Authorization": "Bearer TOKEN"}]

  # Serialization should preserve it as a list
  dumped = entry.model_dump()
  assert dumped["transform"] == [{"Authorization": "Bearer TOKEN"}]
