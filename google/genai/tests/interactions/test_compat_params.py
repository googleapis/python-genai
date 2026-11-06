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

import pytest
from google.genai import Client

def test_params_usage():
    from google.genai.interactions import (
        InteractionCreateParams,
        ToolParam,
        ModelParam,
        ContentParam,
        GenerationConfigParam,
        EnvironmentParam,
        WebhookConfigParam,
    )

    # ToolParam is a Union/TypeAlias, so it cannot be instantiated directly.
    # It must be used as a type hint, passing a dict value at runtime:
    tool_val: ToolParam = {"type": "function", "function": {"name": "get_weather"}}

    client = Client(api_key="placeholder")
    params: InteractionCreateParams = {
        "model": "gemini-2.0-flash",
        "input": "What is the weather?",
        "tools": [tool_val],
        "stream": False,
    }
    
    try:
        result = client.interactions.create(**params)
    except Exception:
        pass

    def process_model(model: ModelParam) -> None:
        pass
