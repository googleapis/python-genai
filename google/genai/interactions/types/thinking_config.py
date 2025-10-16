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

__all__ = ["ThinkingConfig"]


class ThinkingConfig(BaseModel):
    include_thoughts: Optional[bool] = FieldInfo(alias="includeThoughts", default=None)
    """
    Whether to include internal thoughts in the response, if available, default
    true.
    """

    thinking_budget: Optional[int] = FieldInfo(alias="thinkingBudget", default=None)
    """The number of thoughts tokens the model should generate."""
