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


"""Tests for file_search_stores.upload_to_file_search_store()."""

import io
import pathlib
import pytest
from ... import types
from .. import pytest_helper

_FILE_SEARCH_STORE_NAME = 'fileSearchStores/my-store-37cbhu1nw16r'
_FILE_NAME = 'files/mk4h34zkv33d'

test_table: list[pytest_helper.TestTableItem] = []
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='filesearchstores.import_file',
    test_table=test_table,
)


def test_import(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    operation = client.file_search_stores.import_file(
        file_search_store_name=_FILE_SEARCH_STORE_NAME, file_name=_FILE_NAME
    )


def test_chunking(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    operation = client.file_search_stores.import_file(
        file_search_store_name=_FILE_SEARCH_STORE_NAME,
        file_name=_FILE_NAME,
        config=types.ImportFileConfig(
            chunking_config=types.ChunkingConfig(
                white_space_config=types.WhiteSpaceConfig(
                    max_tokens_per_chunk=200,
                    max_overlap_tokens=20,
                )
            ),
        ),
    )


def test_metadata(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    operation = client.file_search_stores.import_file(
        file_search_store_name=_FILE_SEARCH_STORE_NAME,
        file_name=_FILE_NAME,
        config=types.ImportFileConfig(
            custom_metadata=[
                types.CustomMetadata(key='year', numeric_value=2024),
                types.CustomMetadata(key='tag', string_value='story'),
            ],
        ),
    )


@pytest.mark.asyncio
async def test_async_import(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    operation = await client.aio.file_search_stores.import_file(
        file_search_store_name=_FILE_SEARCH_STORE_NAME,
        file_name=_FILE_NAME,
    )


@pytest.mark.asyncio
async def test_async_chunking(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    operation = await client.aio.file_search_stores.import_file(
        file_search_store_name=_FILE_SEARCH_STORE_NAME,
        file_name=_FILE_NAME,
        config=types.ImportFileConfig(
            chunking_config=types.ChunkingConfig(
                white_space_config=types.WhiteSpaceConfig(
                    max_tokens_per_chunk=200,
                    max_overlap_tokens=20,
                )
            ),
        ),
    )


@pytest.mark.asyncio
async def test_async_metadata(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    operation = await client.aio.file_search_stores.import_file(
        file_search_store_name=_FILE_SEARCH_STORE_NAME,
        file_name=_FILE_NAME,
        config=types.ImportFileConfig(
            custom_metadata=[
                types.CustomMetadata(key='year', numeric_value=2024),
                types.CustomMetadata(key='tag', string_value='story'),
            ],
        ),
    )
