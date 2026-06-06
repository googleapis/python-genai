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

__all__ = ["AudioResponseFormat"]


class AudioResponseFormat(BaseModel):
    """Configuration for audio output format."""

    type: Literal["audio"]

    bit_rate: Optional[int] = None
    """Bit rate in bits per second (bps).

    Only applicable for compressed formats (MP3, Opus).
    """

    delivery: Optional[Literal["inline", "uri"]] = None
    """The delivery mode for the audio output."""

    mime_type: Optional[
        Literal["audio/mp3", "audio/ogg_opus", "audio/l16", "audio/wav", "audio/alaw", "audio/mulaw"]
    ] = None
    """The MIME type of the audio output."""

    sample_rate: Optional[int] = None
    """Sample rate in Hz."""
