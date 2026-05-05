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

from typing import Union
from typing_extensions import TypeAlias

from .thought_step_param import ThoughtStepParam
from .user_input_step_param import UserInputStepParam
from .model_output_step_param import ModelOutputStepParam
from .function_call_step_param import FunctionCallStepParam
from .function_result_step_param import FunctionResultStepParam
from .file_search_call_step_param import FileSearchCallStepParam
from .google_maps_call_step_param import GoogleMapsCallStepParam
from .url_context_call_step_param import URLContextCallStepParam
from .file_search_result_step_param import FileSearchResultStepParam
from .google_maps_result_step_param import GoogleMapsResultStepParam
from .google_search_call_step_param import GoogleSearchCallStepParam
from .url_context_result_step_param import URLContextResultStepParam
from .code_execution_call_step_param import CodeExecutionCallStepParam
from .google_search_result_step_param import GoogleSearchResultStepParam
from .mcp_server_tool_call_step_param import MCPServerToolCallStepParam
from .code_execution_result_step_param import CodeExecutionResultStepParam
from .mcp_server_tool_result_step_param import MCPServerToolResultStepParam

__all__ = ["StepParam"]

StepParam: TypeAlias = Union[
    UserInputStepParam,
    ModelOutputStepParam,
    ThoughtStepParam,
    FunctionCallStepParam,
    CodeExecutionCallStepParam,
    URLContextCallStepParam,
    MCPServerToolCallStepParam,
    GoogleSearchCallStepParam,
    FileSearchCallStepParam,
    GoogleMapsCallStepParam,
    FunctionResultStepParam,
    CodeExecutionResultStepParam,
    URLContextResultStepParam,
    GoogleSearchResultStepParam,
    MCPServerToolResultStepParam,
    FileSearchResultStepParam,
    GoogleMapsResultStepParam,
]
