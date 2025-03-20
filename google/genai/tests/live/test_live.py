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


"""Tests for live.py."""
import json
from typing import AsyncIterator
from unittest import mock
from unittest.mock import AsyncMock

import pytest
from websockets import client

from ... import _api_client as api_client
from ... import Client
from ... import client as gl_client
from ... import live
from ... import types


function_declarations = [{
    'name': 'get_current_weather',
    'description': 'Get the current weather in a city',
    'parameters': {
        'type': 'OBJECT',
        'properties': {
            'location': {
                'type': 'STRING',
                'description': 'The location to get the weather for',
            },
            'unit': {
                'type': 'STRING',
                'enum': ['C', 'F'],
            },
        },
    },
}]


def get_current_weather(location: str, unit: str):
  """Get the current weather in a city."""
  return 15 if unit == 'C' else 59


@pytest.fixture
def mock_api_client(vertexai=False):
  api_client = mock.MagicMock(spec=gl_client.BaseApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}  # Ensure headers exist
  api_client.vertexai = vertexai
  return api_client


@pytest.fixture
def mock_websocket():
  websocket = AsyncMock(spec=client.ClientConnection)
  websocket.send = AsyncMock()
  websocket.recv = AsyncMock(
      return_value='{"serverContent": {"turnComplete": true}}'
  )  # Default response
  websocket.close = AsyncMock()
  return websocket


async def _async_iterator_to_list(async_iter):
  return [value async for value in async_iter]


def test_mldev_from_env(monkeypatch):
  api_key = 'google_api_key'
  monkeypatch.setenv('GOOGLE_API_KEY', api_key)

  client = Client()

  assert not client.aio.live.api_client.vertexai
  assert client.aio.live.api_client.api_key == api_key
  assert isinstance(client.aio.live.api_client, api_client.BaseApiClient)


def test_vertex_from_env(monkeypatch):
  project_id = 'fake_project_id'
  location = 'fake-location'
  monkeypatch.setenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')
  monkeypatch.setenv('GOOGLE_CLOUD_PROJECT', project_id)
  monkeypatch.setenv('GOOGLE_CLOUD_LOCATION', location)

  client = Client()

  assert client.aio.live.api_client.vertexai
  assert client.aio.live.api_client.project == project_id
  assert isinstance(client.aio.live.api_client, api_client.BaseApiClient)


