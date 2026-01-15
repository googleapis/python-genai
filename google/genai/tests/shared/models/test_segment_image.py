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


"""Tests for segment_image."""

import os

from .... import types
from ... import pytest_helper

SEGMENT_IMAGE_MODEL_LATEST = 'image-segmentation-001'

SOURCE_IMAGE_FILE_PATH1 = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../data/google.png')
)

SOURCE_IMAGE1 = types.Image.from_file(location=SOURCE_IMAGE_FILE_PATH1)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_segment_background',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._SegmentImageParameters(
            model=SEGMENT_IMAGE_MODEL_LATEST,
            source=types.SegmentImageSource(
                image=SOURCE_IMAGE1,
            ),
            config=types.SegmentImageConfig(
                mode=types.SegmentMode.BACKGROUND,
            ),
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.segment_image',
    test_table=test_table,
)
