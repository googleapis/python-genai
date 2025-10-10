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


"""Tests for tokens.create()."""

import pytest

from ... import types
from .. import pytest_helper


_MODEL = 'models/gemini-live-2.5-flash-preview'


# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_create_no_lock',
        parameters=types.CreateAuthTokenParameters(
            # remove v1alpha after v1beta is available.
            config={'http_options': {'api_version': 'v1alpha'}},
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
    pytest_helper.TestTableItem(
        name='test_create_global_lock',
        parameters=types.CreateAuthTokenParameters(
            # remove v1alpha after v1beta is available.
            config={
                'http_options': {'api_version': 'v1alpha'},
                'uses': 2,
                'live_connect_constraints': {
                    'model': _MODEL,
                    'config': {
                        'response_modalities': ['TEXT'],
                        'temperature': 0.7,
                    },
                },
            },
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
    pytest_helper.TestTableItem(
        name='test_create_lock_non_null_fields',
        parameters=types.CreateAuthTokenParameters(
            # remove v1alpha after v1beta is available.
            config={
                'http_options': {'api_version': 'v1alpha'},
                'uses': 2,
                'live_connect_constraints': {
                    'model': _MODEL,
                    'config': {
                        'response_modalities': ['TEXT'],
                        'temperature': 0.7,
                    },
                },
                'lock_additional_fields': [],
            },
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
    pytest_helper.TestTableItem(
        name='test_create_lock_unset_fields_as_default',
        parameters=types.CreateAuthTokenParameters(
            # remove v1alpha after v1beta is available.
            config={
                'http_options': {'api_version': 'v1alpha'},
                'uses': 2,
                'live_connect_constraints': {
                    'model': _MODEL,
                    'config': {
                        'response_modalities': ['TEXT'],
                        'temperature': 0.7,
                    },
                },
                'lock_additional_fields': ['output_audio_transcription'],
            },
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
    pytest_helper.TestTableItem(
        name='test_create_lock_additional_fields',
        parameters=types.CreateAuthTokenParameters(
            # remove v1alpha after v1beta is available.
            config={
                'http_options': {'api_version': 'v1alpha'},
                'uses': 2,
                'live_connect_constraints': {
                    'model': _MODEL,
                    'config': {
                        'response_modalities': ['TEXT'],
                        'temperature': 0.7,
                    },
                },
                'lock_additional_fields': ['top_k'],
            },
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
    pytest_helper.TestTableItem(
        name='test_create_lock_with_no_params',
        parameters=types.CreateAuthTokenParameters(
            # remove v1alpha after v1beta is available.
            config={
                'http_options': {'api_version': 'v1alpha'},
                'lock_additional_fields': ['output_audio_transcription'],
            },
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
    pytest_helper.TestTableItem(
        name='test_create_lock_with_empty_params',
        parameters=types.CreateAuthTokenParameters(
            # remove v1alpha after v1beta is available.
            config={
                'http_options': {'api_version': 'v1alpha'},
                'lock_additional_fields': ['output_audio_transcription'],
                'live_connect_constraints': {},
            },
        ),
        exception_if_vertex='only supported in the Gemini Developer client',
    ),
]

pytestmark = [
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
        test_method='auth_tokens.create',
        test_table=test_table,
    ),
]


@pytest.mark.asyncio
async def test_async_create_no_lock(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    config = types.CreateAuthTokenConfig(
        http_options=types.HttpOptions(api_version='v1alpha')
    )
    token = await client.aio.auth_tokens.create(config=config)
