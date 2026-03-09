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


"""Tests for batches.create() with invalid source and destinations."""

import pytest

from ... import types
from .. import pytest_helper


_GEMINI_MODEL = 'gemini-2.5-flash'
_EMBEDDING_MODEL = 'gemini-embedding-001'
_DISPLAY_NAME = 'test_batch'

_GENERATE_CONTENT_BQ_OUTPUT_PREFIX = (
    'bq://vertex-sdk-dev.unified_genai_tests_batches.generate_content_output'
)

_EMBEDDING_BQ_INPUT_FILE = (
    'bq://vertex-sdk-dev.unified_genai_tests_batches.embedding_requests'
)


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_union_with_invalid_src',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL,
            src='invalid_src',
            config={
                'display_name': _DISPLAY_NAME,
                'dest': _GENERATE_CONTENT_BQ_OUTPUT_PREFIX,
            },
        ),
        exception_if_mldev='Unsupported source',
        exception_if_vertex='Unsupported source',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_with_invalid_dest',
        parameters=types._CreateBatchJobParameters(
            model=_EMBEDDING_MODEL,
            src=_EMBEDDING_BQ_INPUT_FILE,
            config={
                'display_name': _DISPLAY_NAME,
                'dest': 'invalid_dest',
            },
        ),
        exception_if_mldev='not supported in Gemini API',
        exception_if_vertex='Unsupported destination',
        has_union=True,
    ),
]

pytestmark = [
    pytest.mark.usefixtures('mock_timestamped_unique_name'),
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
        test_method='batches.create',
        test_table=test_table,
    ),
]
