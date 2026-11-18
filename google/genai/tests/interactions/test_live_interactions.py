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
# pyformat: disable
# pylint: skip-file

"""Tests for live Interactions API WebSocket connections."""

import asyncio
from datetime import datetime, timezone
import json
from unittest import mock

import google.auth.credentials
import httpx
import pytest
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed, ConnectionClosedError
from websockets.frames import Close

from ... import _interactions_websocket as interactions_websocket
from ... import _live_interactions_experimental
from ... import client as client_module
from ... import interactions as public_interactions
from ..._gaos import google_genai as gaos_google_genai
from ..._gaos.auth_tokens import AuthTokens
from ..._gaos.google_genai import (
    APIConnectionError,
    APIError,
    APIWebSocketError,
    AsyncGeminiNextGenInteractions,
    ClientEvent,
    GeminiNextGenInteractions,
    InteractionWebSocketConnection,
    ServerEvent,
)
from ..._gaos.interactions import AsyncInteractions
from ..._gaos.types import interactions as interaction_types
from ..._interactions_errors import GeminiNextGenAPIClientError

Client = client_module.Client


@pytest.fixture(autouse=True)
def _use_gaos_interactions(monkeypatch):
  if hasattr(client_module, "GeminiNextGenInteractions"):
    monkeypatch.setattr(
        client_module,
        "GeminiNextGenInteractions",
        GeminiNextGenInteractions,
    )
  if hasattr(client_module, "AsyncGeminiNextGenInteractions"):
    monkeypatch.setattr(
        client_module,
        "AsyncGeminiNextGenInteractions",
        AsyncGeminiNextGenInteractions,
    )


def _new_connection(websocket, interaction_id=None):
  return InteractionWebSocketConnection(
      websocket,
      interaction_id,
      event_parser=gaos_google_genai._parse_server_event,
  )


async def receive_setup(socket):
  raw = await socket.recv()
  await acknowledge(socket, raw)
  return raw


async def acknowledge(socket, raw):
  event = json.loads(raw)
  if event.get("event_type") == "interaction.connect":
    try:
      await socket.send(
          json.dumps({
              "event_type": "interaction.connected",
              "interaction_id": event.get("id", "int_test"),
          })
      )
    except ConnectionClosed:
      pass


@pytest.mark.asyncio
@pytest.mark.parametrize("use_auth_token", [False, True])
async def test_live_interaction_is_available_under_aio(use_auth_token):
  received = []
  request_details = {}

  async def handler(websocket):
    request_details["path"] = websocket.request.path
    request_details["api_key"] = websocket.request.headers.get("x-goog-api-key")
    received.append(json.loads(await receive_setup(websocket)))
    received.append(json.loads(await receive_setup(websocket)))
    await websocket.send(
        json.dumps({
            "event_type": "step.start",
            "index": 0,
            "step": {"type": "model_output"},
        })
    )
    await websocket.send(
        json.dumps({
            "event_type": "step.delta",
            "index": 0,
            "delta": {"type": "text", "text": "Hello from the mock server!"},
        })
    )
    await websocket.send(json.dumps({"event_type": "step.stop", "index": 0}))
    received.append(json.loads(await receive_setup(websocket)))

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="auth_tokens/ephemeral-auth-token" if use_auth_token else "test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )
    context = client.aio.interactions.connect(
        id="int_live_001",
    )

    async with context as connection:
      await connection.send("Hello!")
      events = []
      async for event in connection.receive():
        events.append(event)
        if event.event_type == "step.stop":
          break

  assert request_details == {
      "path": "/v1beta/interactions/live",
      "api_key": (
          "auth_tokens/ephemeral-auth-token"
          if use_auth_token
          else "test-api-key"
      ),
  }
  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_001",
      },
      {
          "event_type": "input",
          "content": [{"type": "text", "text": "Hello!"}],
      },
      {
          "event_type": "interaction.disconnect",
      },
  ]
  assert [event.event_type for event in events] == [
      "interaction.connected",
      "step.start",
      "step.delta",
      "step.stop",
  ]
  assert events[2].delta.text == "Hello from the mock server!"
  await client.aio.aclose()


@pytest.mark.asyncio
async def test_live_interaction_auth_token_api_key_header_and_authorization_stripping():
  received = []
  request_details = {}

  async def handler(websocket):
    request_details["path"] = websocket.request.path
    request_details["api_key"] = websocket.request.headers.get("x-goog-api-key")
    request_details["authorization"] = websocket.request.headers.get("authorization")
    received.append(json.loads(await receive_setup(websocket)))
    received.append(json.loads(await receive_setup(websocket)))

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="auth_tokens/short-lived-token",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
            "headers": {"Authorization": "Bearer secret-oauth-token"},
        },
    )

    async with client.aio.interactions.connect("int_live_001"):
      pass

    await client.aio.aclose()

  assert request_details == {
      "path": "/v1beta/interactions/live",
      "api_key": "auth_tokens/short-lived-token",
      "authorization": None,
  }
  assert received == [
      {"event_type": "interaction.connect", "id": "int_live_001"},
      {"event_type": "interaction.disconnect"},
  ]


@pytest.mark.asyncio
async def test_interactions_websocket_auth_tokens_resource():
  recorded_requests = []

  def handler(request: httpx.Request) -> httpx.Response:
    recorded_requests.append((
        request.method,
        request.url.path,
        request.content.decode("utf-8"),
    ))
    if request.method == "POST" and request.url.path.endswith("/int_bad/auth_tokens"):
      return httpx.Response(
          400,
          headers={"content-type": "application/json"},
          content=b'{"error": {"message": "invalid interaction"}}',
      )
    if request.method == "POST" and request.url.path.endswith("/auth_tokens"):
      return httpx.Response(
          200,
          headers={"content-type": "application/json"},
          content=(
              b'{"auth_token": "auth_tokens/tok_123",'
              b' "expires_at": "2026-10-23T17:00:00Z"}'
          ),
      )
    if (
        request.method == "DELETE"
        and request.url.path.endswith("/auth_tokens/tok_123")
    ):
      return httpx.Response(
          200,
          headers={"content-type": "application/json"},
          content=b"{}",
      )
    return httpx.Response(
        404,
        headers={"content-type": "application/json"},
        content=b'{"error": {"message": "not found"}}',
    )

  http_client = httpx.Client(transport=httpx.MockTransport(handler))
  http_async_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
  expire_dt = datetime(2026, 10, 23, 17, 0, tzinfo=timezone.utc)
  try:
    client = Client(
        api_key="test-api-key",
        http_options={
            "api_version": "v1beta",
            "httpx_client": http_client,
            "httpx_async_client": http_async_client,
        },
    )
    created = client.interactions.auth_tokens.create(
        "int_001", expire_time=expire_dt
    )
    assert created.auth_token == "auth_tokens/tok_123"
    assert recorded_requests[0][0] == "POST"
    assert recorded_requests[0][1] == "/v1beta/interactions/int_001/auth_tokens"
    assert json.loads(recorded_requests[0][2]) == {
        "expire_time": "2026-10-23T17:00:00Z"
    }

    client.interactions.auth_tokens.delete("int_001", created.auth_token)
    assert recorded_requests[1] == (
        "DELETE",
        "/v1beta/interactions/int_001/auth_tokens/tok_123",
        "",
    )

    client.interactions.auth_tokens.delete(
        interaction_id="int_001", auth_token="auth_tokens/tok_123"
    )
    assert recorded_requests[2] == (
        "DELETE",
        "/v1beta/interactions/int_001/auth_tokens/tok_123",
        "",
    )

    created_async = await client.aio.interactions.auth_tokens.create(
        "int_001", api_version="v1alpha", expire_time=expire_dt
    )
    assert created_async.auth_token == "auth_tokens/tok_123"
    assert recorded_requests[3][0] == "POST"
    assert recorded_requests[3][1] == "/v1alpha/interactions/int_001/auth_tokens"
    assert json.loads(recorded_requests[3][2]) == {
        "expire_time": "2026-10-23T17:00:00Z"
    }

    await client.aio.interactions.auth_tokens.delete(
        "int_001", created_async.auth_token, api_version="v1alpha"
    )
    assert recorded_requests[4] == (
        "DELETE",
        "/v1alpha/interactions/int_001/auth_tokens/tok_123",
        "",
    )

    await client.aio.interactions.auth_tokens.delete("int_001", "tok_123")
    assert recorded_requests[5] == (
        "DELETE",
        "/v1beta/interactions/int_001/auth_tokens/tok_123",
        "",
    )

    # The raw and streaming response accessors also strip the prefix.
    expected_delete = (
        "DELETE",
        "/v1beta/interactions/int_001/auth_tokens/tok_123",
        "",
    )
    raw_response = client.interactions.auth_tokens.with_raw_response.delete(
        "int_001", "auth_tokens/tok_123"
    )
    assert raw_response.status_code == 200
    assert recorded_requests[-1] == expected_delete
    with client.interactions.auth_tokens.with_streaming_response.delete(
        interaction_id="int_001", auth_token="auth_tokens/tok_123"
    ) as streaming_response:
      assert streaming_response.status_code == 200
    assert recorded_requests[-1] == expected_delete
    async_raw_response = (
        await client.aio.interactions.auth_tokens.with_raw_response.delete(
            "int_001", "auth_tokens/tok_123"
        )
    )
    assert async_raw_response.status_code == 200
    assert recorded_requests[-1] == expected_delete
    async with client.aio.interactions.auth_tokens.with_streaming_response.delete(
        "int_001", auth_token="auth_tokens/tok_123"
    ) as async_streaming_response:
      assert async_streaming_response.status_code == 200
    assert recorded_requests[-1] == expected_delete

    with pytest.raises(APIError):
      client.interactions.auth_tokens.create("int_bad")
    with pytest.raises(APIError):
      await client.aio.interactions.auth_tokens.create("int_bad")

    creds = mock.MagicMock(
        spec=google.auth.credentials.Credentials, quota_project_id=None
    )
    vertex_client = Client(
        vertexai=True,
        project="test-project",
        location="us-central1",
        credentials=creds,
        http_options={
            "httpx_client": http_client,
            "httpx_async_client": http_async_client,
        },
    )
    request_count_before = len(recorded_requests)
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      vertex_client.interactions.auth_tokens.create("int_001")
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      vertex_client.interactions.auth_tokens.delete(
          "int_001", "auth_tokens/tok_123"
      )
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      await vertex_client.aio.interactions.auth_tokens.create("int_001")
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      await vertex_client.aio.interactions.auth_tokens.delete(
          "int_001", "auth_tokens/tok_123"
      )
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      vertex_client.interactions.auth_tokens.with_raw_response.create("int_001")
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      vertex_client.interactions.auth_tokens.with_streaming_response.delete(
          "int_001", "auth_tokens/tok_123"
      )
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      await vertex_client.aio.interactions.auth_tokens.with_raw_response.create(
          "int_001"
      )
    with pytest.raises(
        ValueError, match="Live Interactions is currently Gemini API only."
    ):
      vertex_client.aio.interactions.auth_tokens.with_streaming_response.delete(
          "int_001", "auth_tokens/tok_123"
      )
    assert len(recorded_requests) == request_count_before
  finally:
    http_client.close()
    await http_async_client.aclose()


