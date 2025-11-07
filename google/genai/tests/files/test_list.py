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


"""Test files list method."""

import pytest

from ... import types
from .. import pytest_helper

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_not_empty',
        exception_if_vertex='only supported in the Gemini Developer client',
        parameters=types._ListFilesParameters(
            config=types.ListFilesConfig(
                page_size=2,
            ),
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='files.list',
    test_table=test_table,
)


def test_pager(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    files = client.files.list(config={'page_size': 2})
    assert 'content-type' in files.sdk_http_response.headers
    assert files.name == 'files'
    assert files.page_size == 2
    assert len(files) <= 2

    # Iterate through all the pages. Then next_page() should raise an exception.
    for _ in files:
      pass
    with pytest.raises(IndexError, match='No more pages to fetch.'):
      files.next_page()


@pytest.mark.asyncio
async def test_async_pager(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    files = await client.aio.files.list(config={'page_size': 2})

    assert 'Content-Type' in files.sdk_http_response.headers
    assert files.name == 'files'
    assert files.page_size == 2
    assert len(files) <= 2

    # Iterate through all the pages. Then next_page() should raise an exception.
    async for _ in files:
      pass
    with pytest.raises(IndexError, match='No more pages to fetch.'):
      await files.next_page()