def test_websocket_base_url():
  base_url = 'https://test.com'
  api_client = gl_client.BaseApiClient(
      api_key='google_api_key',
      http_options={'base_url': base_url},
  )
  assert api_client._websocket_base_url() == 'wss://test.com'


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_text(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  await session.send(input='test')
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_content_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  client_content = {
      'content': [{'parts': [{'text': 'test'}]}],
      'turn_complete': True,
  }
  await session.send(input=client_content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_content(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  client_content = types.LiveClientContent(
      turns=[types.Content(parts=[types.Part(text='test')])], turn_complete=True
  )
  await session.send(input=client_content)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_bytes(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  realtime_input = {'data': b'000000', 'mime_type': 'audio/pcm'}

  await session.send(input=realtime_input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_blob(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  realtime_input = types.Blob(data=b'000000', mime_type='audio/pcm')

  await session.send(input=realtime_input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_realtime_input(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  realtime_input = types.LiveClientRealtimeInput(
      media_chunks=[types.Blob(data='MDAwMDAw', mime_type='audio/pcm')]
  )
  await session.send(input=realtime_input)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'realtime_input' in sent_data


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_tool_response(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  if vertexai:
    tool_response = types.LiveClientToolResponse(
        function_responses=[
            types.FunctionResponse(
                name='get_current_weather',
                response={'temperature': 14.5, 'unit': 'C'},
            )
        ]
    )
  else:
    tool_response = types.LiveClientToolResponse(
        function_responses=[
            types.FunctionResponse(
                name='get_current_weather',
                response={'temperature': 14.5, 'unit': 'C'},
                id='some-id',
            )
        ]
    )
  await session.send(input=tool_response)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'tool_response' in sent_data


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_input_none(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  await session.send(input=None)
  mock_websocket.send.assert_called_once()
  sent_data = json.loads(mock_websocket.send.call_args[0][0])
  assert 'client_content' in sent_data
  assert sent_data['client_content']['turn_complete']


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_send_error(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  with pytest.raises(ValueError):
    await session.send(input=[{'invalid_key': 'invalid_value'}])

  with pytest.raises(ValueError):
    await session.send(input={'invalid_key': 'invalid_value'})


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_receive(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  responses = session.receive()
  responses = await _async_iterator_to_list(responses)
  assert isinstance(responses[0], types.LiveServerMessage)


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_receive_error(
    mock_api_client, mock_websocket, vertexai
):
  mock_websocket.recv = AsyncMock(return_value='invalid json')
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  with pytest.raises(ValueError):
    await session.receive().__anext__()


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_receive_text(
    mock_api_client, mock_websocket, vertexai
):
  mock_websocket.recv = AsyncMock(
      side_effect=[
          '{"serverContent": {"modelTurn": {"parts":[{"text": "test"}]}}}',
          '{"serverContent": {"turnComplete": true}}',
      ]
  )
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  messages = session.receive()
  messages = await _async_iterator_to_list(messages)
  assert isinstance(messages[0], types.LiveServerMessage)
  assert messages[0].server_content.model_turn.parts[0].text == 'test'
  assert messages[1].server_content.turn_complete == True


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_receive_audio(
    mock_api_client, mock_websocket, vertexai
):
  mock_websocket.recv = AsyncMock(
      side_effect=[
          (
              '{"serverContent": {"modelTurn": {"parts":[{"inlineData":'
              ' {"data": "MDAwMDAw", "mime_type": "audio/pcm" }}]}}}'
          ),
          '{"serverContent": {"turnComplete": true}}',
      ]
  )
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  messages = session.receive()
  messages = await _async_iterator_to_list(messages)
  assert isinstance(messages[0], types.LiveServerMessage)
  assert (
      messages[0].server_content.model_turn.parts[0].inline_data.mime_type
      == 'audio/pcm'
  )
  assert (
      messages[0].server_content.model_turn.parts[0].inline_data.data
      == b'000000'
  )

  with pytest.raises(RuntimeError):
    await _async_iterator_to_list(session.receive())


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_receive_tool_call(
    mock_api_client, mock_websocket, vertexai
):
  mock_websocket.recv = AsyncMock(
      side_effect=[
          (
              '{"toolCall": {"functionCalls": [{"name":'
              ' "get_current_weather", "args": {"location": "San Francisco",'
              ' "unit": "C"}}]}}'
          ),
          '{"serverContent": {"turnComplete": true}}',
      ]
  )
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  messages = session.receive()
  messages = await _async_iterator_to_list(messages)
  assert isinstance(messages[0], types.LiveServerMessage)
  assert messages[0].tool_call.function_calls[0].name == 'get_current_weather'
  assert (
      messages[0].tool_call.function_calls[0].args['location']
      == 'San Francisco'
  )
  assert messages[0].tool_call.function_calls[0].args['unit'] == 'C'

  with pytest.raises(RuntimeError):
    await _async_iterator_to_list(session.receive())


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_start_stream(
    mock_api_client, mock_websocket, vertexai
):

  session = live.AsyncSession(
      mock_api_client(vertexai=vertexai), mock_websocket
  )

  async def mock_stream():
    yield b'data1'
    yield b'data2'

  async for message in session.start_stream(
      stream=mock_stream(), mime_type='audio/pcm'
  ):
    assert isinstance(message, types.LiveServerMessage)


@pytest.mark.parametrize('vertexai', [True, False])
@pytest.mark.asyncio
async def test_async_session_close(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      mock_api_client(vertexai=vertexai), mock_websocket
  )
  await session.close()
  mock_websocket.close.assert_called_once()


def test_bidi_setup_to_api_no_config(mock_api_client):
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_mldev(
      model='test_model'
  )
  expected_result = {'setup': {'model': 'test_model'}}
  assert result == expected_result

  result = live.AsyncLive(mock_api_client())._LiveSetup_to_vertex(
      model='test_model'
  )
  expected_result = {
      'setup': {
          'model': 'test_model',
          'generationConfig': {'responseModalities': ['AUDIO']},
      }
  }
  assert result == expected_result


def test_bidi_setup_to_api_speech_config(mock_api_client):

  expected_result = {
      'setup': {
          'model': 'test_model',
          'generationConfig': {
              'speechConfig': {
                  'voiceConfig': {
                      'prebuiltVoiceConfig': {'voiceName': 'en-default'}
                  }
              }
          },
      }
  }
  config_dict = {'speech_config': 'en-default'}
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_mldev(
      model='test_model', config=config_dict
  )
  assert result == expected_result

  config = types.LiveConnectConfig(
      speech_config=types.SpeechConfig(
          voice_config=types.VoiceConfig(
              prebuilt_voice_config=types.PrebuiltVoiceConfig(
                  voice_name='en-default'
              )
          )
      )
  )
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_mldev(
      model='test_model', config=config
  )
  assert result == expected_result
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_vertex(
      model='test_model', config=config
  )
  expected_result['setup']['generationConfig'].update(
      {'responseModalities': ['AUDIO']}
  )
  assert result == expected_result


def test_bidi_setup_to_api_with_config_tools_google_search_retrieval(
    mock_api_client,
):
  config = types.LiveConnectConfig(
      generation_config=types.GenerationConfig(temperature=0.7),
      response_modalities=['TEXT'],
      system_instruction=types.Content(
          parts=[types.Part(text='test instruction')], role='user'
      ),
      tools=[types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())],
  )
  expected_result = {
      'setup': {
          'model': 'test_model',
          'generationConfig': {
              'temperature': 0.7,
              'responseModalities': ['TEXT'],
          },
          'systemInstruction': {
              'parts': [{'text': 'test instruction'}],
              'role': 'user',
          },
          'tools': [{'googleSearchRetrieval': {}}],
      }
  }
  # Test for mldev, config is a LiveConnectConfig
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_mldev(
      model='test_model', config=config
  )
  assert result == expected_result

  # Test for vertex, config is a LiveConnectConfig
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_vertex(
      model='test_model', config=config
  )
  assert result == expected_result


def test_bidi_setup_to_api_with_config_tools_function_declaration(
    mock_api_client,
):
  config_dict = {
      'generation_config': {'temperature': 0.7},
      'tools': [{'function_declarations': function_declarations}],
  }
  config = types.LiveConnectConfig(**config_dict)
  expected_result = {
      'setup': {
          'model': 'test_model',
          'tools': [{
              'functionDeclarations': [{
                  'parameters': {
                      'type': 'OBJECT',
                      'properties': {
                          'location': {
                              'type': 'STRING',
                              'description': (
                                  'The location to get the weather for'
                              ),
                          },
                          'unit': {'type': 'STRING', 'enum': ['C', 'F']},
                      },
                  },
                  'name': 'get_current_weather',
                  'description': 'Get the current weather in a city',
              }],
          }],
      }
  }
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_mldev(
      model='test_model', config=config
  )

  assert result['setup']['tools'][0]['functionDeclarations'][0][
      'description'
  ] == (
      expected_result['setup']['tools'][0]['functionDeclarations'][0][
          'description'
      ]
  )

  result = live.AsyncLive(mock_api_client())._LiveSetup_to_vertex(
      model='test_model', config=config
  )
  assert result['setup']['tools'][0]['functionDeclarations'][0][
      'description'
  ] == (
      expected_result['setup']['tools'][0]['functionDeclarations'][0][
          'description'
      ]
  )


def test_bidi_setup_to_api_with_config_tools_function_directly(
    mock_api_client,
):
  config_dict = {
      'generation_config': {'temperature': 0.7},
      'tools': [get_current_weather],
  }
  config = types.LiveConnectConfig(**config_dict)
  expected_result = {
      'setup': {
          'model': 'test_model',
          'tools': [{
              'functionDeclarations': [{
                  'parameters': {
                      'type': 'OBJECT',
                      'properties': {
                          'location': {
                              'type': 'STRING',
                              'description': (
                                  'The location to get the weather for'
                              ),
                          },
                          'unit': {'type': 'STRING', 'enum': ['C', 'F']},
                      },
                  },
                  'name': 'get_current_weather',
                  'description': 'Get the current weather in a city.',
              }],
          }],
      }
  }
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_mldev(
      model='test_model', config=config
  )

  assert result['setup']['tools'][0]['functionDeclarations'][0][
      'description'
  ] == (
      expected_result['setup']['tools'][0]['functionDeclarations'][0][
          'description'
      ]
  )

  result = live.AsyncLive(mock_api_client())._LiveSetup_to_vertex(
      model='test_model', config=config
  )
  assert result['setup']['tools'][0]['functionDeclarations'][0][
      'description'
  ] == (
      expected_result['setup']['tools'][0]['functionDeclarations'][0][
          'description'
      ]
  )


def test_bidi_setup_to_api_with_config_tools_code_execution(
    mock_api_client,
):
  config_dict = {
      'tools': [{'code_execution': {}}],
  }
  config = types.LiveConnectConfig(**config_dict)
  expected_result = {
      'setup': {
          'model': 'test_model',
          'tools': [{
              'codeExecution': types.ToolCodeExecution(),
          }],
      }
  }
  result = live.AsyncLive(mock_api_client())._LiveSetup_to_mldev(
      model='test_model', config=config
  )

  assert result['setup']['tools'][0] == expected_result['setup']['tools'][0]

  result = live.AsyncLive(mock_api_client())._LiveSetup_to_vertex(
      model='test_model', config=config
  )
  assert result['setup']['tools'][0] == expected_result['setup']['tools'][0]


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_str(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  result = session._parse_client_message('test')
  assert 'client_content' in result
  assert result == {
      'client_content': {
          'turn_complete': False,
          'turns': [{'role': 'user', 'parts': [{'text': 'test'}]}],
      }
  }
  # _parse_client_message returns a TypedDict, so we should be able to
  # construct a LiveClientMessage from it
  assert types.LiveClientMessage(**result)


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_blob(mock_api_client, mock_websocket, vertexai):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  result = session._parse_client_message(
      types.Blob(data=bytes([0, 0, 0]), mime_type='text/plain')
  )
  assert 'realtime_input' in result
  assert result == {
      'realtime_input': {
          'media_chunks': [{'mime_type': 'text/plain', 'data': 'AAAA'}],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_blob_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )

  blob = types.Blob(data=bytes([0, 0, 0]), mime_type='text/plain')
  blob_dict = blob.model_dump()
  result = session._parse_client_message(blob_dict)
  assert 'realtime_input' in result
  assert result == {
      'realtime_input': {
          'media_chunks': [{'mime_type': 'text/plain', 'data': 'AAAA'}],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_client_content(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  result = session._parse_client_message(
      types.LiveClientContent(
          turn_complete=False,
          turns=[types.Content(parts=[types.Part(text='test')], role='user')],
      )
  )
  assert 'client_content' in result
  assert result == {
      'client_content': {
          'turn_complete': False,
          'turns': [{'role': 'user', 'parts': [{'text': 'test'}]}],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_client_content_blob(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  client_content = types.LiveClientContent(
      turn_complete=False,
      turns=[
          types.Content(
              parts=[
                  types.Part(
                      inline_data=types.Blob(
                          data=bytes([0, 0, 0]), mime_type='text/plain'
                      )
                  )
              ],
              role='user',
          )
      ],
  )
  result = session._parse_client_message(client_content)
  assert 'client_content' in result
  assert (
      type(
          result['client_content']['turns'][0]['parts'][0]['inline_data'][
              'data'
          ]
      )
      == str
  )
  assert result == {
      'client_content': {
          'turn_complete': False,
          'turns': [{
              'role': 'user',
              'parts': [
                  {'inline_data': {'mime_type': 'text/plain', 'data': 'AAAA'}}
              ],
          }],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_client_content_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  client_content = types.LiveClientContent(
      turn_complete=False,
      turns=[
          types.Content(
              parts=[
                  types.Part(
                      inline_data=types.Blob(
                          data=bytes([0, 0, 0]), mime_type='text/plain'
                      )
                  )
              ],
              role='user',
          )
      ],
  )
  result = session._parse_client_message(
      client_content.model_dump(mode='json', exclude_none=True)
  )
  assert 'client_content' in result
  assert (
      type(
          result['client_content']['turns'][0]['parts'][0]['inline_data'][
              'data'
          ]
      )
      == str
  )
  assert result == {
      'client_content': {
          'turn_complete': False,
          'turns': [{
              'role': 'user',
              'parts': [
                  {'inline_data': {'mime_type': 'text/plain', 'data': 'AAAA'}}
              ],
          }],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_realtime_input(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.LiveClientRealtimeInput(
      media_chunks=[types.Blob(data=bytes([0, 0, 0]), mime_type='text/plain')]
  )
  result = session._parse_client_message(input)
  assert 'realtime_input' in result
  assert result == {
      'realtime_input': {
          'media_chunks': [{'mime_type': 'text/plain', 'data': 'AAAA'}],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_realtime_input_dict(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.LiveClientRealtimeInput(
      media_chunks=[types.Blob(data=bytes([0, 0, 0]), mime_type='text/plain')]
  )
  result = session._parse_client_message(
      input.model_dump(mode='json', exclude_none=True)
  )
  assert 'realtime_input' in result
  assert result == {
      'realtime_input': {
          'media_chunks': [{'mime_type': 'text/plain', 'data': 'AAAA'}],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_tool_response(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.LiveClientToolResponse(
      function_responses=[
          types.FunctionResponse(
              id='test_id',
              name='test_name',
              response={'result': 'test_response'},
          )
      ]
  )
  result = session._parse_client_message(input)
  assert 'tool_response' in result
  assert result == {
      'tool_response': {
          'function_responses': [
              {
                  'id': 'test_id',
                  'name': 'test_name',
                  'response': {
                      'result': 'test_response',
                  },
              },
          ],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_function_response(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.FunctionResponse(
    id='test_id',
    name='test_name',
    response={'result': 'test_response'},
  )
  result = session._parse_client_message(input)
  assert 'tool_response' in result
  assert result == {
      'tool_response': {
          'function_responses': [
              {
                  'id': 'test_id',
                  'name': 'test_name',
                  'response': {
                      'result': 'test_response',
                  },
              },
          ],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_tool_response_dict_with_only_response(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = {
    'id': 'test_id',
    'name': 'test_name',
    'response': {
        'result': 'test_response',
    }
  }
  result = session._parse_client_message(input)
  assert 'tool_response' in result
  assert result == {
      'tool_response': {
          'function_responses': [
              {
                  'id': 'test_id',
                  'name': 'test_name',
                  'response': {
                      'result': 'test_response',
                  },
              },
          ],
      }
  }


@pytest.mark.parametrize('vertexai', [True, False])
def test_parse_client_message_realtime_tool_response(
    mock_api_client, mock_websocket, vertexai
):
  session = live.AsyncSession(
      api_client=mock_api_client(vertexai=vertexai), websocket=mock_websocket
  )
  input = types.LiveClientToolResponse(
      function_responses=[
          types.FunctionResponse(
              id='test_id',
              name='test_name',
              response={'result': 'test_response'},
          )
      ]
  )

  result = session._parse_client_message(
      input.model_dump(mode='json', exclude_none=True)
  )
  assert 'tool_response' in result
  assert result == {
      'tool_response': {
          'function_responses': [
              {
                  'id': 'test_id',
                  'name': 'test_name',
                  'response': {
                      'result': 'test_response',
                  },
              },
          ],
      }
  }
