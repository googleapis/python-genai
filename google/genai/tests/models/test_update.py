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


import pytest
from ... import errors
from ... import types
from .. import pytest_helper

test_http_options = {'headers': {'test': 'headers'}}

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_mldev_tuned_models_update',
        parameters=types._UpdateModelParameters(
            model='tunedModels/generate-num-8498',
            config={
                'display_name': 'My tuned gemini-1.0',
            },
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_tuned_models_update',
        parameters=types._UpdateModelParameters(
            model='models/7687416965014487040',
            config={
                'description': (
                    'My SupervisedTuningJob 2024-05-16 13:36:47.332273'
                ),
            },
        ),
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_mldev_tuned_models_update_with_http_options_in_method',
        parameters=types._UpdateModelParameters(
            model='tunedModels/generate-num-8498',
            config={
                'display_name': 'My tuned gemini-1.0',
                'http_options': test_http_options,
            },
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_tuned_models_update_with_http_options_in_method',
        parameters=types._UpdateModelParameters(
            model='models/7687416965014487040',
            config={
                'description': (
                    'My SupervisedTuningJob 2024-05-16 13:36:47.332273'
                ),
                'http_options': test_http_options,
            },
        ),
        exception_if_mldev='404',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.update',
    test_table=test_table,
)


@pytest.mark.asyncio
async def test_async_update_tuned_model(client):
  if client._api_client.vertexai:
    with pytest.raises(errors.ClientError) as e:
      await client.aio.models.update(
          model='tunedModels/generate-num-8498',
          config={
              'description': 'My tuned gemini-1.0',
              'http_options': test_http_options,
          },
      )
    assert '404' in str(e)
  else:
    response = await client.aio.models.update(
        model='tunedModels/generate-num-8498',
        config={
            'description': 'My tuned gemini-1.0',
            'http_options': test_http_options,
        },
    )


@pytest.mark.asyncio
async def test_async_update_model(client):
  if client._api_client.vertexai:
    response = await client.aio.models.update(
        model='models/7687416965014487040',
        config={
            'display_name': 'My tuned gemini-1.0',
            'http_options': test_http_options,
        },
    )
  else:
    with pytest.raises(errors.ClientError) as e:
      await client.aio.models.update(
          model='models/7687416965014487040',
          config={
              'display_name': 'My tuned gemini-1.0',
              'http_options': test_http_options,
          },
      )
    assert '404' in str(e)
