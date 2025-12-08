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


import copy
import pytest
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper
from . import constants

_COUNT_TOKENS_PARAMS = types._CountTokensParameters(
    model='gemini-2.5-flash',
    contents=[t.t_content('Tell me a story in 300 words.')],
)

_COUNT_TOKENS_PARAMS_WITH_SYSTEM_INSTRUCTION = copy.deepcopy(
    _COUNT_TOKENS_PARAMS
)
_COUNT_TOKENS_PARAMS_WITH_SYSTEM_INSTRUCTION.config = {
    'system_instruction': t.t_content('you are a chatbot.')
}

_COUNT_TOKENS_PARAMS_WITH_TOOLS = copy.deepcopy(_COUNT_TOKENS_PARAMS)
_COUNT_TOKENS_PARAMS_WITH_TOOLS.config = {
    'tools': [{'google_search_retrieval': {}}]
}

_COUNT_TOKENS_PARAMS_WITH_GENERATION_CONFIG = copy.deepcopy(
    _COUNT_TOKENS_PARAMS
)
_COUNT_TOKENS_PARAMS_WITH_GENERATION_CONFIG.config = {
    'generation_config': {'max_output_tokens': 50}
}

_COUNT_TOKENS_PARAMS_VERTEX_CUSTOM_URL = copy.deepcopy(_COUNT_TOKENS_PARAMS)
_COUNT_TOKENS_PARAMS_VERTEX_CUSTOM_URL.config = {
    'http_options': constants.VERTEX_HTTP_OPTIONS
}
_COUNT_TOKENS_PARAMS_MLDEV_CUSTOM_URL = copy.deepcopy(_COUNT_TOKENS_PARAMS)
_COUNT_TOKENS_PARAMS_MLDEV_CUSTOM_URL.config = {
    'http_options': constants.MLDEV_HTTP_OPTIONS
}


# TODO(b/378952792): MLDev count_tokens needs to merge contents and model
# param into generateContentRequest field.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_count_tokens',
        parameters=_COUNT_TOKENS_PARAMS,
    ),
    pytest_helper.TestTableItem(
        name='test_count_tokens_vertex_custom_url',
        parameters=_COUNT_TOKENS_PARAMS_VERTEX_CUSTOM_URL,
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_count_tokens_mldev_custom_url',
        parameters=_COUNT_TOKENS_PARAMS_MLDEV_CUSTOM_URL,
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_count_tokens_with_system_instruction',
        exception_if_mldev='not supported',
        parameters=_COUNT_TOKENS_PARAMS_WITH_SYSTEM_INSTRUCTION,
    ),
    pytest_helper.TestTableItem(
        name='test_count_tokens_with_tools',
        exception_if_mldev='not supported',
        parameters=_COUNT_TOKENS_PARAMS_WITH_TOOLS,
    ),
    pytest_helper.TestTableItem(
        name='test_count_tokens_with_generation_config',
        exception_if_mldev='not supported',
        parameters=_COUNT_TOKENS_PARAMS_WITH_GENERATION_CONFIG,
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.count_tokens',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async(client):
  response = await client.aio.models.count_tokens(
      model=_COUNT_TOKENS_PARAMS.model, contents=_COUNT_TOKENS_PARAMS.contents
  )
  assert response


def test_different_model_names(client):
  if client._api_client.vertexai:
    response1 = client.models.count_tokens(
        model='gemini-2.5-flash', contents=_COUNT_TOKENS_PARAMS.contents
    )
    assert response1
    response3 = client.models.count_tokens(
        model='publishers/google/models/gemini-2.5-flash',
        contents=_COUNT_TOKENS_PARAMS.contents,
    )
    assert response3
    response4 = client.models.count_tokens(
        model='projects/vertexsdk/locations/us-central1/publishers/google/models/gemini-2.5-flash',
        contents=_COUNT_TOKENS_PARAMS.contents,
    )
    assert response4
  else:
    response1 = client.models.count_tokens(
        model='gemini-2.5-flash', contents=_COUNT_TOKENS_PARAMS.contents
    )
    assert response1
    response2 = client.models.count_tokens(
        model='models/gemini-2.5-flash', contents=_COUNT_TOKENS_PARAMS.contents
    )
    assert response2


def test_extra_body(client):
  config = {
      'http_options': {
          'extra_body': {
              'systemInstruction': {
                  'parts': [{'text': 'you are a chatbot.'}],
                  'role': 'user',
              }
          }
      }
  }
  if client._api_client.vertexai:
    response = client.models.count_tokens(
        model=_COUNT_TOKENS_PARAMS.model,
        contents=_COUNT_TOKENS_PARAMS.contents,
        config=config,
    )
    assert response.total_tokens
  else:
    with pytest.raises(errors.ClientError):
      client.models.count_tokens(
          model=_COUNT_TOKENS_PARAMS.model,
          contents=_COUNT_TOKENS_PARAMS.contents,
          config=config,
      )
