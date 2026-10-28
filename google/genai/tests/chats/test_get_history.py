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


_STREAM_PART_1 = types.Part(text='Thinking.', thought=True)
_STREAM_PART_2 = types.Part(text='Hello ')
_STREAM_PART_3 = types.Part(text='world.', thought_signature=b'sig')


def _stream_chunks(
    parts: list[types.Part],
) -> list[types.GenerateContentResponse]:
  """Builds one stream chunk per part; the last chunk ends with STOP."""
  chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(content=types.Content(role='model', parts=[part]))
          ]
      )
      for part in parts
  ]
  chunks[-1].candidates[0].finish_reason = types.FinishReason.STOP
  return chunks


def _stream_config(disable_afc: bool) -> types.GenerateContentConfig:
  """Builds a config that reaches the AFC or the AFC-disabled branch."""
  return types.GenerateContentConfig(
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          disable=disable_afc
      )
  )


@pytest.fixture
def mock_generate_content_stream_multiple_chunks():
  with mock.patch.object(
      models.Models, 'generate_content_stream'
  ) as mock_generate_content:
    mock_generate_content.return_value = _stream_chunks(
        [_STREAM_PART_1, _STREAM_PART_2, _STREAM_PART_3]
    )
    yield mock_generate_content


@pytest.mark.usefixtures('mock_generate_content_stream_multiple_chunks')
@pytest.mark.parametrize('disable_afc', [False, True])
def test_chat_stream_records_single_model_turn(mock_api_client, disable_afc):
  """A streamed response is recorded as one model turn holding every part."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  chunks = list(
      chat.send_message_stream('Hello', config=_stream_config(disable_afc))
  )

  assert len(chunks) == 3
  expected = [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          role='model',
          parts=[_STREAM_PART_1, _STREAM_PART_2, _STREAM_PART_3],
      ),
  ]
  assert chat.get_history() == expected
  assert chat.get_history(curated=True) == expected
  assert [c.candidates[0].content.parts for c in chunks] == [
      [_STREAM_PART_1],
      [_STREAM_PART_2],
      [_STREAM_PART_3],
  ]


def test_chat_stream_sends_single_model_turn_in_next_request(
    mock_api_client,
):
  """The next request carries the previous streamed reply as one content."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')
  turn2_part = types.Part(text='Second reply.')

  with mock.patch.object(
      models.Models,
      'generate_content_stream',
      side_effect=[
          _stream_chunks([_STREAM_PART_1, _STREAM_PART_2, _STREAM_PART_3]),
          _stream_chunks([turn2_part]),
      ],
  ) as mock_stream:
    list(chat.send_message_stream('Hello'))
    list(chat.send_message_stream('Again'))

  assert mock_stream.call_args_list[1].kwargs['contents'] == [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          role='model',
          parts=[_STREAM_PART_1, _STREAM_PART_2, _STREAM_PART_3],
      ),
      types.UserContent(parts=[types.Part.from_text(text='Again')]),
  ]


def test_chat_stream_invalid_chunk_excludes_merged_turn(mock_api_client):
  """An invalid chunk keeps the merged turn out of the curated history."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  with mock.patch.object(
      models.Models,
      'generate_content_stream',
      return_value=_stream_chunks([_STREAM_PART_2, types.Part()]),
  ):
    list(chat.send_message_stream('Hello'))

  assert chat.get_history() == [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(role='model', parts=[_STREAM_PART_2, types.Part()]),
  ]
  assert not chat.get_history(curated=True)


@pytest.mark.asyncio
@pytest.mark.parametrize('disable_afc', [False, True])
async def test_async_chat_stream_records_single_model_turn(
    mock_api_client, disable_afc
):
  """An async streamed response is recorded as one model turn."""
  models_module = models.AsyncModels(mock_api_client)
  chats_module = chats.AsyncChats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-flash')

  async def _async_stream():
    for chunk in _stream_chunks(
        [_STREAM_PART_1, _STREAM_PART_2, _STREAM_PART_3]
    ):
      yield chunk

  with mock.patch.object(
      models.AsyncModels,
      'generate_content_stream',
      new_callable=mock.AsyncMock,
      return_value=_async_stream(),
  ):
    chunks = [
        chunk
        async for chunk in await chat.send_message_stream(
            'Hello', config=_stream_config(disable_afc)
        )
    ]

  assert len(chunks) == 3
  expected = [
      types.UserContent(parts=[types.Part.from_text(text='Hello')]),
      types.Content(
          role='model',
          parts=[_STREAM_PART_1, _STREAM_PART_2, _STREAM_PART_3],
      ),
  ]
  assert chat.get_history() == expected
  assert chat.get_history(curated=True) == expected
