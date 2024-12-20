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


from pydantic import BaseModel, ValidationError
import pytest
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_candidate_count_zero',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'candidate_count': 0,
            },
        ),
        exception_if_mldev='400'
    ),
    pytest_helper.TestTableItem(
        name='test_max_output_tokens_zero',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'max_output_tokens': 0,
            },
        ),
        exception_if_vertex='400',
        exception_if_mldev='400',
    ),
    pytest_helper.TestTableItem(
        name='test_logprobs_zero',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'logprobs': 0,
            },
        ),
        exception_if_mldev='response_logprobs is true',
        exception_if_vertex='setting response_logprobs to be true',
        skip_in_api_mode='it will encounter 400 for api mode',
    ),
    pytest_helper.TestTableItem(
        name='test_logprobs_zero_with_response_logprobs_true',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'response_logprobs': True,
                'logprobs': 0,
            },
        ),
        # ML DEV discovery doc supports response_logprobs but the backend
        # does not.
        # TODO: update replay test json files when ML Dev backend is updated.
        exception_if_mldev='INVALID_ARGUMENT',
    ),
    pytest_helper.TestTableItem(
        name='test_presence_penalty_zero',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'presence_penalty': 0,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_frequency_penalty_zero',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'frequency_penalty': 0,
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
pytest_plugins = ('pytest_asyncio',)
