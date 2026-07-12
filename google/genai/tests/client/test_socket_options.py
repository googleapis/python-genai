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

"""Tests for TCP keepalive on the default httpx transports.

Regression tests for https://github.com/googleapis/python-genai/issues/2705:
without TCP keepalive, long-running calls that stay silent on the wire are
evicted by NAT gateways and stateful firewalls, hanging the read forever.
"""

import socket

import httpx

from ... import _api_client as api_client


def test_default_socket_options_enable_keepalive():
  options = api_client._default_socket_options()
  assert (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) in options
  # At least one platform-specific keepalive tuning option must be present so
  # probes start before typical NAT idle timeouts.
  assert len(options) > 1


def test_sync_client_gets_keepalive_transport_by_default():
  client = api_client.SyncHttpxClient()
  assert isinstance(client._transport, httpx.HTTPTransport)
  assert (
      socket.SOL_SOCKET,
      socket.SO_KEEPALIVE,
      1,
  ) in client._transport._pool._socket_options


def test_async_client_gets_keepalive_transport_by_default():
  client = api_client.AsyncHttpxClient()
  assert isinstance(client._transport, httpx.AsyncHTTPTransport)
  assert (
      socket.SOL_SOCKET,
      socket.SO_KEEPALIVE,
      1,
  ) in client._transport._pool._socket_options


def test_sync_client_preserves_user_transport():
  transport = httpx.MockTransport(lambda request: httpx.Response(200))
  client = api_client.SyncHttpxClient(transport=transport)
  assert client._transport is transport


def test_async_client_preserves_user_transport():
  transport = httpx.MockTransport(lambda request: httpx.Response(200))
  client = api_client.AsyncHttpxClient(transport=transport)
  assert client._transport is transport
