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


"""Test caches list method."""

import pytest
from ... import types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        skip_in_api_mode='List is not reproducible in the API mode.',
        name='test_caches_list',
        parameters=types._ListCachedContentsParameters(config={'page_size': 3}),
    ),
]
pytestmark = [
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
        test_method='caches.list',
        test_table=test_table,
    )
]


def test_pager(client):
  cached_contents = client.caches.list(config={'page_size': 2})
  assert 'content-type' in cached_contents.sdk_http_response.headers
  assert cached_contents.name == 'cached_contents'
  assert cached_contents.page_size == 2
  assert len(cached_contents) <= 2

  # Iterate through all the pages. Then next_page() should raise an exception.
  for _ in cached_contents:
    pass
  with pytest.raises(IndexError, match='No more pages to fetch.'):
    cached_contents.next_page()


@pytest.mark.asyncio
async def test_async_pager(client):
  cached_contents = await client.aio.caches.list(config={'page_size': 2})

  assert 'Content-Type' in cached_contents.sdk_http_response.headers
  assert cached_contents.name == 'cached_contents'
  assert cached_contents.page_size == 2
  assert len(cached_contents) <= 2

  # Iterate through all the pages. Then next_page() should raise an exception.
  async for _ in cached_contents:
    pass
  with pytest.raises(IndexError, match='No more pages to fetch.'):
    await cached_contents.next_page()
