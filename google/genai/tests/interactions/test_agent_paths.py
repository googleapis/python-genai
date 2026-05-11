
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
#


"""Tests for Agents CRUD URL paths on both GenAI and Vertex AI."""

from unittest import mock
import pytest
from httpx import Request, Response, Client as HTTPClient
from google.genai._interactions_private._client import GeminiNextGenAPIClient


def _make_client(is_vertex):
    """Create a private nextgen client configured for GenAI or Vertex."""
    if is_vertex:
        base_url = "https://us-central1-aiplatform.googleapis.com/"
        api_version = "v1beta1"
    else:
        base_url = "https://generativelanguage.googleapis.com/"
        api_version = "v1beta"

    client = GeminiNextGenAPIClient(
        base_url=base_url,
        api_key="test-key",
        api_version=api_version,
    )
    if is_vertex:
        client._is_vertex = True
        client._vertex_project = "test-project"
        client._vertex_location = "us-central1"
    return client


@pytest.mark.parametrize("is_vertex", [True, False])
def test_agents_create_path(is_vertex):
    client = _make_client(is_vertex)
    if is_vertex:
        expected = "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/test-project/locations/us-central1/agents"
    else:
        expected = "https://generativelanguage.googleapis.com/v1beta/agents"

    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('POST', ''), json={"id": "a"})
        client.agents.create(id="a", base_agent="test")
        request = mock_send.call_args[0][0]
        assert str(request.url) == expected


@pytest.mark.parametrize("is_vertex", [True, False])
def test_agents_list_path(is_vertex):
    client = _make_client(is_vertex)
    if is_vertex:
        expected = "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/test-project/locations/us-central1/agents"
    else:
        expected = "https://generativelanguage.googleapis.com/v1beta/agents"

    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('GET', ''), json={"agents": []})
        client.agents.list()
        request = mock_send.call_args[0][0]
        assert str(request.url) == expected


@pytest.mark.parametrize("is_vertex", [True, False])
def test_agents_get_path(is_vertex):
    client = _make_client(is_vertex)
    if is_vertex:
        expected = "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/test-project/locations/us-central1/agents/my-agent"
    else:
        expected = "https://generativelanguage.googleapis.com/v1beta/agents/my-agent"

    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('GET', ''), json={"id": "my-agent"})
        client.agents.get(id="my-agent")
        request = mock_send.call_args[0][0]
        assert str(request.url) == expected


@pytest.mark.parametrize("is_vertex", [True, False])
def test_agents_delete_path(is_vertex):
    client = _make_client(is_vertex)
    if is_vertex:
        expected = "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/test-project/locations/us-central1/agents/my-agent"
    else:
        expected = "https://generativelanguage.googleapis.com/v1beta/agents/my-agent"

    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('DELETE', ''), json={})
        client.agents.delete(id="my-agent")
        request = mock_send.call_args[0][0]
        assert str(request.url) == expected
