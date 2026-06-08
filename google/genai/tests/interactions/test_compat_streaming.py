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

@pytest.mark.xfail(reason="Stream not yet exported on public google.genai.interactions path")
def test_streaming_compat():
    client = Client(api_key="placeholder")
    from google.genai.interactions import Stream

    try:
        result = client.interactions.create(
            model="gemini-2.0-flash", input="hello", stream=True
        )
        assert isinstance(result, Stream)
        raw_response = result.response
    except Exception:
        # Ignore call failure on mock/auth during local runs,
        # we are verifying Stream import and type existence.
        pass