def test_live_interaction_websocket_url_uses_api_client_base_url():
  api_client = mock.MagicMock()
  api_client._http_options.base_url = "https://generativelanguage.googleapis.com"
  api_client._http_options.api_version = "v1beta"
  api_client.vertexai = False

  assert interactions_websocket._websocket_url(api_client, None) == (
      "wss://generativelanguage.googleapis.com/v1beta/interactions/live"
  )


def test_live_interaction_websocket_url_keeps_plain_scheme_for_http_base():
  api_client = mock.MagicMock()
  api_client._http_options.base_url = "http://127.0.0.1:8080"
  api_client._http_options.api_version = "v1beta"
  api_client.vertexai = False

  assert interactions_websocket._websocket_url(api_client, None) == (
      "ws://127.0.0.1:8080/v1beta/interactions/live"
  )


def test_live_interaction_websocket_url_preserves_base_path_and_query():
  api_client = mock.MagicMock()
  api_client._http_options.base_url = "https://gateway.example.com/genai?key=proxy-key"
  api_client._http_options.api_version = "v1beta"
  api_client.vertexai = False

  assert interactions_websocket._websocket_url(api_client, None) == (
      "wss://gateway.example.com/genai/v1beta/interactions/live?key=proxy-key"
  )


def test_live_interaction_rejects_vertex_project_location(monkeypatch):
  monkeypatch.setenv("GOOGLE_API_USE_MTLS_ENDPOINT", "never")
  mock_creds = mock.Mock(spec=google.auth.credentials.Credentials)
  mock_creds.expired = False
  mock_creds.token = "fake-token"
  mock_creds.quota_project_id = None
  client = Client(
      vertexai=True,
      project="P",
      location="L",
      credentials=mock_creds,
  )

  with pytest.raises(
      ValueError, match="Live Interactions is currently Gemini API only."
  ):
    interactions_websocket._websocket_url(client._api_client, None)
  with pytest.raises(
      ValueError, match="Live Interactions is currently Gemini API only."
  ):
    client.aio.interactions.connect("int_001")


@pytest.mark.asyncio
async def test_live_interaction_rejects_vertex_api_key(monkeypatch):
  monkeypatch.setenv("GOOGLE_API_USE_MTLS_ENDPOINT", "never")
  monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
  monkeypatch.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
  client = Client(
      vertexai=True,
      api_key="vertex-test-key",
  )

  with pytest.raises(
      ValueError, match="Live Interactions is currently Gemini API only."
  ):
    interactions_websocket._websocket_url(client._api_client, None)
  with pytest.raises(
      ValueError, match="Live Interactions is currently Gemini API only."
  ):
    client.aio.interactions.connect("int_001")
  await client.aio.aclose()


@pytest.mark.asyncio
async def test_live_interaction_transport_args_reach_ws_connect():
  received = []
  recorded = {}
  real_ws_connect = interactions_websocket.ws_connect

  def recording_ws_connect(url, **kwargs):
    recorded["url"] = url
    recorded["kwargs"] = kwargs
    return real_ws_connect(url, **kwargs)

  async def handler(websocket):
    received.append(json.loads(await receive_setup(websocket)))
    received.append(json.loads(await receive_setup(websocket)))

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
            "async_client_args": {"open_timeout": 5, "max_size": 2 ** 21},
        },
    )

    context = interactions_websocket.InteractionWebSocketConnectionContext(
        client._api_client,
        "int_live_001",
    )
    with mock.patch.object(interactions_websocket, "ws_connect", recording_ws_connect):
      async with context:
        pass

    await client.aio.aclose()

  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_001",
      },
      {
          "event_type": "interaction.disconnect",
      },
  ]
  assert recorded["url"] == f"ws://127.0.0.1:{port}/v1beta/interactions/live"
  assert "ssl" not in recorded["kwargs"]
  assert recorded["kwargs"]["open_timeout"] == 5
  assert recorded["kwargs"]["max_size"] == 2 ** 21
  assert recorded["kwargs"]["additional_headers"]["x-goog-api-key"] == "test-api-key"


def test_live_interaction_client_transport_args_cannot_override_headers():
  api_client = mock.MagicMock()
  api_client.vertexai = False
  api_client._websocket_ssl_ctx = {"additional_headers": {"Authorization": "spoof"}}

  with pytest.raises(ValueError, match="additional_headers"):
    interactions_websocket.InteractionWebSocketConnectionContext(api_client, "int_test")


@pytest.mark.asyncio
async def test_live_interaction_ssl_kwarg_applies_only_to_wss():
  ssl_context = object()
  api_client = mock.MagicMock()
  api_client._http_options.base_url = "https://example.com"
  api_client._http_options.api_version = "v1beta"
  api_client._http_options.headers = None
  api_client.vertexai = False
  api_client.api_key = "test-api-key"
  api_client._credentials = None
  api_client._websocket_ssl_ctx = {"ssl": ssl_context, "open_timeout": 7}
  websocket = mock.MagicMock()
  websocket.send = mock.AsyncMock()
  websocket.recv = mock.AsyncMock(
      return_value=json.dumps({
          "event_type": "interaction.connected",
          "interaction_id": "int_test",
      })
  )
  connection = mock.MagicMock()
  connection.__aenter__ = mock.AsyncMock(return_value=websocket)
  ws_connect_mock = mock.MagicMock(return_value=connection)

  with mock.patch.object(interactions_websocket, "ws_connect", ws_connect_mock):
    await interactions_websocket.InteractionWebSocketConnectionContext(
        api_client,
        "int_test",
    )

  url = ws_connect_mock.call_args.args[0]
  kwargs = ws_connect_mock.call_args.kwargs
  assert url == "wss://example.com/v1beta/interactions/live"
  assert kwargs["ssl"] is ssl_context
  assert kwargs["open_timeout"] == 7
  websocket.recv.assert_not_awaited()


