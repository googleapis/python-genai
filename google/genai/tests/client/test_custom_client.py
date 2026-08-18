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
import inspect
import socket
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

_PROXY_ENV_VARS = (
    'HTTP_PROXY',
    'HTTPS_PROXY',
    'ALL_PROXY',
    'http_proxy',
    'https_proxy',
    'all_proxy',
)


@pytest.fixture
def no_env_proxy(monkeypatch):
  for name in _PROXY_ENV_VARS:
    monkeypatch.delenv(name, raising=False)


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


# TCP keepalive
@pytest.mark.usefixtures('no_env_proxy')
def test_default_sync_client_enables_tcp_keepalive():
  """The default sync client sets SO_KEEPALIVE on its sockets."""
  client = Client(api_key='google_api_key')

  socket_options = (
      client.models._api_client._httpx_client._transport._pool._socket_options
  )
  assert (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) in socket_options


@pytest.mark.usefixtures('no_env_proxy')
def test_default_async_client_enables_tcp_keepalive():
  """The default async client sets SO_KEEPALIVE on its sockets."""
  client = Client(api_key='google_api_key')

  transport = client.models._api_client._async_httpx_client._transport
  assert (
      socket.SOL_SOCKET,
      socket.SO_KEEPALIVE,
      1,
  ) in transport._pool._socket_options


@pytest.mark.usefixtures('no_env_proxy')
def test_custom_transport_is_not_replaced():
  """A caller-supplied transport wins over the keepalive default."""
  transport = httpx.HTTPTransport()
  async_transport = httpx.AsyncHTTPTransport()
  client = Client(
      api_key='google_api_key',
      http_options={
          'client_args': {'transport': transport},
          'async_client_args': {'transport': async_transport},
      },
  )

  assert client.models._api_client._httpx_client._transport is transport
  assert (
      client.models._api_client._async_httpx_client._transport
      is async_transport
  )


@pytest.mark.usefixtures('no_env_proxy')
def test_env_proxy_keeps_httpx_proxy_mounts(monkeypatch):
  """The default client still honours HTTPS_PROXY from the environment."""
  monkeypatch.setenv('HTTPS_PROXY', 'http://localhost:8080')

  client = Client(api_key='google_api_key')

  assert client.models._api_client._httpx_client._mounts
  assert client.models._api_client._async_httpx_client._mounts


@pytest.mark.usefixtures('no_env_proxy')
def test_keepalive_skips_socket_constants_the_platform_lacks(monkeypatch):
  """A keepalive option the platform does not define is left out."""
  keepidle = getattr(socket, 'TCP_KEEPIDLE', None)
  if keepidle is None:
    pytest.skip('This platform does not define TCP_KEEPIDLE.')
  monkeypatch.delattr(socket, 'TCP_KEEPIDLE')

  client = Client(api_key='google_api_key')

  socket_options = (
      client.models._api_client._httpx_client._transport._pool._socket_options
  )
  assert (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) in socket_options
  assert all(option != keepidle for _, option, _ in socket_options)


@requires_aiohttp
@pytest.mark.asyncio
@pytest.mark.usefixtures('no_env_proxy')
async def test_default_aiohttp_connector_enables_tcp_keepalive():
  """The default aiohttp connector builds sockets with SO_KEEPALIVE set."""
  if (
      'socket_factory'
      not in inspect.signature(aiohttp.TCPConnector.__init__).parameters
  ):
    pytest.skip('The installed aiohttp has no socket_factory parameter.')
  api_client.has_aiohttp = True
  client = Client(api_key='google_api_key')

  session = await client.aio.models._api_client._get_aiohttp_session()
  try:
    sock = session.connector._socket_factory(
        (socket.AF_INET, socket.SOCK_STREAM, 0, '', ('127.0.0.1', 0))
    )
    try:
      assert sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE) == 1
    finally:
      sock.close()
  finally:
    await session.close()


@requires_aiohttp
@pytest.mark.asyncio
@pytest.mark.usefixtures('no_env_proxy')
async def test_aiohttp_socket_factory_tolerates_a_rejected_option(monkeypatch):
  """A keepalive option the kernel rejects still yields a usable socket."""
  if (
      'socket_factory'
      not in inspect.signature(aiohttp.TCPConnector.__init__).parameters
  ):
    pytest.skip('The installed aiohttp has no socket_factory parameter.')
  keepidle = getattr(socket, 'TCP_KEEPIDLE', None)
  if keepidle is None:
    pytest.skip('This platform does not define TCP_KEEPIDLE.')
  real_setsockopt = socket.socket.setsockopt

  def reject_keepidle(self, level, option, value):
    if level == socket.IPPROTO_TCP and option == keepidle:
      raise OSError('Protocol not available')
    return real_setsockopt(self, level, option, value)

  monkeypatch.setattr(socket.socket, 'setsockopt', reject_keepidle)
  api_client.has_aiohttp = True
  client = Client(api_key='google_api_key')

  session = await client.aio.models._api_client._get_aiohttp_session()
  try:
    sock = session.connector._socket_factory(
        (socket.AF_INET, socket.SOCK_STREAM, 0, '', ('127.0.0.1', 0))
    )
    try:
      assert sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE) == 1
    finally:
      sock.close()
  finally:
    await session.close()
