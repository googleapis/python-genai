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


"""Tests for batches.create() with file source."""

import pytest

from ... import types
from .. import pytest_helper


_GEMINI_MODEL = 'gemini-2.5-flash'
_DISPLAY_NAME = 'test_batch'

_MLDEV_GEMINI_MODEL = 'gemini-2.5-flash'
_FILE_NAME = 'files/s0pa54alni6w'

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_union_generate_content_with_file',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'file_name': _FILE_NAME},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_generate_content_with_file',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'file_name': _FILE_NAME},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported',
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
  with pytest_helper.exception_if_vertex(client, ValueError):
    batch_job = await client.aio.batches.create(
        model=_MLDEV_GEMINI_MODEL,
        src={'file_name': _FILE_NAME},
        config={
            'display_name': _DISPLAY_NAME,
        },
    )
    assert batch_job.name.startswith('batches/')
    assert (
        batch_job.model == 'models/' + _MLDEV_GEMINI_MODEL
    )  # Converted to Gemini full name.