@pytest.mark.asyncio
async def test_live_interaction_connect_passes_timeout_as_open_timeout():
  websocket = mock.MagicMock()
  websocket.send = mock.AsyncMock()
  connection = mock.MagicMock()
  connection.__aenter__ = mock.AsyncMock(return_value=websocket)
  ws_connect_mock = mock.MagicMock(return_value=connection)

  client = Client(api_key="test-api-key")
  with mock.patch.object(interactions_websocket, "ws_connect", ws_connect_mock):
    await client.aio.interactions.connect("int_test", timeout=45.0)
  assert ws_connect_mock.call_args.kwargs["open_timeout"] == 45.0
  await client.aio.aclose()

  override_client = Client(
      api_key="test-api-key",
      http_options={"async_client_args": {"open_timeout": 12.0}},
  )
  with mock.patch.object(interactions_websocket, "ws_connect", ws_connect_mock):
    await override_client.aio.interactions.connect("int_test", timeout=45.0)
  assert ws_connect_mock.call_args.kwargs["open_timeout"] == 12.0
  await override_client.aio.aclose()


@pytest.mark.asyncio
async def test_live_interaction_send_forms_and_audio_frames_are_ordered():
  received = []

  async def handler(websocket):
    for _ in range(5):
      received.append(json.loads(await receive_setup(websocket)))

    for event in [
        {
            "event_type": "step.start",
            "index": 0,
            "step": {"type": "thought"},
        },
        {
            "event_type": "step.delta",
            "index": 0,
            "delta": {"type": "text", "text": "Thinking..."},
        },
        {"event_type": "step.stop", "index": 0},
        {
            "event_type": "step.start",
            "index": 1,
            "step": {"type": "model_output"},
        },
        {
            "event_type": "step.delta",
            "index": 1,
            "delta": {
                "type": "audio",
                "mime_type": "audio/pcm",
                "data": "BASE64_AUDIO_RESPONSE",
            },
        },
        {"event_type": "step.stop", "index": 1},
    ]:
      await websocket.send(json.dumps(event))

    received.append(json.loads(await receive_setup(websocket)))

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_001") as connection:
      await connection.send("Describe this image.")
      await connection.send({
          "event_type": "input",
          "content": [{
              "type": "image",
              "mime_type": "image/jpeg",
              "data": "BASE64_IMAGE",
          }],
      })
      await connection.send([
          {
              "event_type": "input",
              "content": [{"type": "text", "text": "First batched input."}],
          },
          {
              "event_type": "input",
              "content": [{"type": "text", "text": "Second batched input."}],
          },
      ])
      await connection.send({
          "event_type": "input",
          "content": [{
              "type": "audio",
              "mime_type": "audio/pcm",
              "data": "BASE64_AUDIO_CHUNK",
          }],
      })
      events = []
      async for event in connection.receive():
        events.append(event)
        if event.event_type == "step.stop" and event.index == 1:
          break

    await client.aio.aclose()

  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_001",
      },
      {
          "event_type": "input",
          "content": [{"type": "text", "text": "Describe this image."}],
      },
      {
          "event_type": "input",
          "content": [{
              "type": "image",
              "mime_type": "image/jpeg",
              "data": "BASE64_IMAGE",
          }],
      },
      {
          "events": [
              {
                  "event_type": "input",
                  "content": [{"type": "text", "text": "First batched input."}],
              },
              {
                  "event_type": "input",
                  "content": [{"type": "text", "text": "Second batched input."}],
              },
          ]
      },
      {
          "event_type": "input",
          "content": [{
              "type": "audio",
              "mime_type": "audio/pcm",
              "data": "BASE64_AUDIO_CHUNK",
          }],
      },
      {
          "event_type": "interaction.disconnect",
      },
  ]
  assert [event.event_type for event in events] == [
      "interaction.connected",
      "step.start",
      "step.delta",
      "step.stop",
      "step.start",
      "step.delta",
      "step.stop",
  ]
  assert events[5].delta.data == "BASE64_AUDIO_RESPONSE"


@pytest.mark.asyncio
async def test_live_interaction_audio_session():
  received = []

  async def handler(websocket):
    received.append(json.loads(await websocket.recv()))
    await websocket.send(
        json.dumps({
            "event_type": "interaction.connected",
            "interaction": {
                "id": "int_live_audio",
                "status": "in_progress",
                "model": "gemini-2.5-flash",
            },
        })
    )

    for _ in range(2):
      received.append(json.loads(await websocket.recv()))

    for event in [
        {
            "event_type": "step.start",
            "index": 0,
            "step": {"type": "model_output"},
        },
        {
            "event_type": "step.delta",
            "index": 0,
            "delta": {
                "type": "audio",
                "mime_type": "audio/pcm",
                "data": "BASE64_AUDIO_RESPONSE_1",
            },
        },
        {
            "event_type": "step.delta",
            "index": 0,
            "delta": {
                "type": "audio",
                "mime_type": "audio/pcm",
                "data": "BASE64_AUDIO_RESPONSE_2",
            },
        },
        {"event_type": "step.stop", "index": 0},
    ]:
      await websocket.send(json.dumps(event))

    received.append(json.loads(await websocket.recv()))
    await websocket.send(
        json.dumps({
            "event_type": "interaction.completed",
            "status": {"code": 0},
            "usage": {"total_input_tokens": 32, "total_output_tokens": 12},
        })
    )

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_audio") as connection:
      await connection.send({
          "event_type": "input",
          "content": [{
              "type": "audio",
              "mime_type": "audio/pcm",
              "data": "BASE64_AUDIO_CHUNK_1",
          }],
      })
      await connection.send({
          "event_type": "input",
          "content": [{
              "type": "audio",
              "mime_type": "audio/pcm",
              "data": "BASE64_AUDIO_CHUNK_2",
          }],
      })
      turn_events = []
      async for event in connection.receive():
        turn_events.append(event)
        if event.event_type == "step.stop":
          break

      await connection.complete()
      terminal_events = [event async for event in connection.receive()]

    await client.aio.aclose()

  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_audio",
      },
      {
          "event_type": "input",
          "content": [{
              "type": "audio",
              "mime_type": "audio/pcm",
              "data": "BASE64_AUDIO_CHUNK_1",
          }],
      },
      {
          "event_type": "input",
          "content": [{
              "type": "audio",
              "mime_type": "audio/pcm",
              "data": "BASE64_AUDIO_CHUNK_2",
          }],
      },
      {"event_type": "interaction.complete"},
  ]
  assert connection.id == "int_live_audio"
  assert [event.event_type for event in turn_events] == [
      "interaction.connected",
      "step.start",
      "step.delta",
      "step.delta",
      "step.stop",
  ]
  assert [event.delta.data for event in turn_events[2:4]] == [
      "BASE64_AUDIO_RESPONSE_1",
      "BASE64_AUDIO_RESPONSE_2",
  ]
  assert terminal_events[0].event_type == "interaction.completed"
  assert isinstance(
      terminal_events[0], interaction_types.LiveInteractionCompletedEvent
  )
  assert terminal_events[0].usage.total_input_tokens == 32


@pytest.mark.asyncio
async def test_live_interaction_context_preserves_user_exceptions():
  connection_obj = mock.MagicMock()
  connection_obj.complete = mock.AsyncMock()
  connection_obj.detach = mock.AsyncMock()
  ws_cm = mock.MagicMock()
  ws_cm.__aexit__ = mock.AsyncMock(return_value=False)
  api_client = mock.MagicMock()
  api_client.vertexai = False
  context = interactions_websocket.InteractionWebSocketConnectionContext(
      api_client, "int_test"
  )
  context._session = connection_obj
  context._connection = ws_cm
  error = RuntimeError("user failure")

  with pytest.raises(RuntimeError) as raised:
    async with context:
      raise error

  assert raised.value is error
  connection_obj.complete.assert_not_awaited()
  exc_type, exc, traceback = ws_cm.__aexit__.await_args.args
  assert exc_type is RuntimeError
  assert exc is error
  assert traceback is not None


