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

from typing import Union
from typing_extensions import Annotated, TypeAlias

from .._utils import PropertyInfo
from .thought_step import ThoughtStep
from .user_input_step import UserInputStep
from .model_output_step import ModelOutputStep
from .function_call_step import FunctionCallStep
from .function_result_step import FunctionResultStep
from .file_search_call_step import FileSearchCallStep
from .google_maps_call_step import GoogleMapsCallStep
from .url_context_call_step import URLContextCallStep
from .file_search_result_step import FileSearchResultStep
from .google_maps_result_step import GoogleMapsResultStep
from .google_search_call_step import GoogleSearchCallStep
from .url_context_result_step import URLContextResultStep
from .code_execution_call_step import CodeExecutionCallStep
from .google_search_result_step import GoogleSearchResultStep
from .mcp_server_tool_call_step import MCPServerToolCallStep
from .code_execution_result_step import CodeExecutionResultStep
from .mcp_server_tool_result_step import MCPServerToolResultStep

__all__ = ["Step"]

Step: TypeAlias = Annotated[
    Union[
        UserInputStep,
        ModelOutputStep,
        ThoughtStep,
        FunctionCallStep,
        CodeExecutionCallStep,
        URLContextCallStep,
        MCPServerToolCallStep,
        GoogleSearchCallStep,
        FileSearchCallStep,
        GoogleMapsCallStep,
        FunctionResultStep,
        CodeExecutionResultStep,
        URLContextResultStep,
        GoogleSearchResultStep,
        MCPServerToolResultStep,
        FileSearchResultStep,
        GoogleMapsResultStep,
    ],
    PropertyInfo(discriminator="type"),
]
