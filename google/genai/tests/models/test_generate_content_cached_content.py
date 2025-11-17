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


from ... import _transformers as t
from ... import types
from .. import pytest_helper

VERTEX_CACHED_CONTENT_NAME = '8163416782997028864'
MLDEV_CACHED_CONTENT_NAME = 'idv6zldt3p2f1lbm31vn41tx2ld42qngpcnka2s3'

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_cached_content_wrong_name',
        exception_if_vertex='INVALID_ARGUMENT',
        exception_if_mldev='INVALID_ARGUMENT',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('What is in these docs?'),
            config={
                'cached_content': 'batchPredictionJobs/123',
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_cached_content_partial_vertex_resource_name_0',
        exception_if_mldev='INVALID_ARGUMENT',
        skip_in_api_mode=(
            'CachedContent API has expiration and permission issues'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('What is in these docs?'),
            config={
                'cached_content': f'locations/us-central1/cachedContents/{VERTEX_CACHED_CONTENT_NAME}',
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_cached_content_partial_vertex_resource_name_1',
        exception_if_mldev='PERMISSION_DENIED',
        skip_in_api_mode=(
            'CachedContent API has expiration and permission issues'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('What is in these docs?'),
            config={
                'cached_content': (
                    f'cachedContents/{VERTEX_CACHED_CONTENT_NAME}'
                ),
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_cached_content_partial_vertex_resource_name_2',
        exception_if_mldev='PERMISSION_DENIED',
        skip_in_api_mode=(
            'CachedContent API has expiration and permission issues'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('What is in these docs?'),
            config={
                'cached_content': VERTEX_CACHED_CONTENT_NAME,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_cached_content_partial_mldev_resource_name_1',
        exception_if_vertex='NOT_FOUND',
        skip_in_api_mode=(
            'CachedContent API has expiration and permission issues'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('What is in these docs?'),
            config={
                'cached_content': f'{MLDEV_CACHED_CONTENT_NAME}',
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_cached_content_for_vertex',
        exception_if_mldev='INVALID_ARGUMENT',
        skip_in_api_mode=(
            'CachedContent API has expiration and permission issues'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('What is in these docs?'),
            config={
                'cached_content': f'projects/964831358985/locations/us-central1/cachedContents/{VERTEX_CACHED_CONTENT_NAME}',
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_cached_content_for_mldev',
        exception_if_vertex='NOT_FOUND',
        skip_in_api_mode=(
            'CachedContent API has expiration and permission issues'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('Tell me a story in 300 words.'),
            config={
                'cached_content': f'cachedContents/{MLDEV_CACHED_CONTENT_NAME}',
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
