# Copyright 2024 Google LLC
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

from pydantic import ValidationError
import pytest

from ... import types
from .. import pytest_helper


IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/bridge1.png')
)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_upscale_no_config',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types.UpscaleImageParameters(
            model='imagen-3.0-generate-001',
            image=types.Image.from_file(location=IMAGE_FILE_PATH),
            upscale_factor='x2',
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_upscale',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types.UpscaleImageParameters(
            model='imagen-3.0-generate-001',
            image=types.Image.from_file(location=IMAGE_FILE_PATH),
            upscale_factor='x2',
            config={
                'include_rai_reason': True,
                'output_mime_type': 'image/jpeg',
                'output_compression_quality': 80,
            },
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.upscale_image',
    test_table=test_table,
)


def test_upscale_extra_config_parameters(client):
  # MLDev currently does not support upscale_image, but the ValidationError
  # occurs before the ValueError.
  try:
    # User is not allowed to set mode or number_of_images
    client.models.upscale_image(
        model='imagen-3.0-generate-001',
        image=types.Image.from_file(location=IMAGE_FILE_PATH),
        upscale_factor='x2',
        config={
            'mode': 'upscale',
            'number_of_images': 1,
        }
    )
    # Should never reach this.
    assert False
  except Exception as e:
    assert isinstance(e, ValidationError)
    assert 'Extra inputs are not permitted' in str(e)


@pytest.mark.asyncio
async def test_upscale_async(client):
  with pytest_helper.exception_if_mldev(client, ValueError):
    response = await client.aio.models.upscale_image(
        model='imagen-3.0-generate-001',
        image=types.Image.from_file(location=IMAGE_FILE_PATH),
        upscale_factor='x2',
        config={
            'include_rai_reason': True,
            'output_mime_type': 'image/jpeg',
            'output_compression_quality': 80,
        },
    )
    assert response.generated_images[0].image.image_bytes


@pytest.mark.asyncio
async def test_upscale_extra_config_parameters_async(client):
  # MLDev currently does not support upscale_image, but the ValidationError
  # occurs before the ValueError.
  try:
    # User is not allowed to set mode or number_of_images
    await client.aio.models.upscale_image(
        model='imagen-3.0-generate-001',
        image=types.Image.from_file(location=IMAGE_FILE_PATH),
        upscale_factor='x2',
        config={
            'mode': 'upscale',
            'number_of_images': 1,
        },
    )
    # Should never reach this.
    assert False
  except Exception as e:
    assert isinstance(e, ValidationError)
    assert 'Extra inputs are not permitted' in str(e)
