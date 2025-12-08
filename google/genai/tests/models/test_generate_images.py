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

import pytest

from ... import types
from .. import pytest_helper

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
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_parameters',
        exception_if_mldev='not supported in Gemini API',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Red skateboard',
            config=types.GenerateImagesConfig(
                image_size='2K',
                aspect_ratio='1:1',
                guidance_scale=15.0,
                safety_filter_level=types.SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
                number_of_images=1,
                person_generation=types.PersonGeneration.DONT_ALLOW,
                include_safety_attributes=True,
                include_rai_reason=True,
                output_mime_type='image/jpeg',
                output_compression_quality=80,
                # The below parameters are not supported in Gemini Developer API.
                negative_prompt='human',
                add_watermark=False,
                seed=1337,
                language='en',
                enhance_prompt=True,
                labels={'imagen_label_key': 'generate_images'}
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_person_generation_enum_parameters',
        exception_if_mldev='enum value is not supported',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Robot holding a red skateboard',
            config=types.GenerateImagesConfig(
                person_generation='ALLOW_ALL',
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_person_generation_enum_parameters_2',
        exception_if_mldev='enum value is not supported',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Robot holding a red skateboard',
            config=types.GenerateImagesConfig(
                person_generation='allow_all',
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_person_generation_enum_parameters_3',
        exception_if_mldev='enum value is not supported',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Robot holding a red skateboard',
            config=types.GenerateImagesConfig(
                person_generation=types.PersonGeneration.ALLOW_ALL,
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_safety_filter_level_enum_parameters',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Robot holding a red skateboard',
            config=types.GenerateImagesConfig(
                safety_filter_level='BLOCK_LOW_AND_ABOVE',
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_safety_filter_level_enum_parameters_2',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Robot holding a red skateboard',
            config=types.GenerateImagesConfig(
                safety_filter_level='block_low_and_above',
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_vertexai_config_safety_filter_level_enum_parameters_3',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Robot holding a red skateboard',
            config=types.GenerateImagesConfig(
                safety_filter_level=types.SafetyFilterLevel.BLOCK_LOW_AND_ABOVE,
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_all_mldev_config_parameters',
        parameters=types._GenerateImagesParameters(
            model=IMAGEN_MODEL_LATEST,
            prompt='Red skateboard',
            config=types.GenerateImagesConfig(
                image_size='2K',
                aspect_ratio='1:1',
                guidance_scale=15.0,
                safety_filter_level='BLOCK_LOW_AND_ABOVE',
                number_of_images=1,
                person_generation='DONT_ALLOW',
                include_safety_attributes=True,
                include_rai_reason=True,
                output_mime_type='image/jpeg',
                output_compression_quality=80,
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


@pytest.mark.asyncio
async def test_simple_prompt_async(client):
  response = await client.aio.models.generate_images(
      model=IMAGEN_MODEL_LATEST,
      prompt='Red skateboard',
      config=types.GenerateImagesConfig(
          number_of_images=1,
          output_mime_type='image/jpeg',
          include_safety_attributes=True,
          include_rai_reason=True,
      ),
  )

  assert response.generated_images[0].image.image_bytes
  # Verify the images accessor works correctly.
  assert (
      response.generated_images[0].image.image_bytes
      == response.images[0].image_bytes
  )
  assert len(response.generated_images) == 1
  assert (
      response.positive_prompt_safety_attributes.content_type
      == 'Positive Prompt'
  )
