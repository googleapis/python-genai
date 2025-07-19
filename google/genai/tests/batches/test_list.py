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


"""Tests for batches.list()."""

import pytest

from ... import errors
from ... import types
from .. import pytest_helper


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_list_batch_jobs',
        parameters=types._ListBatchJobsParameters(
            config=types.ListBatchJobsConfig(
                page_size=5,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_list_batch_jobs_with_config',
        parameters=types._ListBatchJobsParameters(
            config=types.ListBatchJobsConfig(
                filter='display_name:"genai_*"',
                page_size=5,
            ),
        ),
        exception_if_mldev='filter parameter is not supported in Gemini API',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='batches.list',
    test_table=test_table,
)


def test_pager(client):
  batch_jobs = client.batches.list(config={'page_size': 10})
  assert 'content-type' in batch_jobs.sdk_http_response.headers
  assert batch_jobs.name == 'batch_jobs'
  assert batch_jobs.page_size == 10
  assert len(batch_jobs) <= 10

  # Iterate through the first page. Otherwise, too many batches are returned.
  for _ in batch_jobs.page:
    pass


@pytest.mark.asyncio
async def test_async_pager(client):
  batch_jobs = await client.aio.batches.list(config={'page_size': 10})

  assert 'Content-Type' in batch_jobs.sdk_http_response.headers
  assert batch_jobs.name == 'batch_jobs'
  assert batch_jobs.page_size == 10
  assert len(batch_jobs) <= 10

  # Iterate through the first page. Otherwise, too many batches are returned.
  for _ in batch_jobs.page:
    pass
