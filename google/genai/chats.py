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

from typing import Optional
from typing import Union

from . import _transformers as t
from .models import AsyncModels, Models
from .types import Content, ContentDict, GenerateContentConfigOrDict, GenerateContentResponse, PartUnionDict

class _BaseChat:
  """Base chat session."""

  def __init__(
      self,
      *,
      modules: Union[Models, AsyncModels],
      model: str,
      config: GenerateContentConfigOrDict = None,
      history: list[Content],
  ):
    self._modules = modules
    self._model = model
    self._config = config
    self._curated_history = history


class Chat(_BaseChat):
  """Chat session."""

  def send_message(
      self, message: Union[list[PartUnionDict], PartUnionDict]
  ) -> GenerateContentResponse:
    """Sends the conversation history with the additional message and returns the model's response.

    Args:
      message: The message to send to the model.

    Returns:
      The model's response.

    Usage:

    .. code-block:: python

      chat = client.chats.create(model='gemini-1.5-flash')
      response = chat.send_message('tell me a story')
    """

    input_content = t.t_content(self._modules.api_client, message)
    response = self._modules.generate_content(
        model=self._model,
        contents=self._curated_history + [input_content],
        config=self._config,
    )
    if response.candidates and response.candidates[0].content:
      if response.automatic_function_calling_history:
        self._curated_history.extend(
            response.automatic_function_calling_history
        )
      else:
        self._curated_history.append(input_content)
      self._curated_history.append(response.candidates[0].content)
    return response

  def _send_message_stream(self, message: Union[list[ContentDict], str]):
    for content in t.t_contents(self._modules.api_client, message):
      self._curated_history.append(content)
    for chunk in self._modules.generate_content_stream(
        model=self._model, contents=self._curated_history, config=self._config
    ):
      # TODO(b/381089069): add successful response to history
      yield chunk


class Chats:
  """A util class to create chat sessions."""

  def __init__(self, modules: Models):
    self._modules = modules

  def create(
      self,
      *,
      model: str,
      config: GenerateContentConfigOrDict = None,
      history: Optional[list[Content]] = None,
  ) -> Chat:
    """Creates a new chat session.

    Args:
      model: The model to use for the chat.
      config: The configuration to use for the generate content request.
      history: The history to use for the chat.

    Returns:
      A new chat session.
    """
    return Chat(
        modules=self._modules,
        model=model,
        config=config,
        history=history if history else [],
    )


class AsyncChat(_BaseChat):
  """Async chat session."""

  async def send_message(
      self, message: Union[list[PartUnionDict], PartUnionDict]
  ) -> GenerateContentResponse:
    """Sends the conversation history with the additional message and returns model's response.

    Args:
      message: The message to send to the model.

    Returns:
      The model's response.

    Usage:

    .. code-block:: python

      chat = client.chats.create(model='gemini-1.5-flash')
      response = chat.send_message('tell me a story')
    """

    input_content = t.t_content(self._modules.api_client, message)
    response = await self._modules.generate_content(
        model=self._model,
        contents=self._curated_history + [input_content],
        config=self._config,
    )
    if response.candidates and response.candidates[0].content:
      if response.automatic_function_calling_history:
        self._curated_history.extend(
            response.automatic_function_calling_history
        )
      else:
        self._curated_history.append(input_content)
      self._curated_history.append(response.candidates[0].content)
    return response

  async def _send_message_stream(self, message: Union[list[ContentDict], str]):
    for content in t.t_contents(self._modules.api_client, message):
      self._curated_history.append(content)
    async for chunk in self._modules.generate_content_stream(
        model=self._model, contents=self._curated_history, config=self._config
    ):
      # TODO(b/381089069): add successful response to history
      yield chunk


class AsyncChats:
  """A util class to create async chat sessions."""


  def __init__(self, modules: AsyncModels):
    self._modules = modules

  def create(
      self,
      *,
      model: str,
      config: GenerateContentConfigOrDict = None,
      history: Optional[list[Content]] = None,
  ) -> AsyncChat:
    """Creates a new chat session.

    Args:
      model: The model to use for the chat.
      config: The configuration to use for the generate content request.
      history: The history to use for the chat.

    Returns:
      A new chat session.
    """
    return AsyncChat(
        modules=self._modules,
        model=model,
        config=config,
        history=history if history else [],
    )
