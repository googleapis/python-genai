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

"""Tests for documents.delete()."""

import pytest

from ... import types
from .. import pytest_helper

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_delete",
        parameters=types._DeleteDocumentParameters(
            name=(
                "fileSearchStores/fr3l0ri2so25-a3r1ump9x821/documents/asurveyofmodernistpoetrytxt-01zyb2rig5gu"
            ),
            config=types.DeleteDocumentConfig(force=True),
        ),
        exception_if_vertex="only supported in the Gemini Developer client",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="file_search_stores.documents.delete",
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_delete(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    await client.aio.file_search_stores.documents.delete(
        name="fileSearchStores/fr3l0ri2so25-a3r1ump9x821/documents/asurveyofmodernistpoetrytxt-uvmqjtmkm1h2",
        config=types.DeleteDocumentConfig(force=True),
    )
