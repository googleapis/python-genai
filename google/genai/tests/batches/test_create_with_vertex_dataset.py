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


"""Tests for batches.create() with Vertex dataset source."""

import re

import pytest

from .. import pytest_helper
from ... import types


_GEMINI_MODEL = 'gemini-2.5-flash'
_GEMINI_MODEL_FULL_NAME = 'publishers/google/models/gemini-2.5-flash'
_OUTPUT_VERTEX_DATASET_DISPLAY_NAME = 'test_batch_output'
_VERTEX_DATASET_INPUT_NAME = (
    'projects/vertex-sdk-dev/locations/us-central1/datasets/7857316250517504000'
)
_DISPLAY_NAME = 'test_batch'

_BQ_OUTPUT_PREFIX = (
    'bq://vertex-sdk-dev.unified_genai_tests_batches.generate_content_output'
)
_VERTEX_DATASET_DESTINATION = types.VertexMultimodalDatasetDestination(
    bigquery_destination=_BQ_OUTPUT_PREFIX,
    display_name=_OUTPUT_VERTEX_DATASET_DISPLAY_NAME,
)


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_union_generate_content_with_vertex_dataset_name',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL_FULL_NAME,
            src=_VERTEX_DATASET_INPUT_NAME,
            config={
                'display_name': _DISPLAY_NAME,
                'dest': {
                    'vertex_dataset': _VERTEX_DATASET_DESTINATION,
                    'format': 'vertex-dataset',
                },
            },
        ),
        exception_if_mldev='not supported in Gemini API',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_generate_content_with_vertex_dataset_source',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL_FULL_NAME,
            src=types.BatchJobSource(
                vertex_dataset_name=_VERTEX_DATASET_INPUT_NAME,
                format='vertex-dataset',
            ),
            config={
                'display_name': _DISPLAY_NAME,
                'dest': {
                    'vertex_dataset': _VERTEX_DATASET_DESTINATION,
                    'format': 'vertex-dataset',
                },
            },
        ),
        exception_if_mldev='one of',
    ),
    pytest_helper.TestTableItem(
        name='test_generate_content_with_vertex_dataset_source_dict',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL_FULL_NAME,
            src={
                'vertex_dataset_name': _VERTEX_DATASET_INPUT_NAME,
                'format': 'vertex-dataset',
            },
            config={
                'display_name': _DISPLAY_NAME,
                'dest': {
                    'vertex_dataset': _VERTEX_DATASET_DESTINATION,
                    'format': 'vertex-dataset',
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
        src=_VERTEX_DATASET_INPUT_NAME,
        config={
            'dest': {
                'vertex_dataset': _VERTEX_DATASET_DESTINATION,
                'format': 'vertex-dataset',
            },
        },
    )

    assert batch_job.name.startswith('projects/')
    assert (
        batch_job.model == _GEMINI_MODEL_FULL_NAME
    )  # Converted to Vertex full name.
    assert batch_job.src.vertex_dataset_name == _VERTEX_DATASET_INPUT_NAME
    assert batch_job.src.format == 'vertex-dataset'