@pytest.mark.asyncio
async def test_live_interaction_context_closes_after_complete_error():
  connection_obj = mock.MagicMock()
  connection_obj.complete = mock.AsyncMock(
      side_effect=RuntimeError("complete failure")
  )
  connection_obj.detach = mock.AsyncMock()
  ws_cm = mock.MagicMock()
  ws_cm.__aexit__ = mock.AsyncMock(return_value=False)
  api_client = mock.MagicMock()
  api_client.vertexai = False
  context = interactions_websocket.InteractionWebSocketConnectionContext(
      api_client, "int_test"
  )
  context._session = connection_obj
  context._connection = ws_cm

  with pytest.raises(RuntimeError, match="complete failure"):
    async with context:
      await connection_obj.complete()

  connection_obj.detach.assert_awaited_once()
  exc_type, exc, traceback = ws_cm.__aexit__.await_args.args
  assert exc_type is RuntimeError
  assert str(exc) == "complete failure"
  assert traceback is not None


@pytest.mark.parametrize(
    ("error", "expected_code"),
    [
        (
            ConnectionClosedError(
                Close(1005, ""), Close(1000, "sent reason"), True
            ),
            1005,
        ),
        (ConnectionClosedError(None, Close(1000, "sent reason")), 1000),
        (ConnectionClosedError(None, None), 1006),
    ],
)
def test_live_interaction_extracts_safe_close_code(error, expected_code):
  assert interactions_websocket._safe_close_code(error) == expected_code
  connection = _new_connection(mock.MagicMock())
  redacted = connection._redacted_connection_error(error)
  assert isinstance(redacted, APIWebSocketError)
  assert isinstance(redacted, APIConnectionError)
  assert isinstance(redacted, APIError)
  assert redacted.close_code == expected_code
  assert "reason" not in str(redacted)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("frame", "message"),
    [
        (b"\xff", "UTF-8 JSON text"),
        ("not-json", "valid JSON"),
        (
            json.dumps(["not-an-event"]),
            "Live interaction server events must have an event_type.",
        ),
    ],
)
async def test_live_interaction_protocol_errors_are_redacted(frame, message):
  websocket = mock.MagicMock()
  websocket.recv = mock.AsyncMock(return_value=frame)
  connection = _new_connection(websocket)

  with pytest.raises(
      interactions_websocket.APIWebSocketError, match=message
  ) as raised:
    _ = [event async for event in connection.receive()]

  assert isinstance(raised.value, APIConnectionError)
  assert isinstance(raised.value, APIError)
  assert "not-json" not in str(raised.value)


@pytest.mark.asyncio
async def test_live_interaction_handshake_error_does_not_retain_cause():
  api_client = mock.MagicMock()
  api_client.vertexai = False
  context = interactions_websocket.InteractionWebSocketConnectionContext(
      api_client, "int_test"
  )
  context._connect = mock.AsyncMock(
      side_effect=RuntimeError("Authorization: Bearer secret")
  )

  with pytest.raises(interactions_websocket.APIWebSocketError) as raised:
    await context

  assert isinstance(raised.value, APIConnectionError)
  assert isinstance(raised.value, APIError)
  assert raised.value.close_code is None
  assert raised.value.__cause__ is None
  assert "secret" not in str(raised.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["connect", "send"])
async def test_live_interaction_setup_peer_close_is_normalized(stage):
  close_error = ConnectionClosedError(
      Close(1008, "secret policy reason"),
      Close(1008, "secret policy reason"),
      True,
  )
  websocket = mock.MagicMock()
  websocket.close = mock.AsyncMock()
  websocket.send = mock.AsyncMock(
      side_effect=close_error if stage == "send" else None
  )

  api_client = mock.MagicMock()
  api_client.vertexai = False
  context = interactions_websocket.InteractionWebSocketConnectionContext(
      api_client, "int_test"
  )
  if stage == "connect":
    context._connect = mock.AsyncMock(side_effect=close_error)
  else:
    context._connect = mock.AsyncMock(return_value=websocket)

  with pytest.raises(interactions_websocket.APIWebSocketError) as raised:
    await context

  assert str(raised.value) == "The connection closed during live setup."
  assert raised.value.close_code == 1008
  assert raised.value.__cause__ is None
  assert "secret policy reason" not in str(raised.value)
  if stage == "send":
    websocket.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_live_interaction_upgrade_http_status_is_extracted():
  class UpgradeError(Exception):
    def __init__(self):
      super().__init__("HTTP 401 Authorization: Bearer secret")
      self.response = mock.MagicMock(status_code=401)

  api_client = mock.MagicMock()
  api_client.vertexai = False
  context = interactions_websocket.InteractionWebSocketConnectionContext(
      api_client, "int_test"
  )
  context._connect = mock.AsyncMock(side_effect=UpgradeError())

  with pytest.raises(interactions_websocket.APIWebSocketError) as raised:
    await context

  assert str(raised.value) == "The live interaction setup failed."
  assert raised.value.http_status == 401
  assert raised.value.close_code is None
  assert raised.value.__cause__ is None
  assert "secret" not in str(raised.value)


@pytest.mark.asyncio
async def test_live_interaction_unvalidated_server_events_pass_through():
  websocket = mock.MagicMock()
  websocket.close = mock.AsyncMock()
  websocket.recv = mock.AsyncMock(
      return_value=json.dumps({
          "events": [
              {
                  "event_type": "error",
                  "error": "raw-error-string",
              },
              {
                  "event_type": "step.delta",
                  "index": "not-an-int",
                  "delta": 123,
                  "custom": {"ok": True},
              },
              {"event_type": "interaction.completed"},
          ]
      })
  )
  connection = _new_connection(websocket)

  events = [event async for event in connection.receive()]

  assert [event.event_type for event in events] == [
      "error",
      "step.delta",
      "interaction.completed",
  ]
  assert events[0].error == "raw-error-string"
  assert events[1].index == "not-an-int"
  assert events[1].delta == 123
  assert events[1].custom == {"ok": True}
  assert connection._detached is False
  websocket.close.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal_method", ["complete", "cancel"])
async def test_live_interaction_terminal_write_close_is_normalized(terminal_method):
  close_error = ConnectionClosedError(
      Close(1011, "controlled drop"), Close(1011, "controlled drop"), True
  )
  websocket = mock.MagicMock()
  websocket.send = mock.AsyncMock(side_effect=close_error)
  connection = _new_connection(websocket)

  with pytest.raises(interactions_websocket.APIWebSocketError) as raised:
    await getattr(connection, terminal_method)()

  assert isinstance(raised.value, APIConnectionError)
  assert isinstance(raised.value, APIError)
  assert raised.value.close_code == 1011
  assert "controlled drop" not in str(raised.value)


@pytest.mark.asyncio
async def test_live_interaction_close_before_terminal_ack_is_an_error():
  close_error = ConnectionClosedError(
      Close(1011, "controlled drop"), Close(1011, "controlled drop"), True
  )
  websocket = mock.MagicMock()
  websocket.send = mock.AsyncMock()
  websocket.recv = mock.AsyncMock(side_effect=close_error)
  connection = _new_connection(websocket)

  await connection.complete()
  with pytest.raises(interactions_websocket.APIWebSocketError) as raised:
    _ = [event async for event in connection.receive()]

  assert isinstance(raised.value, APIConnectionError)
  assert isinstance(raised.value, APIError)
  assert raised.value.close_code == 1011
  assert "controlled drop" not in str(raised.value)


@pytest.mark.asyncio
async def test_live_interaction_close_after_terminal_ack_is_clean():
  close_error = ConnectionClosedError(
      Close(1000, "normal close"), Close(1000, "normal close"), True
  )
  websocket = mock.MagicMock()
  websocket.recv = mock.AsyncMock(
      side_effect=[
          json.dumps({"events": [{"event_type": "interaction.completed"}, {"event_type": "step.delta", "index": 0, "delta": {"type": "text", "text": "trailing"}}]}),
          close_error,
      ]
  )
  connection = _new_connection(websocket)

  terminal_events = [event async for event in connection.receive()]
  after_terminal = [event async for event in connection.receive()]

  assert terminal_events[0].event_type == "interaction.completed"
  assert after_terminal == []


@pytest.mark.asyncio
async def test_live_interaction_detach_is_not_terminal():
  websocket = mock.MagicMock()
  websocket.send = mock.AsyncMock()
  websocket.close = mock.AsyncMock()
  connection = _new_connection(websocket)

  await connection.detach()

  assert connection._detached is True
  assert connection._terminal is False
  websocket.send.assert_awaited_once_with('{"event_type":"interaction.disconnect"}')
  with pytest.raises(RuntimeError, match="detached"):
    await connection.send("too late for this socket")


