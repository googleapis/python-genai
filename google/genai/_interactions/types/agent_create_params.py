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

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .environment_param import EnvironmentParam
from .allowed_tools_param import AllowedToolsParam

__all__ = [
    "AgentCreateParams",
    "BaseEnvironment",
    "Tool",
    "ToolCodeExecution",
    "ToolGoogleSearch",
    "ToolURLContext",
    "ToolMCPServer",
]


class AgentCreateParams(TypedDict, total=False):
    api_version: str

    id: str
    """The unique identifier for the agent."""

    base_agent: str
    """The base agent to extend."""

    base_environment: BaseEnvironment
    """The environment configuration for the agent."""

    description: str
    """Agent description for developers to quickly read and understand."""

    system_instruction: str
    """System instruction for the agent."""

    tools: Iterable[Tool]
    """The tools available to the agent."""


BaseEnvironment: TypeAlias = Union[str, EnvironmentParam]


class ToolCodeExecution(TypedDict, total=False):
    """A tool that can be used by the model to execute code."""

    type: Required[Literal["code_execution"]]


class ToolGoogleSearch(TypedDict, total=False):
    """A tool that can be used by the model to search Google."""

    type: Required[Literal["google_search"]]

    search_types: List[Literal["web_search", "image_search", "enterprise_web_search"]]
    """The types of search grounding to enable."""


class ToolURLContext(TypedDict, total=False):
    """A tool that can be used by the model to fetch URL context."""

    type: Required[Literal["url_context"]]


class ToolMCPServer(TypedDict, total=False):
    """A MCPServer is a server that can be called by the model to perform actions."""

    type: Required[Literal["mcp_server"]]

    allowed_tools: Iterable[AllowedToolsParam]
    """The allowed tools."""

    headers: Dict[str, str]
    """Optional: Fields for authentication headers, timeouts, etc., if needed."""

    name: str
    """The name of the MCPServer."""

    url: str
    """The full URL for the MCPServer endpoint. Example: "https://api.example.com/mcp" """


Tool: TypeAlias = Union[ToolCodeExecution, ToolGoogleSearch, ToolURLContext, ToolMCPServer]
