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

import pydantic
import pytest

from ... import types
from .. import pytest_helper

CAPABILITY_MODEL_NAME = 'imagen-3.0-capability-001'

IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.png')
)

MASK_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/checkerboard.png')
)

BRIDGE_IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/bridge1.png')
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

mask_ref_image_user_provided = types.MaskReferenceImage(
    reference_id=2,
    reference_image=types.Image.from_file(location=MASK_FILE_PATH),
    config=types.MaskReferenceConfig(
        mask_mode='MASK_MODE_USER_PROVIDED',
        mask_dilation=0.06,
    ),
)

control_ref_image = types.ControlReferenceImage(
    reference_id=2,
    reference_image=types.Image.from_file(location=MASK_FILE_PATH),
    config=types.ControlReferenceConfig(
        control_type='CONTROL_TYPE_SCRIBBLE',
        # Backend creates the control image if this is set to True.
        enable_control_image_computation=False,
    ),
)

style_ref_image_customization = types.StyleReferenceImage(
    reference_id=1,
    reference_image=types.Image.from_file(location=IMAGE_FILE_PATH),
    config=types.StyleReferenceConfig(
        style_description='glowing style',
    ),
)

subject_ref_image_customization = types.SubjectReferenceImage(
    reference_id=1,
    reference_image=types.Image.from_file(location=IMAGE_FILE_PATH),
    config=types.SubjectReferenceConfig(
        subject_type='SUBJECT_TYPE_PRODUCT',
        subject_description='A product logo that is a multi-colored letter G',
    ),
)

dog_content_ref_image = types.ContentReferenceImage(
    reference_id=1,
    reference_image=types.Image(
        gcs_uri='gs://genai-sdk-tests/inputs/images/dog.jpg'
    ),
)

cyberpunk_style_ref_image = types.StyleReferenceImage(
    reference_id=2,
    reference_image=types.Image(
        gcs_uri='gs://genai-sdk-tests/inputs/images/cyberpunk.jpg'
    ),
    config=types.StyleReferenceConfig(
        style_description='cyberpunk style',
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
                number_of_images=1,
                # Test comprehensive configs
                # aspect_ratio is not supported for mask editing
                negative_prompt='human',
                guidance_scale=15.0,
                safety_filter_level=types.SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
                person_generation=types.PersonGeneration.DONT_ALLOW,
                include_safety_attributes=False,
                include_rai_reason=True,
                output_mime_type='image/jpeg',
                output_compression_quality=80,
                base_steps=32,
                add_watermark=False,
                labels={'imagen_label_key': 'edit_image'}
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_edit_mask_inpaint_insert_user_provided',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._EditImageParameters(
            model=CAPABILITY_MODEL_NAME,
            prompt='Change the colors',
            reference_images=[raw_ref_image, mask_ref_image_user_provided],
            config=types.EditImageConfig(
                edit_mode=types.EditMode.EDIT_MODE_INPAINT_INSERTION,
                # aspect_ratio is not supported for mask editing
                number_of_images=1,
                include_rai_reason=True,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_edit_control_user_provided',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._EditImageParameters(
            model=CAPABILITY_MODEL_NAME,
            prompt='Change the colors aligning with the scribble map [2]',
            reference_images=[raw_ref_image, control_ref_image],
            config=types.EditImageConfig(
                number_of_images=1,
                aspect_ratio='9:16',
                include_rai_reason=True,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_edit_style_reference_image_customization',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._EditImageParameters(
            model=CAPABILITY_MODEL_NAME,
            prompt=(
                'Generate an image in glowing style [1] based on the following'
                ' caption: A church in the mountain.'
            ),
            reference_images=[style_ref_image_customization],
            config=types.EditImageConfig(
                number_of_images=1,
                aspect_ratio='9:16',
                include_rai_reason=True,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_edit_subject_image_customization',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._EditImageParameters(
            model=CAPABILITY_MODEL_NAME,
            prompt=(
                'Generate an image containing a mug with the product logo [1]'
                ' visible on the side of the mug.'
            ),
            reference_images=[subject_ref_image_customization],
            config=types.EditImageConfig(
                number_of_images=1,
                aspect_ratio='9:16',
                include_rai_reason=True,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_edit_content_image_ingredients',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._EditImageParameters(
            model='imagen-4.0-ingredients-preview',
            prompt=(
                'Dog in [1] sleeping on the ground at the bottom of the image'
                ' with the cyberpunk city landscape in [2] in the background.'
            ),
            reference_images=[dog_content_ref_image, cyberpunk_style_ref_image],
            config=types.EditImageConfig(
                number_of_images=1,
                aspect_ratio='9:16',
                include_rai_reason=True,
                output_mime_type='image/jpeg',
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


def test_setting_reference_type_raises(client):
  with pytest.raises(pydantic.ValidationError):
    types.SubjectReferenceImage(
        reference_id=1,
        # This test should fail because the user can't set reference_type.
        reference_type='REFERENCE_TYPE_SUBJECT',
        reference_image=types.Image.from_file(location=IMAGE_FILE_PATH),
        config=types.SubjectReferenceConfig(
            subject_type='SUBJECT_TYPE_PRODUCT',
            subject_description=(
                'A product logo that is a multi-colored letter G'
            ),
        ),
    )


@pytest.mark.asyncio
async def test_edit_mask_inpaint_insert_async(client):
  with pytest_helper.exception_if_mldev(client, ValueError):
    response = await client.aio.models.edit_image(
        model=CAPABILITY_MODEL_NAME,
        prompt='Sunlight and clear weather',
        reference_images=[raw_ref_image, mask_ref_image],
        config=types.EditImageConfig(
            edit_mode=types.EditMode.EDIT_MODE_INPAINT_INSERTION,
            number_of_images=1,
            # Test comprehensive configs
            # aspect_ratio is not supported for mask editing
            negative_prompt='human',
            guidance_scale=15.0,
            safety_filter_level=types.SafetyFilterLevel.BLOCK_MEDIUM_AND_ABOVE,
            person_generation=types.PersonGeneration.DONT_ALLOW,
            include_safety_attributes=False,
            include_rai_reason=True,
            output_mime_type='image/jpeg',
            output_compression_quality=80,
            add_watermark=False,
        ),
    )
    assert response.generated_images[0].image.image_bytes
