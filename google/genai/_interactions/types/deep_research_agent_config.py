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

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DeepResearchAgentConfig"]


class DeepResearchAgentConfig(BaseModel):
    """Configuration for the Deep Research agent."""

    type: Literal["deep-research"]

    collaborative_planning: Optional[bool] = None
    """Enables human-in-the-loop planning for the Deep Research agent.

    If set to true, the Deep Research agent will provide a research plan in its
    response. The agent will then proceed only if the user confirms the plan in the
    next turn. Relevant issue: b/482352502.
    """

    thinking_summaries: Optional[Literal["auto", "none"]] = None
    """Whether to include thought summaries in the response."""

    visualization: Optional[Literal["off", "auto"]] = None
    """Whether to include visualizations in the response."""
