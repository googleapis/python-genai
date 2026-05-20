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


"""Tests for Agents API URL paths."""

from unittest import mock
import google.auth
from httpx import Client as HTTPClient
from httpx import Request, Response
import pytest
from ..._api_client import AsyncHttpxClient
from .. import pytest_helper


@mock.patch.object(google.auth, 'default', autospec=True)
def test_urls(mock_auth_default, client):
  agent_id = 'test-agent-id'

  mock_creds = mock.Mock()
  mock_creds.token = 'test-token'
  mock_creds.expired = False
  mock_creds.quota_project_id = 'test-quota-project'
  mock_auth_default.return_value = (mock_creds, 'test-project')

  if client._api_client.vertexai:
    if client._api_client.location == 'global':
      expected_base_url = (
          f'https://aiplatform.googleapis.com/v1beta1'
          f'/projects/{client._api_client.project}/locations/global'
      )
    else:
      expected_base_url = (
          f'https://{client._api_client.location}-aiplatform.googleapis.com'
          f'/v1beta1/projects/{client._api_client.project}'
          f'/locations/{client._api_client.location}'
      )
  else:
    expected_base_url = 'https://generativelanguage.googleapis.com/v1beta'

  with mock.patch.object(HTTPClient, 'send') as mock_send:
    # 1. Create Agent
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    client.agents.create(
        id=agent_id,
        description='Test agent',
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents'

    # 2. Get Agent
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    client.agents.get(id=agent_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents/{agent_id}'

    # 3. List Agents
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    client.agents.list()
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents'

    # 4. Delete Agent
    mock_send.reset_mock()
    mock_send.return_value = Response(
        200, json={}, request=Request('DELETE', '')
    )
    client.agents.delete(id=agent_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents/{agent_id}'


@pytest.mark.asyncio
@mock.patch.object(google.auth, 'default', autospec=True)
async def test_async_urls(mock_auth_default, client):
  agent_id = 'test-agent-id'

  mock_creds = mock.Mock()
  mock_creds.token = 'test-token'
  mock_creds.expired = False
  mock_creds.quota_project_id = 'test-quota-project'
  mock_auth_default.return_value = (mock_creds, 'test-project')

  if client._api_client.vertexai:
    if client._api_client.location == 'global':
      expected_base_url = (
          f'https://aiplatform.googleapis.com/v1beta1'
          f'/projects/{client._api_client.project}/locations/global'
      )
    else:
      expected_base_url = (
          f'https://{client._api_client.location}-aiplatform.googleapis.com'
          f'/v1beta1/projects/{client._api_client.project}'
          f'/locations/{client._api_client.location}'
      )
  else:
    expected_base_url = 'https://generativelanguage.googleapis.com/v1beta'

  with mock.patch.object(AsyncHttpxClient, 'send') as mock_send:
    # 1. Create Agent
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    await client.aio.agents.create(
        id=agent_id,
        description='Test agent',
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents'

    # 2. Get Agent
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    await client.aio.agents.get(id=agent_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents/{agent_id}'

    # 3. List Agents
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    await client.aio.agents.list()
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents'

    # 4. Delete Agent
    mock_send.reset_mock()
    mock_send.return_value = Response(
        200, json={}, request=Request('DELETE', '')
    )
    await client.aio.agents.delete(id=agent_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/agents/{agent_id}'


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_table=[],
)
