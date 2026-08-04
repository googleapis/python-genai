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

"""Utils for working with MCP tools."""
import contextlib
import httpx
import sys

from importlib.metadata import PackageNotFoundError, version
import typing
from typing import Any, Optional, Sequence, Union

import google.auth
from google.auth.transport.requests import Request

from . import _common
from . import types
from ._api_client import _MULTI_REGIONAL_LOCATIONS

if sys.version_info >= (3, 10):
  from typing import TypeGuard
else:
  from typing_extensions import TypeGuard

def _is_mcp_loaded() -> bool:
  return "mcp" in sys.modules

if typing.TYPE_CHECKING:
  from mcp.types import Tool as McpTool
  from mcp import ClientSession as McpClientSession
  from mcp.client.streamable_http import streamable_http_client
  from mcp.shared._httpx_utils import create_mcp_http_client
else:
  McpClientSession: typing.Type = Any
  McpTool: typing.Type = Any
  streamable_http_client: Any = None
  create_mcp_http_client: Any = None


class AllowedToolsMcpSession:
  """Wraps an MCP ``ClientSession`` with an allowlist of tool names.

  Use :func:`with_allowed_tools` to construct instances. Filtering happens in
  ``list_tools`` so function declarations and the AFC adapter map stay aligned.
  """

  def __init__(self, session: Any, allowed_tools: Sequence[str]):
    if not allowed_tools:
      raise ValueError(
          'allowed_tools must be a non-empty sequence of tool names.'
      )
    self._session = session
    self._allowed_tools = set(allowed_tools)

  @property
  def allowed_tools(self) -> set[str]:
    return set(self._allowed_tools)

  @property
  def session(self) -> Any:
    return self._session

  async def list_tools(self) -> Any:
    """Returns session tools filtered to the allowlist."""
    try:
      from mcp import types as mcp_types
    except ImportError as e:
      raise ImportError(
          'The mcp package is required to use with_allowed_tools.'
      ) from e

    result = await self._session.list_tools()
    available = {tool.name for tool in result.tools}
    missing = sorted(self._allowed_tools - available)
    if missing:
      raise ValueError(
          'allowed_tools includes tool names not provided by the MCP session:'
          f' {missing}. Available tools: {sorted(available)}.'
      )
    filtered = [
        tool for tool in result.tools if tool.name in self._allowed_tools
    ]
    return mcp_types.ListToolsResult(tools=filtered)

  async def call_tool(
      self,
      name: str,
      arguments: Optional[dict[str, Any]] = None,
  ) -> Any:
    """Calls a tool on the underlying session if it is allowlisted."""
    if name not in self._allowed_tools:
      raise ValueError(
          f'Tool {name!r} is not in allowed_tools'
          f' {sorted(self._allowed_tools)}.'
      )
    return await self._session.call_tool(
        name=name, arguments=arguments if arguments is not None else {}
    )


def with_allowed_tools(
    session: Any, allowed_tools: Sequence[str]
) -> AllowedToolsMcpSession:
  """Returns an MCP session wrapper that exposes only ``allowed_tools``.

  Example::

    from google.genai import mcp as genai_mcp

    config = types.GenerateContentConfig(
        tools=[genai_mcp.with_allowed_tools(session, ['tool_a', 'tool_b'])],
    )
  """
  return AllowedToolsMcpSession(session, allowed_tools)


def is_mcp_client_session(
    obj: Any,
) -> TypeGuard[Union[McpClientSession, AllowedToolsMcpSession]]:
  """Returns True if ``obj`` is an MCP ClientSession or allowlist wrapper."""
  if isinstance(obj, AllowedToolsMcpSession):
    return True
  if not _is_mcp_loaded():
    return False
  try:
    from mcp import ClientSession as _McpClientSession
  except ImportError:
    return False
  return isinstance(obj, _McpClientSession)

def mcp_to_gemini_tool(tool: McpTool) -> types.Tool:
  """Translates an MCP tool to a Google GenAI tool."""
  return types.Tool(
      function_declarations=[{
          "name": tool.name,
          "description": tool.description,
          "parameters": types.Schema.from_json_schema(
              json_schema=types.JSONSchema(
                  **_filter_to_supported_schema(tool.inputSchema)
              )
          ),
      }]
  )


def agent_platform_to_gemini_tool(tool: McpTool) -> types.Tool:
  """Translates an Agent Platform tool to a Google GenAI tool."""
  return types.Tool(
      function_declarations=[
          {
              "name": tool.name,
              "description": tool.description,
              "parameters_json_schema": tool.inputSchema,
          }
      ]
  )


def mcp_to_gemini_tools(
    tools: list[McpTool],
    is_agent_platform: bool = False,
) -> list[types.Tool]:
  """Translates a list of MCP tools to a list of Google GenAI tools."""
  if is_agent_platform:
    return [agent_platform_to_gemini_tool(tool) for tool in tools]
  return [mcp_to_gemini_tool(tool) for tool in tools]


