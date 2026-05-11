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

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["VideoResponseFormatParam"]


class VideoResponseFormatParam(TypedDict, total=False):
    """Configuration for video output format."""

    type: Required[Literal["video"]]

    aspect_ratio: Annotated[Literal["16:9", "9:16"], PropertyInfo(alias="aspectRatio")]
    """The aspect ratio for the video output."""

    delivery: Literal["inline", "uri"]
    """The delivery mode for the video output."""

    duration: str
    """The duration for the video output."""

    gcs_uri: Annotated[str, PropertyInfo(alias="gcsUri")]
    """The GCS URI to store the video output.

    Required for Vertex if delivery mode is URI.
    """
