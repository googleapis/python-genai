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

from .... import types as genai_types
from ... import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_list_batch_jobs',
        parameters=genai_types._ListBatchJobsParameters(
            config=genai_types.ListBatchJobsConfig(
                page_size=2,
            ),
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='batches.list',
    test_table=test_table,
)

pytest_plugins = ('pytest_asyncio',)
