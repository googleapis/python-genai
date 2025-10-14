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


"""Tests for batches._create_embeddings()"""

import pytest

from ... import types
from .. import pytest_helper

_MLDEV_EMBEDDING_BATCH_INLINE_OPERATION_NAME = (
    'batches/wdx71o8cgbzoa6gg3be1mg7g8ulrhapcjgo3'
)
_MLDEV_EMBEDDING_BATCH_FILE_OPERATION_NAME = (
    'batches/507oatd242het8ox60pwsmn7tcmtkrj8itff'
)

_DISPLAY_NAME = 'test_batch'
_MLDEV_EMBEDDING_MODEL = 'gemini-embedding-001'
_EMBED_CONTENT_FILE_NAME = 'files/mq9e3mg3u2y5'
_INLINED_EMBED_CONTENT_REQUESTS = {
    'config': {'output_dimensionality': 64},
    'contents': [
        {
            'parts': [{
                'text': '1',
            }],
        },
        {
            'parts': [{
                'text': '2',
            }],
        },
        {
            'parts': [{
                'text': '3',
            }],
        },
    ],
}

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_from_inlined',
        parameters=types._CreateEmbeddingsBatchJobParameters(
            model=_MLDEV_EMBEDDING_MODEL,
            src={'inlined_requests': _INLINED_EMBED_CONTENT_REQUESTS},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='Vertex AI does not support',
    ),
]

pytestmark = [
    pytest.mark.usefixtures('mock_timestamped_unique_name'),
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
        test_method='batches.create_embeddings',
        test_table=test_table,
        http_options={
            'api_version': 'v1alpha',
            'base_url': (
                'https://autopush-generativelanguage.sandbox.googleapis.com'
            ),
        },
    ),
]


@pytest.mark.asyncio
async def test_async_from_inline(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    batch_job = await client.aio.batches.create_embeddings(
        model=_MLDEV_EMBEDDING_MODEL,
        src={'inlined_requests': _INLINED_EMBED_CONTENT_REQUESTS},
    )
    assert batch_job.name.startswith('batches/')


def test_from_file(client):
  """Tests creating a batch job with an embedding file name."""
  with pytest_helper.exception_if_vertex(client, ValueError):
    batch_job = client.batches.create_embeddings(
        model=_MLDEV_EMBEDDING_MODEL,
        src={'file_name': _EMBED_CONTENT_FILE_NAME},
        config={
            'display_name': _DISPLAY_NAME,
        },
    )
    assert batch_job.name.startswith('batches/')
    assert batch_job.model == 'models/' + _MLDEV_EMBEDDING_MODEL


@pytest.mark.asyncio
async def test_async_from_file(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    batch_job = await client.aio.batches.create_embeddings(
        model=_MLDEV_EMBEDDING_MODEL,
        src={'file_name': _EMBED_CONTENT_FILE_NAME},
        config={
            'display_name': _DISPLAY_NAME,
        },
    )
    assert batch_job.name.startswith('batches/')
    assert (
        batch_job.model == 'models/' + _MLDEV_EMBEDDING_MODEL
    )  # Converted to Gemini full name.


def test_get_inline(client):
  """Tests getting a batch job that used inline requests."""
  with pytest_helper.exception_if_vertex(client, ValueError):
    name = _MLDEV_EMBEDDING_BATCH_INLINE_OPERATION_NAME
    batch_job = client.batches.get(name=name)
    assert batch_job.dest.inlined_embed_content_responses is not None


@pytest.mark.asyncio
async def test_async_get_inline(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    name = _MLDEV_EMBEDDING_BATCH_INLINE_OPERATION_NAME
    batch_job = await client.aio.batches.get(name=name)

    assert batch_job.dest.inlined_embed_content_responses is not None


def test_get_file(client):
  """Tests getting a batch job that used a file source."""
  with pytest_helper.exception_if_vertex(client, ValueError):
    name = _MLDEV_EMBEDDING_BATCH_FILE_OPERATION_NAME
    batch_job = client.batches.get(name=name)
    assert batch_job.dest.file_name is not None


@pytest.mark.asyncio
async def test_async_get_file(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    name = _MLDEV_EMBEDDING_BATCH_FILE_OPERATION_NAME
    batch_job = await client.aio.batches.get(name=name)

    assert batch_job.dest.file_name is not None
