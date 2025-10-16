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
# mypy: ignore-errors

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .function_param import FunctionParam

__all__ = ["ToolParam", "GoogleSearch", "CodeExecution", "URLContext"]


class GoogleSearch(TypedDict, total=False):
    type: Required[Literal["google_search"]]


class CodeExecution(TypedDict, total=False):
    type: Required[Literal["code_execution"]]


class URLContext(TypedDict, total=False):
    type: Required[Literal["url_context"]]


ToolParam: TypeAlias = Union[FunctionParam, GoogleSearch, CodeExecution, URLContext]
