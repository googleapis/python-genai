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
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr, Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config

__all__ = ["GoogleMapsCallStepParam", "Arguments"]


class Arguments(TypedDict, total=False):
    """The arguments to pass to the Google Maps tool."""

    queries: SequenceNotStr[str]
    """The queries to be executed."""


class GoogleMapsCallStepParam(TypedDict, total=False):
    """Google Maps call step."""

    id: Required[str]
    """Required. A unique ID for this specific tool call."""

    type: Required[Literal["google_maps_call"]]

    arguments: Arguments
    """The arguments to pass to the Google Maps tool."""

    signature: Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]
    """A signature hash for backend validation."""


set_pydantic_config(GoogleMapsCallStepParam, {"arbitrary_types_allowed": True})
