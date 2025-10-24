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

"""Tests for caches.create(), caches.get(), and caches.delete()."""

from .... import types as genai_types
from ... import pytest_helper


def create_get_delete(client, parameters):
  if client.vertexai:
    cache = client.caches.create(
        model=parameters.model,
        config=parameters.config,
    )
  else:
    # For MLDev, we must create the file before creating the cache.
    file = client.files.upload(file="tests/data/a-man-and-a-dog.png")
    config = genai_types.CreateCachedContentConfig(
        contents=[
            genai_types.Part.from_uri(
                file_uri=file.uri,
                mime_type=file.mime_type,
            )
        ]
        * 5
    )
    cache = client.caches.create(model=parameters.model, config=config)
  got_cache = client.caches.get(name=cache.name)
  client.caches.delete(name=got_cache.name)


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_create_get_delete",
        parameters=genai_types._CreateCachedContentParameters(
            model="gemini-2.5-flash",
            config=genai_types.CreateCachedContentConfig(
                contents=[genai_types.Part.from_uri(
                    file_uri="gs://cloud-samples-data/generative-ai/image/a-man-and-a-dog.png",
                    mime_type="image/png",
                )] * 5
            ),
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="create_get_delete",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
