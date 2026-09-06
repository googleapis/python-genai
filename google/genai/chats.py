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

from collections.abc import Iterator
import contextlib
import logging
import sys
from typing import Any, AsyncIterator, Optional, Union, get_args


from . import _extra_utils
from . import _mcp_utils
from . import _transformers as t
from . import errors
from . import types
from .models import AsyncModels, Models
from .types import Content, ContentOrDict, GenerateContentConfigOrDict, GenerateContentResponse, Part, PartUnionDict


if sys.version_info >= (3, 10):
  from typing import TypeGuard
else:
  from typing_extensions import TypeGuard

logger = logging.getLogger("google_genai.chats")

def _validate_content(content: Content) -> bool:
  if not content.parts:
    return False
  for part in content.parts:
    if part == Part():
      return False
  return True


def _validate_contents(contents: list[Content]) -> bool:
  if not contents:
    return False
  for content in contents:
    if not _validate_content(content):
      return False
  return True


def _validate_response(response: GenerateContentResponse) -> bool:
  if not response.candidates:
    return False
  if not response.candidates[0].content:
    return False
  return _validate_content(response.candidates[0].content)


def _extract_curated_history(
    comprehensive_history: list[Content],
) -> list[Content]:
  """Extracts the curated (valid) history from a comprehensive history.

  The comprehensive history contains all turns (user input and model responses),
  including any invalid or rejected model outputs. This function filters that
  history to return only the valid turns.

  Args:
      comprehensive_history: A list representing the complete chat history.
        Including invalid turns.

  Returns:
      curated history, which is a list of valid turns.
  """
  if not comprehensive_history:
    return []
  curated_history = []
  length = len(comprehensive_history)
  i = 0
  current_input = comprehensive_history[i]
  while i < length:
    if comprehensive_history[i].role not in ["user", "model"]:
      raise ValueError(
          f"Role must be user or model, but got {comprehensive_history[i].role}"
      )

    if comprehensive_history[i].role == "user":
      current_input = comprehensive_history[i]
      curated_history.append(current_input)
      i += 1
    else:
      current_output = []
      is_valid = True
      while i < length and comprehensive_history[i].role == "model":
        current_output.append(comprehensive_history[i])
        if is_valid and not _validate_content(comprehensive_history[i]):
          is_valid = False
        i += 1
      if is_valid:
        curated_history.extend(current_output)
      elif curated_history:
        curated_history.pop()
  return curated_history


class _BaseChat:
  """Base chat session."""

  def __init__(
      self,
      *,
      model: str,
      config: Optional[GenerateContentConfigOrDict] = None,
      history: list[ContentOrDict],
  ):
    self._model = model
    self._config = _extra_utils.get_usage_header(
        config, types.GenerateContentConfig, usage="chat"  # type: ignore[arg-type]
    )
    content_models = []
    for content in history:
      if not isinstance(content, Content):
        content_model = Content.model_validate(content)
      else:
        content_model = content
      content_models.append(content_model)
    self._comprehensive_history = content_models
    """Comprehensive history is the full history of the chat, including turns of the invalid contents from the model and their associated inputs.
    """
    self._curated_history = _extract_curated_history(content_models)
    """Curated history is the set of valid turns that will be used in the subsequent send requests.
    """

  def record_history(
      self,
      user_input: Content,
      model_output: list[Content],
      is_valid: bool,
  ) -> None:
    """Records the chat history.

    Maintaining both comprehensive and curated histories.

    Args:
      user_input: The user's input content.
      model_output: A list of `Content` from the model's response. This can be
        an empty list if the model produced no output.
      is_valid: A boolean flag indicating whether the current model output is
        considered valid.
    """
    input_contents = [user_input]
    # Appends an empty content when model returns empty response, so that the
    # history is always alternating between user and model.
    output_contents = (
        model_output if model_output else [Content(role="model", parts=[])]
    )
    self._comprehensive_history.extend(input_contents)
    self._comprehensive_history.extend(output_contents)
    if is_valid:
      self._curated_history.extend(input_contents)
      self._curated_history.extend(output_contents)

  def get_history(self, curated: bool = False) -> list[Content]:
    """Returns the chat history.

    Args:
        curated: A boolean flag indicating whether to return the curated (valid)
          history or the comprehensive (all turns) history. Defaults to False
          (returns the comprehensive history).

    Returns:
        A list of `Content` objects representing the chat history.
    """
    if curated:
      return self._curated_history
    else:
      return self._comprehensive_history