@pytest.mark.asyncio
async def test_live_interaction_detach_sends_disconnect_frame():
  received = []

  async def handler(websocket):
    async for message in websocket:
      await acknowledge(websocket, message)
      received.append(json.loads(message))

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_001") as connection:
      await connection.detach()

    await client.aio.aclose()

  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_001",
      },
      {
          "event_type": "interaction.disconnect",
      },
  ]


@pytest.mark.asyncio
async def test_live_interaction_detach_after_terminal_skips_disconnect_frame():
  received = []

  async def handler(websocket):
    async for message in websocket:
      await acknowledge(websocket, message)
      event = json.loads(message)
      received.append(event)
      if event["event_type"] == "interaction.complete":
        await websocket.send(
            json.dumps({
                "event_type": "interaction.completed",
                "status": {"code": 0},
            })
        )

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_001") as connection:
      await connection.complete()
      _ = [event async for event in connection.receive()]
      await connection.detach()

    await client.aio.aclose()

  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_001",
      },
      {"event_type": "interaction.complete"},
  ]


@pytest.mark.asyncio
async def test_live_interaction_detach_after_connection_error_is_non_throwing():
  async def handler(websocket):
    await receive_setup(websocket)
    await websocket.close(code=1011, reason="controlled drop")

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_001") as connection:
      with pytest.raises(interactions_websocket.APIWebSocketError) as raised:
        _ = [event async for event in connection.receive()]
      assert isinstance(raised.value, APIConnectionError)
      assert isinstance(raised.value, APIError)
      await connection.detach()

    await client.aio.aclose()

  assert connection._detached is True


@pytest.mark.asyncio
async def test_live_interaction_receive_streams_continuously_until_completed():
  websocket = mock.MagicMock()
  websocket.recv = mock.AsyncMock(
      side_effect=[
          json.dumps({
              "event_type": "step.start",
              "index": 0,
              "step": {"type": "thought"},
          }),
          json.dumps({"event_type": "step.stop", "index": 0}),
          json.dumps({
              "event_type": "step.start",
              "index": 1,
              "step": {"type": "transcription"},
          }),
          json.dumps({"event_type": "step.stop", "index": 1}),
          json.dumps({
              "event_type": "step.start",
              "index": 2,
              "step": {"type": "model_output"},
          }),
          json.dumps({"event_type": "step.completed", "index": 2}),
          json.dumps({"event_type": "step.stop", "index": 2}),
          json.dumps({
              "event_type": "step.start",
              "index": 3,
              "step": {"type": "model_output"},
          }),
          json.dumps({"event_type": "step.stop", "index": 3}),
          json.dumps({"event_type": "interaction.completed"}),
      ]
  )
  connection = _new_connection(websocket)

  events = [event async for event in connection.receive()]

  assert [
      (event.event_type, getattr(event, "index", None)) for event in events
  ] == [
      ("step.start", 0),
      ("step.stop", 0),
      ("step.start", 1),
      ("step.stop", 1),
      ("step.start", 2),
      ("step.completed", 2),
      ("step.stop", 2),
      ("step.start", 3),
      ("step.stop", 3),
      ("interaction.completed", None),
  ]
  assert websocket.recv.await_count == 10


@pytest.mark.asyncio
async def test_live_interaction_receive_streams_until_detach_and_clears_buffer():
  websocket = mock.MagicMock()
  websocket.send = mock.AsyncMock()
  websocket.close = mock.AsyncMock()
  websocket.recv = mock.AsyncMock(
      return_value=json.dumps({
          "events": [
              {
                  "event_type": "step.start",
                  "index": 0,
                  "step": {"type": "thought"},
              },
              {"event_type": "step.stop", "index": 0},
              {
                  "event_type": "step.start",
                  "index": 1,
                  "step": {"type": "transcription"},
              },
              {"event_type": "step.stop", "index": 1},
              {
                  "event_type": "step.start",
                  "index": 2,
                  "step": {"type": "model_output"},
              },
              {"event_type": "step.stop", "index": 2},
              {
                  "event_type": "step.start",
                  "index": 3,
                  "step": {"type": "model_output"},
              },
              {"event_type": "step.stop", "index": 3},
          ]
      })
  )
  connection = _new_connection(websocket)

  events = []
  async for event in connection.receive():
    events.append(event)
    if event.event_type == "step.stop" and event.index == 2:
      await connection.detach()

  assert [
      (event.event_type, getattr(event, "index", None)) for event in events
  ] == [
      ("step.start", 0),
      ("step.stop", 0),
      ("step.start", 1),
      ("step.stop", 1),
      ("step.start", 2),
      ("step.stop", 2),
  ]
  assert len(connection._pending_events) == 0
  assert [event async for event in connection.receive()] == []
  websocket.recv.assert_awaited_once()


@pytest.mark.asyncio
async def test_live_interaction_step_events_without_valid_index_are_permissive():
  websocket = mock.MagicMock()
  websocket.recv = mock.AsyncMock(
      return_value=json.dumps({
          "events": [
              {"event_type": "step.start", "step": {"type": "thought"}},
              {
                  "event_type": "step.start",
                  "index": True,
                  "step": {"type": "thought"},
              },
              {
                  "event_type": "step.delta",
                  "delta": {"type": "text", "text": "chunk"},
              },
              {"event_type": "step.stop", "step_index": 0},
              {"event_type": "interaction.completed"},
          ]
      })
  )
  connection = _new_connection(websocket)

  events = [event async for event in connection.receive()]
  assert [event.event_type for event in events] == [
      "step.start",
      "step.start",
      "step.delta",
      "step.stop",
      "interaction.completed",
  ]


@pytest.mark.asyncio
async def test_live_interaction_error_event_is_yielded_not_raised():
  websocket = mock.MagicMock()
  websocket.recv = mock.AsyncMock(
      side_effect=[
          json.dumps({
              "event_type": "error",
              "error": {"code": "invalid_argument", "message": "bad input"},
          }),
          json.dumps({"event_type": "interaction.completed"}),
      ]
  )
  connection = _new_connection(websocket)

  events = [event async for event in connection.receive()]

  assert [event.event_type for event in events] == ["error", "interaction.completed"]
  assert events[0].error.code == "invalid_argument"


@pytest.mark.asyncio
async def test_live_interaction_context_does_not_complete_on_user_exception():
  received = []

  async def handler(websocket):
    async for message in websocket:
      await acknowledge(websocket, message)
      received.append(json.loads(message))

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    with pytest.raises(RuntimeError, match="user failure"):
      async with client.aio.interactions.connect("int_live_001"):
        raise RuntimeError("user failure")

    await client.aio.aclose()

  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_001",
      },
      {
          "event_type": "interaction.disconnect",
      },
  ]


@pytest.mark.asyncio
async def test_live_interaction_can_resume_after_close():
  connections = []

  async def handler(websocket):
    frames = [json.loads(await websocket.recv())]
    connections.append(frames)
    await websocket.send(
        json.dumps({
            "event_type": "interaction.connected",
            "interaction": {
                "id": "int_live_resume",
                "status": "in_progress",
                "steps": [],
            },
        })
    )
    await websocket.send(
        json.dumps({
            "event_type": "step.start",
            "index": 0,
            "step": {"type": "model_output"},
        })
    )
    await websocket.send(
        json.dumps({
            "event_type": "step.stop",
            "index": 0,
        })
    )
    async for message in websocket:
      await acknowledge(websocket, message)
      frames.append(json.loads(message))

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_resume") as connection:
      original_events = []
      async for event in connection.receive():
        original_events.append(event)
        if event.event_type == "step.stop":
          break
      interaction_id = connection.id
      await connection.detach()

    async with client.aio.interactions.connect(
        id=interaction_id,
    ) as resumed_connection:
      resumed_events = []
      async for event in resumed_connection.receive():
        resumed_events.append(event)
        if event.event_type == "step.stop":
          break

    await client.aio.aclose()

  assert interaction_id == "int_live_resume"
  assert original_events[0].event_type == "interaction.connected"
  assert resumed_connection.id == "int_live_resume"
  assert resumed_events[0].event_type == "interaction.connected"
  assert connections == [
      [
          {
              "event_type": "interaction.connect",
              "id": "int_live_resume",
          },
          {
              "event_type": "interaction.disconnect",
          },
      ],
      [
          {
              "event_type": "interaction.connect",
              "id": "int_live_resume",
          },
          {
              "event_type": "interaction.disconnect",
          },
      ],
  ]


