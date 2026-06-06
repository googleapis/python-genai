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

from ... import _api_client
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_disable_thinking',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('Explain the monty hall problem.'),
            config={
                'thinking_config': {
                    'thinking_budget': 0},
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_thinking_level',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('Explain the monty hall problem.'),
            config={
                'thinking_config': {
                    'thinking_level': "LOW"
                },
            },
        ),
    ),
]


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)


def test_thinking_budget(client):
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents='What is the sum of natural numbers from 1 to 100?',
        config={
            'thinking_config': {
                'include_thoughts': True,
                'thinking_budget': 10000,
            },
        },
    )
    has_thought = False
    if response.candidates:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.thought:
                    has_thought = True
                    break
    assert has_thought
