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

from .._models import BaseModel

__all__ = ["GoogleMapsResult", "Place", "PlaceReviewSnippet"]


class PlaceReviewSnippet(BaseModel):
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


class Place(BaseModel):
    name: Optional[str] = None
    """Title of the place."""

    place_id: Optional[str] = None
    """The ID of the place, in `places/{place_id}` format."""

    review_snippets: Optional[List[PlaceReviewSnippet]] = None
    """
    Snippets of reviews that are used to generate answers about the
    features of a given place in Google Maps.
    """

    url: Optional[str] = None
    """URI reference of the place."""


class GoogleMapsResult(BaseModel):
    """The result of the Google Maps."""

    places: Optional[List[Place]] = None
    """The places that were found."""

    widget_context_token: Optional[str] = None
    """Resource name of the Google Maps widget context token."""
