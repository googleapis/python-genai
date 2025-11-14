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

"""Tests for upscale_image."""

import os

from .... import types
from ... import pytest_helper

IMAGEN_MODEL_LATEST = 'imagen-4.0-upscale-preview'

IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data/bridge1.png')
)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_upscale',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types.UpscaleImageParameters(
            model=IMAGEN_MODEL_LATEST,
            image=types.Image.from_file(location=IMAGE_FILE_PATH),
            upscale_factor='x2',
            config=types.UpscaleImageConfig(
                include_rai_reason=True,
                output_mime_type='image/jpeg',
                output_compression_quality=80,
                enhance_input_image=True,
                image_preservation_factor=0.6,
            ),
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.upscale_image',
    test_table=test_table,
)
