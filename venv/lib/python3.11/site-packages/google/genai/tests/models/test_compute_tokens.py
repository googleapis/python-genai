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


import pytest
from ... import _transformers as t
from ... import types
from .. import pytest_helper
from . import constants

_COMPUTE_TOKENS_PARAMS = types._ComputeTokensParameters(
    model='gemini-2.5-flash',
    contents=[t.t_content('Tell me a story in 300 words.')],
)
_COMPUTE_TOKENS_PARAMS_VERTEX_CUSTOM_URL = types._ComputeTokensParameters(
    model='gemini-2.5-flash',
    contents=[t.t_content('Tell me a story in 300 words.')],
    config={'http_options': constants.VERTEX_HTTP_OPTIONS},
)
_COMPUTE_TOKENS_PARAMS_MLDEV_CUSTOM_URL = types._ComputeTokensParameters(
    model='gemini-2.5-flash',
    contents=[t.t_content('Tell me a story in 300 words.')],
    config={'http_options': constants.MLDEV_HTTP_OPTIONS},
)
_UNICODE_STRING = '这是一条unicode测试🤪❤★'

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_compute_tokens',
        exception_if_mldev='only supported in',
        parameters=types._ComputeTokensParameters(
            model='gemini-2.5-flash',
            contents=[t.t_content('Tell me a story in 300 words.')],
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_compute_tokens_vertex_custom_url',
        parameters=_COMPUTE_TOKENS_PARAMS_VERTEX_CUSTOM_URL,
        exception_if_mldev='only supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_compute_tokens_mldev_custom_url',
        parameters=_COMPUTE_TOKENS_PARAMS_MLDEV_CUSTOM_URL,
        exception_if_vertex='404',
        exception_if_mldev='only supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_compute_tokens_unicode',
        exception_if_mldev='only supported in',
        parameters=types._ComputeTokensParameters(
            model='gemini-2.5-flash', contents=[t.t_content(_UNICODE_STRING)]
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.compute_tokens',
    test_table=test_table,
)


def test_token_bytes_deserialization(client):
  if client._api_client.vertexai:
    response = client.models.compute_tokens(
        model=_COMPUTE_TOKENS_PARAMS.model,
        contents=_UNICODE_STRING,
    )
    decoded_tokens = b''.join(response.tokens_info[0].tokens)
    assert (
        decoded_tokens
        == b'\xe8\xbf\x99\xe6\x98\xaf\xe4\xb8\x80\xe6\x9d\xa1unicode\xe6\xb5\x8b\xe8\xaf\x95\xf0\x9f\xa4\xaa\xe2\x9d\xa4\xe2\x98\x85'
    )
    assert decoded_tokens.decode('utf-8') == _UNICODE_STRING


@pytest.mark.asyncio
async def test_async(client):
  if client._api_client.vertexai:
    response = await client.aio.models.compute_tokens(
        model=_COMPUTE_TOKENS_PARAMS.model,
        contents=_COMPUTE_TOKENS_PARAMS.contents,
    )
    assert response
  else:
    with pytest.raises(Exception):
      await client.aio.models.compute_tokens(
          model=_COMPUTE_TOKENS_PARAMS.model,
          contents=_COMPUTE_TOKENS_PARAMS.contents,
      )


def test_different_model_names(client):
  if client._api_client.vertexai:
    response1 = client.models.compute_tokens(
        model='gemini-2.5-flash', contents=_COMPUTE_TOKENS_PARAMS.contents
    )
    assert response1
    response3 = client.models.compute_tokens(
        model='publishers/google/models/gemini-2.5-flash',
        contents=_COMPUTE_TOKENS_PARAMS.contents,
    )
    assert response3
    response4 = client.models.compute_tokens(
        model='projects/vertexsdk/locations/us-central1/publishers/google/models/gemini-2.5-flash',
        contents=_COMPUTE_TOKENS_PARAMS.contents,
    )
    assert response4