def has_mcp_tool_usage(tools: types.ToolListUnion) -> bool:
  """Checks whether the list of tools contains any MCP tools or sessions."""
  for tool in tools:
    if is_mcp_client_session(tool):
      return True
  if not _is_mcp_loaded():
    return False
  try:
    from mcp.types import Tool as _McpTool
  except ImportError:
    _McpTool = type('DummyTool', (), {})  # type: ignore

  for tool in tools:
    if isinstance(tool, _McpTool):
      return True
  return False


def has_mcp_session_usage(tools: types.ToolListUnion) -> bool:
  """Checks whether the list of tools contains any MCP sessions."""
  for tool in tools:
    if is_mcp_client_session(tool):
      return True
  return False


def set_mcp_usage_header(headers: dict[str, str]) -> None:
  """Sets the MCP version label in the Google API client header."""
  if not _is_mcp_loaded():
    return
  try:
    version_label = version("mcp")
  except PackageNotFoundError:
    version_label = "0.0.0"
  existing_header = headers.get("x-goog-api-client", "")
  headers["x-goog-api-client"] = (
      existing_header + f" mcp_used/{version_label}"
  ).lstrip()


def _filter_to_supported_schema(
    schema: _common.StringDict,
) -> _common.StringDict:
  """Filters the schema to only include fields that are supported by JSONSchema."""
  supported_fields: set[str] = set(types.JSONSchema.model_fields.keys())

  supported_fields.update([
      "additionalProperties", "anyOf", "oneOf", "$defs", "$ref"
  ])

  schema_field_names = (
      "items",
      "additionalProperties",
      "additional_properties",
  )
  list_schema_field_names = ("anyOf", "any_of", "oneOf", "one_of")
  dict_schema_field_names = ("properties", "defs", "$defs")

  filtered_schema: dict[str, Any] = {}
  for field_name, field_value in schema.items():
    if field_name in schema_field_names:
      filtered_schema[field_name] = _filter_to_supported_schema(field_value)
    elif field_name in list_schema_field_names:
      filtered_schema[field_name] = [
          _filter_to_supported_schema(value) for value in field_value
      ]
    elif field_name in dict_schema_field_names:
      filtered_schema[field_name] = {
          key: _filter_to_supported_schema(value)
          for key, value in field_value.items()
      }
    elif field_name in supported_fields:
      filtered_schema[field_name] = field_value

  return filtered_schema

@contextlib.asynccontextmanager
async def _connect_agent_platform_mcp(api_client: Any, toolset_name: str) -> typing.AsyncIterator[Any]:
  """Internal helper to manage the Agent Platform MCP lifecycle per request."""
  if streamable_http_client is None:
    raise ImportError(
      "The 'mcp' package is required to use Agent Platform MCP servers."
    )

  base_url = None
  if hasattr(api_client, '_http_options') and hasattr(api_client._http_options, 'base_url'):
    base_url = api_client._http_options.base_url

  if base_url:
    if base_url.endswith("/"):
      base_url = base_url[:-1]
    mcp_url = f"{base_url}/mcp/{toolset_name}"
  else:
    location = getattr(api_client, "location", "global")
    if location == "global":
      mcp_url = f"https://aiplatform.googleapis.com/mcp/{toolset_name}"
    elif location in _MULTI_REGIONAL_LOCATIONS:
      mcp_url = f"https://aiplatform.{location}.rep.googleapis.com/mcp/{toolset_name}"
    else:
      mcp_url = f"https://{location}-aiplatform.googleapis.com/mcp/{toolset_name}"

  token = await api_client._async_access_token()
  project = getattr(api_client, "project", None)

  headers = {}
  if hasattr(api_client, "_http_options") and api_client._http_options and api_client._http_options.headers:
    headers = dict(api_client._http_options.headers)

  headers["Authorization"] = f"Bearer {token}"
  if project:
    headers["X-Goog-User-Project"] = project

  set_mcp_usage_header(headers)

  http_client = httpx.AsyncClient(headers=headers, timeout=None)

  try:
    async with http_client:
      async with streamable_http_client(
          url=mcp_url, http_client=http_client
      ) as streams:
        read_stream, write_stream, _ = streams
        async with McpClientSession(read_stream, write_stream) as session:
          await session.initialize()
          try:
            yield session
          except GeneratorExit:
            return

  except BaseException as eg:

    error_messages = []

    def _extract_errors(exc: Any) -> None:
      # Handle potentially nested ExceptionGroups
      if hasattr(exc, "exceptions"):
        for e in exc.exceptions:
          _extract_errors(e)
      else:
        msg = f"{type(exc).__name__}: {str(exc)}"
        if hasattr(exc, "response") and exc.response is not None:
          status = getattr(
              exc.response,
              "status_code",
              getattr(exc.response, "status", "Unknown"),
          )
          text = getattr(exc.response, "text", str(exc.response))
          if callable(text):
            text = str(exc.response)
          msg += f" (HTTP {status}: {text})"
        error_messages.append(msg)

    if type(eg).__name__ in ("ExceptionGroup", "BaseExceptionGroup") or hasattr(
        eg, "exceptions"
    ):
      _extract_errors(eg)
      raise ValueError(
          f"Failed to connect to Agent Platform MCP Server at {mcp_url}.\n"
          f"Underlying errors: {error_messages}"
      ) from eg
