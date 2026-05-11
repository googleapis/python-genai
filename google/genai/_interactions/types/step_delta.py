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

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .annotation import Annotation
from .text_content import TextContent
from .image_content import ImageContent

__all__ = [
    "StepDelta",
    "Delta",
    "DeltaText",
    "DeltaImage",
    "DeltaAudio",
    "DeltaDocument",
    "DeltaVideo",
    "DeltaThoughtSummary",
    "DeltaThoughtSummaryContent",
    "DeltaThoughtSignature",
    "DeltaTextAnnotationDelta",
    "DeltaArgumentsDelta",
]


class DeltaText(BaseModel):
    text: str

    type: Literal["text"]


class DeltaImage(BaseModel):
    type: Literal["image"]

    data: Optional[str] = None

    mime_type: Optional[
        Literal[
            "image/png", "image/jpeg", "image/webp", "image/heic", "image/heif", "image/gif", "image/bmp", "image/tiff"
        ]
    ] = None

    resolution: Optional[Literal["low", "medium", "high", "ultra_high"]] = None
    """The resolution of the media."""

    uri: Optional[str] = None


class DeltaAudio(BaseModel):
    type: Literal["audio"]

    channels: Optional[int] = None
    """The number of audio channels."""

    data: Optional[str] = None

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

    rate: Optional[int] = None
    """Deprecated. Use sample_rate instead. The value is ignored."""

    sample_rate: Optional[int] = None
    """The sample rate of the audio."""

    uri: Optional[str] = None


class DeltaDocument(BaseModel):
    type: Literal["document"]

    data: Optional[str] = None

    mime_type: Optional[Literal["application/pdf"]] = None

    uri: Optional[str] = None


class DeltaVideo(BaseModel):
    type: Literal["video"]

    data: Optional[str] = None

    mime_type: Optional[
        Literal[
            "video/mp4",
            "video/mpeg",
            "video/mpg",
            "video/mov",
            "video/avi",
            "video/x-flv",
            "video/webm",
            "video/wmv",
            "video/3gpp",
        ]
    ] = None

    resolution: Optional[Literal["low", "medium", "high", "ultra_high"]] = None
    """The resolution of the media."""

    uri: Optional[str] = None


DeltaThoughtSummaryContent: TypeAlias = Annotated[Union[TextContent, ImageContent], PropertyInfo(discriminator="type")]


class DeltaThoughtSummary(BaseModel):
    type: Literal["thought_summary"]

    content: Optional[DeltaThoughtSummaryContent] = None
    """A new summary item to be added to the thought."""


class DeltaThoughtSignature(BaseModel):
    type: Literal["thought_signature"]

    signature: Optional[str] = None
    """Signature to match the backend source to be part of the generation."""


class DeltaTextAnnotationDelta(BaseModel):
    type: Literal["text_annotation_delta"]

    annotations: Optional[List[Annotation]] = None
    """Citation information for model-generated content."""


class DeltaArgumentsDelta(BaseModel):
    type: Literal["arguments_delta"]

    partial_arguments: Optional[str] = None


Delta: TypeAlias = Annotated[
    Union[
        DeltaText,
        DeltaImage,
        DeltaAudio,
        DeltaDocument,
        DeltaVideo,
        DeltaThoughtSummary,
        DeltaThoughtSignature,
        DeltaTextAnnotationDelta,
        DeltaArgumentsDelta,
    ],
    PropertyInfo(discriminator="type"),
]


class StepDelta(BaseModel):
    delta: Delta

    event_type: Literal["step.delta"]

    index: int

    event_id: Optional[str] = None
    """
    The event_id token to be used to resume the interaction stream, from this event.
    """
