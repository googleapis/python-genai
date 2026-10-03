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


import copy
import pytest
from ... import types
from .. import pytest_helper
from . import constants
from ... import _transformers as t

_CREATE_CACHED_CONTENT_PARAMETERS_GCS_URI = types._CreateCachedContentParameters(
    model='gemini-2.5-flash',
    config={
        'contents': [
            types.Content(
                role='user',
                parts=[
                    types.Part(
                        fileData=types.FileData(
                            fileUri='gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf',
                            mimeType='application/pdf',
                        )
                    ),
                    types.Part(
                        fileData=types.FileData(
                            fileUri='gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf',
                            mimeType='application/pdf',
                        )
                    ),
                ],
            )
        ],
        'system_instruction': t.t_content('What is the sum of the two pdfs?'),
        'display_name': 'test cache',
        'ttl': '86400s',
        'http_options': constants.VERTEX_HTTP_OPTIONS,
    },
)

_CREATE_CACHED_CONTENT_PARAMETERS_GOOGLEAI_FILE = types._CreateCachedContentParameters(
    model='gemini-2.5-flash',
    config={
        'contents': [
            types.Content(
                role='user',
                parts=[
                    types.Part(
                        fileData=types.FileData(
                            mimeType='application/pdf',
                            fileUri='https://generativelanguage.googleapis.com/v1beta/files/v200dhvn15h7',
                        )
                    )
                ],
            )
        ],
        'system_instruction': t.t_content('What is the sum of the two pdfs?'),
        'display_name': 'test cache',
        'ttl': '86400s',
        'http_options': constants.MLDEV_HTTP_OPTIONS,
    },
)

# Replay mode is not supported for caches tests due to the error message
# inconsistency in api and replay mode.
# To run api mode tests, use the following steps:
# 1. First create the resource.
#   sh run_tests.sh pytest -s tests/caches/test_create.py --mode=api
#   1.1 If mldev test_create fails, update the uploaded file using this colab
#       https://colab.sandbox.google.com/drive/1Fv6KGSs0cg6tlpcUHdsclHussXMEGOXk#scrollTo=RSKmFPx00MVL.
# 2. Find the resource name in debugging print and change the resource name constants.py.
# 3. Run and record get and update tests.
#   sh run_tests.sh pytest -s tests/caches/test_get.py --mode=api && sh run_tests.sh pytest -s tests/caches/test_update.py --mode=api && sh run_tests.sh pytest -s tests/caches/test_delete.py --mode=api
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_caches_create_with_gcs_uri',
        exception_if_mldev='404',
        parameters=_CREATE_CACHED_CONTENT_PARAMETERS_GCS_URI,
    ),
    pytest_helper.TestTableItem(
        name='test_caches_create_with_googleai_file',
        exception_if_vertex='404',
        parameters=_CREATE_CACHED_CONTENT_PARAMETERS_GOOGLEAI_FILE,
        skip_in_api_mode='Create is not reproducible in the API mode.',
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='caches.create',
    test_table=test_table,
)
pytest_plugins = ('pytest_asyncio',)
