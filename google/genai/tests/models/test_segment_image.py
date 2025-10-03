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

import pytest

from ... import types
from .. import pytest_helper

SEGMENT_IMAGE_MODEL_LATEST = 'image-segmentation-001'

SOURCE_IMAGE_FILE_PATH1 = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.png')
)

SOURCE_IMAGE1 = types.Image.from_file(location=SOURCE_IMAGE_FILE_PATH1)

SOURCE_IMAGE_FILE_PATH2 = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/skateboard_stop_sign.jpg')
)

SOURCE_IMAGE2 = types.Image.from_file(location=SOURCE_IMAGE_FILE_PATH2)

SCRIBBLE_IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/segmentation_scribble.jpg')
)

SCRIBBLE_IMAGE = types.Image.from_file(location=SCRIBBLE_IMAGE_FILE_PATH)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_segment_foreground',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._SegmentImageParameters(
            model=SEGMENT_IMAGE_MODEL_LATEST,
            source=types.SegmentImageSource(
                image=SOURCE_IMAGE1,
            ),
            config=types.SegmentImageConfig(
                mode=types.SegmentMode.FOREGROUND,
                max_predictions=1,
                confidence_threshold=0.02,
                mask_dilation=0.02,
                binary_color_threshold=98,
                labels={'imagen_label_key': 'segment_image'}
            ),
        ),
    ),
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
    pytest_helper.TestTableItem(
        name='test_segment_prompt',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._SegmentImageParameters(
            model=SEGMENT_IMAGE_MODEL_LATEST,
            source=types.SegmentImageSource(
                image=SOURCE_IMAGE1,
                prompt='The letter G',
            ),
            config=types.SegmentImageConfig(
                mode=types.SegmentMode.PROMPT,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_segment_semantic',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._SegmentImageParameters(
            model=SEGMENT_IMAGE_MODEL_LATEST,
            source=types.SegmentImageSource(
                image=SOURCE_IMAGE2,
                prompt='skateboard',
            ),
            config=types.SegmentImageConfig(
                mode=types.SegmentMode.SEMANTIC,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_segment_interactive',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._SegmentImageParameters(
            model=SEGMENT_IMAGE_MODEL_LATEST,
            source=types.SegmentImageSource(
                image=SOURCE_IMAGE2,
                scribble_image=types.ScribbleImage(image=SCRIBBLE_IMAGE),
            ),
            config=types.SegmentImageConfig(
                mode=types.SegmentMode.INTERACTIVE,
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


@pytest.mark.asyncio
async def test_segment_foreground_async(client):
  with pytest_helper.exception_if_mldev(client, ValueError):
    response = await client.aio.models.segment_image(
        model=SEGMENT_IMAGE_MODEL_LATEST,
        source=types.SegmentImageSource(
            image=SOURCE_IMAGE2,
        ),
        config=types.SegmentImageConfig(
            mode=types.SegmentMode.FOREGROUND,
            max_predictions=1,
            confidence_threshold=0.02,
            mask_dilation=0.02,
            binary_color_threshold=98,
        )
    )
    assert response.generated_masks[0].mask.image_bytes
    assert len(response.generated_masks) == 1
    assert response.generated_masks[0].labels[0].label == 'foreground'
    assert response.generated_masks[0].labels[0].score > 0
