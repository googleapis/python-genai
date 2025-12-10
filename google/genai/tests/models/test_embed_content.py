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
# pylint: disable=protected-access


"""Tests for models.embedContent()."""

import os
import pytest

from ... import _transformers as t
from ... import types
from .. import pytest_helper


def _get_bytes_from_file(relative_path: str) -> bytes:
  abs_file_path = os.path.abspath(
      os.path.join(os.path.dirname(__file__), relative_path)
  )
  with open(abs_file_path, 'rb') as file:
    return file.read()

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_single_text',
        parameters=types.EmbedContentParameters(
            model='text-embedding-004',
            contents=t.t_contents('What is your name?'),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_multi_texts_with_config',
        parameters=types.EmbedContentParameters(
            model='text-embedding-004',
            contents=[
                t.t_content('What is your name?'),
                t.t_content('I am a model.'),
            ],
            config={
                'output_dimensionality': 10,
                'title': 'test_title',
                'task_type': 'RETRIEVAL_DOCUMENT',
                'http_options': {
                    'headers': {'test': 'headers'},
                },
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_single_text_with_mime_type_not_supported_in_mldev',
        parameters=types.EmbedContentParameters(
            model='text-embedding-004',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 10,
                'mime_type': 'text/plain',
            },
        ),
        exception_if_mldev='parameter is not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_single_text_with_auto_truncate_not_supported_in_mldev',
        parameters=types.EmbedContentParameters(
            model='text-embedding-004',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 10,
                'auto_truncate': True,
            },
        ),
        exception_if_mldev='parameter is not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_text_only_with_config',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2-exp-11-2025',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 10,
                'title': 'test_title',
                'task_type': 'RETRIEVAL_DOCUMENT',
                'http_options': {
                    'headers': {'test': 'headers'},
                },
                'auto_truncate': True,
            },
        ),
        # auto_truncate not supported on MLDev.
        exception_if_mldev='parameter is not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_text_only',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2-exp-11-2025',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 100,
            },
        ),
        # Model not exposed on MLDev.
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_maas',
        parameters=types.EmbedContentParameters(
            model=(
                'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
            ),
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 100,
            },
        ),
        # Model not exposed on MLDev.
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_gcs_image_and_config',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2-exp-11-2025',
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_text(
                            text='Similar things to the following image:'
                        ),
                        types.Part.from_uri(
                            file_uri='gs://cloud-samples-data/generative-ai/image/a-man-and-a-dog.png',
                            mime_type='image/png',
                        ),
                    ],
                )
            ],
            config={
                'output_dimensionality': 10,
                'title': 'test_title',
                'task_type': 'RETRIEVAL_DOCUMENT',
                'http_options': {
                    'headers': {'test': 'headers'},
                },
            },
        ),
        # Model not exposed on MLDev.
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_inline_pdf',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2-exp-11-2025',
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(
                            data=_get_bytes_from_file('../data/story.pdf'),
                            mime_type='application/pdf',
                        ),
                    ],
                )
            ],
            config={
                'output_dimensionality': 100,
            },
        ),
        # Model not exposed on MLDev.
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_list_of_contents_error',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2-exp-11-2025',
            contents=[
                types.Content(parts=[types.Part.from_text(text='hello')]),
                types.Content(parts=[types.Part.from_text(text='world')]),
            ],
        ),
        exception_if_vertex='supports',
        exception_if_mldev='404',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.embed_content',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async(client):
  response = await client.aio.models.embed_content(
      model='text-embedding-004',
      contents='What is your name?',
      config={'output_dimensionality': 10},
  )
  assert response


@pytest.mark.asyncio
async def test_async_new_api(client):
  if not client.vertexai:
    return
  response = await client.aio.models.embed_content(
      model='gemini-embedding-2-exp-11-2025',
      contents=t.t_contents('What is your name?'),
      config={'output_dimensionality': 10},
  )
  assert response