@pytest.mark.asyncio
async def test_live_interaction_transport_loss_fails_fast():
  async def handler(websocket):
    await receive_setup(websocket)
    await websocket.close(code=1011, reason="controlled drop")

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_001") as connection:
      with pytest.raises(interactions_websocket.APIWebSocketError) as raised:
        _ = [event async for event in connection.receive()]

    assert isinstance(raised.value, APIConnectionError)
    assert isinstance(raised.value, APIError)
    assert "controlled drop" not in str(raised.value)
    assert raised.value.close_code == 1011

    await client.aio.aclose()


@pytest.mark.asyncio
async def test_live_interaction_receives_batched_and_unknown_events():
  async def handler(websocket):
    await receive_setup(websocket)
    await websocket.send(
        json.dumps({
            "events": [
                {
                    "event_type": "step.start",
                    "index": 0,
                    "step": {"type": "model_output"},
                },
                {
                    "event_type": "step.delta",
                    "index": 0,
                    "delta": {"type": "text", "text": "Batched output."},
                },
                {"event_type": "step.stop", "index": 0},
                {
                    "event_type": "server.extension",
                    "nested": {"value": "preserved"},
                },
            ],
        })
    )
    await receive_setup(websocket)

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_001") as connection:
      events = []
      async for event in connection.receive():
        events.append(event)
        if event.event_type == "server.extension":
          break

    await client.aio.aclose()

  assert [event.event_type for event in events] == [
      "interaction.connected",
      "step.start",
      "step.delta",
      "step.stop",
      "server.extension",
  ]
  assert events[1].index == 0
  assert events[2].index == 0
  assert events[2].delta.text == "Batched output."
  assert events[4].nested == {"value": "preserved"}


@pytest.mark.asyncio
async def test_live_interaction_cancel_frame():
  received = []

  async def handler(websocket):
    async for message in websocket:
      await acknowledge(websocket, message)
      event = json.loads(message)
      received.append(event)
      if event["event_type"] == "interaction.cancel":
        await websocket.send(
            json.dumps({
                "event_type": "interaction.completed",
                "status": {"code": 1},
            })
        )

  async with serve(handler, "127.0.0.1", 0) as server:
    port = server.sockets[0].getsockname()[1]
    client = Client(
        api_key="test-api-key",
        http_options={
            "base_url": f"http://127.0.0.1:{port}",
            "api_version": "v1beta",
        },
    )

    async with client.aio.interactions.connect("int_live_001") as connection:
      connected = await anext(connection.receive())
      await connection.cancel()
      events = [event async for event in connection.receive()]

      with pytest.raises(RuntimeError, match="already terminal"):
        await connection.send("too late")

    await client.aio.aclose()

  assert received == [
      {
          "event_type": "interaction.connect",
          "id": "int_live_001",
      },
      {"event_type": "interaction.cancel"},
  ]
  assert connected.event_type == "interaction.connected"
  assert events == []


@pytest.mark.asyncio
async def test_async_unary_create_remains_awaitable():
  client = Client(api_key="test-api-key")
  interaction = interaction_types.Interaction(
      id="int_unary_001",
      status="completed",
      model="gemini-2.5-flash",
  )

  with mock.patch.object(
      AsyncInteractions,
      "create",
      return_value=interaction,
  ):
    result = await client.aio.interactions.create(
        model="gemini-2.5-flash",
        input="Tell me a joke.",
    )

  assert result.id == "int_unary_001"
  await client.aio.aclose()


@pytest.mark.asyncio
async def test_live_interaction_detach_swallows_transport_close_errors():
  websocket = mock.AsyncMock()
  websocket.send.side_effect = RuntimeError("disconnect write failed")
  websocket.close.side_effect = RuntimeError("teardown failed")
  connection = _new_connection(websocket)

  await connection.detach()

  websocket.send.assert_awaited_once()
  websocket.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_live_interaction_double_detach_closes_once():
  websocket = mock.AsyncMock()
  connection = _new_connection(websocket)

  await connection.detach()
  await connection.detach()

  websocket.send.assert_awaited_once()
  websocket.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_shared_live_event_contract():
  passthrough_events = [
      {
          "event_type": "input",
          "content": [{"type": "text", "text": "hello"}],
      },
      {"event_type": "input"},
      {"event_type": "input", "content": []},
      {
          "event_type": "input",
          "content": {"type": "text", "text": "hello"},
      },
      {"event_type": "user_input", "custom_field": 42},
      {"event_type": "interaction.complete"},
      {"event_type": "interaction.cancel"},
      {"event_type": "interaction.disconnect"},
      {"event_type": "interaction.connect", "id": "int_test"},
  ]
  for event in passthrough_events:
    websocket = mock.AsyncMock()
    connection = _new_connection(websocket)
    await connection.send(event)
    websocket.send.assert_awaited_once()
    assert json.loads(websocket.send.await_args.args[0]) == event

  websocket = mock.AsyncMock()
  connection = _new_connection(websocket)
  await connection.send([
      {"event_type": "input"},
      interaction_types.CompleteInteractionEvent(
          event_type="interaction.complete"
      ),
  ])
  websocket.send.assert_awaited_once()
  assert json.loads(websocket.send.await_args.args[0]) == {
      "events": [
          {"event_type": "input"},
          {"event_type": "interaction.complete"},
      ]
  }

  websocket = mock.AsyncMock()
  connection = _new_connection(websocket)
  await connection.send(
      interaction_types.WorldSetupEvent(
          world_prompt={"text": "A coral reef"},
          reference_image={"data": "AAA=", "mime_type": "image/jpeg"},
      )
  )
  websocket.send.assert_awaited_once()
  assert json.loads(websocket.send.await_args.args[0]) == {
      "event_type": "world_setup",
      "world_prompt": {"text": "A coral reef"},
      "reference_image": {"data": "AAA=", "mime_type": "image/jpeg"},
  }


@pytest.mark.asyncio
async def test_receive_retains_pending_events_after_caller_break():
  websocket = mock.AsyncMock()
  websocket.recv.return_value = json.dumps({
      "events": [
          {"event_type": "step.start", "index": 0, "step": {"type": "model_output"}},
          {"event_type": "step.stop", "index": 0},
          {"event_type": "step.start", "index": 1, "step": {"type": "model_output"}},
          {"event_type": "step.stop", "index": 1},
          {"event_type": "interaction.completed"},
      ]
  })
  connection = _new_connection(websocket)
  first = []
  async for event in connection.receive():
    first.append(event)
    if event.event_type == "step.stop":
      break
  assert len(connection._pending_events) == 3
  second = [event async for event in connection.receive()]
  assert [(event.event_type, event.index) for event in first] == [
      ("step.start", 0),
      ("step.stop", 0),
  ]
  assert [
      (event.event_type, getattr(event, "index", None)) for event in second
  ] == [
      ("step.start", 1),
      ("step.stop", 1),
      ("interaction.completed", None),
  ]
  websocket.recv.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_returns_without_waiting_for_ack_and_preserves_id():
  written = asyncio.Event()
  release = asyncio.Event()
  frames = []

  async def handler(socket):
    frames.append(json.loads(await socket.recv()))
    written.set()
    await release.wait()
    await socket.send(
        json.dumps({
            "events": [
                {
                    "event_type": "interaction.connected",
                    "interaction_id": "different_server_id",
                },
                {
                    "event_type": "error",
                    "error": {
                        "code": "INVALID_ARGUMENT",
                        "message": "ordinary event",
                    },
                },
                {"event_type": "interaction.completed"},
            ]
        })
    )
    await socket.wait_closed()

  async with serve(handler, "127.0.0.1", 0) as server:
    client = Client(
        api_key="test",
        http_options={
            "base_url": f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}"
        },
    )
    context = client.aio.interactions.connect("int_test")
    connection = await context
    await written.wait()
    assert connection.id == "int_test"
    release.set()
    assert [event.event_type async for event in connection.receive()] == [
        "interaction.connected",
        "error",
        "interaction.completed",
    ]
    assert connection.id == "int_test"
    await context.__aexit__(None, None, None)
    await client.aio.aclose()
    assert frames == [{"event_type": "interaction.connect", "id": "int_test"}]


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_setup_timeout_and_cancellation_release_transport(cancel):
  entered = asyncio.Event()
  websocket = mock.MagicMock()
  websocket.close = mock.AsyncMock()
  ws_cm = mock.MagicMock()
  ws_cm.__aexit__ = mock.AsyncMock(return_value=False)

  api_client = mock.MagicMock()
  api_client.vertexai = False
  context = interactions_websocket.InteractionWebSocketConnectionContext(
      api_client, "int_test", timeout=1 if cancel else 0.05
  )

  async def slow_connect():
    context._connection = ws_cm
    entered.set()
    await asyncio.Event().wait()
    return websocket

  context._connect = slow_connect
  task = asyncio.ensure_future(context)
  await entered.wait()
  if cancel:
    task.cancel()
  with pytest.raises(
      asyncio.CancelledError if cancel else interactions_websocket.APIWebSocketError
  ):
    await task
  ws_cm.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_empty_event_batches_are_ignored():
  socket = mock.MagicMock()
  socket.recv = mock.AsyncMock(
      side_effect=[
          json.dumps({"events": []}),
          json.dumps({"events": [{"event_type": "interaction.completed"}]}),
      ]
  )
  connection = _new_connection(socket)

  events = [event async for event in connection.receive()]
  assert [event.event_type for event in events] == ["interaction.completed"]
  assert socket.recv.await_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "frame",
    [
        "not-a-dict",
        123,
        {},
        {"event_type": ""},
        {"event_type": 1},
        {"events": {"event_type": "step.start", "index": 0}},
        {"events": ["not-a-dict"]},
        {"events": [{"event_type": "step.start", "index": 0}, {}]},
    ],
)
async def test_server_events_without_event_type_raise_and_detach(frame):
  socket = mock.MagicMock()
  socket.recv = mock.AsyncMock(return_value=json.dumps(frame))
  socket.close = mock.AsyncMock()
  connection = _new_connection(socket)

  with pytest.raises(
      interactions_websocket.APIWebSocketError,
      match="Live interaction server events must have an event_type.",
  ) as raised:
    await anext(connection.receive())
  assert isinstance(raised.value, APIConnectionError)
  assert isinstance(raised.value, APIError)
  assert connection._detached is True
  socket.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_interaction_connected_events_do_not_replace_connection_id():
  socket = mock.MagicMock()
  socket.recv = mock.AsyncMock(
      side_effect=[
          json.dumps(
              {"event_type": "interaction.connected", "interaction_id": "other"}
          ),
          json.dumps({"event_type": "interaction.completed"}),
      ]
  )
  connection = _new_connection(
      socket, "int_test"
  )

  events = [event async for event in connection.receive()]
  assert [event.event_type for event in events] == [
      "interaction.connected",
      "interaction.completed",
  ]
  assert connection.id == "int_test"


