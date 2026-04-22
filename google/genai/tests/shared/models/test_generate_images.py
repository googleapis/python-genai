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
"""Tests for generate_images."""

from .... import types
from ... import pytest_helper

IMAGEN_MODEL_LATEST = 'imagen-4.0-generate-001'

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_simple_prompt',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Red skateboard',
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_images',
    test_table=test_table,
)
