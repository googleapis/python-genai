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

from .... import types as genai_types
from ... import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_embed',
        parameters=genai_types._EmbedContentParameters(
            model='text-embedding-004',
            contents='Hello world!',
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
