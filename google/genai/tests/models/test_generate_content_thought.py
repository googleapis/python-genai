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

from ... import errors
from .. import pytest_helper
from ... import _api_client

# TODO: b/372730941 - Re-enable this test once HTTP options are supported for
# all languages.
"""
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_generate_content_thought',
        parameters=types._GenerateContentParameters(
            model='models/gemini-2.0-flash-thinking-exp',
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
)


def test_no_thought_with_include_thoughts_v1alpha(client):
  # Thoughts have been disabled in the API.
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    response = client.models.generate_content(
        model='gemini-2.0-flash-thinking-exp',
        contents='What is the sum of natural numbers from 1 to 100?',
        config={
            'thinking_config': {'include_thoughts': True},
            'http_options': {'api_version': 'v1alpha'},
        },
    )
    has_thought = False
    if response.candidates:
      for candidate in response.candidates:
        for part in candidate.content.parts:
          if part.thought:
            has_thought = True
            break
    assert not has_thought


def test_no_thought_with_default_config(client):
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    response = client.models.generate_content(
        model='gemini-2.0-flash-thinking-exp',
        contents='What is the sum of natural numbers from 1 to 100?',
    )
    has_thought = False
    for candidate in response.candidates:
      for part in candidate.content.parts:
        if part.thought:
          has_thought = True
          break
    assert not has_thought
