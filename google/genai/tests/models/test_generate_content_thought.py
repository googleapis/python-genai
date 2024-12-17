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


from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper

# TODO: b/372730941 - Re-enable this test once HTTP options are supported for
# all languages.
"""
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_generate_content_thought',
        parameters=types._GenerateContentParameters(
            model='models/gemini-2.0-flash-exp-thinking',
            contents=t.t_contents(
                None, 'What is the sum of natural numbers from 1 to 100?'
            ),
        ),
        exception_if_vertex='404',
        skip_in_api_mode=(
            'Requires HTTP options support (not currently present in Go SDK).'
        ),
    ),
]
"""


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    http_options={
        'api_version': 'v1alpha',
    },
)


def test_generate_content_has_thought(client):
  contents = 'What is the sum of natural numbers from 1 to 100?'
  config = types.GenerateContentConfig()
  response = client.models.generate_content(
      model='gemini-2.0-flash-exp-thinking',
      contents=contents,
      config=config,
  )
  has_thought = False
  thought = ''
  if response.candidates:
    for candidate in response.candidates:
      for part in candidate.content.parts:
        if part.thought:
          has_thought = True
          thought = part.text
          break
  assert has_thought
  assert thought not in response.text
