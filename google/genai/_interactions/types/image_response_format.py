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

__all__ = ["ImageResponseFormat"]


class ImageResponseFormat(BaseModel):
    """Configuration for image output format."""

    type: Literal["image"]

    aspect_ratio: Optional[
        Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "1:8", "8:1", "1:4", "4:1"]
    ] = None
    """The aspect ratio for the image output."""

    delivery: Optional[Literal["inline", "uri"]] = None
    """The delivery mode for the image output."""

    image_size: Optional[Literal["512", "1K", "2K", "4K"]] = None
    """The size of the image output."""

    mime_type: Optional[Literal["image/jpeg"]] = None
    """The MIME type of the image output."""
