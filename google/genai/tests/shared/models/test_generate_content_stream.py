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

"""Tests for models.generate_content_stream()."""

from .... import types as genai_types
from ... import pytest_helper
from pydantic import BaseModel


class _GenerateContentStreamParameters(BaseModel):
    model: str
    contents: str


def generate_content_stream(client, parameters):
  response = client.models.generate_content_stream(
      model=parameters.model,
      contents=parameters.contents,
  )
  for _ in response:
    pass


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_generate_content_stream',
        parameters=_GenerateContentStreamParameters(
            model='gemini-2.5-flash',
            contents='The quick brown fox jumps over the lazy dog.',
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='generate_content_stream',
    test_table=test_table,
)

pytest_plugins = ('pytest_asyncio',)
