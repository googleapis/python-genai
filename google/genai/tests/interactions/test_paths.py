
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


"""Tests for Interactions API URL paths."""

from unittest import mock
import pytest
from httpx import Request, Response
from ..._api_client import AsyncHttpxClient
from httpx import Client as HTTPClient
from .. import pytest_helper
import google.auth

@mock.patch.object(google.auth, "default", autospec=True)
def test_interactions_paths(mock_auth_default, client):
    interaction_id = "test-interaction-id"

    mock_creds = mock.Mock()
    mock_creds.token = "test-token"
    mock_creds.expired = False
    mock_creds.quota_project_id = "test-quota-project"
    mock_auth_default.return_value = (mock_creds, "test-project")

    if client._api_client.vertexai:
        expected_base_url = f'https://{client._api_client.location}-aiplatform.googleapis.com/v1beta1/projects/{client._api_client.project}/locations/{client._api_client.location}'
    else:
        expected_base_url = "https://generativelanguage.googleapis.com/v1beta"

    with mock.patch.object(HTTPClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('GET', ''))
        client.interactions.get(id=interaction_id)
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == f'{expected_base_url}/interactions/{interaction_id}'

        mock_send.reset_mock()
        mock_send.return_value = Response(200, request=Request('POST', ''))
        client.interactions.cancel(id=interaction_id)
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == f'{expected_base_url}/interactions/{interaction_id}/cancel'

        mock_send.reset_mock()
        mock_send.return_value = Response(200, request=Request('DELETE', ''))
        client.interactions.delete(id=interaction_id)
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == f'{expected_base_url}/interactions/{interaction_id}'

@pytest.mark.asyncio
@mock.patch.object(google.auth, "default", autospec=True)
async def test_async_interactions_paths(mock_auth_default, client):
    interaction_id = "test-interaction-id"

    mock_creds = mock.Mock()
    mock_creds.token = "test-token"
    mock_creds.expired = False
    mock_creds.quota_project_id = "test-quota-project"
    mock_auth_default.return_value = (mock_creds, "test-project")

    if client._api_client.vertexai:
        expected_base_url = f'https://{client._api_client.location}-aiplatform.googleapis.com/v1beta1/projects/{client._api_client.project}/locations/{client._api_client.location}'
    else:
        expected_base_url = "https://generativelanguage.googleapis.com/v1beta"

    with mock.patch.object(AsyncHttpxClient, "send") as mock_send:
        mock_send.return_value = Response(200, request=Request('GET', ''))
        await client.aio.interactions.get(id=interaction_id)
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == f'{expected_base_url}/interactions/{interaction_id}'

        mock_send.reset_mock()
        mock_send.return_value = Response(200, request=Request('POST', ''))
        await client.aio.interactions.cancel(id=interaction_id)
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == f'{expected_base_url}/interactions/{interaction_id}/cancel'

        mock_send.reset_mock()
        mock_send.return_value = Response(200, request=Request('DELETE', ''))
        await client.aio.interactions.delete(id=interaction_id)
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert str(request.url) == f'{expected_base_url}/interactions/{interaction_id}'

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_table=[],
)
