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

from .step import Step
from .._utils import PropertyInfo
from .._models import BaseModel
from .annotation import Annotation
from .error_event import ErrorEvent
from .content_stop import ContentStop
from .text_content import TextContent
from .content_delta import ContentDelta
from .content_start import ContentStart
from .image_content import ImageContent
from .interaction_start_event import InteractionStartEvent
from .interaction_status_update import InteractionStatusUpdate
from .interaction_complete_event import InteractionCompleteEvent

__all__ = [
    "InteractionSSEEvent",
    "StepStart",
    "StepDelta",
    "StepDeltaDelta",
    "StepDeltaDeltaText",
    "StepDeltaDeltaImage",
    "StepDeltaDeltaAudio",
    "StepDeltaDeltaDocument",
    "StepDeltaDeltaVideo",
    "StepDeltaDeltaThoughtSummary",
    "StepDeltaDeltaThoughtSummaryContent",
    "StepDeltaDeltaThoughtSignature",
    "StepDeltaDeltaTextAnnotationDelta",
    "StepDeltaDeltaArgumentsDelta",
    "StepStop",
]


class StepStart(BaseModel):
    event_type: Literal["step.start"]

    index: int

    step: Step
    """A step in the interaction."""

    event_id: Optional[str] = None
    """
    The event_id token to be used to resume the interaction stream, from this event.
    """


class StepDeltaDeltaText(BaseModel):
    text: str

    type: Literal["text"]


class StepDeltaDeltaImage(BaseModel):
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


class StepDeltaDeltaAudio(BaseModel):
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


class StepDeltaDeltaDocument(BaseModel):
    type: Literal["document"]

    data: Optional[str] = None

    mime_type: Optional[Literal["application/pdf"]] = None

    uri: Optional[str] = None


class StepDeltaDeltaVideo(BaseModel):
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


StepDeltaDeltaThoughtSummaryContent: TypeAlias = Annotated[
    Union[TextContent, ImageContent], PropertyInfo(discriminator="type")
]


class StepDeltaDeltaThoughtSummary(BaseModel):
    type: Literal["thought_summary"]

    content: Optional[StepDeltaDeltaThoughtSummaryContent] = None
    """A new summary item to be added to the thought."""


class StepDeltaDeltaThoughtSignature(BaseModel):
    type: Literal["thought_signature"]

    signature: Optional[str] = None
    """Signature to match the backend source to be part of the generation."""


class StepDeltaDeltaTextAnnotationDelta(BaseModel):
    type: Literal["text_annotation_delta"]

    annotations: Optional[List[Annotation]] = None
    """Citation information for model-generated content."""


class StepDeltaDeltaArgumentsDelta(BaseModel):
    type: Literal["arguments_delta"]

    partial_arguments: Optional[str] = None


StepDeltaDelta: TypeAlias = Annotated[
    Union[
        StepDeltaDeltaText,
        StepDeltaDeltaImage,
        StepDeltaDeltaAudio,
        StepDeltaDeltaDocument,
        StepDeltaDeltaVideo,
        StepDeltaDeltaThoughtSummary,
        StepDeltaDeltaThoughtSignature,
        StepDeltaDeltaTextAnnotationDelta,
        StepDeltaDeltaArgumentsDelta,
    ],
    PropertyInfo(discriminator="type"),
]


class StepDelta(BaseModel):
    delta: StepDeltaDelta

    event_type: Literal["step.delta"]

    index: int

    event_id: Optional[str] = None
    """
    The event_id token to be used to resume the interaction stream, from this event.
    """


class StepStop(BaseModel):
    event_type: Literal["step.stop"]

    index: int

    event_id: Optional[str] = None
    """
    The event_id token to be used to resume the interaction stream, from this event.
    """


InteractionSSEEvent: TypeAlias = Annotated[
    Union[
        InteractionStartEvent,
        InteractionCompleteEvent,
        InteractionStatusUpdate,
        ContentStart,
        ContentDelta,
        ContentStop,
        ErrorEvent,
        StepStart,
        StepDelta,
        StepStop,
    ],
    PropertyInfo(discriminator="event_type"),
]
