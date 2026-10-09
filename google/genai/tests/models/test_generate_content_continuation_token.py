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


import pytest
from ... import errors
from ... import types
from .. import pytest_helper

pytestmark = [
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
    ),
]
pytest_plugins = ('pytest_asyncio',)

MODEL_NAME_VERTEX = 'test-model1'
MODEL_NAME_MLDEV = 'test-model2'

VERTEX_HTTP_OPTIONS = {
    'api_version': 'v1beta1',
    'base_url': 'https://autopush-aiplatform.sandbox.googleapis.com/',
}
MLDEV_HTTP_OPTIONS = {
    'base_url': 'https://autopush-generativelanguage.sandbox.googleapis.com/',
}


def divide_integers(numerator: int, denominator: int) -> int:
  """Divides two integers."""
  return numerator // denominator


def test_gc_without_afc_continuation_token(client):

  response = None
  if client._api_client.vertexai:
    response = client.models.generate_content(
        model=MODEL_NAME_VERTEX,
        contents=(
            'Write an exhaustive, multi-chapter textbook on compiler design '
            'that is around 40,000 tokens long.'
        ),
        config=types.GenerateContentConfig(
            http_options=VERTEX_HTTP_OPTIONS,
        ),
    )
  else:
    response = client.models.generate_content(
        model=MODEL_NAME_MLDEV,
        contents=(
            'Write an exhaustive, multi-chapter textbook on compiler design '
            'that is around 40,000 tokens long.'
        ),
        config=types.GenerateContentConfig(
            http_options=MLDEV_HTTP_OPTIONS,
        ),
    )

  assert response and response.text
  assert response.candidates[0].finish_reason == types.FinishReason.CONTINUATION


def test_gc_without_afc_continuation_token_opt_in(client):

  response = None
  if client._api_client.vertexai:
    response = client.models.generate_content(
        model=MODEL_NAME_VERTEX,
        contents=(
            'Write an exhaustive, multi-chapter textbook on compiler design '
            'that is around 40,000 tokens long.'
        ),
        config=types.GenerateContentConfig(
            http_options=VERTEX_HTTP_OPTIONS,
            automatic_continuation=True,
        ),
    )
  else:
    response = client.models.generate_content(
        model=MODEL_NAME_MLDEV,
        contents=(
            'Write an exhaustive, multi-chapter textbook on compiler design '
            'that is around 40,000 tokens long.'
        ),
        config=types.GenerateContentConfig(
            http_options=MLDEV_HTTP_OPTIONS,
            automatic_continuation=True,
        ),
    )

  assert response and response.text
  assert response.candidates[0].finish_reason == types.FinishReason.STOP


def test_gc_with_afc_continuation_token_opt_in(client):

  response = None
  if client._api_client.vertexai:
    response = client.models.generate_content(
        model=MODEL_NAME_VERTEX,
        contents=(
            'Use the tool to divide 100 by 2, then write an exhaustive,'
            ' multi-chapter textbook on compiler design that is around 40,000'
            ' tokens long.'
        ),
        config=types.GenerateContentConfig(
            http_options=VERTEX_HTTP_OPTIONS,
            automatic_continuation=True,
            tools=[divide_integers],
        ),
    )
  else:
    response = client.models.generate_content(
        model=MODEL_NAME_MLDEV,
        contents=(
            'Use the tool to divide 100 by 2, then write an exhaustive,'
            ' multi-chapter textbook on compiler design that is around 40,000'
            ' tokens long.'
        ),
        config=types.GenerateContentConfig(
            http_options=MLDEV_HTTP_OPTIONS,
            automatic_continuation=True,
            tools=[divide_integers],
        ),
    )

  assert response and response.text
  assert response.candidates[0].finish_reason == types.FinishReason.STOP
