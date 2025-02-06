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

"""Live client. The live module is experimental."""

import asyncio
import base64
import contextlib
import json
import logging
from typing import AsyncIterator, Optional, Sequence, Union

import google.auth
from websockets import ConnectionClosed

from . import _api_module
from . import _common
from . import _transformers as t
from . import client
from . import errors
from . import types
from ._api_client import ApiClient
from ._common import experimental_warning
from ._common import get_value_by_path as getv
from ._common import set_value_by_path as setv
from .models import _Content_from_mldev
from .models import _Content_from_vertex
from .models import _Content_to_mldev
from .models import _Content_to_vertex
from .models import _GenerateContentConfig_to_mldev
from .models import _GenerateContentConfig_to_vertex
from .models import _SafetySetting_to_mldev
from .models import _SafetySetting_to_vertex
from .models import _SpeechConfig_to_mldev
from .models import _SpeechConfig_to_vertex
from .models import _Tool_to_mldev
from .models import _Tool_to_vertex

try:
  from websockets.asyncio.client import ClientConnection
  from websockets.asyncio.client import connect
except ModuleNotFoundError:
  from websockets.client import ClientConnection
  from websockets.client import connect


_FUNCTION_RESPONSE_REQUIRES_ID = (
    'FunctionResponse request must have an `id` field from the'
    ' response of a ToolCall.FunctionalCalls in Google AI.'
)


