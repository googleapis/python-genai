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

import asyncio
import os
import sys
import pytest

IS_NOT_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS') != 'true'


@pytest.mark.skipif(IS_NOT_GITHUB_ACTIONS,
                    reason='This test is only run on GitHub Actions.')
def test_library_can_be_imported_without_optional_dependencies():
  """Tests that the library works without optional dependencies (including httpx)."""
  with pytest.raises(ImportError):
    import httpx  # pylint: disable=g-import-not-at-top,unused-import
  assert 'httpx' not in sys.modules

  from google import genai
  from google.genai import errors
  from google.genai import interactions
  from google.genai import types
  import httpx2

  assert interactions is not None

  def handler(request: httpx2.Request) -> httpx2.Response:
    path = request.url.path
    if path.endswith(':streamGenerateContent'):
      return httpx2.Response(
          status_code=200,
          content=(
              b'data: {"candidates": [{"content": {"parts": [{"text": "Hello "}], "role": "model"}}]}\n\n'
              b'data: {"candidates": [{"content": {"parts": [{"text": "world"}], "role": "model"}}]}\n\n'
          ),
          headers={'content-type': 'text/event-stream'},
      )
    if path.endswith('/models/bad-model:generateContent'):
      return httpx2.Response(
          status_code=400,
          json={'error': {'code': 400, 'message': 'Bad request', 'status': 'INVALID_ARGUMENT'}},
      )
    if '/interactions/' in path:
      return httpx2.Response(
          status_code=200,
          headers={'content-type': 'application/json'},
          content=b'{"id": "test-id", "status": "completed"}',
      )
    return httpx2.Response(
        status_code=200,
        json={
            'candidates': [{
                'content': {'parts': [{'text': 'ok'}], 'role': 'model'},
                'finishReason': 'STOP',
            }]
        },
    )

  transport = httpx2.MockTransport(handler)
  client = genai.Client(
      api_key='test-api-key',
      http_options=types.HttpOptions(
          client_args={'transport': transport},
          async_client_args={'transport': transport},
      ),
  )
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)

  # Sync generate_content, streaming, error handling, and interactions.
  resp = client.models.generate_content(model='gemini-2.5-flash', contents='hi')
  assert resp.text == 'ok'

  chunks = list(
      client.models.generate_content_stream(
          model='gemini-2.5-flash', contents='hi'
      )
  )
  assert ''.join(c.text for c in chunks) == 'Hello world'

  with pytest.raises(errors.ClientError):
    client.models.generate_content(model='bad-model', contents='hi')

  interaction = client.interactions.get(id='test-id')
  assert interaction.status == 'completed'

  # Async generate_content, streaming, error handling, and interactions.
  async def _run_async() -> None:
    async_resp = await client.aio.models.generate_content(
        model='gemini-2.5-flash', contents='hi'
    )
    assert async_resp.text == 'ok'

    async_chunks = [
        c
        async for c in await client.aio.models.generate_content_stream(
            model='gemini-2.5-flash', contents='hi'
        )
    ]
    assert ''.join(c.text for c in async_chunks) == 'Hello world'

    with pytest.raises(errors.ClientError):
      await client.aio.models.generate_content(model='bad-model', contents='hi')

    async_interaction = await client.aio.interactions.get(id='test-id')
    assert async_interaction.status == 'completed'

  asyncio.run(_run_async())
  assert 'httpx' not in sys.modules
