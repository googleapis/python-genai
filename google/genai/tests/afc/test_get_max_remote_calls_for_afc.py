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


"""Tests for the max remote calls budget for AFC.

Covers both reading it off the config, and what the AFC loop does once it is
spent.
"""

from unittest import mock
import pytest
from ... import _api_client
from ... import _extra_utils
from ... import chats
from ... import models
from ... import types
from ..._extra_utils import get_max_remote_calls_afc


def test_config_is_none():
  assert get_max_remote_calls_afc(None) == 10


def test_afc_unset_max_unset():
  assert get_max_remote_calls_afc(types.GenerateContentConfig()) == 10


def test_afc_unset_max_set():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  maximum_remote_calls=20,
              ),
          )
      )
      == 20
  )


def test_afc_disabled_max_unset():
  with pytest.raises(ValueError):
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=True,
              ),
          )
      )


def test_afc_disabled_max_set():
  with pytest.raises(ValueError):
    get_max_remote_calls_afc(
        types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True,
                maximum_remote_calls=20,
            ),
        )
    )


def test_afc_d_max_unset():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=False,
              ),
          )
      )
      == 10
  )


def test_afc_d_max_set():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=False,
                  maximum_remote_calls=5,
              ),
          )
      )
      == 5
  )


def test_afc_enabled_max_set_to_zero():
  with pytest.raises(ValueError):
    get_max_remote_calls_afc(
        types.GenerateContentConfig(
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=0,
            ),
        )
    )


def test_afc_enabled_max_set_to_negative():
  with pytest.raises(ValueError):
    get_max_remote_calls_afc(
        types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=-1,
            ),
        )
    )


def test_afc_enabled_max_set_to_float():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=False,
                  maximum_remote_calls=5.0,
              ),
          )
      )
      == 5
  )


TEST_FUNCTION_CALL_CONTENT = types.Content(
    parts=[
        types.Part(
            function_call=types.FunctionCall(
                name='get_current_weather',
                args={'location': 'San Francisco'},
            )
        )
    ],
    role='model',
)


TEST_FUNCTION_RESPONSE_PART = types.Part(
    function_response=types.FunctionResponse(
        name='get_current_weather',
        response={'result': 'sunny'},
    )
)


def get_current_weather(location: str) -> str:
  """Returns the current weather.

  Args:
    location: The city and State, e.g. San Francisco, CA.
  """
  return 'sunny'


@pytest.fixture
def mock_api_client():
  api_client = mock.MagicMock(spec=_api_client.BaseApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}
  api_client.vertexai = False
  # BaseApiClient assigns these in __init__, so they are not part of the spec
  # and a mock would raise AttributeError on them. The private SDK's
  # generate_content reads both to decide whether the request goes over a
  # secure session; None sends it down the ordinary path.
  api_client._ws_connection = None
  api_client.tls_connection = None
  return api_client


def _afc_config(maximum_remote_calls: int) -> types.GenerateContentConfig:
  return types.GenerateContentConfig(
      tools=[get_current_weather],
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          maximum_remote_calls=maximum_remote_calls
      ),
  )


def test_generate_content_spent_budget_does_not_run_functions(mock_api_client):
  """The one allowed request is spent asking, so nothing is run."""
  with mock.patch.object(
      models.Models, '_generate_content'
  ) as mock_generate_content, mock.patch.object(
      _extra_utils, 'get_function_response_parts'
  ) as mock_get_function_response_parts:
    mock_generate_content.return_value = types.GenerateContentResponse(
        candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
    )

    response = models.Models(api_client_=mock_api_client).generate_content(
        model='test_model',
        contents='what is the weather in San Francisco?',
        config=_afc_config(1),
    )

  assert mock_generate_content.call_count == 1
  # The result could not have been delivered, so the function is never called.
  mock_get_function_response_parts.assert_not_called()
  assert response.candidates[0].content.parts[0].function_call


