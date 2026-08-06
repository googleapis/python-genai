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

"""Tests for Tool Search and defer_loading in Interactions API."""

import json
from unittest import mock
import pytest
from httpx import Request, Response
from httpx import Client as HTTPClient
from ... import Client
from ..._api_client import AsyncHttpxClient
from ..._gaos.types.interactions.stepdelta import StepDelta
from ..._gaos.types.interactions.toolsearchcalldelta import ToolSearchCallDelta
from ..._gaos.types.interactions.toolsearchresultdelta import ToolSearchResultDelta
from ...interactions import (
    Function,
    MCPServer,
    ToolSearch,
)


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
  monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
  monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
  monkeypatch.delenv("GOOGLE_CLOUD_LOCATION", raising=False)


def test_create_interaction_with_tool_search_and_mcp_defer_loading():
  client = Client()

  with mock.patch.object(HTTPClient, "send") as mock_send:
    mock_send.return_value = Response(
        200,
        request=Request("POST", ""),
        headers={"content-type": "application/json"},
        content=json.dumps({"id": "interactions/test-id", "status": "completed"}),
    )
    client.interactions.create(
        model="gemini-2.5-flash",
        input="What is the weather in Boston?",
        tools=[
            ToolSearch(),
            MCPServer(
                name="weather_server",
                url="https://example.com/mcp",
                defer_loading=True,
            ),
        ],
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    body = json.loads(request.content.decode("utf-8"))
    assert body["model"] == "gemini-2.5-flash"
    assert body["tools"] == [
        {"type": "tool_search"},
        {
            "type": "mcp_server",
            "name": "weather_server",
            "url": "https://example.com/mcp",
            "defer_loading": True,
        },
    ]


def test_create_interaction_with_tool_search_and_function_defer_loading():
  client = Client()

  with mock.patch.object(HTTPClient, "send") as mock_send:
    mock_send.return_value = Response(
        200,
        request=Request("POST", ""),
        headers={"content-type": "application/json"},
        content=json.dumps({"id": "interactions/test-id", "status": "completed"}),
    )
    client.interactions.create(
        model="gemini-2.5-flash",
        input="Find the stock price of GOOG",
        tools=[
            {"type": "tool_search"},
            {
                "type": "function",
                "name": "get_stock_price",
                "description": "Retrieves real-time stock price.",
                "defer_loading": True,
                "parameters": {
                    "type": "object",
                    "properties": {"ticker": {"type": "string"}},
                    "required": ["ticker"],
                },
            },
        ],
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    body = json.loads(request.content.decode("utf-8"))
    assert body["tools"] == [
        {"type": "tool_search"},
        {
            "type": "function",
            "name": "get_stock_price",
            "description": "Retrieves real-time stock price.",
            "defer_loading": True,
            "parameters": {
                "type": "object",
                "properties": {"ticker": {"type": "string"}},
                "required": ["ticker"],
            },
        },
    ]


@pytest.mark.asyncio
async def test_async_create_interaction_with_tool_search():
  client = Client()

  with mock.patch.object(AsyncHttpxClient, "send") as mock_send:
    mock_send.return_value = Response(
        200,
        request=Request("POST", ""),
        headers={"content-type": "application/json"},
        content=json.dumps({"id": "interactions/test-id", "status": "completed"}),
    )
    await client.aio.interactions.create(
        model="gemini-2.5-flash",
        input="What is the weather?",
        tools=[
            ToolSearch(),
            MCPServer(
                name="weather_server",
                url="https://example.com/mcp",
                defer_loading=True,
            ),
        ],
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    body = json.loads(request.content.decode("utf-8"))
    assert body["tools"][0]["type"] == "tool_search"
    assert body["tools"][1]["defer_loading"] is True


def test_deserialize_tool_search_call_and_result_deltas():
  call_delta_raw = {
      "type": "tool_search_call",
      "arguments": {
          "function_names": ["weather_server_get_weather"],
          "query": "weather in Boston",
      },
      "signature": "sig_abc123",
  }
  step_delta = StepDelta.model_validate({"delta": call_delta_raw, "index": 0})
  assert isinstance(step_delta.delta, ToolSearchCallDelta)
  assert step_delta.delta.type == "tool_search_call"
  assert step_delta.delta.signature == "sig_abc123"
  assert step_delta.delta.arguments.function_names == [
      "weather_server_get_weather"
  ]
  assert step_delta.delta.arguments.query == "weather in Boston"

  result_delta_raw = {
      "type": "tool_search_result",
      "result": [
          {
              "name": "weather_server_get_weather",
              "description": "Get current weather for location",
              "defer_loading": False,
              "parameters": {
                  "type": "object",
                  "properties": {"location": {"type": "string"}},
              },
          }
      ],
      "signature": "sig_xyz789",
  }
  step_delta_result = StepDelta.model_validate(
      {"delta": result_delta_raw, "index": 1}
  )
  assert isinstance(step_delta_result.delta, ToolSearchResultDelta)
  assert step_delta_result.delta.type == "tool_search_result"
  assert step_delta_result.delta.signature == "sig_xyz789"
  assert len(step_delta_result.delta.result) == 1
  func = step_delta_result.delta.result[0]
  assert isinstance(func, Function)
  assert func.name == "weather_server_get_weather"
  assert func.description == "Get current weather for location"
  assert func.defer_loading is False


def test_create_interaction_with_client_tool_search():
  client = Client()

  with mock.patch.object(HTTPClient, "send") as mock_send:
    mock_send.return_value = Response(
        200,
        request=Request("POST", ""),
        headers={"content-type": "application/json"},
        content=json.dumps({"id": "interactions/test-id", "status": "completed"}),
    )
    client.interactions.create(
        model="gemini-2.5-flash",
        input="Find tools and answer",
        tools=[
            ToolSearch(
                execution="client",
                name="custom_tool_search",
                description="Client-side tool search implementation",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            ),
        ],
    )
    mock_send.assert_called_once()
    request = mock_send.call_args[0][0]
    body = json.loads(request.content.decode("utf-8"))
    assert body["tools"] == [
        {
            "type": "tool_search",
            "execution": "client",
            "name": "custom_tool_search",
            "description": "Client-side tool search implementation",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        }
    ]

