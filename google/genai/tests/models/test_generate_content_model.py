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
from ... import errors
from ... import types
from .. import pytest_helper

tuned_model_endpoint = (
    'projects/801452371447/locations/us-central1/endpoints/4095574160837705728'
)


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_tuned_model',
        parameters=types._GenerateContentParameters(
            model=tuned_model_endpoint,
            contents=t.t_contents('Tell me a story in 300 words.'),
        ),
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_start_with_publishers',
        parameters=types._GenerateContentParameters(
            model='publishers/google/models/gemini-2.5-flash',
            contents=t.t_contents('Tell me a story in 50 words.'),
        ),
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_start_with_models',
        parameters=types._GenerateContentParameters(
            model='models/gemini-2.5-flash',
            contents=t.t_contents('Tell me a story in 50 words.'),
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_publisher_model',
        parameters=types._GenerateContentParameters(
            model='google/gemini-2.5-flash',
            contents=t.t_contents('Tell me a story in 50 words.'),
        ),
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_empty_model',
        parameters=types._GenerateContentParameters(
            model='',
            contents=t.t_contents('Tell me a story in 50 words.'),
        ),
        exception_if_mldev='model',
        exception_if_vertex='model',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)
pytest_plugins = ('pytest_asyncio',)


def test_tuned_model_stream(client):
  # Vertex AI endpoints is not supported in MLDev.
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    chunks = 0
    for chunk in client.models.generate_content_stream(
        model=tuned_model_endpoint,
        contents='Tell me a story in 300 words.',
    ):
      chunks += 1
      assert chunk.text is not None or chunk.candidates[0].finish_reason
    assert chunks >= 2


def test_start_with_models_stream(client):
  # vertex ai require publishers/ prefix for gemini
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    chunks = 0
    for chunk in client.models.generate_content_stream(
        model='models/gemini-2.5-flash',
        contents='Tell me a story in 50 words.',
    ):
      chunks += 1
      assert chunk.text is not None or chunk.candidates[0].finish_reason
    assert chunks >= 2


def test_models_stream_with_non_empty_last_chunk(client):
  chunks = list(
      client.models.generate_content_stream(
          model='gemini-2.5-flash',
          contents='Tell me a story in 300 words.',
      )
  )
  assert chunks[-1].text


@pytest.mark.asyncio
async def test_start_with_models_stream_async(client):
  # vertex ai require publishers/ prefix for gemini
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    chunks = 0
    async for chunk in await client.aio.models.generate_content_stream(
        model='models/gemini-2.5-flash',
        contents='Tell me a story in 300 words.',
    ):
      chunks += 1
      assert chunk.text is not None or chunk.candidates[0].finish_reason
    assert chunks > 2


@pytest.mark.asyncio
async def test_start_with_models_async(client):
  # vertex ai require publishers/ prefix for gemini
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    await client.aio.models.generate_content(
        model='models/gemini-2.5-flash',
        contents='Tell me a story in 50 words.',
    )
