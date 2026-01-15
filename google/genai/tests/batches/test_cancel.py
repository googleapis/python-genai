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


"""Tests for batches.cancel()."""

import pytest

from ... import types
from .. import pytest_helper


# Vertex AI batch job name.
_BATCH_JOB_NAME = '6339625664542408704'
_BATCH_JOB_FULL_RESOURCE_NAME = (
    'projects/964831358985/locations/us-central1/'
    f'batchPredictionJobs/{_BATCH_JOB_NAME}'
)
# MLDev batch operation name.
_MLDEV_BATCH_OPERATION_NAME = 'batches/0yew7plxupyybd7appsrq5vw7w0lp3l79lab'
_INVALID_BATCH_JOB_NAME = 'invalid_name'


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_cancel_batch_job',
        parameters=types._CancelBatchJobParameters(
            name=_BATCH_JOB_NAME,
        ),
        exception_if_mldev='Invalid batch job name',
        skip_in_api_mode=('Cannot cancel a batch job multiple times in Vertex'),
    ),
    pytest_helper.TestTableItem(
        name='test_cancel_batch_operation',
        parameters=types._CancelBatchJobParameters(
            name=_MLDEV_BATCH_OPERATION_NAME,
        ),
        exception_if_vertex='Invalid batch job name',
    ),
    pytest_helper.TestTableItem(
        name='test_cancel_batch_job_with_invalid_name',
        parameters=types._CancelBatchJobParameters(
            name=_INVALID_BATCH_JOB_NAME,
        ),
        exception_if_mldev='Invalid batch job name',
        exception_if_vertex='Invalid batch job name',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='batches.cancel',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_cancel(client):
  if client.vertexai:
    name = _BATCH_JOB_NAME
  else:
    name = _MLDEV_BATCH_OPERATION_NAME
  await client.aio.batches.cancel(name=name)
