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
from typing import Any, AsyncIterator, Dict, Optional, Sequence, Union, get_args

import google.auth
import pydantic
from websockets import ConnectionClosed

from . import _api_module
from . import _common
from . import _transformers as t
from . import client
from . import errors
from . import types
from ._api_client import BaseApiClient
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
from .models import _ToolConfig_to_mldev
from .models import _ToolConfig_to_vertex

try:
  from websockets.asyncio.client import ClientConnection  # type: ignore
  from websockets.asyncio.client import connect  # type: ignore
except ModuleNotFoundError:
  # This try/except is for TAP, mypy complains about it which is why we have the type: ignore
  from websockets.client import ClientConnection  # type: ignore
  from websockets.client import connect  # type: ignore

logger = logging.getLogger('google_genai.live')

_FUNCTION_RESPONSE_REQUIRES_ID = (
    'FunctionResponse request must have an `id` field from the'
    ' response of a ToolCall.FunctionalCalls in Google AI.'
)


class AsyncSession:
  """AsyncSession. The live module is experimental."""

  def __init__(
      self, api_client: client.BaseApiClient, websocket: ClientConnection
  ):
    self._api_client = api_client
    self._ws = websocket

  async def send(
      self,
      *,
      input: Optional[
          Union[
              types.ContentListUnion,
              types.ContentListUnionDict,
              types.LiveClientContentOrDict,
              types.LiveClientRealtimeInputOrDict,
              types.LiveClientToolResponseOrDict,
              types.FunctionResponseOrDict,
              Sequence[types.FunctionResponseOrDict],
          ]
      ] = None,
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
      async with client.aio.live.connect(model='...', config=config) as session:
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
    try:
      raw_response = await self._ws.recv(decode=False)
    except TypeError:
      raw_response = await self._ws.recv()
    if raw_response:
      try:
        response = json.loads(raw_response)
      except json.decoder.JSONDecodeError:
        raise ValueError(f'Failed to parse response: {raw_response!r}')
    else:
      response = {}
    if self._api_client.vertexai:
      response_dict = self._LiveServerMessage_from_vertex(response)
    else:
      response_dict = self._LiveServerMessage_from_mldev(response)

    return types.LiveServerMessage._from_response(
        response=response_dict, kwargs=parameter_model.model_dump()
    )

  async def _send_loop(
      self,
      data_stream: AsyncIterator[bytes],
      mime_type: str,
      stop_event: asyncio.Event,
  ):
    async for data in data_stream:
      model_input = types.LiveClientRealtimeInput(
        media_chunks=[types.Blob(data=data, mime_type=mime_type)]
      )
      await self.send(input=model_input)
      # Give a chance for the receive loop to process responses.
      await asyncio.sleep(10**-12)
    # Give a chance for the receiver to process the last response.
    stop_event.set()

  def _LiveServerContent_from_mldev(
      self,
      from_object: Union[dict, object],
  ) -> Dict[str, Any]:
    to_object: dict[str, Any] = {}
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
  ) -> Dict[str, Any]:
    to_object: dict[str, Any] = {}
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
  ) -> Dict[str, Any]:
    to_object: dict[str, Any] = {}
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
  ) -> Dict[str, Any]:
    to_object: dict[str, Any] = {}
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
  ) -> Dict[str, Any]:
    to_object: dict[str, Any] = {}
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
  ) -> Dict[str, Any]:
    to_object: dict[str, Any] = {}
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
      input: Optional[
          Union[
              types.ContentListUnion,
              types.ContentListUnionDict,
              types.LiveClientContentOrDict,
              types.LiveClientRealtimeInputOrDict,
              types.LiveClientToolResponseOrDict,
              types.FunctionResponseOrDict,
              Sequence[types.FunctionResponseOrDict],
          ]
      ] = None,
      end_of_turn: Optional[bool] = False,
  ) -> types.LiveClientMessageDict:

    formatted_input: Any = input

    if not input:
      logging.info('No input provided. Assume it is the end of turn.')
      return {'client_content': {'turn_complete': True}}
    if isinstance(input, str):
      formatted_input = [input]
    elif isinstance(input, dict) and 'data' in input:
      try:
        blob_input = types.Blob(**input)
      except pydantic.ValidationError:
        raise ValueError(
            f'Unsupported input type "{type(input)}" or input content "{input}"'
        )
      if (
          isinstance(blob_input, types.Blob)
          and isinstance(blob_input.data, bytes)
      ):
        formatted_input = [
            blob_input.model_dump(mode='json', exclude_none=True)
        ]
    elif isinstance(input, types.Blob):
      formatted_input = [input]
    elif isinstance(input, dict) and 'name' in input and 'response' in input:
      # ToolResponse.FunctionResponse
      if not (self._api_client.vertexai) and 'id' not in input:
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      formatted_input = [input]

    if isinstance(formatted_input, Sequence) and any(
        isinstance(c, dict) and 'name' in c and 'response' in c
        for c in formatted_input
    ):
      # ToolResponse.FunctionResponse
      function_responses_input = []
      for item in formatted_input:
        if isinstance(item, dict):
          try:
            function_response_input = types.FunctionResponse(**item)
          except pydantic.ValidationError:
            raise ValueError(
                f'Unsupported input type "{type(input)}" or input content'
                f' "{input}"'
            )
          if (
              function_response_input.id is None
              and not self._api_client.vertexai
          ):
            raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
          else:
            function_response_dict = function_response_input.model_dump(
                exclude_none=True, mode='json'
            )
            function_response_typeddict = types.FunctionResponseDict(
                name=function_response_dict.get('name'),
                response=function_response_dict.get('response'),
            )
            if function_response_dict.get('id'):
              function_response_typeddict['id'] = function_response_dict.get(
                  'id'
              )
            function_responses_input.append(function_response_typeddict)
      client_message = types.LiveClientMessageDict(
          tool_response=types.LiveClientToolResponseDict(
              function_responses=function_responses_input
          )
      )
    elif isinstance(formatted_input, Sequence) and any(
        isinstance(c, str) for c in formatted_input
    ):
      to_object: dict[str, Any] = {}
      content_input_parts: list[types.PartUnion] = []
      for item in formatted_input:
        if isinstance(item, get_args(types.PartUnion)):
          content_input_parts.append(item)
      if self._api_client.vertexai:
        contents = [
            _Content_to_vertex(self._api_client, item, to_object)
            for item in t.t_contents(self._api_client, content_input_parts)
        ]
      else:
        contents = [
            _Content_to_mldev(self._api_client, item, to_object)
            for item in t.t_contents(self._api_client, content_input_parts)
        ]

      content_dict_list: list[types.ContentDict] = []
      for item in contents:
        try:
          content_input = types.Content(**item)
        except pydantic.ValidationError:
          raise ValueError(
              f'Unsupported input type "{type(input)}" or input content'
              f' "{input}"'
          )
        content_dict_list.append(
            types.ContentDict(
                parts=content_input.model_dump(exclude_none=True, mode='json')[
                    'parts'
                ],
                role=content_input.role,
            )
        )

      client_message = types.LiveClientMessageDict(
          client_content=types.LiveClientContentDict(
              turns=content_dict_list, turn_complete=end_of_turn
          )
      )
    elif isinstance(formatted_input, Sequence):
      if any((isinstance(b, dict) and 'data' in b) for b in formatted_input):
        pass
      elif any(isinstance(b, types.Blob) for b in formatted_input):
        formatted_input = [
            b.model_dump(exclude_none=True, mode='json')
            for b in formatted_input
        ]
      else:
        raise ValueError(
            f'Unsupported input type "{type(input)}" or input content "{input}"'
        )

      client_message = types.LiveClientMessageDict(
          realtime_input=types.LiveClientRealtimeInputDict(
              media_chunks=formatted_input
          )
      )

    elif isinstance(formatted_input, dict):
      if 'content' in formatted_input or 'turns' in formatted_input:
        # TODO(b/365983264) Add validation checks for content_update input_dict.
        if 'turns' in formatted_input:
          content_turns = formatted_input['turns']
        else:
          content_turns = formatted_input['content']
        client_message = types.LiveClientMessageDict(
            client_content=types.LiveClientContentDict(
                turns=content_turns,
                turn_complete=formatted_input.get('turn_complete'),
            )
        )
      elif 'media_chunks' in formatted_input:
        try:
          realtime_input = types.LiveClientRealtimeInput(**formatted_input)
        except pydantic.ValidationError:
          raise ValueError(
              f'Unsupported input type "{type(input)}" or input content'
              f' "{input}"'
          )
        client_message = types.LiveClientMessageDict(
            realtime_input=types.LiveClientRealtimeInputDict(
                media_chunks=realtime_input.model_dump(
                    exclude_none=True, mode='json'
                )['media_chunks']
            )
        )
      elif 'function_responses' in formatted_input:
        try:
          tool_response_input = types.LiveClientToolResponse(**formatted_input)
        except pydantic.ValidationError:
          raise ValueError(
              f'Unsupported input type "{type(input)}" or input content'
              f' "{input}"'
          )
        client_message = types.LiveClientMessageDict(
            tool_response=types.LiveClientToolResponseDict(
                function_responses=tool_response_input.model_dump(
                    exclude_none=True, mode='json'
                )['function_responses']
            )
        )
      else:
        raise ValueError(
            f'Unsupported input type "{type(input)}" or input content "{input}"'
        )
    elif isinstance(formatted_input, types.LiveClientRealtimeInput):
      realtime_input_dict = formatted_input.model_dump(
          exclude_none=True, mode='json'
      )
      client_message = types.LiveClientMessageDict(
          realtime_input=types.LiveClientRealtimeInputDict(
              media_chunks=realtime_input_dict.get('media_chunks')
          )
      )
      if (
          client_message['realtime_input'] is not None
          and client_message['realtime_input']['media_chunks'] is not None
          and isinstance(
              client_message['realtime_input']['media_chunks'][0]['data'], bytes
          )
      ):
        formatted_media_chunks: list[types.BlobDict] = []
        for item in client_message['realtime_input']['media_chunks']:
          if isinstance(item, dict):
            try:
              blob_input = types.Blob(**item)
            except pydantic.ValidationError:
              raise ValueError(
                  f'Unsupported input type "{type(input)}" or input content'
                  f' "{input}"'
              )
            if (
                isinstance(blob_input, types.Blob)
                and isinstance(blob_input.data, bytes)
                and blob_input.data is not None
            ):
              formatted_media_chunks.append(
                  types.BlobDict(
                      data=base64.b64decode(blob_input.data),
                      mime_type=blob_input.mime_type,
                  )
              )

        client_message['realtime_input'][
            'media_chunks'
        ] = formatted_media_chunks

    elif isinstance(formatted_input, types.LiveClientContent):
      client_content_dict = formatted_input.model_dump(
          exclude_none=True, mode='json'
      )
      client_message = types.LiveClientMessageDict(
          client_content=types.LiveClientContentDict(
              turns=client_content_dict.get('turns'),
              turn_complete=client_content_dict.get('turn_complete'),
          )
      )
    elif isinstance(formatted_input, types.LiveClientToolResponse):
      # ToolResponse.FunctionResponse
      if (
          not (self._api_client.vertexai)
          and formatted_input.function_responses is not None
          and not (formatted_input.function_responses[0].id)
      ):
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      client_message = types.LiveClientMessageDict(
          tool_response=types.LiveClientToolResponseDict(
              function_responses=formatted_input.model_dump(
                  exclude_none=True, mode='json'
              ).get('function_responses')
          )
      )
    elif isinstance(formatted_input, types.FunctionResponse):
      if not (self._api_client.vertexai) and not (formatted_input.id):
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      function_response_dict = formatted_input.model_dump(
          exclude_none=True, mode='json'
      )
      function_response_typeddict = types.FunctionResponseDict(
          name=function_response_dict.get('name'),
          response=function_response_dict.get('response'),
      )
      if function_response_dict.get('id'):
        function_response_typeddict['id'] = function_response_dict.get('id')
      client_message = types.LiveClientMessageDict(
          tool_response=types.LiveClientToolResponseDict(
              function_responses=[function_response_typeddict]
          )
      )
    elif isinstance(formatted_input, Sequence) and isinstance(
        formatted_input[0], types.FunctionResponse
    ):
      if not (self._api_client.vertexai) and not (formatted_input[0].id):
        raise ValueError(_FUNCTION_RESPONSE_REQUIRES_ID)
      function_response_list: list[types.FunctionResponseDict] = []
      for item in formatted_input:
        function_response_dict = item.model_dump(exclude_none=True, mode='json')
        function_response_typeddict = types.FunctionResponseDict(
            name=function_response_dict.get('name'),
            response=function_response_dict.get('response'),
        )
        if function_response_dict.get('id'):
          function_response_typeddict['id'] = function_response_dict.get('id')
        function_response_list.append(function_response_typeddict)
      client_message = types.LiveClientMessageDict(
          tool_response=types.LiveClientToolResponseDict(
              function_responses=function_response_list
          )
      )

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
      self, model: str, config: Optional[types.LiveConnectConfig] = None
  ):

    to_object: dict[str, Any] = {}
    if getv(config, ['generation_config']) is not None:
      setv(
          to_object,
          ['generationConfig'],
          _GenerateContentConfig_to_mldev(
              self._api_client,
              getv(config, ['generation_config']),
              to_object,
          ),
      )
    if getv(config, ['response_modalities']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['responseModalities'] = getv(
            config, ['response_modalities']
        )
      else:
        to_object['generationConfig'] = {
            'responseModalities': getv(config, ['response_modalities'])
        }
    if getv(config, ['speech_config']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['speechConfig'] = _SpeechConfig_to_mldev(
            self._api_client,
            t.t_speech_config(
                self._api_client, getv(config, ['speech_config'])
            ),
            to_object,
        )
      else:
        to_object['generationConfig'] = {
            'speechConfig': _SpeechConfig_to_mldev(
                self._api_client,
                t.t_speech_config(
                    self._api_client, getv(config, ['speech_config'])
                ),
                to_object,
            )
        }

    if getv(config, ['system_instruction']) is not None:
      setv(
          to_object,
          ['systemInstruction'],
          _Content_to_mldev(
              self._api_client,
              t.t_content(
                  self._api_client, getv(config, ['system_instruction'])
              ),
              to_object,
          ),
      )
    if getv(config, ['tools']) is not None:
      setv(
          to_object,
          ['tools'],
          [
              _Tool_to_mldev(
                  self._api_client, t.t_tool(self._api_client, item), to_object
              )
              for item in t.t_tools(self._api_client, getv(config, ['tools']))
          ],
      )
    if getv(config, ['tool_config']) is not None:
      setv(
          to_object,
          ['toolConfig'],
          _ToolConfig_to_mldev(
              self._api_client,
              getv(config, ['tool_config']),
              to_object,
          ),
      )

    return_value = {'setup': {'model': model}}
    return_value['setup'].update(to_object)
    return return_value

  def _LiveSetup_to_vertex(
      self, model: str, config: Optional[types.LiveConnectConfig] = None
  ):

    to_object: dict[str, Any] = {}

    if getv(config, ['generation_config']) is not None:
      setv(
          to_object,
          ['generationConfig'],
          _GenerateContentConfig_to_vertex(
              self._api_client,
              getv(config, ['generation_config']),
              to_object,
          ),
      )
    if getv(config, ['response_modalities']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['responseModalities'] = getv(
            config, ['response_modalities']
        )
      else:
        to_object['generationConfig'] = {
            'responseModalities': getv(config, ['response_modalities'])
        }
    else:
      # Set default to AUDIO to align with MLDev API.
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig'].update({'responseModalities': ['AUDIO']})
      else:
        to_object.update(
            {'generationConfig': {'responseModalities': ['AUDIO']}}
        )
    if getv(config, ['speech_config']) is not None:
      if getv(to_object, ['generationConfig']) is not None:
        to_object['generationConfig']['speechConfig'] = _SpeechConfig_to_vertex(
            self._api_client,
            t.t_speech_config(
                self._api_client, getv(config, ['speech_config'])
            ),
            to_object,
        )
      else:
        to_object['generationConfig'] = {
            'speechConfig': _SpeechConfig_to_vertex(
                self._api_client,
                t.t_speech_config(
                    self._api_client, getv(config, ['speech_config'])
                ),
                to_object,
            )
        }
    if getv(config, ['system_instruction']) is not None:
      setv(
          to_object,
          ['systemInstruction'],
          _Content_to_vertex(
              self._api_client,
              t.t_content(
                  self._api_client, getv(config, ['system_instruction'])
              ),
              to_object,
          ),
      )
    if getv(config, ['tools']) is not None:
      setv(
          to_object,
          ['tools'],
          [
              _Tool_to_vertex(
                  self._api_client, t.t_tool(self._api_client, item), to_object
              )
              for item in t.t_tools(self._api_client, getv(config, ['tools']))
          ],
      )
    if getv(config, ['tool_config']) is not None:
      setv(
          to_object,
          ['toolConfig'],
          _ToolConfig_to_vertex(
              self._api_client,
              getv(config, ['tool_config']),
              to_object,
          ),
      )

    return_value = {'setup': {'model': model}}
    return_value['setup'].update(to_object)
    return return_value

  @experimental_warning(
      'The live API is experimental and may change in future versions.',
  )
  @contextlib.asynccontextmanager
  async def connect(
      self,
      *,
      model: str,
      config: Optional[types.LiveConnectConfigOrDict] = None,
  ) -> AsyncIterator[AsyncSession]:
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
    transformed_model = t.t_model(self._api_client, model)
    # Ensure the config is a LiveConnectConfig.
    if config is None:
      parameter_model = types.LiveConnectConfig()
    elif isinstance(config, dict):
      if config.get('system_instruction') is None:
        system_instruction = None
      else:
        system_instruction = t.t_content(
            self._api_client, config.get('system_instruction')
        )
      parameter_model = types.LiveConnectConfig(
          generation_config=config.get('generation_config'),
          response_modalities=config.get('response_modalities'),
          speech_config=config.get('speech_config'),
          system_instruction=system_instruction,
          tools=config.get('tools'),
      )
    else:
      parameter_model = config

    if self._api_client.api_key:
      api_key = self._api_client.api_key
      version = self._api_client._http_options.api_version
      uri = f'{base_url}/ws/google.ai.generativelanguage.{version}.GenerativeService.BidiGenerateContent?key={api_key}'
      headers = self._api_client._http_options.headers
      request_dict = _common.convert_to_dict(
          self._LiveSetup_to_mldev(
              model=transformed_model,
              config=parameter_model,
          )
      )
      request = json.dumps(request_dict)
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
      headers = self._api_client._http_options.headers
      if headers is not None:
        headers.update({
            'Authorization': 'Bearer {}'.format(bearer_token),
        })
      version = self._api_client._http_options.api_version
      uri = f'{base_url}/ws/google.cloud.aiplatform.{version}.LlmBidiService/BidiGenerateContent'
      location = self._api_client.location
      project = self._api_client.project
      if transformed_model.startswith('publishers/'):
        transformed_model = (
            f'projects/{project}/locations/{location}/' + transformed_model
        )
      request_dict = _common.convert_to_dict(
          self._LiveSetup_to_vertex(
              model=transformed_model,
              config=parameter_model,
          )
      )
      request = json.dumps(request_dict)

    try:
      async with connect(uri, additional_headers=headers) as ws:
        await ws.send(request)
        logger.info(await ws.recv(decode=False))

        yield AsyncSession(api_client=self._api_client, websocket=ws)
    except TypeError:
      # Try with the older websockets API
      async with connect(uri, extra_headers=headers) as ws:
        await ws.send(request)
        logger.info(await ws.recv())

        yield AsyncSession(api_client=self._api_client, websocket=ws)
