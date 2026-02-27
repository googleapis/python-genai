
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

import json
from unittest import mock
import pytest
from httpx import Request, Response
from ... import Client

def test_create_interaction_persistence_request_body():
    client = Client(api_key='fake-key')
    
    with mock.patch("httpx.Client.send") as mock_send:
        mock_send.return_value = Response(
            200, 
            request=Request('POST', ''), 
            content=json.dumps({"id": "new-id"}).encode()
        )
        
        client.interactions.create(
            model="gemini-2.0-flash",
            input="Hello",
            previous_interaction_id="old-id",
            generation_config={
                "max_output_tokens": 100
            }
        )
        
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        body = json.loads(request.read())
        
        # Verify snake_case parameters are converted to camelCase in the request body
        assert body["previousInteractionId"] == "old-id"
        assert body["generationConfig"]["maxOutputTokens"] == 100
        assert "previous_interaction_id" not in body

def test_create_interaction_persistence_response_parsing():
    client = Client(api_key='fake-key')
    
    with mock.patch("httpx.Client.send") as mock_send:
        mock_send.return_value = Response(
            200, 
            request=Request('POST', ''), 
            content=json.dumps({
                "id": "new-id",
                "previousInteractionId": "old-id",
                "status": "completed",
                "created": "2024-03-22T18:11:19Z",
                "updated": "2024-03-22T18:11:19Z",
                "usage": {
                    "totalInputTokens": 10,
                    "totalOutputTokens": 20
                }
            }).encode()
        )
        
        interaction = client.interactions.create(
            model="gemini-2.0-flash",
            input="Hello"
        )
        
        # Verify camelCase response fields are correctly mapped to snake_case properties
        assert interaction.id == "new-id"
        assert interaction.previous_interaction_id == "old-id"
        assert interaction.usage.total_input_tokens == 10
        assert interaction.usage.total_output_tokens == 20
