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


"""Tests for file_search_stores.documents.get()."""

import pytest

from ... import types
from .. import pytest_helper

# A Document name known to exist in the test environment.
# Replace with a real one from your test setup.
_EXISTING_DOCUMENT_NAME = "fileSearchStores/fr3l0ri2so25-a3r1ump9x821/documents/asurveyofmodernistpoetrytxt-uvmqjtmkm1h2"
_NON_EXISTENT_DOCUMENT_NAME = (
    "fileSearchStores/fr3l0ri2so25-a3r1ump9x821/documents/non-existent-document"
)
_INVALID_DOCUMENT_NAME = "fileSearchStores/fr3l0ri2so25-a3r1ump9x821/documents/_invalid_document_name"
_NOT_A_DOCUMENT_NAME = "genai-test-document"

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_get_success",
        parameters=types._GetDocumentParameters(name=_EXISTING_DOCUMENT_NAME),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
    pytest_helper.TestTableItem(
        name="test_get_not_found",
        parameters=types._GetDocumentParameters(
            name=_NON_EXISTENT_DOCUMENT_NAME
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
        exception_if_mldev="Documents does not exist",
    ),
    pytest_helper.TestTableItem(
        name="test_get_invalid_name",
        parameters=types._GetDocumentParameters(name=_INVALID_DOCUMENT_NAME),
        exception_if_vertex="only supported in the Gemini Developer client",
        # Validation should catch this before the API call
        exception_if_mldev="INVALID_ARGUMENT",
    ),
    pytest_helper.TestTableItem(
        name="test_get_not_a_document_name",
        parameters=types._GetDocumentParameters(name=_NOT_A_DOCUMENT_NAME),
        exception_if_vertex="only supported in the Gemini Developer client",
        exception_if_mldev="Not Found",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="file_search_stores.documents.get",
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_get(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    # This test relies on the mocking/replays set up by pytest_helper
    # For a success case:
    try:
      document = await client.aio.file_search_stores.documents.get(
          name=_EXISTING_DOCUMENT_NAME
      )
      assert document is not None
      assert document.name == _EXISTING_DOCUMENT_NAME
    except Exception as e:
      # Depending on the mock setup, errors might be raised directly
      print(f"Async get failed: {e}")
      raise