class AsyncSession:
  """AsyncSession. The live module is experimental."""

  def __init__(self, api_client: client.ApiClient, websocket: ClientConnection):
    self._api_client = api_client
    self._ws = websocket

  async def send(
      self,
      *,
      input: Union[
          types.ContentListUnion,
          types.ContentListUnionDict,
          types.LiveClientContentOrDict,
          types.LiveClientRealtimeInputOrDict,
          types.LiveClientToolResponseOrDict,
          types.FunctionResponseOrDict,
          Sequence[types.FunctionResponseOrDict],
      ],
      end_of_turn: Optional[bool] = False,
  ):
    """Send input to the model.

    The method will send the input request to the server.

    Args:
      input: The input request to the model.
      end_of_turn: Whether the input is the last message in a turn.

    Example usage:

    .. code-block:: python

      client = genai.Client(api_key=API_KEY)

      async with client.aio.live.connect(model='...') as session:
        await session.send(input='Hello world!', end_of_turn=True)
        async for message in session.receive():
          print(message)
    """
    client_message = self._parse_client_message(input, end_of_turn)
    await self._ws.send(json.dumps(client_message))

  async def receive(self) -> AsyncIterator[types.LiveServerMessage]:
    """Receive model responses from the server.

    The method will yield the model responses from the server. The returned
    responses will represent a complete model turn. When the returned message
    is function call, user must call `send` with the function response to
    continue the turn.

    The live module is experimental.

    Yields:
      The model responses from the server.

    Example usage:

    .. code-block:: python

      client = genai.Client(api_key=API_KEY)

      async with client.aio.live.connect(model='...') as session:
        await session.send(input='Hello world!', end_of_turn=True)
        async for message in session.receive():
          print(message)
    """
    # TODO(b/365983264) Handle intermittent issues for the user.
    while result := await self._receive():
      if result.server_content and result.server_content.turn_complete:
        yield result
        break
      yield result

  async def start_stream(
      self, *, stream: AsyncIterator[bytes], mime_type: str
  ) -> AsyncIterator[types.LiveServerMessage]:
    """start a live session from a data stream.

    The interaction terminates when the input stream is complete.
    This method will start two async tasks. One task will be used to send the
    input stream to the model and the other task will be used to receive the
    responses from the model.

    The live module is experimental.

    Args:
      stream: An iterator that yields the model response.
      mime_type: The MIME type of the data in the stream.

    Yields:
      The audio bytes received from the model and server response messages.

    Example usage:

    .. code-block:: python

      client = genai.Client(api_key=API_KEY)
      config = {'response_modalities': ['AUDIO']}
      async def audio_stream():
        stream = read_audio()
        for data in stream:
          yield data
      async with client.aio.live.connect(model='...') as session:
        for audio in session.start_stream(stream = audio_stream(),
        mime_type = 'audio/pcm'):
          play_audio_chunk(audio.data)
    """
    stop_event = asyncio.Event()
    # Start the send loop. When stream is complete stop_event is set.
    asyncio.create_task(self._send_loop(stream, mime_type, stop_event))
    recv_task = None
    while not stop_event.is_set():
      try:
        recv_task = asyncio.create_task(self._receive())
        await asyncio.wait(
            [
                recv_task,
                asyncio.create_task(stop_event.wait()),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        if recv_task.done():
          yield recv_task.result()
          # Give a chance for the send loop to process requests.
          await asyncio.sleep(10**-12)
      except ConnectionClosed:
        break
    if recv_task is not None and not recv_task.done():
      recv_task.cancel()
      # Wait for the task to finish (cancelled or not)
      try:
        await recv_task
      except asyncio.CancelledError:
        pass

  async def _receive(self) -> types.LiveServerMessage:
    parameter_model = types.LiveServerMessage()
    raw_response = await self._ws.recv(decode=False)
    if raw_response:
      try:
        response = json.loads(raw_response)
      except json.decoder.JSONDecodeError:
        raise ValueError(f'Failed to parse response: {raw_response}')
    else:
      response = {}
    if self._api_client.vertexai:
      response_dict = self._LiveServerMessage_from_vertex(response)
    else:
      response_dict = self._LiveServerMessage_from_mldev(response)

    return types.LiveServerMessage._from_response(
        response_dict, parameter_model
    )

  async def _send_loop(
      self,
      data_stream: AsyncIterator[bytes],
      mime_type: str,
      stop_event: asyncio.Event,
  ):
    async for data in data_stream:
      input = {'data': data, 'mimeType': mime_type}
      await self.send(input=input)
      # Give a chance for the receive loop to process responses.
      await asyncio.sleep(10**-12)
    # Give a chance for the receiver to process the last response.
    stop_event.set()

  def _LiveServerContent_from_mldev(
      self,
      from_object: Union[dict, object],
  ) -> dict:
    to_object = {}
    if getv(from_object, ['modelTurn']) is not None:
      setv(
          to_object,
          ['model_turn'],
          _Content_from_mldev(
              self._api_client,
              getv(from_object, ['modelTurn']),
          ),
      )
    if getv(from_object, ['turnComplete']) is not None:
      setv(to_object, ['turn_complete'], getv(from_object, ['turnComplete']))
    if getv(from_object, ['interrupted']) is not None:
      setv(to_object, ['interrupted'], getv(from_object, ['interrupted']))
    return to_object

  def _LiveToolCall_from_mldev(
      self,
      from_object: Union[dict, object],
  ) -> dict:
    to_object = {}
    if getv(from_object, ['functionCalls']) is not None:
      setv(
          to_object,
          ['function_calls'],
          getv(from_object, ['functionCalls']),
      )
    return to_object

  def _LiveToolCall_from_vertex(
      self,
      from_object: Union[dict, object],
  ) -> dict:
    to_object = {}
    if getv(from_object, ['functionCalls']) is not None:
      setv(
          to_object,
          ['function_calls'],
          getv(from_object, ['functionCalls']),
      )
    return to_object

  def _LiveServerMessage_from_mldev(
      self,
      from_object: Union[dict, object],
  ) -> dict:
    to_object = {}
    if getv(from_object, ['serverContent']) is not None:
      setv(
          to_object,
          ['server_content'],
          self._LiveServerContent_from_mldev(
              getv(from_object, ['serverContent'])
          ),
      )
    if getv(from_object, ['toolCall']) is not None:
      setv(
          to_object,
          ['tool_call'],
          self._LiveToolCall_from_mldev(getv(from_object, ['toolCall'])),
      )
    if getv(from_object, ['toolCallCancellation']) is not None:
      setv(
          to_object,
          ['tool_call_cancellation'],
          getv(from_object, ['toolCallCancellation']),
      )
    return to_object

  def _LiveServerContent_from_vertex(
      self,
      from_object: Union[dict, object],
  ) -> dict:
    to_object = {}
    if getv(from_object, ['modelTurn']) is not None:
      setv(
          to_object,
          ['model_turn'],
          _Content_from_vertex(
              self._api_client,
              getv(from_object, ['modelTurn']),
          ),
      )
    if getv(from_object, ['turnComplete']) is not None:
      setv(to_object, ['turn_complete'], getv(from_object, ['turnComplete']))
    if getv(from_object, ['interrupted']) is not None:
      setv(to_object, ['interrupted'], getv(from_object, ['interrupted']))
    return to_object

  def _LiveServerMessage_from_vertex(
      self,
      from_object: Union[dict, object],
  ) -> dict:
    to_object = {}
    if getv(from_object, ['serverContent']) is not None:
      setv(
          to_object,
          ['server_content'],
          self._LiveServerContent_from_vertex(
              getv(from_object, ['serverContent'])
          ),
      )

    if getv(from_object, ['toolCall']) is not None:
      setv(
          to_object,
          ['tool_call'],
          self._LiveToolCall_from_vertex(getv(from_object, ['toolCall'])),
      )
    if getv(from_object, ['toolCallCancellation']) is not None:
      setv(
          to_object,
          ['tool_call_cancellation'],
          getv(from_object, ['toolCallCancellation']),
      )
    return to_object

  def _parse_client_message(
      self,
      input: Union[
          types.ContentListUnion,
          types.ContentListUnionDict,
          types.LiveClientContentOrDict,
          types.LiveClientRealtimeInputOrDict,
          types.LiveClientRealtimeInputOrDict,
          types.LiveClientToolResponseOrDict,
          types.FunctionResponseOrDict,
          Sequence[types.FunctionResponseOrDict],
      ],
      end_of_turn: Optional[bool] = False,
  ) -> dict:
    if isinstance(input, str):
      input = [input]
    elif isinstance(input, dict) and 'data' in input:
      if isinstance(input['data'], bytes):
        decoded_data = base64.b64encode(input['data']).decode('utf-8')
        input['data'] = decoded_data
      input = [input]
    elif isinstance(input, types.Blob):
      input.data = base64.b64encode(input.data).decode('utf-8')
      input = [input]
    elif isinstance(input, dict) and 'name' in input and 'response' in input:
      # ToolResponse.FunctionResponse
      if not (self._api_client.vertexai) and 'id' not in input:
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      input = [input]

    if isinstance(input, Sequence) and any(
        isinstance(c, dict) and 'name' in c and 'response' in c for c in input
    ):
      # ToolResponse.FunctionResponse
      if not (self._api_client.vertexai):
        for item in input:
          if 'id' not in item:
            raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      client_message = {'tool_response': {'function_responses': input}}
    elif isinstance(input, Sequence) and any(isinstance(c, str) for c in input):
      to_object = {}
      if self._api_client.vertexai:
        contents = [
            _Content_to_vertex(self._api_client, item, to_object)
            for item in t.t_contents(self._api_client, input)
        ]
      else:
        contents = [
            _Content_to_mldev(self._api_client, item, to_object)
            for item in t.t_contents(self._api_client, input)
        ]

      client_message = {
          'client_content': {'turns': contents, 'turn_complete': end_of_turn}
      }
    elif isinstance(input, Sequence):
      if any((isinstance(b, dict) and 'data' in b) for b in input):
        pass
      elif any(isinstance(b, types.Blob) for b in input):
        input = [b.model_dump(exclude_none=True) for b in input]
      else:
        raise ValueError(
            f'Unsupported input type "{type(input)}" or input content "{input}"'
        )

      client_message = {'realtime_input': {'media_chunks': input}}

    elif isinstance(input, dict) and 'content' in input:
      # TODO(b/365983264) Add validation checks for content_update input_dict.
      client_message = {'client_content': input}
    elif isinstance(input, types.LiveClientRealtimeInput):
      client_message = {'realtime_input': input.model_dump(exclude_none=True)}
      if isinstance(
          client_message['realtime_input']['media_chunks'][0]['data'], bytes
      ):
        client_message['realtime_input']['media_chunks'] = [
            {
                'data': base64.b64encode(item['data']).decode('utf-8'),
                'mime_type': item['mime_type'],
            }
            for item in client_message['realtime_input']['media_chunks']
        ]

    elif isinstance(input, types.LiveClientContent):
      client_message = {'client_content': input.model_dump(exclude_none=True)}
    elif isinstance(input, types.LiveClientToolResponse):
      # ToolResponse.FunctionResponse
      if not (self._api_client.vertexai) and not (
          input.function_responses[0].id
      ):
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      client_message = {'tool_response': input.model_dump(exclude_none=True)}
    elif isinstance(input, types.FunctionResponse):
      if not (self._api_client.vertexai) and not (input.id):
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      client_message = {
          'tool_response': {
              'function_responses': [input.model_dump(exclude_none=True)]
          }
      }
    elif isinstance(input, Sequence) and isinstance(
        input[0], types.FunctionResponse
    ):
      if not (self._api_client.vertexai) and not (input[0].id):
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      client_message = {
          'tool_response': {
              'function_responses': [
                  c.model_dump(exclude_none=True) for c in input
              ]
          }
      }
    else:
      raise ValueError(
          f'Unsupported input type "{type(input)}" or input content "{input}"'
      )

    return client_message

  async def close(self):
    # Close the websocket connection.
    await self._ws.close()


class AsyncLive(_api_module.BaseModule):
  """AsyncLive. The live module is experimental."""

  def _LiveSetup_to_mldev(
      self, model: str, config: Optional[types.LiveConnectConfigOrDict] = None
  ):
    if isinstance(config, types.LiveConnectConfig):
      from_object = config.model_dump(exclude_none=True)
    else:
      from_object = config

    to_object = {}
    if getv(from_object, ['generation_config']) is not None:
      setv(
          to_object,
          ['generationConfig'],
          _GenerateContentConfig_to_mldev(
              self._api_client,
              getv(from_object, ['generation_config']),
              to_object,
          ),
      )
    if getv(from_object, ['response_modalities']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['responseModalities'] = from_object[
            'response_modalities'
        ]
      else:
        to_object['generationConfig'] = {
            'responseModalities': from_object['response_modalities']
        }
    if getv(from_object, ['speech_config']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['speechConfig'] = _SpeechConfig_to_mldev(
            self._api_client,
            t.t_speech_config(
                self._api_client, getv(from_object, ['speech_config'])
            ),
            to_object,
        )
      else:
        to_object['generationConfig'] = {
            'speechConfig': _SpeechConfig_to_mldev(
                self._api_client,
                t.t_speech_config(
                    self._api_client, getv(from_object, ['speech_config'])
                ),
                to_object,
            )
        }

    if getv(from_object, ['system_instruction']) is not None:
      setv(
          to_object,
          ['systemInstruction'],
          _Content_to_mldev(
              self._api_client,
              t.t_content(
                  self._api_client, getv(from_object, ['system_instruction'])
              ),
              to_object,
          ),
      )
    if getv(from_object, ['tools']) is not None:
      setv(
          to_object,
          ['tools'],
          [
              _Tool_to_mldev(self._api_client, item, to_object)
              for item in getv(from_object, ['tools'])
          ],
      )

    return_value = {'setup': {'model': model}}
    return_value['setup'].update(to_object)
    return return_value

  def _LiveSetup_to_vertex(
      self, model: str, config: Optional[types.LiveConnectConfigOrDict] = None
  ):
    if isinstance(config, types.LiveConnectConfig):
      from_object = config.model_dump(exclude_none=True)
    else:
      from_object = config

    to_object = {}

    if getv(from_object, ['generation_config']) is not None:
      setv(
          to_object,
          ['generationConfig'],
          _GenerateContentConfig_to_vertex(
              self._api_client,
              getv(from_object, ['generation_config']),
              to_object,
          ),
      )
    if getv(from_object, ['response_modalities']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['responseModalities'] = from_object[
            'response_modalities'
        ]
      else:
        to_object['generationConfig'] = {
            'responseModalities': from_object['response_modalities']
        }
    else:
      # Set default to AUDIO to align with MLDev API.
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig'].update({'responseModalities': ['AUDIO']})
      else:
        to_object.update(
            {'generationConfig': {'responseModalities': ['AUDIO']}}
        )
    if getv(from_object, ['speech_config']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['speechConfig'] = _SpeechConfig_to_vertex(
            self._api_client,
            t.t_speech_config(
                self._api_client, getv(from_object, ['speech_config'])
            ),
            to_object,
        )
      else:
        to_object['generationConfig'] = {
            'speechConfig': _SpeechConfig_to_vertex(
                self._api_client,
                t.t_speech_config(
                    self._api_client, getv(from_object, ['speech_config'])
                ),
                to_object,
            )
        }
    if getv(from_object, ['system_instruction']) is not None:
      setv(
          to_object,
          ['systemInstruction'],
          _Content_to_vertex(
              self._api_client,
              t.t_content(
                  self._api_client, getv(from_object, ['system_instruction'])
              ),
              to_object,
          ),
      )
    if getv(from_object, ['tools']) is not None:
      setv(
          to_object,
          ['tools'],
          [
              _Tool_to_vertex(self._api_client, item, to_object)
              for item in getv(from_object, ['tools'])
          ],
      )

    return_value = {'setup': {'model': model}}
    return_value['setup'].update(to_object)
    return return_value

  @experimental_warning(
      "The live API is experimental and may change in future versions.",
  )
  @contextlib.asynccontextmanager
  async def connect(
      self,
      *,
      model: str,
      config: Optional[types.LiveConnectConfigOrDict] = None,
  ) -> AsyncSession:
    """Connect to the live server.

    The live module is experimental.

    Usage:

    .. code-block:: python

      client = genai.Client(api_key=API_KEY)
      config = {}
      async with client.aio.live.connect(model='...', config=config) as session:
        await session.send(input='Hello world!', end_of_turn=True)
        async for message in session.receive():
          print(message)
    """
    base_url = self._api_client._websocket_base_url()
    if self._api_client.api_key:
      api_key = self._api_client.api_key
      version = self._api_client._http_options['api_version']
      uri = f'{base_url}/ws/google.ai.generativelanguage.{version}.GenerativeService.BidiGenerateContent?key={api_key}'
      headers = self._api_client._http_options['headers']

      transformed_model = t.t_model(self._api_client, model)
      request = json.dumps(
          self._LiveSetup_to_mldev(model=transformed_model, config=config)
      )
    else:
      # Get bearer token through Application Default Credentials.
      creds, _ = google.auth.default(
          scopes=['https://www.googleapis.com/auth/cloud-platform']
      )

      # creds.valid is False, and creds.token is None
      # Need to refresh credentials to populate those
      auth_req = google.auth.transport.requests.Request()
      creds.refresh(auth_req)
      bearer_token = creds.token
      headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer {}'.format(bearer_token),
      }
      version = self._api_client._http_options['api_version']
      uri = f'{base_url}/ws/google.cloud.aiplatform.{version}.LlmBidiService/BidiGenerateContent'
      location = self._api_client.location
      project = self._api_client.project
      transformed_model = t.t_model(self._api_client, model)
      if transformed_model.startswith('publishers/'):
        transformed_model = (
            f'projects/{project}/locations/{location}/' + transformed_model
        )

      request = json.dumps(
          self._LiveSetup_to_vertex(model=transformed_model, config=config)
      )

    async with connect(uri, additional_headers=headers) as ws:
      await ws.send(request)
      logging.info(await ws.recv(decode=False))

      yield AsyncSession(api_client=self._api_client, websocket=ws)
