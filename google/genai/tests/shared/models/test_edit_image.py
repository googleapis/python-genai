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


"""Tests for edit_image."""

import os

from .... import types
from ... import pytest_helper

CAPABILITY_MODEL_NAME = 'imagen-3.0-capability-001'

IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data/google.png')
)

MASK_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data/checkerboard.png')
)

raw_ref_image = types.RawReferenceImage(
    reference_id=1,
    reference_image=types.Image.from_file(location=IMAGE_FILE_PATH),
)

mask_ref_image = types.MaskReferenceImage(
    reference_id=2,
    config=types.MaskReferenceConfig(
        mask_mode='MASK_MODE_BACKGROUND',
        mask_dilation=0.06,
    ),
)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_edit_mask_inpaint_insert',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._EditImageParameters(
            model=CAPABILITY_MODEL_NAME,
            prompt='Sunlight and clear weather',
            reference_images=[raw_ref_image, mask_ref_image],
            config=types.EditImageConfig(
                edit_mode=types.EditMode.EDIT_MODE_INPAINT_INSERTION,
            ),
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.edit_image',
    test_table=test_table,
)
