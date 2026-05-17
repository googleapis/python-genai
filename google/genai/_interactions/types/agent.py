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

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .environment import Environment
from .allowed_tools import AllowedTools

__all__ = [
    "Agent",
    "BaseEnvironment",
    "Tool",
    "ToolCodeExecution",
    "ToolGoogleSearch",
    "ToolURLContext",
    "ToolMCPServer",
]

BaseEnvironment: TypeAlias = Union[str, Environment]


class ToolCodeExecution(BaseModel):
    """A tool that can be used by the model to execute code."""

    type: Literal["code_execution"]


class ToolGoogleSearch(BaseModel):
    """A tool that can be used by the model to search Google."""

    type: Literal["google_search"]

    search_types: Optional[List[Literal["web_search", "image_search", "enterprise_web_search"]]] = None
    """The types of search grounding to enable."""


class ToolURLContext(BaseModel):
    """A tool that can be used by the model to fetch URL context."""

    type: Literal["url_context"]


class ToolMCPServer(BaseModel):
    """A MCPServer is a server that can be called by the model to perform actions."""

    type: Literal["mcp_server"]

    allowed_tools: Optional[List[AllowedTools]] = None
    """The allowed tools."""

    headers: Optional[Dict[str, str]] = None
    """Optional: Fields for authentication headers, timeouts, etc., if needed."""

    name: Optional[str] = None
    """The name of the MCPServer."""

    url: Optional[str] = None
    """The full URL for the MCPServer endpoint. Example: "https://api.example.com/mcp" """


Tool: TypeAlias = Annotated[
    Union[ToolCodeExecution, ToolGoogleSearch, ToolURLContext, ToolMCPServer], PropertyInfo(discriminator="type")
]


class Agent(BaseModel):
    """
    An agent definition for the CreateAgent API.
    This message is the target for annotation-parser-based JSON parsing.
    New format:
      {
        "id": "customer-sentinel",
        "base_agent": "",
        "system_instruction": "...",
        "base_environment": { "type": "remote", "sources": [...] },
        "tools": [ {"type": "code_execution"} ]
      }
    """

    id: Optional[str] = None
    """The unique identifier for the agent."""

    base_agent: Optional[str] = None
    """The base agent to extend."""

    base_environment: Optional[BaseEnvironment] = None
    """The environment configuration for the agent."""

    description: Optional[str] = None
    """Agent description for developers to quickly read and understand."""

    system_instruction: Optional[str] = None
    """System instruction for the agent."""

    tools: Optional[List[Tool]] = None
    """The tools available to the agent."""
