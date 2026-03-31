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

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["PlaceCitationParam", "ReviewSnippet"]


class ReviewSnippet(TypedDict, total=False):
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


class PlaceCitationParam(TypedDict, total=False):
    """A place citation annotation."""

    type: Required[Literal["place_citation"]]

    end_index: int
    """End of the attributed segment, exclusive."""

    name: str
    """Title of the place."""

    place_id: str
    """The ID of the place, in `places/{place_id}` format."""

    review_snippets: Iterable[ReviewSnippet]
    """
    Snippets of reviews that are used to generate answers about the
    features of a given place in Google Maps.
    """

    start_index: int
    """Start of segment of the response that is attributed to this source.

    Index indicates the start of the segment, measured in bytes.
    """

    url: str
    """URI reference of the place."""
