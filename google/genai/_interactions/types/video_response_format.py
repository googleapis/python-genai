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

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["VideoResponseFormat"]


class VideoResponseFormat(BaseModel):
    """Configuration for video output format."""

    type: Literal["video"]

    aspect_ratio: Optional[Literal["16:9", "9:16"]] = FieldInfo(alias="aspectRatio", default=None)
    """The aspect ratio for the video output."""

    delivery: Optional[Literal["inline", "uri"]] = None
    """The delivery mode for the video output."""

    duration: Optional[str] = None
    """The duration for the video output."""

    gcs_uri: Optional[str] = FieldInfo(alias="gcsUri", default=None)
    """The GCS URI to store the video output.

    Required for Vertex if delivery mode is URI.
    """