@pytest.mark.asyncio
async def test_cancel_marks_terminal_and_handles_clean_close_and_noops():
  close_error = ConnectionClosedError(
      Close(1000, "closed after cancel"),
      Close(1000, "closed after cancel"),
      True,
  )
  socket = mock.MagicMock()
  socket.send = mock.AsyncMock()
  socket.recv = mock.AsyncMock(side_effect=close_error)
  socket.close = mock.AsyncMock()
  connection = _new_connection(
      socket, "int_test"
  )

  await connection.cancel()
  assert connection._terminal is True
  socket.send.assert_awaited_once_with('{"event_type":"interaction.cancel"}')
  socket.close.assert_awaited_once()

  await connection.cancel()
  await connection.complete()
  socket.send.assert_awaited_once()

  with pytest.raises(RuntimeError, match="already terminal"):
    await connection.send("more input")

  assert [event async for event in connection.receive()] == []

  await connection.detach()
  socket.send.assert_awaited_once()
  socket.close.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cancel_payload",
    [
        {"event_type": "interaction.cancel"},
        interaction_types.CancelInteractionEvent(
            event_type="interaction.cancel"
        ),
        [
            {
                "event_type": "input",
                "content": [{"type": "text", "text": "before cancel"}],
            },
            {"event_type": "interaction.cancel"},
        ],
    ],
)
async def test_send_cancel_event_single_and_batch_marks_terminal(
    cancel_payload,
):
  close_error = ConnectionClosedError(
      Close(1000, "closed"), Close(1000, "closed"), True
  )
  socket = mock.MagicMock()
  socket.send = mock.AsyncMock()
  socket.recv = mock.AsyncMock(side_effect=close_error)
  socket.close = mock.AsyncMock()
  connection = _new_connection(
      socket, "int_test"
  )

  await connection.send(cancel_payload)
  assert connection._terminal is True
  socket.close.assert_awaited_once()

  with pytest.raises(RuntimeError, match="already terminal"):
    await connection.send("after cancel")

  await connection.complete()
  await connection.cancel()
  socket.send.assert_awaited_once()

  assert [event async for event in connection.receive()] == []

  await connection.detach()
  socket.send.assert_awaited_once()
  socket.close.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cancel_action",
    [
        "cancel_method",
        "send_single",
        "send_batch",
    ],
)
async def test_cancel_or_send_cancel_ends_active_waiting_receive_without_close(
    cancel_action,
):
  waiting_on_recv = asyncio.Event()
  socket = mock.MagicMock()
  socket.send = mock.AsyncMock()
  socket.close = mock.AsyncMock()
  call_count = 0

  async def recv():
    nonlocal call_count
    call_count += 1
    if call_count == 1:
      return json.dumps({
          "event_type": "step.start",
          "index": 0,
          "step": {"type": "model_output"},
      })
    waiting_on_recv.set()
    await asyncio.Event().wait()

  socket.recv = mock.AsyncMock(side_effect=recv)
  connection = _new_connection(
      socket, "int_test"
  )

  events = []

  async def consume():
    async for event in connection.receive():
      events.append(event.event_type)

  consumer_task = asyncio.create_task(consume())
  await waiting_on_recv.wait()

  if cancel_action == "cancel_method":
    await connection.cancel()
  elif cancel_action == "send_single":
    await connection.send({"event_type": "interaction.cancel"})
  else:
    await connection.send([
        {
            "event_type": "input",
            "content": [{"type": "text", "text": "before cancel"}],
        },
        {"event_type": "interaction.cancel"},
    ])

  await asyncio.wait_for(consumer_task, timeout=1.0)
  assert events == ["step.start"]
  assert [event async for event in connection.receive()] == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cancel_action",
    [
        "cancel_method",
        "send_single",
        "send_batch",
    ],
)
async def test_cancel_or_send_cancel_drains_buffered_events_and_terminates_receive(
    cancel_action,
):
  socket = mock.MagicMock()
  socket.send = mock.AsyncMock()
  socket.close = mock.AsyncMock()
  socket.recv = mock.AsyncMock(
      return_value=json.dumps({
          "events": [
              {
                  "event_type": "step.start",
                  "index": 0,
                  "step": {"type": "model_output"},
              },
              {
                  "event_type": "step.delta",
                  "index": 0,
                  "delta": {"type": "text", "text": "buffered before cancel"},
              },
              {"event_type": "step.stop", "index": 0},
          ]
      })
  )
  connection = _new_connection(
      socket, "int_test"
  )

  events = []
  async for event in connection.receive():
    events.append(event.event_type)
    if event.event_type == "step.start":
      if cancel_action == "cancel_method":
        await connection.cancel()
      elif cancel_action == "send_single":
        await connection.send({"event_type": "interaction.cancel"})
      else:
        await connection.send([
            {
                "event_type": "input",
                "content": [{"type": "text", "text": "before cancel"}],
            },
            {"event_type": "interaction.cancel"},
        ])

  assert events == ["step.start", "step.delta", "step.stop"]
  socket.recv.assert_awaited_once()
  assert [event async for event in connection.receive()] == []


