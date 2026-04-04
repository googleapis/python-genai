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


"""Tests for file_search_stores.get()."""

import pytest

from ... import types
from .. import pytest_helper

# A FileSearchStore name known to exist in the test environment.
# Replace with a real one from your test setup.
_EXISTING_FILE_SEARCH_STORE_NAME = "fileSearchStores/5en07ei3kojo-yo8sjqgvx2xf"
_NON_EXISTENT_FILE_SEARCH_STORE_NAME = (
    "fileSearchStores/non-existent-file-search-store"
)
_INVALID_FILE_SEARCH_STORE_NAME = (
    "fileSearchStores/_invalid_file_search_store_name"
)
_NOT_A_FILE_SEARCH_STORE_NAME = "genai-test-file-search-store"

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_get_success",
        parameters=types._GetFileSearchStoreParameters(
            name=_EXISTING_FILE_SEARCH_STORE_NAME
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
    pytest_helper.TestTableItem(
        name="test_get_not_found",
        parameters=types._GetFileSearchStoreParameters(
            name=_NON_EXISTENT_FILE_SEARCH_STORE_NAME
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
        # Expect an exception to be raised by the mock
        exception_if_mldev="PERMISSION_DENIED",
    ),
    pytest_helper.TestTableItem(
        name="test_get_invalid_name",
        parameters=types._GetFileSearchStoreParameters(
            name=_INVALID_FILE_SEARCH_STORE_NAME
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
        # Validation should catch this before the API call
        exception_if_mldev="INVALID_ARGUMENT",
    ),
    pytest_helper.TestTableItem(
        name="test_get_not_a_file_search_store_name",
        parameters=types._GetFileSearchStoreParameters(
            name=_NOT_A_FILE_SEARCH_STORE_NAME
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
        exception_if_mldev="Not Found",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="file_search_stores.get",
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_get(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    # This test relies on the mocking/replays set up by pytest_helper
    # For a success case:
    try:
      file_search_store = await client.aio.file_search_stores.get(
          name=_EXISTING_FILE_SEARCH_STORE_NAME
      )
      assert file_search_store is not None
      assert file_search_store.name == _EXISTING_FILE_SEARCH_STORE_NAME
    except Exception as e:
      # Depending on the mock setup, errors might be raised directly
      print(f"Async get failed: {e}")
      raise
