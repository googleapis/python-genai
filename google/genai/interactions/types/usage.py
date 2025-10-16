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

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Usage"]


class Usage(BaseModel):
    cached_tokens: Optional[int] = FieldInfo(alias="cachedTokens", default=None)
    """Number of tokens in the cached part of the prompt (the cached content)."""

    input_tokens: Optional[int] = FieldInfo(alias="inputTokens", default=None)
    """Number of tokens in the prompt (context)."""

    output_tokens: Optional[int] = FieldInfo(alias="outputTokens", default=None)
    """Total number of tokens across all the generated response candidates."""

    reasoning_tokens: Optional[int] = FieldInfo(alias="reasoningTokens", default=None)
    """Number of tokens of thoughts for thinking models."""

    tool_use_tokens: Optional[int] = FieldInfo(alias="toolUseTokens", default=None)
    """Number of tokens present in tool-use prompt(s)."""

    total_tokens: Optional[int] = FieldInfo(alias="totalTokens", default=None)
    """
    Total token count for the interaction request (prompt + response
    candidates + other internal tokens).
    """
