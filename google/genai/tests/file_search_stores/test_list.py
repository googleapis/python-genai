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

"""Tests for file_search_stores.list()."""

import pytest

from ... import types
from .. import pytest_helper

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_list_default",
        parameters=types._ListFileSearchStoresParameters(),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
    pytest_helper.TestTableItem(
        name="test_list_with_page_size",
        parameters=types._ListFileSearchStoresParameters(
            config=types.ListFileSearchStoresConfig(
                page_size=5,
            ),
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="file_search_stores.list",
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_pager(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    # Iterate through the first page.
    async for file_search_store in await client.aio.file_search_stores.list(
        config={"page_size": 2}
    ):
      assert isinstance(file_search_store, types.FileSearchStore)
      break  # Only check one item
