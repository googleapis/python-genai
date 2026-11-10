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


def test_send_message_without_afc_continuation_token(client):
  if client._api_client.vertexai:
    chat = client.chats.create(
        model=MODEL_NAME_VERTEX,
        config=types.GenerateContentConfig(
            http_options=VERTEX_HTTP_OPTIONS,
        ),
    )
  else:
    chat = client.chats.create(
        model=MODEL_NAME_MLDEV,
        config=types.GenerateContentConfig(
            http_options=MLDEV_HTTP_OPTIONS,
        ),
    )
  with pytest_helper.exception_if_mldev(client, errors.ServerError):
    response = chat.send_message(
        'Write an exhaustive, multi-chapter textbook on compiler design '
        'that is around 40,000 tokens long.'
    )
    assert response.text
    assert response.candidates[0].finish_reason == types.FinishReason.STOP
    assert len(chat.get_history()) == 2
    assert chat.get_history()[0].role == 'user'
    assert chat.get_history()[1].role == 'model'


def test_send_message_with_afc_continuation_token(client):
  if client._api_client.vertexai:
    model_name = MODEL_NAME_VERTEX
    config = types.GenerateContentConfig(
        http_options=VERTEX_HTTP_OPTIONS,
        tools=[divide_integers],
    )
  else:
    model_name = MODEL_NAME_MLDEV
    config = types.GenerateContentConfig(
        http_options=MLDEV_HTTP_OPTIONS,
        tools=[divide_integers],
    )
  chat = client.chats.create(
      model=model_name,
      config=config,
  )
  response = chat.send_message(
      'First compute 100 / 2 using the tool, then write an exhaustive '
      '40,000-token treatise incorporating that result.'
  )

  chat_history = chat.get_history()
  assert response.text
  assert response.candidates[0].finish_reason == types.FinishReason.STOP
  # [0] user prompt
  # [1] model function_call
  # [2] user function_response
  # [3] merged model long decode
  assert len(chat_history) == 4
  assert chat_history[0].role == 'user'
  assert chat_history[1].role == 'model'
  assert chat_history[1].parts[0].function_call.name == 'divide_integers'
  assert chat_history[2].role == 'user'
  assert chat_history[2].parts[0].function_response.name == 'divide_integers'
  assert chat_history[3].role == 'model'


@pytest.mark.asyncio
async def test_async_send_message_without_afc_continuation_token(client):
  if client._api_client.vertexai:
    model_name = MODEL_NAME_VERTEX
    config = types.GenerateContentConfig(
        http_options=VERTEX_HTTP_OPTIONS,
    )
  else:
    model_name = MODEL_NAME_MLDEV
    config = types.GenerateContentConfig(
        http_options=MLDEV_HTTP_OPTIONS,
    )
  chat = client.aio.chats.create(model=model_name, config=config)
  response = await chat.send_message(
      'Write an exhaustive, multi-chapter textbook on compiler design '
      'that is around 50,000 tokens long.'
  )

  assert response.text
  assert response.candidates[0].finish_reason == types.FinishReason.STOP
  assert chat.get_history()[0].role == 'user'
  assert chat.get_history()[1].role == 'model'
