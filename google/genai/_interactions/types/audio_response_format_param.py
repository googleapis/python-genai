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

from typing_extensions import Literal, Required, TypedDict

__all__ = ["AudioResponseFormatParam"]


class AudioResponseFormatParam(TypedDict, total=False):
    """Configuration for audio output format."""

    type: Required[Literal["audio"]]

    bit_rate: int
    """Bit rate in bits per second (bps).

    Only applicable for compressed formats (MP3, Opus).
    """

    delivery: Literal["inline", "uri"]
    """The delivery mode for the audio output."""

    mime_type: Literal["audio/mp3", "audio/ogg_opus", "audio/l16", "audio/wav", "audio/alaw", "audio/mulaw"]
    """The MIME type of the audio output."""

    sample_rate: int
    """Sample rate in Hz."""
