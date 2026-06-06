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

"""Tests for live response handling."""
import json
from typing import cast
from unittest import mock
from unittest.mock import AsyncMock

import pytest

from ... import _api_client as api_client
from ... import _common
from ... import Client
from ... import client as gl_client
from ... import live
from ... import types


def mock_api_client(vertexai=False):
  """Creates a mock BaseApiClient."""
  mock_client = mock.MagicMock(spec=gl_client.BaseApiClient)
  if not vertexai:
    mock_client.api_key = 'TEST_API_KEY'
    mock_client.location = None
    mock_client.project = None
  else:
    mock_client.api_key = None
    mock_client.location = 'us-central1'
    mock_client.project = 'test_project'

  mock_client._host = lambda: 'test_host'
  mock_client._http_options = types.HttpOptions.model_validate(
      {'headers': {}}
  )
  mock_client.vertexai = vertexai
  return mock_client


@pytest.fixture
def mock_websocket():
  """Provides a mock websocket connection."""
  # Use live.ClientConnection if that's the specific type hint in AsyncSession
  websocket = AsyncMock(spec=live.ClientConnection)
  websocket.send = AsyncMock()
  # Set default recv value, will be overridden in the test
  websocket.recv = AsyncMock(return_value='{}')
  websocket.close = AsyncMock()
  return websocket


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_receive_server_content(mock_websocket, vertexai):

  raw_response_json = json.dumps({
      "usageMetadata": {
          "promptTokenCount": 15,
          "responseTokenCount": 25,
          "candidatesTokenCount": 50,
          "totalTokenCount": 200,
          "responseTokensDetails": [
              {
                  "tokenCount": 20,
                  "modality": "TEXT",
              }
          ],
          "candidatesTokensDetails": [
              {
                  "tokenCount": 10,
                  "modality": "TEXT",
              }
          ],
      },
      "serverContent": {
          "modelTurn": {
              "parts": [{"text": "This is a simple response."}]
          },
          "turnComplete": True,
          "groundingMetadata": {
              "web_search_queries": ["test query"],
              "groundingChunks": [{
                  "web": {
                      "domain": "google.com",
                      "title": "Search results",
                  }
              }]
          }
      }
  })
  mock_websocket.recv.return_value = raw_response_json

  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  result = await session._receive()

  # Assert the results
  assert isinstance(result, types.LiveServerMessage)

  assert (
      result.server_content.model_turn.parts[0].text
      == "This is a simple response."
  )
  assert result.server_content.turn_complete
  assert result.server_content.grounding_metadata.web_search_queries == ["test query"]
  assert result.server_content.grounding_metadata.grounding_chunks[0].web.domain == "google.com"
  assert result.server_content.grounding_metadata.grounding_chunks[0].web.title == "Search results"
  # Verify usageMetadata was parsed
  assert isinstance(result.usage_metadata, types.UsageMetadata)
  assert result.usage_metadata.prompt_token_count == 15
  assert result.usage_metadata.total_token_count == 200
  if not vertexai:
    assert result.usage_metadata.response_token_count == 25
    assert result.usage_metadata.response_tokens_details[0].token_count == 20
  else:
    # VertexAI maps candidatesTokenCount to responseTokenCount and maps
    # candidatesTokensDetails to responseTokensDetails.
    assert result.usage_metadata.response_token_count == 50
    assert result.usage_metadata.response_tokens_details[0].token_count == 10

@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_receive_server_content_with_turn_reason(mock_websocket, vertexai):
  """Tests parsing of LiveServerContent with turn_complete_reason and waiting_for_input."""

  raw_response_json = json.dumps({
      "serverContent": {
          "modelTurn": {
              "parts": [{"text": "Please provide more details."}]
          },
          "turnComplete": True,
          "turnCompleteReason": "NEED_MORE_INPUT",
          "waitingForInput": True
      }
  })
  mock_websocket.recv.return_value = raw_response_json

  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  result = await session._receive()

  # Assert the results
  assert isinstance(result, types.LiveServerMessage)
  assert result.server_content is not None

  assert result.server_content.model_turn.parts[0].text == "Please provide more details."
  assert result.server_content.turn_complete is True
  assert result.server_content.turn_complete_reason == types.TurnCompleteReason.NEED_MORE_INPUT
  assert result.server_content.waiting_for_input is True
