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


import pytest
from ... import types
from .. import pytest_helper
from . import constants


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        skip_in_api_mode='Get is not reproducible in the API mode.',
        name='test_caches_get_with_vertex_cache_name',
        exception_if_mldev='PERMISSION_DENIED',
        parameters=types._GetCachedContentParameters(
            name=constants.CACHED_CONTENT_NAME_VERTEX,
        ),
    ),
    pytest_helper.TestTableItem(
        skip_in_api_mode='Get is not reproducible in the API mode.',
        name='test_caches_get_with_mldev_cache_name',
        exception_if_vertex='NOT_FOUND',
        parameters=types._GetCachedContentParameters(
            name=constants.CACHED_CONTENT_NAME_MLDEV,
        ),
    ),
    pytest_helper.TestTableItem(
        skip_in_api_mode='Get is not reproducible in the API mode.',
        name='test_caches_get_with_mldev_cache_name_partial_1',
        exception_if_vertex='NOT_FOUND',
        parameters=types._GetCachedContentParameters(
            name='cachedContents/o239k1gxzz0juy9wqstndhncr85krehehf551hqh'
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='caches.get',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_get(client):
  if client._api_client.vertexai:
    response = await client.aio.caches.get(
        name=constants.CACHED_CONTENT_NAME_VERTEX
    )
    assert response
  else:
    await client.aio.caches.get(name=constants.CACHED_CONTENT_NAME_MLDEV)


def test_different_cache_name_formats(client):
  if client._api_client.vertexai:
    response1 = client.caches.get(
        name='projects/964831358985/locations/us-central1/cachedContents/2164089915711684608'
    )
    assert response1
    response2 = client.caches.get(
        name='locations/us-central1/cachedContents/2164089915711684608'
    )
    assert response2
    response3 = client.caches.get(
        name='cachedContents/2164089915711684608'
    )
    assert response3
    response4 = client.caches.get(
        name='2164089915711684608'
    )
    assert response4
  else:
    response1 = client.caches.get(
        name='cachedContents/o239k1gxzz0juy9wqstndhncr85krehehf551hqh'
    )
    assert response1
    response2 = client.caches.get(
        name='o239k1gxzz0juy9wqstndhncr85krehehf551hqh'
    )
    assert response2
