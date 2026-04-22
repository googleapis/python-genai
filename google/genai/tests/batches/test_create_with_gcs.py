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


"""Tests for batches.create() with Google Cloud Storage source."""

import pytest

from ... import types
from .. import pytest_helper


_GEMINI_MODEL = 'gemini-2.5-flash'
_GEMINI_MODEL_FULL_NAME = 'publishers/google/models/gemini-2.5-flash'
_EMBEDDING_MODEL = 'gemini-embedding-001'
_EMBEDDING_MODEL_FULL_NAME = 'publishers/google/models/gemini-embedding-001'
_DISPLAY_NAME = 'test_batch'

_GENERATE_CONTENT_GCS_INPUT_FILE = (
    'gs://unified-genai-tests/batches/input/generate_content_requests.jsonl'
)
_GENERATE_CONTENT_GCS_OUTPUT_PREFIX = 'gs://unified-genai-tests/batches/output'

_EMBEDDING_GCS_INPUT_FILE = (
    'gs://unified-genai-tests/batches/input/embedding_requests.jsonl'
)
_EMBEDDING_GCS_OUTPUT_PREFIX = 'gs://unified-genai-tests/batches/output'


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_union_generate_content_with_gcs',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL,
            src=_GENERATE_CONTENT_GCS_INPUT_FILE,
        ),
        exception_if_mldev='not supported in Gemini API',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_embedding_with_gcs',
        parameters=types._CreateBatchJobParameters(
            model='text-embedding-004',
            src=_EMBEDDING_GCS_INPUT_FILE,
            config={
                'display_name': _DISPLAY_NAME,
                'dest': _EMBEDDING_GCS_OUTPUT_PREFIX,
            },
        ),
        exception_if_mldev='not supported in Gemini API',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_with_http_options',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL,
            src=_GENERATE_CONTENT_GCS_INPUT_FILE,
            config={
                'http_options': {
                    'api_version': 'v1',
                    'headers': {'test': 'headers'},
                },
            },
        ),
        exception_if_mldev='not supported in Gemini API',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_generate_content_with_gcs',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL,
            src={
                'gcs_uri': [_GENERATE_CONTENT_GCS_INPUT_FILE],
                'format': 'jsonl',
            },
            config={
                'display_name': _DISPLAY_NAME,
                'dest': {
                    'gcs_uri': _GENERATE_CONTENT_GCS_OUTPUT_PREFIX,
                    'format': 'jsonl',
                },
            },
        ),
        exception_if_mldev='one of',
    ),
]

pytestmark = [
    pytest.mark.usefixtures('mock_timestamped_unique_name'),
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
        test_method='batches.create',
        test_table=test_table,
    ),
]


@pytest.mark.asyncio
async def test_async_create(client):
  with pytest_helper.exception_if_mldev(client, ValueError):
    batch_job = await client.aio.batches.create(
        model=_GEMINI_MODEL,
        src=_GENERATE_CONTENT_GCS_INPUT_FILE,
    )

    assert batch_job.name.startswith('projects/')
    assert (
        batch_job.model == _GEMINI_MODEL_FULL_NAME
    )  # Converted to Vertex full name.
    assert batch_job.src.gcs_uri == [_GENERATE_CONTENT_GCS_INPUT_FILE]
    assert batch_job.src.format == 'jsonl'
