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

import pydantic
import pytest

from ... import _api_client
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_image_generation_config',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash-image',
            contents=t.t_contents('A photorealistic red apple on a table.'),
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio='16:9',
                )
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_image_generation_filtered',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash-image',
            contents=t.t_contents('Make a zombie anime style'),
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio='16:9',
                )
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_image_generation_config_validation_none',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash-image',
            contents=t.t_contents('A photorealistic red apple on a table.'),
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=None
            ),
        ),
    ),
]


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)


def test_image_generation_wrong_config(client):
  with pytest.raises(pydantic.ValidationError):
    client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=t.t_contents('A photorealistic red apple on a table.'),
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.GenerateImagesConfig(
                aspect_ratio='16:9',
                number_of_images=1,
            )
        ),
    )


def test_image_generation_validation_model_dump(client):
  config = types.GenerateContentConfig(
      response_modalities=['IMAGE'],
  )

  class Foo(pydantic.BaseModel):
    value: types.GenerateContentConfig

  f = Foo(value=config)
  in_memory = f.model_dump(mode='json')
  Foo.model_validate(in_memory)
