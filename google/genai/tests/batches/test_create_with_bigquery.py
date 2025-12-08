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


"""Tests for batches.create() with BigQuery source."""

import pytest

from ... import types
from .. import pytest_helper


_GEMINI_MODEL = 'gemini-2.5-flash'
_GEMINI_MODEL_FULL_NAME = 'publishers/google/models/gemini-2.5-flash'
_EMBEDDING_MODEL = 'text-embedding-004'
_EMBEDDING_MODEL_FULL_NAME = 'publishers/google/models/text-embedding-004'
_DISPLAY_NAME = 'test_batch'
_GENERATE_CONTENT_BQ_INPUT_FILE = (
    'bq://vertex-sdk-dev.unified_genai_tests_batches.generate_content_requests'
)
_GENERATE_CONTENT_BQ_OUTPUT_PREFIX = (
    'bq://vertex-sdk-dev.unified_genai_tests_batches.generate_content_output'
)

_EMBEDDING_BQ_INPUT_FILE = (
    'bq://vertex-sdk-dev.unified_genai_tests_batches.embedding_requests'
)
_EMBEDDING_BQ_OUTPUT_PREFIX = (
    'bq://vertex-sdk-dev.unified_genai_tests_batches.embedding_output'
)


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_union_generate_content_with_bigquery',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL_FULL_NAME,
            src=_GENERATE_CONTENT_BQ_INPUT_FILE,
        ),
        exception_if_mldev='not supported in Gemini API',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_embedding_with_bigquery',
        parameters=types._CreateBatchJobParameters(
            model=_EMBEDDING_MODEL_FULL_NAME,
            src=_EMBEDDING_BQ_INPUT_FILE,
            config={
                'display_name': _DISPLAY_NAME,
                'dest': _EMBEDDING_BQ_OUTPUT_PREFIX,
            },
        ),
        exception_if_mldev='not supported in Gemini API',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_generate_content_with_bigquery',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL_FULL_NAME,
            src={
                'bigquery_uri': _GENERATE_CONTENT_BQ_INPUT_FILE,
                'format': 'bigquery',
            },
            config={
                'display_name': _DISPLAY_NAME,
                'dest': {
                    'bigquery_uri': _GENERATE_CONTENT_BQ_OUTPUT_PREFIX,
                    'format': 'bigquery',
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
        src=_GENERATE_CONTENT_BQ_INPUT_FILE,
    )

    assert batch_job.name.startswith('projects/')
    assert (
        batch_job.model == _GEMINI_MODEL_FULL_NAME
    )  # Converted to Vertex full name.
    assert batch_job.src.bigquery_uri == _GENERATE_CONTENT_BQ_INPUT_FILE
    assert batch_job.src.format == 'bigquery'
