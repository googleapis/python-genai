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
"""Lifecycle tests for Triggers API."""

from __future__ import annotations

import pytest

from . import conftest

TRIGGER_BODY = {
    "id": "projects/my-project/locations/my-location/triggers/svc_abc",
    "schedule": "0 0 * * *",
    "time_zone": "UTC",
    "interaction": {
        "agent": "projects/my-project/locations/my-location/agents/my-agent",
        "input": "test-input",
        "environment": {
            "type": "remote",
            "network": {
                "allowlist": [
                    {
                        "domain": "api.github.com",
                        "transform": {
                            "Authorization": (
                                "Bearer"
                                " ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                            )
                        },
                    },
                    {"domain": "github.com"},
                ]
            },
        },
    },
}


@pytest.mark.parametrize(
    "input_value, expected_input_value",
    [
        ("test-input-str", "test-input-str"),
        (
            [{"type": "user_input", "content": [{"type": "text", "text": "test-input-step"}]}],
            [{"type": "user_input", "content": [{"type": "text", "text": "test-input-step"}]}],
        ),
        (
            [{"type": "text", "text": "test-input-content-1"}, {"type": "text", "text": "test-input-content-2"}],
            [
                {
                    "type": "user_input",
                    "content": [
                        {"type": "text", "text": "test-input-content-1"},
                        {"type": "text", "text": "test-input-content-2"},
                    ],
                }
            ],
        ),
        (
            {"type": "text", "text": "test-input-single-content"},
            {"type": "text", "text": "test-input-single-content"},
        ),
        (
            [{"text": "test-input-content-shorthand-1"}, {"text": "test-input-content-shorthand-2"}],
            [
                {
                    "type": "user_input",
                    "content": [
                        {"type": "text", "text": "test-input-content-shorthand-1"},
                        {"type": "text", "text": "test-input-content-shorthand-2"},
                    ],
                }
            ],
        ),
    ]
)
def test_python_triggers_lifecycle_routes_through_google_genai_client(
    mock_gaos_server: conftest.MockGaosServer,
    input_value,
    expected_input_value,
):
  mock_gaos_server.default_response = TRIGGER_BODY
  client = mock_gaos_server.client

  trigger = client.triggers.create(
      interaction={
          "agent": "projects/my-project/locations/my-location/agents/my-agent",
          "input": input_value,
          "environment": {
              "type": "remote",
              "network": {
                  "allowlist": [
                      {
                          "domain": "api.github.com",
                          "transform": {
                              "Authorization": (
                                  "Bearer"
                                  " ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                              )
                          },
                      },
                      {"domain": "github.com"},
                  ]
              },
          },
      },
      schedule="0 0 * * *",
      time_zone="UTC",
  )
  client.triggers.list(filter_="some-filter", page_size=10)
  fetched = client.triggers.get(id="svc_abc")
  client.triggers.update(
      id="svc_abc",
      display_name="updated-name",
      status="paused",
  )
  client.triggers.delete(id="svc_abc")
  client.triggers.run(trigger_id="svc_abc")
  client.triggers.list_executions(trigger_id="svc_abc", page_size=5)

  assert trigger.schedule == "0 0 * * *"
  assert fetched.schedule == "0 0 * * *"
  assert mock_gaos_server.captured == [
      "POST /v1beta/triggers",
      "GET /v1beta/triggers?filter=some-filter&page_size=10",
      "GET /v1beta/triggers/svc_abc",
      "PATCH /v1beta/triggers/svc_abc",
      "DELETE /v1beta/triggers/svc_abc",
      "POST /v1beta/triggers/svc_abc/executions",
      "GET /v1beta/triggers/svc_abc/executions?page_size=5",
  ]

  # Verify the serialized interaction input in the CREATE request
  create_body = mock_gaos_server.captured_bodies[0]
  interaction_in_req = create_body["interaction"]

  # Assert that the input was serialized correctly
  assert interaction_in_req["input"] == expected_input_value
