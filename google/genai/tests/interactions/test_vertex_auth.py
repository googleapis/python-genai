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

import typing
import pytest
from unittest.mock import Mock, MagicMock
from httpx import Request, Response
from ..._interactions import GeminiNextGenAPIClient


@pytest.fixture
def client_adapter():
    """
    Shared mock equivalent to the jasmine.SpyObj<GeminiNextGenAPIClientAdapter>.
    """
    adapter = MagicMock()
    adapter.is_vertex_ai.return_value = False
    adapter.get_project.return_value = "my-project"
    adapter.get_location.return_value = "my-location"
    adapter.get_auth_headers.return_value = {}
    return adapter


class TestInteractionsRoutedToGemini:
    @pytest.fixture(autouse=True)
    def setup_client(self, client_adapter, monkeypatch):
        client_adapter.is_vertex_ai.return_value = False

        client = GeminiNextGenAPIClient(
            client_adapter=client_adapter,
            base_url="https://my.base.host",
            api_key="my-api-key",
            api_version="somev1",
        )

        # Spy on client._client.send
        def send_mock(
            request: Request,
            *args,
            **kwargs
        ):
            return Response(request=request, status_code=200)

        self.send_mock = client._client.send = Mock(wraps=send_mock)
        self.client_adapter = client_adapter
        self.client = client

    def test_should_send_requests_to_existing_paths_without_client_auth_headers(self):
        self.client.interactions.create(
            agent="some-agent",
            input="some input",
        )

        req: Request = self.send_mock.call_args_list[0][0][0]

        assert req.url == "https://my.base.host/somev1/interactions"
        assert req.method.lower() == "post"
        # in Gemini mode with apiKey, auth headers from adapter should NOT be called
        self.client_adapter.get_auth_headers.assert_not_called()

    def test_should_retry_the_call(self):
        def failing_fetch(request=Request, *args, **kwargs):
            return Response(
                request=request,
                status_code=500,
                headers={"retry-after-ms": "1"},
            )

        self.client.max_retries = 4
        self.send_mock.side_effect = failing_fetch

        with pytest.raises(Exception):
            self.client.interactions.create(
                agent="some-agent",
                input="some input",
            )

        # initial call + 4 retries
        assert self.send_mock.call_count == 5

    def test_should_not_invoke_client_auth_headers_if_manually_given(self):
        # First call: manual Authorization header
        self.client.api_key = None
        self.client.interactions.create(
            agent="some-agent",
            input="some input",
            extra_headers={
                "Authorization": "Bearer some-manual-token",
            }
        )

        self.client_adapter.get_auth_headers.assert_not_called()

        req: Request = self.send_mock.call_args_list[0][0][0]
        assert req.headers.get("Authorization") == "Bearer some-manual-token"
        assert "x-goog-api-key" not in req.headers

        # Reset spies
        self.send_mock.reset_mock()
        self.client_adapter.get_auth_headers.reset_mock()

        # Second call: manual x-goog-api-key
        self.client.interactions.create(
            agent="some-agent",
            input="some input",
            extra_headers={
                "x-goog-api-key": "some-manual-key"
            }
        )

        self.client_adapter.get_auth_headers.assert_not_called()

        req: Request = self.send_mock.call_args_list[0][0][0]
        assert req.headers.get("x-goog-api-key") == "some-manual-key"
        assert "Authorization" not in req.headers


class TestInteractionsRoutedToVertex:
    @pytest.fixture(autouse=True)
    def setup_client(self, client_adapter):
        client_adapter.is_vertex_ai.return_value = True
        client_adapter.get_auth_headers.return_value = {
            "Authorization": "Bearer some-token",
        }

        client = GeminiNextGenAPIClient(
            client_adapter=client_adapter,
            base_url="https://my.base.host",
            api_version="somev1",
        )

        # Spy on client._client.send
        def send_mock(request: Request, *args, **kwargs):
            return Response(request=request, status_code=200)

        self.send_mock = client._client.send = Mock(wraps=send_mock)
        self.client_adapter = client_adapter
        self.client = client

    def test_should_send_requests_to_new_paths_with_client_auth_headers(self):
        # Override auth headers for this test
        self.client_adapter.get_auth_headers.return_value = {
            "Authorization": "Bearer my-access-token",
        }

        self.client.interactions.create(
            agent="some-agent",
            input="some input",
        )

        req: Request = self.send_mock.call_args_list[0][0][0]

        assert (
            req.url
            == "https://my.base.host/somev1/projects/my-project/locations/my-location/interactions"
        )
        assert req.method.lower() == "post"
        self.client_adapter.get_auth_headers.assert_called()

        assert req.headers.get("Authorization") == "Bearer my-access-token"

    def test_should_retry_the_call(self):
        def failing_fetch(request: Request, *args, **kwargs):
            return Response(
                request=request,
                status_code=500,
                headers={"retry-after-ms": "1"},
            )

        self.send_mock.side_effect = failing_fetch
        self.client.max_retries = 4

        with pytest.raises(Exception):
            self.client.interactions.create(
                agent="some-agent",
                input="some input",
            )

        assert self.send_mock.call_count == 5
        # Vertex path should re-fetch auth headers on each retry
        assert self.client_adapter.get_auth_headers.call_count == 5

    def test_should_override_client_auth_headers_if_manually_given(self):
        # Manual Authorization header
        self.client.interactions.create(
            agent="some-agent",
            input="some input",
            extra_headers={
                "Authorization": "Bearer some-manual-token"
            }
        )

        req: Request = self.send_mock.call_args_list[0][0][0]
        assert req.headers.get("Authorization") == "Bearer some-manual-token"

        # Reset spies
        self.send_mock.reset_mock()
        self.client_adapter.get_auth_headers.reset_mock()

        # Manual x-goog-api-key header
        self.client.interactions.create(
            agent="some-agent",
            input="some input",
            extra_headers={
                "x-goog-api-key": "some-manual-key"
            }
        )

        req: Request = self.send_mock.call_args_list[0][0][0]
        assert req.headers.get("x-goog-api-key") == "some-manual-key"
