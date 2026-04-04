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


"""Tests for batches.get()."""

import pytest

from ... import types
from .. import pytest_helper


# Vertex AI batch job name.
_BATCH_JOB_NAME = '5798522612028014592'
_BATCH_JOB_FULL_RESOURCE_NAME = (
    'projects/964831358985/locations/us-central1/'
    f'batchPredictionJobs/{_BATCH_JOB_NAME}'
)
# MLDev batch operation name.
_MLDEV_BATCH_OPERATION_NAME = 'batches/z2p8ksus4lyxt25rntl3fpd67p2niw4hfij5'
_INVALID_BATCH_JOB_NAME = 'invalid_name'


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_get_batch_job',
        parameters=types._GetBatchJobParameters(
            name=_BATCH_JOB_NAME,
        ),
        exception_if_mldev='Invalid batch job name',
    ),
    pytest_helper.TestTableItem(
        name='test_get_batch_operation',
        parameters=types._GetBatchJobParameters(
            name=_MLDEV_BATCH_OPERATION_NAME,
        ),
        exception_if_vertex='Invalid batch job name',
    ),
    pytest_helper.TestTableItem(
        name='test_get_batch_job_with_invalid_name',
        parameters=types._GetBatchJobParameters(
            name=_INVALID_BATCH_JOB_NAME,
        ),
        exception_if_mldev='Invalid batch job name',
        exception_if_vertex='Invalid batch job name',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='batches.get',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_get(client):
  if client.vertexai:
    name = _BATCH_JOB_NAME
  else:
    name = _MLDEV_BATCH_OPERATION_NAME
  batch_job = await client.aio.batches.get(name=name)

  assert batch_job