def test_generate_content_stream_spent_budget_does_not_run_functions(
    mock_api_client,
):
  """The same over a stream: chunks are yielded, nothing is run."""
  with mock.patch.object(
      models.Models, '_generate_content_stream'
  ) as mock_generate_content_stream, mock.patch.object(
      _extra_utils, 'get_function_response_parts'
  ) as mock_get_function_response_parts:
    mock_generate_content_stream.return_value = [
        types.GenerateContentResponse(
            candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
        )
    ]

    chunks = list(
        models.Models(api_client_=mock_api_client).generate_content_stream(
            model='test_model',
            contents='what is the weather in San Francisco?',
            config=_afc_config(1),
        )
    )

  assert mock_generate_content_stream.call_count == 1
  mock_get_function_response_parts.assert_not_called()
  assert chunks[0].candidates[0].content.parts[0].function_call


def test_send_message_spent_budget_records_the_turn_once(mock_api_client):
  """The turn is recorded once, as the message and the unanswered call."""
  with mock.patch.object(
      models.Models, '_generate_content'
  ) as mock_generate_content, mock.patch.object(
      _extra_utils, 'get_function_response_parts'
  ) as mock_get_function_response_parts:
    mock_generate_content.return_value = types.GenerateContentResponse(
        candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
    )

    chat = chats.Chats(models.Models(api_client_=mock_api_client)).create(
        model='test_model', config=_afc_config(1)
    )
    chat.send_message('what is the weather in San Francisco?')
    history = chat.get_history()

  mock_get_function_response_parts.assert_not_called()
  # The model's function call is recorded once, not twice, and the history is
  # left ready for the caller to answer that call themselves.
  assert [content.role for content in history] == ['user', 'model']
  assert history[1].parts[0].function_call


def test_send_message_budget_of_two_answers_the_call(mock_api_client):
  """A budget of two is the smallest that lets the model answer."""
  with mock.patch.object(
      models.Models, '_generate_content'
  ) as mock_generate_content:
    mock_generate_content.side_effect = [
        types.GenerateContentResponse(
            candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
        ),
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        parts=[types.Part(text='It is sunny.')], role='model'
                    )
                )
            ]
        ),
    ]

    chat = chats.Chats(models.Models(api_client_=mock_api_client)).create(
        model='test_model', config=_afc_config(2)
    )
    response = chat.send_message('what is the weather in San Francisco?')
    history = chat.get_history()

  assert response.text == 'It is sunny.'
  assert [content.role for content in history] == [
      'user',
      'model',
      'user',
      'model',
  ]
  assert history[2].parts[0].function_response


def test_spent_budget_leaves_the_afc_history_empty(mock_api_client):
  """Nothing ran, so automatic function calling added no turns to report."""
  with mock.patch.object(
      models.Models, '_generate_content'
  ) as mock_generate_content, mock.patch.object(
      _extra_utils, 'get_function_response_parts'
  ):
    mock_generate_content.return_value = types.GenerateContentResponse(
        candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
    )

    response = models.Models(api_client_=mock_api_client).generate_content(
        model='test_model',
        contents='what is the weather in San Francisco?',
        config=_afc_config(1),
    )

  assert not response.automatic_function_calling_history


def test_afc_history_holds_the_rounds_that_completed(mock_api_client):
  """A round that was delivered is reported; the budget stops after it."""
  with mock.patch.object(
      models.Models, '_generate_content'
  ) as mock_generate_content, mock.patch.object(
      _extra_utils, 'get_function_response_parts'
  ) as mock_get_function_response_parts:
    mock_generate_content.side_effect = [
        types.GenerateContentResponse(
            candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
        ),
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        parts=[types.Part(text='It is sunny.')], role='model'
                    )
                )
            ]
        ),
    ]
    mock_get_function_response_parts.return_value = [
        TEST_FUNCTION_RESPONSE_PART
    ]

    response = models.Models(api_client_=mock_api_client).generate_content(
        model='test_model',
        contents='what is the weather in San Francisco?',
        config=_afc_config(2),
    )

  history = response.automatic_function_calling_history
  assert [content.role for content in history] == ['user', 'model', 'user']
  assert history[1].parts[0].function_call
  assert history[2].parts[0].function_response
