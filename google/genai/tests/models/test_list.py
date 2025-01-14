# Copyright 2024 Google LLC
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


"""Tests for models.list."""

import pytest

from ... import types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_tuned_models',
        parameters=types._ListModelsParameters(),
    ),
    pytest_helper.TestTableItem(
        name='test_base_models',
        parameters=types._ListModelsParameters(config={'query_base': True}),
    ),
    pytest_helper.TestTableItem(
        name='test_with_config',
        parameters=types._ListModelsParameters(config={'page_size': 3}),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.list',
    test_table=test_table,
)


def test_tuned_models_pager(client):
  pager = client.models.list(config={'page_size': 10})

  assert pager.name == 'models'
  assert pager.page_size == 10
  assert len(pager) <= 10

  # Iterate through all the pages. Then next_page() should raise an exception.
  for _ in pager:
    pass
  with pytest.raises(IndexError, match='No more pages to fetch.'):
    pager.next_page()


def test_base_models_pager(client):
  pager = client.models.list(config={'page_size': 10, 'query_base': True})

  assert pager.name == 'models'
  assert pager.page_size == 10
  assert len(pager) <= 10

  # Iterate through all the pages. Then next_page() should raise an exception.
  for _ in pager:
    pass
  with pytest.raises(IndexError, match='No more pages to fetch.'):
    pager.next_page()


@pytest.mark.asyncio
async def test_async_pager(client):
  pager = await client.aio.models.list(config={'page_size': 10})

  assert pager.name == 'models'
  assert pager.page_size == 10
  assert len(pager) <= 10

  # Iterate through all the pages. Then next_page() should raise an exception.
  async for _ in pager:
    pass
  with pytest.raises(IndexError, match='No more pages to fetch.'):
    await pager.next_page()
