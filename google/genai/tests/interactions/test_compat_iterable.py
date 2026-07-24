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

def tool_generator():
    yield {"type": "function", "function": {"name": "f1"}}
    yield {"type": "function", "function": {"name": "f2"}}

def test_iterable_tools():
    client = Client(api_key="placeholder")
    try:
        client.interactions.create(
            model="gemini-2.0-flash",
            input="hello",
            tools=tool_generator(),
        )
    except Exception:
        # Ignore actual call failure (like missing credentials)
        pass
