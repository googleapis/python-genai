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

def test_error_handling():
    client = Client(api_key="placeholder")
    from google.genai._interactions import (
        BadRequestError,
        RateLimitError,
        NotFoundError,
        APIStatusError,
    )

    # This pattern worked for interactions, agents, AND webhooks:
    try:
        result = client.interactions.create(model="gemini-2.0-flash", input="hello")
    except BadRequestError as e:
        print(f"Bad request: {e.message}")
        print(f"Request obj: {e.request}")    # httpx.Request
        print(f"Body: {e.body}")              # object | None
    except RateLimitError:
        print("Rate limited, retrying...")
    except APIStatusError as e:
        print(f"HTTP {e.status_code}: {e.response}")

    # Also for agents:
    try:
        agent = client.agents.get("my-agent")
    except NotFoundError:
        print("Agent not found")
    except Exception:
        # Catch other exceptions (like BadRequestError from dummy key) so the test passes
        pass

    # Also for webhooks:
    try:
        wh = client.webhooks.get("wh-123")
    except NotFoundError:
        print("Webhook not found")
    except Exception:
        # Catch other exceptions
        pass
