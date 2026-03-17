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

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["PlaceCitation", "ReviewSnippet"]


class ReviewSnippet(BaseModel):
    """
    Encapsulates a snippet of a user review that answers a question about
    the features of a specific place in Google Maps.
    """

    review_id: Optional[str] = None
    """The ID of the review snippet."""

    title: Optional[str] = None
    """Title of the review."""

    url: Optional[str] = None
    """A link that corresponds to the user review on Google Maps."""


class PlaceCitation(BaseModel):
    """A place citation annotation."""

    type: Literal["place_citation"]

    end_index: Optional[int] = None
    """End of the attributed segment, exclusive."""

    name: Optional[str] = None
    """Title of the place."""

    place_id: Optional[str] = None
    """The ID of the place, in `places/{place_id}` format."""

    review_snippets: Optional[List[ReviewSnippet]] = None
    """
    Snippets of reviews that are used to generate answers about the
    features of a given place in Google Maps.
    """

    start_index: Optional[int] = None
    """Start of segment of the response that is attributed to this source."""

    url: Optional[str] = None
    """URI reference of the place."""
