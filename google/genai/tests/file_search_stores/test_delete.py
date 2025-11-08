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

"""Tests for file_search_stores.delete()."""

import pytest

from ... import types
from .. import pytest_helper

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_delete_with_name",
        parameters=types._DeleteFileSearchStoreParameters(
            name="fileSearchStores/acxjj7m366ln-aw6xyp94icll",
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
    pytest_helper.TestTableItem(
        name="test_delete_with_name_and_force",
        parameters=types._DeleteFileSearchStoreParameters(
            name="fileSearchStores/7igesc9r2zw9-0mpxpsqubv7s",
            config=types.DeleteFileSearchStoreConfig(force=True),
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="file_search_stores.delete",
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_delete(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    await client.aio.file_search_stores.delete(
        name="fileSearchStores/my-file-search-store-l65kcyel9lkz"
    )


@pytest.mark.asyncio
async def test_async_force_delete(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    await client.aio.file_search_stores.delete(
        name="fileSearchStores/my-file-search-store-vjtrjw6re8oz",
        config=types.DeleteFileSearchStoreConfig(force=True),
    )
