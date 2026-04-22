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


from unittest import mock

import pytest

from ... import chats
from ... import client
from ... import models
from ... import types

AFC_HISTORY = [
    types.Content(
        role='user',
        parts=[types.Part.from_text(text='afc input')],
    ),
    types.Content(
        role='model',
        parts=[
            types.Part(
                function_call=types.FunctionCall(
                    name='foo', args={'bar': 'baz'}
                )
            )
        ],
    ),
]


pytest_plugins = 'pytest_asyncio'


@pytest.fixture
def mock_api_client(vertexai=False):
  api_client = mock.MagicMock(spec=client.ApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}  # Ensure headers exist
  api_client.vertexai = vertexai
  return api_client


@pytest.fixture
def mock_generate_content_with_empty_text_part():
  with mock.patch.object(
      models.Models, 'generate_content'
  ) as mock_generate_content:
    mock_generate_content.return_value = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role='model',
                    parts=[types.Part(text='')],
                )
            )
        ]
    )
    yield mock_generate_content


@pytest.fixture
def mock_generate_content_empty_content():
  with mock.patch.object(
      models.Models, 'generate_content'
  ) as mock_generate_content:
    mock_generate_content.return_value = types.GenerateContentResponse(
        candidates=[]
    )
    yield mock_generate_content


@pytest.fixture
def mock_generate_content_stream_with_empty_text_part():
  with mock.patch.object(
      models.Models, 'generate_content_stream'
  ) as mock_generate_content:
    mock_generate_content.return_value = [
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role='model',
                        parts=[types.Part(text='')],
                    ),
                    finish_reason=types.FinishReason.STOP,
                )
            ]
        )
    ]
    yield mock_generate_content


@pytest.fixture
def mock_generate_content_stream_empty_content():
  with mock.patch.object(
      models.Models, 'generate_content_stream'
  ) as mock_generate_content:
    mock_generate_content.return_value = [
        types.GenerateContentResponse(candidates=[])
    ]
    yield mock_generate_content


@pytest.fixture
def mock_generate_content_afc_history():
  with mock.patch.object(
      models.Models, 'generate_content'
  ) as mock_generate_content:
    mock_generate_content.return_value = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role='model',
                    parts=[types.Part.from_text(text='afc output')],
                )
            )
        ],
        automatic_function_calling_history=AFC_HISTORY,
    )
    yield mock_generate_content


@pytest.fixture
def mock_generate_content_stream_afc_history():
  with mock.patch.object(
      models.Models, 'generate_content_stream'
  ) as mock_generate_content:
    mock_generate_content.return_value = [
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role='model',
                        parts=[types.Part.from_text(text='afc output')],
                    ),
                    finish_reason=types.FinishReason.STOP,
                )
            ],
            automatic_function_calling_history=AFC_HISTORY,
        )
    ]
    yield mock_generate_content


def test_history_start_with_valid_model_content():
  history = [
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='Hello there! how can I help you?')],
      ),
      types.Content(role='user', parts=[types.Part.from_text(text='Hello')]),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == history