@pytest.mark.asyncio
async def test_live_interaction_receive_parses_cancelled_event():
  websocket = mock.MagicMock()
  websocket.recv = mock.AsyncMock(
      return_value=json.dumps({
          "event_type": "interaction.cancelled",
          "usage": {"total_input_tokens": 7},
      })
  )
  connection = _new_connection(websocket)

  events = [event async for event in connection.receive()]

  assert len(events) == 1
  assert isinstance(events[0], interaction_types.InteractionCancelledEvent)
  assert events[0].usage.total_input_tokens == 7
  assert [event async for event in connection.receive()] == []
  websocket.recv.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "terminal_type",
    [
        "interaction.completed",
        "interaction.canceled",
        "interaction.cancelled",
        "reconnection_required",
    ],
)
async def test_received_terminal_events_mark_session_terminal(terminal_type):
  socket = mock.MagicMock()
  socket.send = mock.AsyncMock()
  socket.close = mock.AsyncMock()
  socket.recv = mock.AsyncMock(
      return_value=json.dumps({
          "events": [
              {"event_type": "step.start", "index": 0, "step": {"type": "model_output"}},
              {"event_type": terminal_type},
          ]
      })
  )
  connection = _new_connection(
      socket, "int_test"
  )

  events = [event async for event in connection.receive()]
  assert [event.event_type for event in events] == ["step.start", terminal_type]
  assert connection._terminal is True
  assert connection._detached is False
  socket.close.assert_awaited_once()

  assert [event async for event in connection.receive()] == []
  socket.recv.assert_awaited_once()

  with pytest.raises(RuntimeError, match="already terminal"):
    await connection.send("too late")

  await connection.complete()
  await connection.cancel()
  socket.send.assert_not_awaited()

  await connection.detach()
  socket.send.assert_not_awaited()
  socket.close.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("frame", "message"),
    [
        (b"\xff", "UTF-8 JSON text"),
        ("not-json", "valid JSON"),
    ],
)
async def test_malformed_established_event_detaches_after_valid_prefix(
    frame, message
):
  closed = asyncio.Event()

  async def handler(socket):
    await receive_setup(socket)
    await socket.send(frame)
    await socket.wait_closed()
    closed.set()

  async with serve(handler, "127.0.0.1", 0) as server:
    client = Client(
        api_key="test",
        http_options={
            "base_url": f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}"
        },
    )
    async with client.aio.interactions.connect("int_test") as connection:
      events = connection.receive()
      assert (await anext(events)).event_type == "interaction.connected"
      with pytest.raises(
          interactions_websocket.APIWebSocketError, match=message
      ) as raised:
        await anext(events)
      assert isinstance(raised.value, APIConnectionError)
      assert isinstance(raised.value, APIError)
      await asyncio.wait_for(closed.wait(), 1)
      assert not connection._pending_events
      with pytest.raises(RuntimeError, match="detached") as state_error:
        await connection.send("after protocol failure")
      assert not isinstance(state_error.value, APIError)
    await client.aio.aclose()


@pytest.mark.asyncio
async def test_terminal_receive_is_exhausted_without_reading_the_socket_again():
  socket = mock.AsyncMock()
  socket.recv.return_value = json.dumps({"event_type": "interaction.completed"})
  connection = _new_connection(socket)
  assert [event.event_type async for event in connection.receive()] == [
      "interaction.completed"
  ]
  assert [event async for event in connection.receive()] == []
  socket.recv.assert_awaited_once()


@pytest.mark.asyncio
async def test_concurrent_receive_calls_are_rejected():
  entered = asyncio.Event()
  release = asyncio.Event()
  socket = mock.AsyncMock()

  async def recv():
    entered.set()
    await release.wait()
    return json.dumps({"event_type": "interaction.completed"})

  socket.recv.side_effect = recv
  connection = _new_connection(socket)
  first = asyncio.create_task(anext(connection.receive()))
  await entered.wait()

  with pytest.raises(
      RuntimeError, match="Only one receive iterator may be active at a time."
  ):
    await anext(connection.receive())

  release.set()
  assert (await first).event_type == "interaction.completed"
  assert [event async for event in connection.receive()] == []
  socket.recv.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("empty_batch", [[], ()])
async def test_send_empty_event_batch_raises_value_error(empty_batch):
  socket = mock.AsyncMock()
  connection = _new_connection(socket)

  with pytest.raises(ValueError, match="Empty client event batch."):
    await connection.send(empty_batch)

  socket.send.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_payload", [None, 123, True])
async def test_send_invalid_payload_types_raise_value_error(invalid_payload):
  socket = mock.AsyncMock()
  connection = _new_connection(socket)

  with pytest.raises(
      ValueError, match="Live client events must be mappings or Pydantic models."
  ):
    await connection.send(invalid_payload)

  socket.send.assert_not_awaited()


@pytest.mark.parametrize("invalid_id", ["", "   ", "\t\n"])
def test_connect_rejects_empty_or_whitespace_interaction_id(invalid_id):
  client = Client(api_key="test-api-key")

  with pytest.raises(
      ValueError, match="A non-empty interaction ID is required to connect."
  ):
    client.aio.interactions.connect(invalid_id)


@pytest.mark.asyncio
async def test_detach_after_connection_error_skips_disconnect_io():
  close_error = ConnectionClosedError(
      Close(1011, "server drop"), Close(1011, "server drop"), True
  )
  socket = mock.MagicMock()
  socket.send = mock.AsyncMock()
  socket.recv = mock.AsyncMock(side_effect=close_error)
  socket.close = mock.AsyncMock()
  connection = _new_connection(socket)

  with pytest.raises(interactions_websocket.APIWebSocketError):
    _ = [event async for event in connection.receive()]

  await connection.detach()
  socket.send.assert_not_awaited()
  socket.close.assert_awaited_once()


def test_api_websocket_error_hierarchy_and_exports():
  assert APIWebSocketError is interactions_websocket.APIWebSocketError
  assert (
      InteractionWebSocketConnection
      is interactions_websocket.InteractionWebSocketConnection
  )
  specialized_conn = InteractionWebSocketConnection[ClientEvent, ServerEvent]
  assert getattr(specialized_conn, "__origin__", None) is InteractionWebSocketConnection
  assert ClientEvent is interaction_types.ClientEvent
  assert ServerEvent is interaction_types.ServerEvent
  assert hasattr(interaction_types, "ClientEvent")
  assert hasattr(interaction_types, "ServerEvent")
  assert hasattr(public_interactions, "ClientEvent")
  assert hasattr(public_interactions, "ServerEvent")
  assert not hasattr(public_interactions, "ClientEventBatch")
  assert not hasattr(public_interactions, "ClientEventList")
  assert "ClientEventBatch" not in public_interactions.__all__
  assert "ClientEventList" not in public_interactions.__all__
  default_err = APIWebSocketError()
  assert isinstance(
      default_err,
      (
          APIWebSocketError,
          APIConnectionError,
          APIError,
          GeminiNextGenAPIClientError,
      ),
  )
  assert str(default_err) == "WebSocket connection error."
  assert default_err.message == "WebSocket connection error."
  assert default_err.request is None
  assert default_err.body is None
  assert default_err.close_code is None
  assert default_err.http_status is None
  assert default_err.server_code is None

  detailed_err = APIWebSocketError(
      "Handshake rejected.",
      close_code=1008,
      http_status=403,
      server_code="PERMISSION_DENIED",
  )
  assert str(detailed_err) == "Handshake rejected."
  assert detailed_err.close_code == 1008
  assert detailed_err.http_status == 403
  assert detailed_err.server_code == "PERMISSION_DENIED"

  for legacy_name in (
      "LiveInteractionError",
      "LiveInteractionSetupError",
      "LiveInteractionClosedError",
      "LiveInteractionProtocolError",
      "LiveInteractionStateError",
  ):
    assert not hasattr(interactions_websocket, legacy_name)


def test_interactions_websocket_exposed_in_public_gaos():
  from ..._gaos import google_genai as public_google_genai
  assert hasattr(public_google_genai.AsyncGeminiNextGenInteractions, "connect")
  assert "auth_tokens" in public_google_genai.GeminiNextGenInteractions.__annotations__
  assert "auth_tokens" in public_google_genai.AsyncGeminiNextGenInteractions.__annotations__


def test_sync_client_does_not_expose_interactions_websocket_connect():
  client = Client(api_key="test-api-key")
  assert not hasattr(client.interactions, "connect")


@pytest.mark.asyncio
async def test_live_interactions_experimental_warning_emits_once_per_process(
    monkeypatch, recwarn
):
  monkeypatch.setattr(
      _live_interactions_experimental,
      "_live_interactions_experimental_warned",
      False,
  )
  client = Client(api_key="test-api-key")
  token = interaction_types.InteractionAuthToken(auth_token="tok_123")

  # Accessing client.interactions or client.aio.interactions alone does not warn.
  _ = client.interactions
  _ = client.aio.interactions
  assert [
      w
      for w in recwarn.list
      if "Live Interactions usage" in str(w.message)
  ] == []

  with mock.patch.object(AuthTokens, "create", return_value=token):
    client.interactions.auth_tokens.create("int_001")
    client.interactions.auth_tokens.create("int_002")

  _ = client.aio.interactions.connect("int_001")

  experimental_warnings = [
      w
      for w in recwarn.list
      if "Live Interactions usage" in str(w.message)
  ]
  assert len(experimental_warnings) == 1
  assert issubclass(experimental_warnings[0].category, UserWarning)
  assert experimental_warnings[0].filename == __file__
  assert (
      str(experimental_warnings[0].message)
      == _live_interactions_experimental._LIVE_INTERACTIONS_EXPERIMENTAL_WARNING
  )
  await client.aio.aclose()
