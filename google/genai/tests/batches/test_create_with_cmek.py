# Copyright 2026 Google LLC
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


"""Tests for batches.create() with Customer-Managed Encryption Key (CMEK)."""

import pytest

from ... import types
from .. import pytest_helper


_GEMINI_MODEL = 'gemini-2.5-flash'
_DISPLAY_NAME = 'test_batch'
_KMS_KEY_NAME = 'projects/test-project/locations/us-central1/keyRings/test-keyring/cryptoKeys/test-key'

_GENERATE_CONTENT_GCS_INPUT_FILE = (
    'gs://unified-genai-tests/batches/input/generate_content_requests.jsonl'
)

# All tests will be run for both Vertex and MLDev.
# Test 1: EncryptionSpec as typed model
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_create_with_encryption_spec',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL,
            src=_GENERATE_CONTENT_GCS_INPUT_FILE,
            config=types.CreateBatchJobConfig(
                display_name=_DISPLAY_NAME,
                encryption_spec=types.EncryptionSpec(
                    kms_key_name=_KMS_KEY_NAME,
                ),
            ),
        ),
        exception_if_mldev='only supported in Gemini Enterprise',
        exception_if_vertex='INVALID_ARGUMENT',  # key doesn't exist
    ),
    # Test 2: EncryptionSpec as dict
    pytest_helper.TestTableItem(
        name='test_create_with_encryption_spec_dict',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL,
            src=_GENERATE_CONTENT_GCS_INPUT_FILE,
            config={
                'display_name': _DISPLAY_NAME,
                'encryption_spec': {
                    'kms_key_name': _KMS_KEY_NAME,
                },
            },
        ),
        exception_if_mldev='only supported in Gemini Enterprise',
        exception_if_vertex='INVALID_ARGUMENT',
    ),
    # Test 3: EncryptionSpec with inlined requests (MLDev raises ValueError)
    pytest_helper.TestTableItem(
        name='test_create_with_encryption_spec_inlined',
        parameters=types._CreateBatchJobParameters(
            model=_GEMINI_MODEL,
            src={
                'inlined_requests': [
                    {
                        'contents': [
                            {'parts': [{'text': 'say hello'}], 'role': 'user'}
                        ]
                    },
                ]
            },
            config=types.CreateBatchJobConfig(
                display_name=_DISPLAY_NAME,
                encryption_spec=types.EncryptionSpec(
                    kms_key_name=_KMS_KEY_NAME,
                ),
            ),
        ),
        exception_if_mldev='only supported in Gemini Enterprise',
        exception_if_vertex='INVALID_ARGUMENT',
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
