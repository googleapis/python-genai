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

__all__ = ["AudioContent"]


class AudioContent(BaseModel):
    """An audio content block."""

    type: Literal["audio"]

    channels: Optional[int] = None
    """The number of audio channels."""

    data: Optional[str] = None
    """The audio content."""

    mime_type: Optional[
        Literal[
            "audio/wav",
            "audio/mp3",
            "audio/aiff",
            "audio/aac",
            "audio/ogg",
            "audio/flac",
            "audio/mpeg",
            "audio/m4a",
            "audio/l16",
            "audio/opus",
            "audio/alaw",
            "audio/mulaw",
        ]
    ] = None
    """The mime type of the audio."""

    sample_rate: Optional[int] = None
    """The sample rate of the audio."""

    uri: Optional[str] = None
    """The URI of the audio."""
