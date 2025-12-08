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

from .... import types
from ... import pytest_helper

PRODUCT_RECONTEXT_MODEL_LATEST = 'imagen-product-recontext-preview-06-30'

BACKPACK1 = types.Image(
    gcs_uri='gs://genai-sdk-tests/inputs/images/backpack1.png',
)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_product_recontext',
        exception_if_mldev='only supported in the Vertex AI client',
        parameters=types._RecontextImageParameters(
            model=PRODUCT_RECONTEXT_MODEL_LATEST,
            source=types.RecontextImageSource(
                prompt='On a school desk',
                product_images=[
                    types.ProductImage(product_image=BACKPACK1)
                ],
            ),
            config=types.RecontextImageConfig(
                number_of_images=1,
                add_watermark=True,
                output_mime_type='image/jpeg',
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
