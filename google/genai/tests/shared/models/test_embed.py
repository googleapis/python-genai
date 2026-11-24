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


"""Tests for models.embed()."""

import os

import pytest

from .... import types as genai_types
from ... import pytest_helper


@pytest.fixture
def location_override(request):
  # gemini-embedding-001 is not served on the Vertex global endpoint, so its
  # Vertex case runs in us-central1. The client fixture ignores this for mldev.
  if (
      request.node.originalname == 'test_embed'
      and os.environ.get('GOOGLE_CLOUD_LOCATION') == 'global'
  ):
    return 'us-central1'
  return None


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_embed',
        parameters=genai_types.EmbedContentParameters(
            model='gemini-embedding-001',
            contents='Hello world!',
            config={
                'output_dimensionality': 10,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_embed_gemini_embedding_2',
        parameters=genai_types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents='Hello world!',
            config={
                'output_dimensionality': 10,
            },
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.embed_content',
    test_table=test_table,
)

pytest_plugins = ('pytest_asyncio',)