def _is_part_type(
    contents: Union[list[PartUnionDict], PartUnionDict],
) -> TypeGuard[t.ContentType]:
  if isinstance(contents, list):
    return all(_is_part_type(part) for part in contents)
  else:
    allowed_part_types = get_args(types.PartUnion)
    if type(contents) in allowed_part_types:
      return True
    else:
      # Some images don't pass isinstance(item, PIL.Image.Image)
      # For example <class 'PIL.JpegImagePlugin.JpegImageFile'>
      if types.PIL_Image is not None and isinstance(contents, types.PIL_Image):
        return True
    return False


class Chat(_BaseChat):
  """Chat session."""

  def __init__(
      self,
      *,
      modules: Models,
      model: str,
      config: Optional[GenerateContentConfigOrDict] = None,
      history: list[ContentOrDict],
  ):
    self._modules = modules
    super().__init__(
        model=model,
        config=config,
        history=history,
    )

  def send_message(
      self,
      message: Union[list[PartUnionDict], PartUnionDict],
      config: Optional[GenerateContentConfigOrDict] = None,
  ) -> GenerateContentResponse:
    """Sends the conversation history with the additional message and returns the model's response.

    Args:
      message: The message to send to the model.
      config:  Optional config to override the default Chat config for this
        request.

    Returns:
      The model's response.

    Usage:

    .. code-block:: python

      chat = client.chats.create(model='gemini-2.0-flash')
      response = chat.send_message('tell me a story')
    """

    if not _is_part_type(message):
      raise ValueError(
          f"Message must be a valid part type: {types.PartUnion} or"
          f" {types.PartUnionDict}, got {type(message)}"
      )
    method_config = config if config else self._config
    method_config = _extra_utils.get_usage_header(
        method_config, types.GenerateContentConfig, usage="chat"  # type: ignore[arg-type]
    )
    parsed_config = _extra_utils.parse_config_for_mcp_usage(method_config)
    if (
        parsed_config
        and parsed_config.tools
        and _mcp_utils.has_mcp_session_usage(parsed_config.tools)
    ):
      raise errors.UnsupportedFunctionError(
          "MCP sessions are not supported in synchronous methods."
      )
    incompatible_tools_indexes = (
        _extra_utils.find_afc_incompatible_tool_indexes(method_config)
    )
    user_input = t.t_content(message)
    contents_to_model = self._curated_history + [user_input]  # type: ignore[arg-type]
    if _extra_utils.should_disable_afc(method_config):
      response = self._modules.generate_content(
          model=self._model,
          contents=contents_to_model,  # type: ignore[arg-type]
          config=parsed_config,
      )
      model_output = (
          [response.candidates[0].content]
          if response.candidates and response.candidates[0].content
          else []
      )
      self.record_history(
          user_input=user_input,
          model_output=model_output,
          is_valid=_validate_response(response),
      )
      return response

    if incompatible_tools_indexes:
      _extra_utils.log_afc_incompatible_tools_warning(
          method_config, incompatible_tools_indexes
      )

      if parsed_config:
        parsed_config.automatic_function_calling = (
            types.AutomaticFunctionCallingConfig(disable=True)
        )
      response = self._modules.generate_content(
          model=self._model,
          contents=contents_to_model,  # type: ignore[arg-type]
          config=parsed_config,
      )
      model_output = (
          [response.candidates[0].content]
          if response.candidates and response.candidates[0].content
          else []
      )
      self.record_history(
          user_input=user_input,
          model_output=model_output,
          is_valid=_validate_response(response),
      )
      return response
    # AFC handling
    remaining_remote_calls_afc = _extra_utils.get_max_remote_calls_afc(
        parsed_config
    )
    # Because we cannot remove automatic_function_calling from the
    # GenerateContentConfig, we set it to None to disable it
    if parsed_config:
      parsed_config.automatic_function_calling = (
          types.AutomaticFunctionCallingConfig(disable=True)
      )
    logger.info(
        f"AFC is enabled with max remote calls: {remaining_remote_calls_afc}."
    )
    parsed_config = _extra_utils.get_usage_header(
        parsed_config, types.GenerateContentConfig, usage='afc'  # type: ignore[arg-type]
    )
    response = types.GenerateContentResponse()
    function_map = _extra_utils.get_function_map(parsed_config)
    i = 0
    while remaining_remote_calls_afc > 0:
      i += 1
      response = self._modules.generate_content(
          model=self._model,
          contents=contents_to_model,  # type: ignore[arg-type]
          config=parsed_config,
      )
      if (
          not function_map
          or not response
          or not response.candidates
          or not response.candidates[0].content
          or not response.candidates[0].content.parts
      ):
        break

      func_response_parts = _extra_utils.get_function_response_parts(
          response, function_map
      )
      if not func_response_parts:
        break
      logger.info(f"AFC remote call {i} is done.")
      remaining_remote_calls_afc -= 1
      if remaining_remote_calls_afc == 0:
        logger.info("Reached max remote calls for automatic function calling.")
      func_call_content = response.candidates[0].content
      func_response_content = types.Content(
          role="user", parts=func_response_parts
      )
      contents_to_model.append(func_call_content)
      contents_to_model.append(func_response_content)
      model_output = [func_call_content]
      self.record_history(
          user_input=user_input,
          model_output=model_output,
          is_valid=_validate_response(response),
      )
      user_input = func_response_content

    model_output = (
        [response.candidates[0].content]
        if response.candidates and response.candidates[0].content
        else []
    )
    self.record_history(
        user_input=user_input,
        model_output=model_output,
        is_valid=_validate_response(response),
    )
    return response


  def send_message_stream(
      self,
      message: Union[list[PartUnionDict], PartUnionDict],
      config: Optional[GenerateContentConfigOrDict] = None,
  ) -> Iterator[GenerateContentResponse]:
    """Sends the conversation history with the additional message and yields the model's response in chunks.

    Args:
      message: The message to send to the model.
      config: Optional config to override the default Chat config for this
        request.

    Yields:
      The model's response in chunks.

    Usage:

    .. code-block:: python

      chat = client.chats.create(model='gemini-2.0-flash')
      for chunk in chat.send_message_stream('tell me a story'):
        print(chunk.text)
    """

    method_config = config if config else self._config
    method_config = _extra_utils.get_usage_header(
        method_config, types.GenerateContentConfig, usage="chat"  # type: ignore[arg-type]
    )
    parsed_config = _extra_utils.parse_config_for_mcp_usage(method_config)
    if (
        parsed_config
        and parsed_config.tools
        and _mcp_utils.has_mcp_session_usage(parsed_config.tools)
    ):
      raise errors.UnsupportedFunctionError(
          "MCP sessions are not supported in synchronous methods."
      )
    if not _is_part_type(message):
      raise ValueError(
          f"Message must be a valid part type: {types.PartUnion} or"
          f" {types.PartUnionDict}, got {type(message)}"
      )
    incompatible_tools_indexes = (
        _extra_utils.find_afc_incompatible_tool_indexes(method_config)
    )
    user_input = t.t_content(message)
    contents_to_model = self._curated_history + [user_input]  # type: ignore[arg-type]
    model_output = []
    finish_reason = None
    is_valid = True
    chunk = None
    disable_afc = _extra_utils.should_disable_afc(method_config)
    if not disable_afc and incompatible_tools_indexes:
      _extra_utils.log_afc_incompatible_tools_warning(
          method_config, incompatible_tools_indexes
      )
      if parsed_config:
        parsed_config.automatic_function_calling = (
            types.AutomaticFunctionCallingConfig(disable=True)
        )
      disable_afc = True

    if disable_afc:
      if isinstance(self._modules, Models):
        for chunk in self._modules.generate_content_stream(
            model=self._model,
            contents=contents_to_model,  # type: ignore[arg-type]
            config=parsed_config,
        ):
          if not _validate_response(chunk):
            is_valid = False
          if chunk.candidates and chunk.candidates[0].content:
            model_output.append(chunk.candidates[0].content)
          if chunk.candidates and chunk.candidates[0].finish_reason:
            finish_reason = chunk.candidates[0].finish_reason
          yield chunk
        self.record_history(
            user_input=user_input,
            model_output=model_output,
            is_valid=is_valid
            and model_output is not None
            and finish_reason is not None,
        )
      return

    # AFC handling
    remaining_remote_calls_afc = _extra_utils.get_max_remote_calls_afc(
        parsed_config
    )
    # Because we cannot remove automatic_function_calling from the
    # GenerateContentConfig, we set it to None to disable it
    if parsed_config:
      parsed_config.automatic_function_calling = (
          types.AutomaticFunctionCallingConfig(disable=True)
      )
    parsed_config = _extra_utils.get_usage_header(
        parsed_config, types.GenerateContentConfig, usage="afc"  # type: ignore[arg-type]
    )
    logger.info(
        f"AFC is enabled with max remote calls: {remaining_remote_calls_afc}."
    )
    function_map = _extra_utils.get_function_map(parsed_config)
    i = 0
    if isinstance(self._modules, Models):
      while remaining_remote_calls_afc > 0:
        i += 1
        response_stream = self._modules.generate_content_stream(
            model=self._model,
            contents=contents_to_model,  # type: ignore[arg-type]
            config=parsed_config,
        )

        model_output = []
        finish_reason = None
        is_valid = True
        func_response_parts = []
        chunk = None

        for chunk in response_stream:
          if not _validate_response(chunk):
            is_valid = False

          if (
              function_map
              and chunk.candidates
              and chunk.candidates[0].content
              and chunk.candidates[0].content.parts
          ):
            chunk_func_response_parts = (
                _extra_utils.get_function_response_parts(chunk, function_map)
            )
            if chunk_func_response_parts:
              func_response_parts.extend(chunk_func_response_parts)

          if chunk.candidates and chunk.candidates[0].content:
            model_output.append(chunk.candidates[0].content)
          if chunk.candidates and chunk.candidates[0].finish_reason:
            finish_reason = chunk.candidates[0].finish_reason
          yield chunk

        if not function_map or not func_response_parts:
          break

        logger.info(f"AFC remote call {i} is done.")
        remaining_remote_calls_afc -= 1
        if remaining_remote_calls_afc == 0:
          logger.info(
              "Reached max remote calls for automatic function calling."
          )

        if chunk and chunk.candidates and chunk.candidates[0].content:
          func_response_content = types.Content(
              role="user", parts=func_response_parts
          )
          contents_to_model.extend(model_output)
          contents_to_model.append(func_response_content)

          self.record_history(
              user_input=user_input,
              model_output=model_output,
              is_valid=is_valid,
          )
          user_input = func_response_content

      self.record_history(
          user_input=user_input,
          model_output=model_output,
          is_valid=bool(
              is_valid
              and model_output is not None
              and finish_reason is not None
          ),
      )