def test_history_start_with_invalid_model_content():
  history = [
      types.Content(
          role='model',
          parts=[],
      ),
      types.Content(role='user', parts=[types.Part.from_text(text='Hello')]),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == [types.Content(role='user', parts=[types.Part.from_text(text='Hello')])]


def test_history_with_consecutive_valid_user_inputs():
  history = [
      types.Content(
          role='user',
          parts=[types.Part.from_text(text='user input 1')],
      ),
       types.Content(
          role='user',
          parts=[types.Part.from_text(text='user input 2')],
      ),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == history


def test_history_with_valid_and_invalid_user_inputs():
  history = [
      types.Content(
          role='user',
          parts=[types.Part.from_text(text='user input 1')],
      ),
      types.Content(
          role='user',
          parts=[], # invalid content
      ),
      types.Content(
          role='user',
          parts=[types.Part.from_text(text='user input 2')],
      ),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == history


def test_history_with_consecutive_valid_model_outputs():
  history = [
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output 1')],
      ),
       types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output 2')],
      ),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == history


def test_history_with_valid_and_invalid_model_output():
  history = [
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output 1')],
      ),
      types.Content(
          role='model',
          parts=[], # invalid content
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output 2')],
      ),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == []


def test_history_end_with_user_input():
  history = [
      types.Content(
          role='user',
          parts=[types.Part.from_text(text='user input 1')],
      ),
       types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output')],
      ),
       types.Content(
          role='user',
          parts=[types.Part.from_text(text='user input 2')],
      ),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == history


def test_unrecognized_role_in_history():
  history = [
      types.Content(role='user', parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          role='invalid_role',
          parts=[types.Part.from_text(text='Hello there! how can I help you?')],
      ),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  with pytest.raises(ValueError) as e:
    chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert 'Role must be user or model' in str(e)


def test_sync_chat_create():
  history = [
      types.Content(
          role='user', parts=[types.Part.from_text(text='user input turn 1')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 1')],
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 1')],
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='user input turn 2')],
      ),
  ]

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == history


def test_async_chat_create():
  history = [
      types.Content(
          role='user', parts=[types.Part.from_text(text='user input turn 1')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 1')],
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 1')],
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='user input turn 2')],
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 2')],
      ),
  ]

  models_module = models.AsyncModels(mock_api_client)
  chats_module = chats.AsyncChats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == history


def test_sync_chat_create_with_history_dict():
  history = [
      {'role': 'user', 'parts': [{'text': 'user input turn 1'}]},
      {'role': 'model', 'parts': [{'text': 'model output turn 1'}]},
      {'role': 'user', 'parts': [{'text': 'user input turn 2'}]},
      {'role': 'model', 'parts': [{'text': 'model output turn 2'}]},
  ]
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  expected_history = [
      types.Content(
          role='user', parts=[types.Part.from_text(text='user input turn 1')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 1')],
      ),
      types.Content(
          role='user', parts=[types.Part.from_text(text='user input turn 2')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 2')],
      ),
  ]
  assert chat.get_history() == expected_history
  assert chat.get_history(curated=True) == expected_history


def test_async_chat_create_with_history_dict():
  history = [
      {'role': 'user', 'parts': [{'text': 'user input turn 1'}]},
      {'role': 'model', 'parts': [{'text': 'model output turn 1'}]},
      {'role': 'user', 'parts': [{'text': 'user input turn 2'}]},
      {'role': 'model', 'parts': [{'text': 'model output turn 2'}]},
  ]
  models_module = models.AsyncModels(mock_api_client)
  chats_module = chats.AsyncChats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash', history=history)

  expected_history = [
      types.Content(
          role='user', parts=[types.Part.from_text(text='user input turn 1')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 1')],
      ),
      types.Content(
          role='user', parts=[types.Part.from_text(text='user input turn 2')]
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='model output turn 2')],
      ),
  ]
  assert chat.get_history() == expected_history
  assert chat.get_history(curated=True) == expected_history


def test_history_with_invalid_turns():
  valid_input = types.Content(
      role='user', parts=[types.Part.from_text(text='Hello')]
  )
  valid_output = [
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='Hello there! how can I help you?')],
      ),
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='Hello there! how can I help you?')],
      ),
  ]
  invalid_input = types.Content(
      role='user',
      parts=[
          types.Part.from_text(text='a input will be rejected by the model')
      ],
  )
  invalid_output = types.Content(
      role='model',
      parts=[],
  )
  comprehensive_history = []
  comprehensive_history.append(valid_input)
  comprehensive_history.extend(valid_output)
  comprehensive_history.append(invalid_input)
  comprehensive_history.append(invalid_output)
  curated_history = []
  curated_history.append(valid_input)
  curated_history.extend(valid_output)

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(
      model='gemini-2.5-flash', history=comprehensive_history
  )

  assert chat.get_history() == comprehensive_history
  assert chat.get_history(curated=True) == curated_history


def test_chat_with_empty_text_part(mock_generate_content_with_empty_text_part):
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  chat.send_message('Hello')

  expected_comprehensive_history = [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          parts=[types.Part(text='')],
          role='model',
      ),
  ]
  assert chat.get_history() == expected_comprehensive_history
  assert chat.get_history(curated=True) == expected_comprehensive_history


def test_chat_with_empty_content(mock_generate_content_empty_content):
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  chat.send_message('Hello')

  expected_comprehensive_history = [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          parts=[],
          role='model',
      ),
  ]
  assert chat.get_history() == expected_comprehensive_history
  assert not chat.get_history(curated=True)


def test_chat_stream_with_empty_text_part(
    mock_generate_content_stream_with_empty_text_part,
):
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  chunks = chat.send_message_stream('Hello')
  for chunk in chunks:
    pass

  expected_comprehensive_history = [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          parts=[types.Part(text='')],
          role='model',
      ),
  ]
  assert chat.get_history() == expected_comprehensive_history
  assert chat.get_history(curated=True) == expected_comprehensive_history


def test_chat_stream_with_empty_content(
    mock_generate_content_stream_empty_content,
):
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  chunks = chat.send_message_stream('Hello')
  for chunk in chunks:
    pass

  expected_comprehensive_history = [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          parts=[],
          role='model',
      ),
  ]
  assert chat.get_history() == expected_comprehensive_history
  assert not chat.get_history(curated=True)


def test_chat_with_afc_history(mock_generate_content_afc_history):
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  chat.send_message('Hello')

  expected_history = AFC_HISTORY + [
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='afc output')],
      ),
  ]
  assert chat.get_history() == expected_history
  assert chat.get_history(curated=True) == expected_history


def test_chat_stream_with_afc_history(mock_generate_content_stream_afc_history):
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  chunks = chat.send_message_stream('Hello')
  for chunk in chunks:
    pass

  expected_history = AFC_HISTORY + [
      types.Content(
          role='model',
          parts=[types.Part.from_text(text='afc output')],
      ),
  ]
  assert chat.get_history() == expected_history
  assert chat.get_history(curated=True) == expected_history
