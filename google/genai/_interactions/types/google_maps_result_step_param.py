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

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config

__all__ = ["GoogleMapsResultStepParam", "Result", "ResultPlace", "ResultPlaceReviewSnippet"]


class ResultPlaceReviewSnippet(TypedDict, total=False):
    """
    Encapsulates a snippet of a user review that answers a question about
    the features of a specific place in Google Maps.
    """

    review_id: str
    """The ID of the review snippet."""

    title: str
    """Title of the review."""

    url: str
    """A link that corresponds to the user review on Google Maps."""


class ResultPlace(TypedDict, total=False):
    name: str

    place_id: str

    review_snippets: Iterable[ResultPlaceReviewSnippet]

    url: str


class Result(TypedDict, total=False):
    """The result of the Google Maps."""

    places: Iterable[ResultPlace]

    widget_context_token: str


class GoogleMapsResultStepParam(TypedDict, total=False):
    """Google Maps result step."""

    call_id: Required[str]
    """Required. ID to match the ID from the function call block."""

    result: Required[Iterable[Result]]

    type: Required[Literal["google_maps_result"]]

    signature: Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]
    """A signature hash for backend validation."""


set_pydantic_config(GoogleMapsResultStepParam, {"arbitrary_types_allowed": True})
