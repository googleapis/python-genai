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


"""Tests for recontext_image."""

import pytest

from ... import types
from .. import pytest_helper

VIRTUAL_TRY_ON_IMAGE_MODEL_LATEST = 'virtual-try-on-001'

PERSON_IMAGE = types.Image(
    gcs_uri='gs://genai-sdk-tests/inputs/images/man.jpg',
)

PANTS = types.Image(
    gcs_uri='gs://genai-sdk-tests/inputs/images/pants.jpg',
)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_virtual_try_on',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._RecontextImageParameters(
            model=VIRTUAL_TRY_ON_IMAGE_MODEL_LATEST,
            source=types.RecontextImageSource(
                person_image=PERSON_IMAGE,
                product_images=[
                    types.ProductImage(product_image=PANTS)
                ],
            ),
            config=types.RecontextImageConfig(
                number_of_images=1,
                output_mime_type='image/jpeg',
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_virtual_try_on_all_config',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._RecontextImageParameters(
            model=VIRTUAL_TRY_ON_IMAGE_MODEL_LATEST,
            source=types.RecontextImageSource(
                person_image=PERSON_IMAGE,
                product_images=[
                    types.ProductImage(
                        product_image=PANTS
                    )
                ],
            ),
            config=types.RecontextImageConfig(
                number_of_images=1,
                output_mime_type='image/jpeg',
                base_steps=32,
                seed=1337,
                add_watermark=False,
                safety_filter_level=types.SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
                person_generation=types.PersonGeneration.ALLOW_ADULT,
                output_compression_quality=75,
                enhance_prompt=False,
            ),
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.recontext_image',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_virtual_try_on_async(client):
  with pytest_helper.exception_if_mldev(client, ValueError):
    response = await client.aio.models.recontext_image(
        model=VIRTUAL_TRY_ON_IMAGE_MODEL_LATEST,
        source=types.RecontextImageSource(
            person_image=PERSON_IMAGE,
            product_images=[
                types.ProductImage(product_image=PANTS)
            ],
        ),
        config=types.RecontextImageConfig(
            number_of_images=1,
            output_mime_type='image/jpeg',
        ),
    )
    assert len(response.generated_images) == 1
    assert response.generated_images[0].image.image_bytes
