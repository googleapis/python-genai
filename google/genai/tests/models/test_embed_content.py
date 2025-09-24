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

import pytest

from ... import _transformers as t
from ... import types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_single_text',
        parameters=types._EmbedContentParameters(
            model='text-embedding-004',
            contents=t.t_contents('What is your name?'),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_multi_texts_with_config',
        parameters=types._EmbedContentParameters(
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
        parameters=types._EmbedContentParameters(
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
        parameters=types._EmbedContentParameters(
            model='text-embedding-004',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 10,
                'auto_truncate': True,
            },
        ),
        exception_if_mldev='parameter is not supported',
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
