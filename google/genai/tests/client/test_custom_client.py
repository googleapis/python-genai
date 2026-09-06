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

"""Tests for custom clients."""
import asyncio
from unittest import mock

from google.oauth2 import credentials
import httpx
import pytest

from ... import _api_client as api_client
from ... import Client


try:
  import aiohttp

  AIOHTTP_NOT_INSTALLED = False
except ImportError:
  AIOHTTP_NOT_INSTALLED = True
  aiohttp = mock.MagicMock()

requires_aiohttp = pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason='aiohttp is not installed, skipping test.'
)


# Httpx
def test_constructor_with_httpx_clients():
  mldev_http_options = {
      'httpx_client': httpx.Client(trust_env=False),
      'httpx_async_client': httpx.AsyncClient(trust_env=False),
  }
  vertexai_http_options = {
      'httpx_client': httpx.Client(trust_env=False),
      'httpx_async_client': httpx.AsyncClient(trust_env=False),
  }

  # Even if aiohttp is installed, expect it to be disabled when httpx clients
  # are provided.
  api_client.has_aiohttp = True

  mldev_client = Client(
      api_key='google_api_key', http_options=mldev_http_options
  )
  assert not mldev_client.models._api_client._httpx_client.trust_env
  assert not mldev_client.models._api_client._async_httpx_client.trust_env
  # Expect aiohttp to be disabled when httpx clients are provided, regardless of
  # whether aiohttp is installed.
  assert not mldev_client.models._api_client._use_aiohttp()

  vertexai_client = Client(
      vertexai=True,
      project='fake_project_id',
      location='fake-location',
      http_options=vertexai_http_options,
  )
  assert not vertexai_client.models._api_client._httpx_client.trust_env
  assert not vertexai_client.models._api_client._async_httpx_client.trust_env
  # Expect aiohttp to be disabled when httpx clients are provided, regardless of
  # whether aiohttp is installed.
  assert not mldev_client.models._api_client._use_aiohttp()


# Aiohttp
@requires_aiohttp
@pytest.mark.asyncio
@pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason='aiohttp is not installed, skipping test.'
)
async def test_constructor_with_aiohttp_clients():
  api_client.has_aiohttp = True
  mldev_http_options = {
      'aiohttp_client': aiohttp.ClientSession(trust_env=False),
  }
  vertexai_http_options = {
      'aiohttp_client': aiohttp.ClientSession(trust_env=False),
  }
  mldev_client = Client(
      api_key='google_api_key', http_options=mldev_http_options
  )
  assert not mldev_client.models._api_client._aiohttp_session.trust_env

  vertexai_client = Client(
      vertexai=True,
      project='fake_project_id',
      location='fake-location',
      http_options=vertexai_http_options,
  )
  assert not vertexai_client.models._api_client._aiohttp_session.trust_env

