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


import copy
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

SPLIT_FUNCTION_CALL_PARTS = [
    types.Part(
        function_call=types.FunctionCall(name='what_date_is_today', args={}),
        thought_signature=b'sig1',
    ),
    types.Part(
        function_call=types.FunctionCall(name='what_time_is_now', args={})
    ),
    types.Part(text=''),
]


def what_date_is_today() -> str:
  """Returns today's date."""
  return '2026-01-01'


def what_time_is_now() -> str:
  """Returns the current time."""
  return '12:00'


def _split_function_call_chunks() -> list[types.GenerateContentResponse]:
  """Returns one streamed model turn split across three chunks."""
  chunks = []
  for i, part in enumerate(SPLIT_FUNCTION_CALL_PARTS):
    is_last = i == len(SPLIT_FUNCTION_CALL_PARTS) - 1
    chunks.append(
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(role='model', parts=[part]),
                    finish_reason=types.FinishReason.STOP if is_last else None,
                )
            ]
        )
    )
  return chunks


def _text_chunks() -> list[types.GenerateContentResponse]:
  return [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='It is noon.')]
                  ),
                  finish_reason=types.FinishReason.STOP,
              )
          ]
      )
  ]


pytest_plugins = 'pytest_asyncio'


@pytest.fixture
def mock_api_client(vertexai=False):
  api_client = mock.MagicMock(spec=client.BaseApiClient)
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


def _assert_merged_afc_request(contents: list[types.Content]) -> None:
  assert [c.role for c in contents] == ['user', 'model', 'user']
  assert contents[1].parts == SPLIT_FUNCTION_CALL_PARTS
  assert contents[1].parts[0].thought_signature == b'sig1'
  assert [p.function_response.name for p in contents[2].parts] == [
      'what_date_is_today',
      'what_time_is_now',
  ]


def test_chat_stream_afc_merges_split_function_calls(mock_api_client):
  """A streamed turn split over chunks is sent and recorded as one content."""
  requests = []
  streams = [_split_function_call_chunks(), _text_chunks()]

  def fake_stream(**kwargs):
    requests.append(copy.deepcopy(kwargs['contents']))
    return streams[len(requests) - 1]

  with mock.patch.object(
      models.Models, 'generate_content_stream', side_effect=fake_stream
  ):
    chat = chats.Chats(
        modules=models.Models(api_client_=mock_api_client)
    ).create(
        model='gemini-3-flash',
        config=types.GenerateContentConfig(
            tools=[what_date_is_today, what_time_is_now]
        ),
    )
    for _ in chat.send_message_stream('What date and time is it?'):
      pass

  assert len(requests) == 2
  _assert_merged_afc_request(requests[1])
  assert [c.role for c in chat.get_history()] == [
      'user',
      'model',
      'user',
      'model',
  ]


@pytest.mark.asyncio
async def test_async_chat_stream_afc_merges_split_function_calls(
    mock_api_client,
):
  """A streamed turn split over chunks is sent and recorded as one content."""
  requests = []
  streams = [_split_function_call_chunks(), _text_chunks()]

  async def fake_stream(**kwargs):
    requests.append(copy.deepcopy(kwargs['contents']))
    chunks = streams[len(requests) - 1]

    async def generator():
      for chunk in chunks:
        yield chunk

    return generator()

  with mock.patch.object(
      models.AsyncModels,
      'generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=fake_stream,
  ):
    chat = chats.AsyncChats(
        modules=models.AsyncModels(api_client_=mock_api_client)
    ).create(
        model='gemini-3-flash',
        config=types.GenerateContentConfig(
            tools=[what_date_is_today, what_time_is_now]
        ),
    )
    async for _ in await chat.send_message_stream('What date and time is it?'):
      pass

  assert len(requests) == 2
  _assert_merged_afc_request(requests[1])
  assert [c.role for c in chat.get_history()] == [
      'user',
      'model',
      'user',
      'model',
  ]


def test_chat_stream_afc_disabled_merges_split_function_calls(
    mock_api_client,
):
  """Without AFC, a streamed turn is still recorded as one model content."""
  with mock.patch.object(
      models.Models,
      'generate_content_stream',
      return_value=_split_function_call_chunks(),
  ):
    chat = chats.Chats(
        modules=models.Models(api_client_=mock_api_client)
    ).create(
        model='gemini-3-flash',
        config=types.GenerateContentConfig(
            tools=[what_date_is_today, what_time_is_now],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )
    for _ in chat.send_message_stream('What date and time is it?'):
      pass

  history = chat.get_history()
  assert [c.role for c in history] == ['user', 'model']
  assert history[1].parts == SPLIT_FUNCTION_CALL_PARTS
  assert chat.get_history(curated=True) == history


@pytest.mark.asyncio
async def test_async_chat_stream_afc_disabled_merges_split_function_calls(
    mock_api_client,
):
  """Without AFC, a streamed turn is still recorded as one model content."""

  async def generator():
    for chunk in _split_function_call_chunks():
      yield chunk

  with mock.patch.object(
      models.AsyncModels,
      'generate_content_stream',
      new_callable=mock.AsyncMock,
      return_value=generator(),
  ):
    chat = chats.AsyncChats(
        modules=models.AsyncModels(api_client_=mock_api_client)
    ).create(
        model='gemini-3-flash',
        config=types.GenerateContentConfig(
            tools=[what_date_is_today, what_time_is_now],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )
    async for _ in await chat.send_message_stream('What date and time is it?'):
      pass

  history = chat.get_history()
  assert [c.role for c in history] == ['user', 'model']
  assert history[1].parts == SPLIT_FUNCTION_CALL_PARTS
  assert chat.get_history(curated=True) == history
