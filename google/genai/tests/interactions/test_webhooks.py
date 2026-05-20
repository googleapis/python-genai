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


"""Tests for Webhooks API URL paths."""

from unittest import mock
import google.auth
from httpx import Client as HTTPClient
from httpx import Request, Response
import pytest
from ..._api_client import AsyncHttpxClient
from .. import pytest_helper


@mock.patch.object(google.auth, 'default', autospec=True)
def test_urls(mock_auth_default, client):
  webhook_id = 'test-webhook-id'

  mock_creds = mock.Mock()
  mock_creds.token = 'test-token'
  mock_creds.expired = False
  mock_creds.quota_project_id = 'test-quota-project'
  mock_auth_default.return_value = (mock_creds, 'test-project')

  if client._api_client.vertexai:
    if client._api_client.location == 'global':
      expected_base_url = f'https://aiplatform.googleapis.com/v1beta1/projects/{client._api_client.project}/locations/global'
    else:
      expected_base_url = f'https://{client._api_client.location}-aiplatform.googleapis.com/v1beta1/projects/{client._api_client.project}/locations/{client._api_client.location}'
  else:
    expected_base_url = 'https://generativelanguage.googleapis.com/v1beta'

  with mock.patch.object(HTTPClient, 'send') as mock_send:
    # 1. Create Webhook
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    client.webhooks.create(
        subscribed_events=['batch.succeeded'],
        uri='https://example.com/webhook',
        name='test-webhook',
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks'

    # 2. Get Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    client.webhooks.get(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}'

    # 3. List Webhooks
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    client.webhooks.list()
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks'

    # 4. Update Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(
        200, json={}, request=Request('PATCH', '')
    )
    client.webhooks.update(
        id=webhook_id,
        name='updated-webhook',
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}'

    # 5. Ping Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    client.webhooks.ping(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}:ping'

    # 6. Rotate Signing Secret
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    client.webhooks.rotate_signing_secret(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert (
        str(request.url)
        == f'{expected_base_url}/webhooks/{webhook_id}:rotateSigningSecret'
    )

    # 7. Delete Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(
        200, json={}, request=Request('DELETE', '')
    )
    client.webhooks.delete(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}'


@pytest.mark.asyncio
@mock.patch.object(google.auth, 'default', autospec=True)
async def test_async_urls(mock_auth_default, client):
  webhook_id = 'test-webhook-id'

  mock_creds = mock.Mock()
  mock_creds.token = 'test-token'
  mock_creds.expired = False
  mock_creds.quota_project_id = 'test-quota-project'
  mock_auth_default.return_value = (mock_creds, 'test-project')

  if client._api_client.vertexai:
    if client._api_client.location == 'global':
      expected_base_url = f'https://aiplatform.googleapis.com/v1beta1/projects/{client._api_client.project}/locations/global'
    else:
      expected_base_url = f'https://{client._api_client.location}-aiplatform.googleapis.com/v1beta1/projects/{client._api_client.project}/locations/{client._api_client.location}'
  else:
    expected_base_url = 'https://generativelanguage.googleapis.com/v1beta'

  with mock.patch.object(AsyncHttpxClient, 'send') as mock_send:
    # 1. Create Webhook
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    await client.aio.webhooks.create(
        subscribed_events=['batch.succeeded'],
        uri='https://example.com/webhook',
        name='test-webhook',
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks'

    # 2. Get Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    await client.aio.webhooks.get(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}'

    # 3. List Webhooks
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('GET', ''))
    await client.aio.webhooks.list()
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks'

    # 4. Update Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(
        200, json={}, request=Request('PATCH', '')
    )
    await client.aio.webhooks.update(
        id=webhook_id,
        name='updated-webhook',
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}'

    # 5. Ping Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    await client.aio.webhooks.ping(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}:ping'

    # 6. Rotate Signing Secret
    mock_send.reset_mock()
    mock_send.return_value = Response(200, json={}, request=Request('POST', ''))
    await client.aio.webhooks.rotate_signing_secret(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert (
        str(request.url)
        == f'{expected_base_url}/webhooks/{webhook_id}:rotateSigningSecret'
    )

    # 7. Delete Webhook
    mock_send.reset_mock()
    mock_send.return_value = Response(
        200, json={}, request=Request('DELETE', '')
    )
    await client.aio.webhooks.delete(id=webhook_id)
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    assert str(request.url) == f'{expected_base_url}/webhooks/{webhook_id}'


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_table=[],
)