class Chats:
  """A util class to create chat sessions."""

  def __init__(self, modules: Models):
    self._modules = modules

  def create(
      self,
      *,
      model: str,
      config: Optional[GenerateContentConfigOrDict] = None,
      history: Optional[list[ContentOrDict]] = None,
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

  def __init__(
      self,
      *,
      modules: AsyncModels,
      model: str,
      config: Optional[GenerateContentConfigOrDict] = None,
      history: list[ContentOrDict],
  ):
    self._modules = modules
    super().__init__(
        model=model,
        config=config,
        history=history,
    )

  async def send_message(
      self,
      message: Union[list[PartUnionDict], PartUnionDict],
      config: Optional[GenerateContentConfigOrDict] = None,
  ) -> GenerateContentResponse:
    """Sends the conversation history with the additional message and returns model's response.

    Args:
      message: The message to send to the model.
      config: Optional config to override the default Chat config for this
        request.

    Returns:
      The model's response.

    Usage:

    .. code-block:: python

      chat = client.aio.chats.create(model='gemini-2.0-flash')
      response = await chat.send_message('tell me a story')
    """
    method_config = config if config else self._config
    method_config = _extra_utils.get_usage_header(
        method_config,  # type: ignore[arg-type]
        types.GenerateContentConfig,
        usage="chat",
    )
    if not _is_part_type(message):
      raise ValueError(
          f"Message must be a valid part type: {types.PartUnion} or"
          f" {types.PartUnionDict}, got {type(message)}"
      )

    user_input = t.t_content(message)
    contents_to_model = self._curated_history + [user_input]  # type: ignore[arg-type]

    if _extra_utils.should_disable_afc(method_config):
      response = await self._modules.generate_content(
          model=self._model,
          contents=contents_to_model,  # type: ignore[arg-type]
          config=method_config,
      )
      model_output = (
          [response.candidates[0].content]
          if response.candidates and response.candidates[0].content
          else []
      )
      self.record_history(
          user_input=user_input,
          model_output=model_output,
          is_valid=_validate_response(response),
      )
      return response

    incompatible_tools_indexes = (
        _extra_utils.find_afc_incompatible_tool_indexes(
            method_config,
            is_agent_platform=getattr(
                self._modules._api_client, "vertexai", False
            ),
        )
    )

    if not method_config:
      parsed_config = None
    elif isinstance(method_config, dict):
      parsed_config = types.GenerateContentConfig(**method_config)
    else:
      parsed_config = method_config.model_copy(deep=True)

    if incompatible_tools_indexes:
      _extra_utils.log_afc_incompatible_tools_warning(
          method_config, incompatible_tools_indexes
      )

      if parsed_config:
        parsed_config.automatic_function_calling = (
            types.AutomaticFunctionCallingConfig(disable=True)
        )
      response = await self._modules.generate_content(
          model=self._model,
          contents=contents_to_model,  # type: ignore[arg-type]
          config=parsed_config,
      )
      model_output = (
          [response.candidates[0].content]
          if response.candidates and response.candidates[0].content
          else []
      )
      self.record_history(
          user_input=user_input,
          model_output=model_output,
          is_valid=_validate_response(response),
      )
      return response

    # AFC handling
    parsed_config = _extra_utils.get_usage_header(
        parsed_config,  # type: ignore[arg-type]
        types.GenerateContentConfig,
        usage="afc",
    )
    async with contextlib.AsyncExitStack() as stack:
      # Intercept Agent Platform MCP servers and open connections
      if (
          self._modules._api_client.vertexai
          and _extra_utils.has_agent_platform_mcp_servers(parsed_config)
          and parsed_config is not None
      ):
        new_tools: list[Any] = []
        if parsed_config.tools:
          for tool in parsed_config.tools:
            if isinstance(tool, types.Tool) and tool.mcp_servers:
              # Only keep the tool if it has fields besides mcp_servers
              if (
                  tool.function_declarations
                  or tool.google_search
                  or tool.retrieval
                  or tool.google_search_retrieval
                  or tool.code_execution
              ):
                tool_copy = tool.model_copy(update={'mcp_servers': None})
                new_tools.append(tool_copy)

              for server in tool.mcp_servers:
                if (
                    getattr(server, 'streamable_http_transport', None)
                    is not None
                ):
                  raise ValueError(
                      "The 'streamable_http_transport' parameter is only"
                      ' supported in Gemini Developer API mode, not in Gemini'
                      ' Enterprise Agent Platform mode.'
                  )

                # Open the stream and tie its lifespan to the AsyncExitStack
                if server.name is not None:
                  session = await stack.enter_async_context(
                      _mcp_utils._connect_agent_platform_mcp(
                          self._modules._api_client, server.name
                      )
                  )
                  new_tools.append(session)
                else:
                  raise ValueError(
                      "Agent Platform MCP servers require a 'name' field."
                  )
            else:
              new_tools.append(tool)
          parsed_config.tools = new_tools

      # Convert active sessions to tools and adapters
      final_parsed_config, mcp_to_genai_tool_adapters = (
          await _extra_utils.parse_config_for_mcp_sessions(
              parsed_config,
              is_agent_platform=getattr(
                  self._modules._api_client, "vertexai", False
              ),
          )
      )

      remaining_remote_calls_afc = _extra_utils.get_max_remote_calls_afc(
          final_parsed_config
      )
      if final_parsed_config:
        final_parsed_config.automatic_function_calling = (
            types.AutomaticFunctionCallingConfig(
                disable=True,
            )
        )

      logger.info(
          f"AFC is enabled with max remote calls: {remaining_remote_calls_afc}."
      )

      response = types.GenerateContentResponse()
      function_map = _extra_utils.get_function_map(
          final_parsed_config,
          mcp_to_genai_tool_adapters,
          is_caller_method_async=True,
      )

      i = 0
      while remaining_remote_calls_afc > 0:
        i += 1
        response = await self._modules.generate_content(
            model=self._model,
            contents=contents_to_model,  # type: ignore[arg-type]
            config=final_parsed_config,
        )
        if (
            not function_map
            or not response
            or not response.candidates
            or not response.candidates[0].content
            or not response.candidates[0].content.parts
        ):
          break

        func_response_parts = (
            await _extra_utils.get_function_response_parts_async(
                response, function_map
            )
        )
        if not func_response_parts:
          break

        logger.info(f"AFC remote call {i} is done.")
        remaining_remote_calls_afc -= 1
        if remaining_remote_calls_afc == 0:
          logger.info(
              "Reached max remote calls for automatic function calling."
          )

        func_call_content = response.candidates[0].content
        func_response_content = types.Content(
            role="user", parts=func_response_parts
        )

        contents_to_model.append(func_call_content)
        contents_to_model.append(func_response_content)

        model_output = [func_call_content]
        self.record_history(
            user_input=user_input,
            model_output=model_output,
            is_valid=_validate_response(response),
        )
        user_input = func_response_content

      model_output = (
          [response.candidates[0].content]
          if response.candidates and response.candidates[0].content
          else []
      )
      self.record_history(
          user_input=user_input,
          model_output=model_output,
          is_valid=_validate_response(response),
      )
      return response


  async def send_message_stream(
      self,
      message: Union[list[PartUnionDict], PartUnionDict],
      config: Optional[GenerateContentConfigOrDict] = None,
  ) -> AsyncIterator[GenerateContentResponse]:
    """Sends the conversation history with the additional message and yields the model's response in chunks.

    Args:
      message: The message to send to the model.
      config: Optional config to override the default Chat config for this
        request.

    Yields:
      The model's response in chunks.

    Usage:

    .. code-block:: python

      chat = client.aio.chats.create(model='gemini-2.0-flash')
      async for chunk in await chat.send_message_stream('tell me a story'):
        print(chunk.text)
    """

    if not _is_part_type(message):
      raise ValueError(
          f"Message must be a valid part type: {types.PartUnion} or"
          f" {types.PartUnionDict}, got {type(message)}"
      )
    input_content = t.t_content(message)

    async def async_generator():  # type: ignore[no-untyped-def]
      method_config = config if config else self._config
      method_config = _extra_utils.get_usage_header(
          method_config,  # type: ignore[arg-type]
          types.GenerateContentConfig,
          usage="chat",
      )
      parsed_config = _extra_utils.parse_config_for_mcp_usage(method_config)
      disable_afc = _extra_utils.should_disable_afc(method_config)
      incompatible_tools_indexes = (
          _extra_utils.find_afc_incompatible_tool_indexes(
              method_config,
              is_agent_platform=getattr(
                  self._modules._api_client, "vertexai", False
              ),
          )
      )
      user_input = input_content
      contents_to_model = self._curated_history + [user_input]  # type: ignore[arg-type]
      if not disable_afc and incompatible_tools_indexes:
        _extra_utils.log_afc_incompatible_tools_warning(
            method_config, incompatible_tools_indexes
        )
        if parsed_config:
          parsed_config.automatic_function_calling = (
              types.AutomaticFunctionCallingConfig(
                  disable=True,
              )
          )
        disable_afc = True

      if disable_afc:
        output_contents = []
        finish_reason = None
        is_valid = True
        chunk = None
        async for chunk in await self._modules.generate_content_stream(  # type: ignore[attr-defined]
            model=self._model,
            contents=contents_to_model,  # type: ignore[arg-type]
            config=parsed_config,
        ):
          if not _validate_response(chunk):
            is_valid = False
          if chunk.candidates and chunk.candidates[0].content:
            output_contents.append(chunk.candidates[0].content)
          if chunk.candidates and chunk.candidates[0].finish_reason:
            finish_reason = chunk.candidates[0].finish_reason
          yield chunk

        if not output_contents or finish_reason is None:
          is_valid = False

        self.record_history(
            user_input=user_input,
            model_output=output_contents,
            is_valid=is_valid,
        )
        return

      # AFC handling
      parse_config = _extra_utils.get_usage_header(
          parsed_config,  # type: ignore[arg-type]
          types.GenerateContentConfig,
          usage="afc",
      )
      async with contextlib.AsyncExitStack() as stack:
        # Intercept Agent Platform MCP servers and open connections
        if (
            self._modules._api_client.vertexai
            and _extra_utils.has_agent_platform_mcp_servers(parsed_config)
            and parsed_config is not None
        ):
          new_tools: list[Any] = []
          if parsed_config.tools:
            for tool in parsed_config.tools:
              if isinstance(tool, types.Tool) and tool.mcp_servers:
                # Only keep the tool if it has fields besides mcp_servers
                if (
                    tool.function_declarations
                    or tool.google_search
                    or tool.retrieval
                    or tool.google_search_retrieval
                    or tool.code_execution
                ):
                  tool_copy = tool.model_copy(update={'mcp_servers': None})
                  new_tools.append(tool_copy)

                for server in tool.mcp_servers:
                  if (
                      getattr(server, 'streamable_http_transport', None)
                      is not None
                  ):
                    raise ValueError(
                        "The 'streamable_http_transport' parameter is only"
                        ' supported in Gemini Developer API mode, not in Gemini'
                        ' Enterprise Agent Platform mode.'
                    )

                  # Open the stream and tie its lifespan to the AsyncExitStack
                  if server.name is not None:
                    session = await stack.enter_async_context(
                        _mcp_utils._connect_agent_platform_mcp(
                            self._modules._api_client, server.name
                        )
                    )
                    new_tools.append(session)
                  else:
                    raise ValueError(
                        "Agent Platform MCP servers require a 'name' field."
                    )
              else:
                new_tools.append(tool)
            parsed_config.tools = new_tools

        # Convert active sessions to tools and adapters
        final_parsed_config, mcp_to_genai_tool_adapters = (
            await _extra_utils.parse_config_for_mcp_sessions(
                parsed_config,
                is_agent_platform=getattr(
                    self._modules._api_client, "vertexai", False
                ),
            )
        )

        remaining_remote_calls_afc = _extra_utils.get_max_remote_calls_afc(
            final_parsed_config
        )
        if final_parsed_config:
          final_parsed_config.automatic_function_calling = (
              types.AutomaticFunctionCallingConfig(
                  disable=True,
              )
          )

        logger.info(
            "AFC is enabled with max remote calls:"
            f" {remaining_remote_calls_afc}."
        )

        function_map = _extra_utils.get_function_map(
            final_parsed_config,
            mcp_to_genai_tool_adapters,
            is_caller_method_async=True,
        )

        i = 0
        model_output: list[types.Content] = []
        finish_reason = None
        is_valid = True

        while remaining_remote_calls_afc > 0:
          i += 1
          response_stream = await self._modules.generate_content_stream(
              model=self._model,
              contents=contents_to_model,  # type: ignore[arg-type]
              config=final_parsed_config,
          )

          model_output = []
          finish_reason = None
          is_valid = True
          func_response_parts = []
          chunk = None

          async for chunk in response_stream:
            if not _validate_response(chunk):
              is_valid = False

            if (
                function_map
                and chunk.candidates
                and chunk.candidates[0].content
                and chunk.candidates[0].content.parts
            ):
              chunk_func_response_parts = (
                  await _extra_utils.get_function_response_parts_async(
                      chunk, function_map
                  )
              )
              if chunk_func_response_parts:
                func_response_parts.extend(chunk_func_response_parts)

            if chunk.candidates and chunk.candidates[0].content:
              model_output.append(chunk.candidates[0].content)
            if chunk.candidates and chunk.candidates[0].finish_reason:
              finish_reason = chunk.candidates[0].finish_reason
            yield chunk

          if not function_map or not func_response_parts:
            break

          logger.info(f"AFC remote call {i} is done.")
          remaining_remote_calls_afc -= 1
          if remaining_remote_calls_afc == 0:
            logger.info(
                "Reached max remote calls for automatic function calling."
            )

          func_response_content = types.Content(
              role="user", parts=func_response_parts
          )

          contents_to_model.extend(model_output)
          contents_to_model.append(func_response_content)

          self.record_history(
              user_input=user_input,
              model_output=model_output,
              is_valid=is_valid,
          )
          user_input = func_response_content

        self.record_history(
            user_input=user_input,
            model_output=model_output,
            is_valid=bool(
                is_valid
                and model_output
                and finish_reason is not None
            ),
        )

    return async_generator()  # type: ignore[no-untyped-call, no-any-return]


class AsyncChats:
  """A util class to create async chat sessions."""

  def __init__(self, modules: AsyncModels):
    self._modules = modules

  def create(
      self,
      *,
      model: str,
      config: Optional[GenerateContentConfigOrDict] = None,
      history: Optional[list[ContentOrDict]] = None,
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
