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


"""Tests for generate_image."""

import pytest

from ... import types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_simple_prompt',
        parameters=types._GenerateImagesParameters(
            model='imagen-3.0-generate-002',
            prompt='Create a blue circle',
            config={'number_of_images': 1, 'output_mime_type': 'image/jpeg'},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_parameters',
        exception_if_mldev='not supported in Gemini API',
        parameters=types._GenerateImagesParameters(
            model='imagen-3.0-generate-002',
            prompt='Robot holding a red skateboard',
            config={
                'aspect_ratio': '1:1',
                'negative_prompt': 'human',
                'guidance_scale': 15.0,
                'safety_filter_level': 'BLOCK_MEDIUM_AND_ABOVE',
                'number_of_images': 1,
                'person_generation': 'DONT_ALLOW',
                'include_safety_attributes': False,
                'include_rai_reason': True,
                'output_mime_type': 'image/jpeg',
                'output_compression_quality': 80,
                # The below parameters are not supported in Google AI.
                'add_watermark': False,
                'seed': 1337,
                'language': 'en',
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_mldev_config_parameters',
        parameters=types._GenerateImagesParameters(
            model='imagen-3.0-generate-002',
            prompt='Robot holding a red skateboard',
            config={
                'aspect_ratio': '1:1',
                'negative_prompt': 'human',
                'guidance_scale': 15.0,
                'safety_filter_level': 'BLOCK_MEDIUM_AND_ABOVE',
                'number_of_images': 1,
                'person_generation': 'DONT_ALLOW',
                'include_safety_attributes': False,
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
    test_method='models.generate_images',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_simple_prompt_async(client):
  response = await client.aio.models.generate_images(
      model='imagen-3.0-generate-002',
      prompt='Create a blue circle',
      config={'number_of_images': 1, 'output_mime_type': 'image/jpeg'},
  )
  assert response.generated_images[0].image.image_bytes
