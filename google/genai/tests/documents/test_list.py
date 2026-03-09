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

"""Tests for file_search_stores.documents.list()."""

import pytest

from ... import types
from .. import pytest_helper

_FILE_SEARCH_STORE_NAME = "fileSearchStores/gzn7kdl2wpxl-4z2yqvuxbcxw"

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_list_default",
        parameters=types._ListDocumentsParameters(
            parent=_FILE_SEARCH_STORE_NAME
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
    pytest_helper.TestTableItem(
        name="test_list_with_page_size",
        parameters=types._ListDocumentsParameters(
            parent=_FILE_SEARCH_STORE_NAME,
            config=types.ListDocumentsConfig(
                page_size=2,
            ),
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="file_search_stores.documents.list",
    test_table=test_table,
    http_options={
        "base_url": "https://autopush-generativelanguage.sandbox.googleapis.com/",
    }
)


def test_pager(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    # Iterate through the first page.
    for document in client.file_search_stores.documents.list(
        parent=_FILE_SEARCH_STORE_NAME, config={"page_size": 2}
    ):
      assert isinstance(document, types.Document)

@pytest.mark.asyncio
async def test_async_pager(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    # Iterate through the first page.
    async for document in await client.aio.file_search_stores.documents.list(
        parent=_FILE_SEARCH_STORE_NAME, config={"page_size": 2}
    ):
      assert isinstance(document, types.Document)
