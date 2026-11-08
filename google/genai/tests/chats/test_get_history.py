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


def get_weather(city: str) -> dict[str, int]:
  """Returns the weather for a city."""
  del city  # Unused.
  return {'c': 21}


_AFC_CONFIG = types.GenerateContentConfig(tools=[get_weather])

_PRIOR_VALID_TURN = [
    types.Content(role='user', parts=[types.Part.from_text(text='hi')]),
    types.Content(role='model', parts=[types.Part.from_text(text='hello')]),
]


def _function_call_content() -> types.Content:
  return types.Content(
      role='model',
      parts=[
          types.Part.from_function_call(
              name='get_weather', args={'city': 'Paris'}
          )
      ],
  )


def _function_response_content() -> types.Content:
  return types.Content(
      role='user',
      parts=[
          types.Part.from_function_response(
              name='get_weather', response={'result': {'c': 21}}
          )
      ],
  )


def _call_response() -> types.GenerateContentResponse:
  return types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=_function_call_content(),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )


def _blocked_response() -> types.GenerateContentResponse:
  return types.GenerateContentResponse(
      candidates=[types.Candidate(finish_reason=types.FinishReason.SAFETY)]
  )


def _text_response(text: str) -> types.GenerateContentResponse:
  return types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part.from_text(text=text)]
              ),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )


def _user_text(text: str) -> types.Content:
  return types.UserContent(parts=[types.Part.from_text(text=text)])


_EMPTY_MODEL_CONTENT = types.Content(role='model', parts=[])


def test_chat_afc_invalid_final_turn_drops_exchange(mock_api_client):
  """A rejected final AFC answer drops the exchange from later requests."""
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', config=_AFC_CONFIG
  )
  with mock.patch.object(
      models.Models,
      'generate_content',
      side_effect=[_call_response(), _blocked_response(), _text_response('ok')],
  ) as mock_generate_content:
    chat.send_message('what is the weather in Paris')

    assert chat.get_history() == [
        _user_text('what is the weather in Paris'),
        _function_call_content(),
        _function_response_content(),
        _EMPTY_MODEL_CONTENT,
    ]
    assert not chat.get_history(curated=True)

    chat.send_message('try again')
    assert mock_generate_content.call_args_list[2].kwargs['contents'] == [
        _user_text('try again')
    ]


def test_chat_afc_invalid_final_turn_keeps_earlier_turns(mock_api_client):
  """Dropping a rejected AFC exchange keeps the valid turns before it."""
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', config=_AFC_CONFIG, history=_PRIOR_VALID_TURN
  )
  with mock.patch.object(
      models.Models,
      'generate_content',
      side_effect=[_call_response(), _blocked_response()],
  ):
    chat.send_message('what is the weather in Paris')

  assert chat.get_history(curated=True) == _PRIOR_VALID_TURN
  assert len(chat.get_history()) == 6


def test_chat_afc_invalid_final_turn_after_two_calls_drops_exchange(
    mock_api_client,
):
  """Every function call and response of a rejected exchange is dropped."""
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', config=_AFC_CONFIG
  )
  with mock.patch.object(
      models.Models,
      'generate_content',
      side_effect=[_call_response(), _call_response(), _blocked_response()],
  ):
    chat.send_message('what is the weather in Paris')

  assert len(chat.get_history()) == 6
  assert not chat.get_history(curated=True)


def test_chat_stream_afc_invalid_final_turn_drops_exchange(mock_api_client):
  """The streaming AFC path drops the exchange when the final stream is empty."""
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', config=_AFC_CONFIG
  )
  with mock.patch.object(
      models.Models,
      'generate_content_stream',
      side_effect=[
          iter([_call_response()]),
          iter([types.GenerateContentResponse(candidates=[])]),
      ],
  ):
    for _ in chat.send_message_stream('what is the weather in Paris'):
      pass

  assert chat.get_history() == [
      _user_text('what is the weather in Paris'),
      _function_call_content(),
      _function_response_content(),
      _EMPTY_MODEL_CONTENT,
  ]
  assert not chat.get_history(curated=True)


@pytest.mark.asyncio
async def test_async_chat_afc_invalid_final_turn_drops_exchange(
    mock_api_client,
):
  """The async AFC path drops the exchange when the final answer is invalid."""
  chat = chats.AsyncChats(modules=models.AsyncModels(mock_api_client)).create(
      model='gemini-2.5-flash', config=_AFC_CONFIG
  )
  with mock.patch.object(
      models.AsyncModels,
      'generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[_call_response(), _blocked_response()],
  ):
    await chat.send_message('what is the weather in Paris')

  assert len(chat.get_history()) == 4
  assert not chat.get_history(curated=True)


@pytest.mark.asyncio
async def test_async_chat_stream_afc_invalid_final_turn_drops_exchange(
    mock_api_client,
):
  """The async streaming AFC path drops the exchange on an empty final stream."""

  async def call_stream():
    yield _call_response()

  async def empty_stream():
    yield types.GenerateContentResponse(candidates=[])

  chat = chats.AsyncChats(modules=models.AsyncModels(mock_api_client)).create(
      model='gemini-2.5-flash', config=_AFC_CONFIG
  )
  with mock.patch.object(
      models.AsyncModels,
      'generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[call_stream(), empty_stream()],
  ):
    async for _ in await chat.send_message_stream(
        'what is the weather in Paris'
    ):
      pass

  assert len(chat.get_history()) == 4
  assert not chat.get_history(curated=True)


def test_history_afc_invalid_final_turn_drops_exchange(mock_api_client):
  """A saved history with a rejected AFC exchange curates to the turns before."""
  history = _PRIOR_VALID_TURN + [
      _user_text('what is the weather in Paris'),
      _function_call_content(),
      _function_response_content(),
      _function_call_content(),
      _function_response_content(),
      _EMPTY_MODEL_CONTENT,
  ]
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', history=history
  )

  assert chat.get_history() == history
  assert chat.get_history(curated=True) == _PRIOR_VALID_TURN


def test_chat_afc_valid_final_turn_keeps_exchange(mock_api_client):
  """A valid AFC exchange stays in the curated history."""
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', config=_AFC_CONFIG
  )
  with mock.patch.object(
      models.Models,
      'generate_content',
      side_effect=[_call_response(), _text_response('21 degrees')],
  ):
    chat.send_message('what is the weather in Paris')

  assert chat.get_history(curated=True) == [
      _user_text('what is the weather in Paris'),
      _function_call_content(),
      _function_response_content(),
      _text_response('21 degrees').candidates[0].content,
  ]


def test_chat_afc_spent_budget_keeps_function_call(mock_api_client):
  """With no remote calls left, the unanswered function call is kept."""
  config = types.GenerateContentConfig(
      tools=[get_weather],
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          maximum_remote_calls=1
      ),
  )
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', config=config
  )
  with mock.patch.object(
      models.Models, 'generate_content', side_effect=[_call_response()]
  ):
    chat.send_message('what is the weather in Paris')

  assert chat.get_history(curated=True) == [
      _user_text('what is the weather in Paris'),
      _function_call_content(),
  ]


def test_history_spent_budget_tail_survives_rejected_next_turn(
    mock_api_client,
):
  """A rejected plain turn after a spent-budget tail drops only its input."""
  history = [
      _user_text('what is the weather in Paris'),
      _function_call_content(),
      _user_text('and in Rome?'),
      _EMPTY_MODEL_CONTENT,
  ]
  chat = chats.Chats(modules=models.Models(mock_api_client)).create(
      model='gemini-2.5-flash', history=history
  )

  assert chat.get_history(curated=True) == history[:2]
