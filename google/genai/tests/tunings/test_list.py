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


"""Tests for tunings.list()."""

import pytest

from ... import types as genai_types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_default',
        parameters=genai_types._ListTuningJobsParameters(),
    ),
    pytest_helper.TestTableItem(
        name='test_with_config',
        parameters=genai_types._ListTuningJobsParameters(
            config=genai_types.ListTuningJobsConfig(page_size=2)
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='tunings.list',
    test_table=test_table,
)

pytest_plugins = ('pytest_asyncio',)


def test_pager(client):
  tuning_jobs = client.tunings.list(config={'page_size': 2})
  assert 'content-type' in tuning_jobs.sdk_http_response.headers
  assert tuning_jobs.name == 'tuning_jobs'
  assert tuning_jobs.page_size == 2
  assert len(tuning_jobs) <= 2

  # Iterate through all the pages. Then next_page() should raise an exception.
  for _ in tuning_jobs:
    pass
  with pytest.raises(IndexError, match='No more pages to fetch.'):
    tuning_jobs.next_page()


@pytest.mark.asyncio
async def test_async_pager(client):
  tuning_jobs = await client.aio.tunings.list(config={'page_size': 2})

  assert 'Content-Type' in tuning_jobs.sdk_http_response.headers
  assert tuning_jobs.name == 'tuning_jobs'
  assert tuning_jobs.page_size == 2
  assert len(tuning_jobs) <= 2

  # Iterate through all the pages. Then next_page() should raise an exception.
  async for _ in tuning_jobs:
    pass
  with pytest.raises(IndexError, match='No more pages to fetch.'):
    await tuning_jobs.next_page()
