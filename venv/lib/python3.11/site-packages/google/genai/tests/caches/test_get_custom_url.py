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


import pytest
from ... import types
from .. import pytest_helper
from . import constants


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        skip_in_api_mode='Get is not reproducible in the API mode.',
        name='test_caches_get_with_vertex_cache_name',
        exception_if_mldev='404',
        parameters=types._GetCachedContentParameters(
            name=constants.CACHED_CONTENT_NAME_VERTEX,
            config={
                'http_options': constants.VERTEX_HTTP_OPTIONS,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        skip_in_api_mode='Get is not reproducible in the API mode.',
        name='test_caches_get_with_mldev_cache_name',
        exception_if_vertex='404',
        parameters=types._GetCachedContentParameters(
            name=constants.CACHED_CONTENT_NAME_MLDEV,
            config={
                'http_options': constants.MLDEV_HTTP_OPTIONS,
            },
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='caches.get',
    test_table=test_table,
)
