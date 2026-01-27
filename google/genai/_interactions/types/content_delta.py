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

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .annotation import Annotation
from .text_content import TextContent
from .image_content import ImageContent
from .audio_mime_type import AudioMimeType
from .image_mime_type import ImageMimeType
from .video_mime_type import VideoMimeType
from .document_mime_type import DocumentMimeType
from .url_context_result import URLContextResult
from .google_search_result import GoogleSearchResult
from .url_context_call_arguments import URLContextCallArguments
from .google_search_call_arguments import GoogleSearchCallArguments
from .code_execution_call_arguments import CodeExecutionCallArguments

__all__ = [
    "ContentDelta",
    "Delta",
    "DeltaTextDelta",
    "DeltaImageDelta",
    "DeltaAudioDelta",
    "DeltaDocumentDelta",
    "DeltaVideoDelta",
    "DeltaThoughtSummaryDelta",
    "DeltaThoughtSummaryDeltaContent",
    "DeltaThoughtSignatureDelta",
    "DeltaFunctionCallDelta",
    "DeltaFunctionResultDelta",
    "DeltaFunctionResultDeltaResult",
    "DeltaFunctionResultDeltaResultItems",
    "DeltaFunctionResultDeltaResultItemsItem",
    "DeltaCodeExecutionCallDelta",
    "DeltaCodeExecutionResultDelta",
    "DeltaURLContextCallDelta",
    "DeltaURLContextResultDelta",
    "DeltaGoogleSearchCallDelta",
    "DeltaGoogleSearchResultDelta",
    "DeltaMCPServerToolCallDelta",
    "DeltaMCPServerToolResultDelta",
    "DeltaMCPServerToolResultDeltaResult",
    "DeltaMCPServerToolResultDeltaResultItems",
    "DeltaMCPServerToolResultDeltaResultItemsItem",
    "DeltaFileSearchCallDelta",
    "DeltaFileSearchResultDelta",
    "DeltaFileSearchResultDeltaResult",
]


class DeltaTextDelta(BaseModel):
    type: Literal["text"]

    annotations: Optional[List[Annotation]] = None
    """Citation information for model-generated content."""

    text: Optional[str] = None


class DeltaImageDelta(BaseModel):
    type: Literal["image"]

    data: Optional[str] = None

    mime_type: Optional[ImageMimeType] = None
    """The mime type of the image."""

    resolution: Optional[Literal["low", "medium", "high", "ultra_high"]] = None
    """The resolution of the media."""

    uri: Optional[str] = None


class DeltaAudioDelta(BaseModel):
    type: Literal["audio"]

    data: Optional[str] = None

    mime_type: Optional[AudioMimeType] = None
    """The mime type of the audio."""

    uri: Optional[str] = None


class DeltaDocumentDelta(BaseModel):
    type: Literal["document"]

    data: Optional[str] = None

    mime_type: Optional[DocumentMimeType] = None
    """The mime type of the document."""

    uri: Optional[str] = None


class DeltaVideoDelta(BaseModel):
    type: Literal["video"]

    data: Optional[str] = None

    mime_type: Optional[VideoMimeType] = None
    """The mime type of the video."""

    resolution: Optional[Literal["low", "medium", "high", "ultra_high"]] = None
    """The resolution of the media."""

    uri: Optional[str] = None


DeltaThoughtSummaryDeltaContent: TypeAlias = Annotated[
    Union[TextContent, ImageContent], PropertyInfo(discriminator="type")
]


class DeltaThoughtSummaryDelta(BaseModel):
    type: Literal["thought_summary"]

    content: Optional[DeltaThoughtSummaryDeltaContent] = None
    """A text content block."""


class DeltaThoughtSignatureDelta(BaseModel):
    type: Literal["thought_signature"]

    signature: Optional[str] = None
    """Signature to match the backend source to be part of the generation."""


class DeltaFunctionCallDelta(BaseModel):
    type: Literal["function_call"]

    id: Optional[str] = None
    """A unique ID for this specific tool call."""

    arguments: Optional[Dict[str, object]] = None

    name: Optional[str] = None


DeltaFunctionResultDeltaResultItemsItem: TypeAlias = Union[TextContent, ImageContent, object]


class DeltaFunctionResultDeltaResultItems(BaseModel):
    items: Optional[List[DeltaFunctionResultDeltaResultItemsItem]] = None


DeltaFunctionResultDeltaResult: TypeAlias = Union[DeltaFunctionResultDeltaResultItems, str]


class DeltaFunctionResultDelta(BaseModel):
    type: Literal["function_result"]

    call_id: Optional[str] = None
    """ID to match the ID from the function call block."""

    is_error: Optional[bool] = None

    name: Optional[str] = None

    result: Optional[DeltaFunctionResultDeltaResult] = None
    """Tool call result delta."""


class DeltaCodeExecutionCallDelta(BaseModel):
    type: Literal["code_execution_call"]

    id: Optional[str] = None
    """A unique ID for this specific tool call."""

    arguments: Optional[CodeExecutionCallArguments] = None
    """The arguments to pass to the code execution."""


class DeltaCodeExecutionResultDelta(BaseModel):
    type: Literal["code_execution_result"]

    call_id: Optional[str] = None
    """ID to match the ID from the function call block."""

    is_error: Optional[bool] = None

    result: Optional[str] = None

    signature: Optional[str] = None


class DeltaURLContextCallDelta(BaseModel):
    type: Literal["url_context_call"]

    id: Optional[str] = None
    """A unique ID for this specific tool call."""

    arguments: Optional[URLContextCallArguments] = None
    """The arguments to pass to the URL context."""


class DeltaURLContextResultDelta(BaseModel):
    type: Literal["url_context_result"]

    call_id: Optional[str] = None
    """ID to match the ID from the function call block."""

    is_error: Optional[bool] = None

    result: Optional[List[URLContextResult]] = None

    signature: Optional[str] = None


class DeltaGoogleSearchCallDelta(BaseModel):
    type: Literal["google_search_call"]

    id: Optional[str] = None
    """A unique ID for this specific tool call."""

    arguments: Optional[GoogleSearchCallArguments] = None
    """The arguments to pass to Google Search."""


class DeltaGoogleSearchResultDelta(BaseModel):
    type: Literal["google_search_result"]

    call_id: Optional[str] = None
    """ID to match the ID from the function call block."""

    is_error: Optional[bool] = None

    result: Optional[List[GoogleSearchResult]] = None

    signature: Optional[str] = None


class DeltaMCPServerToolCallDelta(BaseModel):
    type: Literal["mcp_server_tool_call"]

    id: Optional[str] = None
    """A unique ID for this specific tool call."""

    arguments: Optional[Dict[str, object]] = None

    name: Optional[str] = None

    server_name: Optional[str] = None


DeltaMCPServerToolResultDeltaResultItemsItem: TypeAlias = Union[str, ImageContent, object]


class DeltaMCPServerToolResultDeltaResultItems(BaseModel):
    items: Optional[List[DeltaMCPServerToolResultDeltaResultItemsItem]] = None


DeltaMCPServerToolResultDeltaResult: TypeAlias = Union[DeltaMCPServerToolResultDeltaResultItems, str]


class DeltaMCPServerToolResultDelta(BaseModel):
    type: Literal["mcp_server_tool_result"]

    call_id: Optional[str] = None
    """ID to match the ID from the function call block."""

    name: Optional[str] = None

    result: Optional[DeltaMCPServerToolResultDeltaResult] = None
    """Tool call result delta."""

    server_name: Optional[str] = None


class DeltaFileSearchCallDelta(BaseModel):
    type: Literal["file_search_call"]

    id: Optional[str] = None
    """A unique ID for this specific tool call."""


class DeltaFileSearchResultDeltaResult(BaseModel):
    """The result of the File Search."""

    file_search_store: Optional[str] = None
    """The name of the file search store."""

    text: Optional[str] = None
    """The text of the search result."""

    title: Optional[str] = None
    """The title of the search result."""


class DeltaFileSearchResultDelta(BaseModel):
    type: Literal["file_search_result"]

    result: Optional[List[DeltaFileSearchResultDeltaResult]] = None


Delta: TypeAlias = Annotated[
    Union[
        DeltaTextDelta,
        DeltaImageDelta,
        DeltaAudioDelta,
        DeltaDocumentDelta,
        DeltaVideoDelta,
        DeltaThoughtSummaryDelta,
        DeltaThoughtSignatureDelta,
        DeltaFunctionCallDelta,
        DeltaFunctionResultDelta,
        DeltaCodeExecutionCallDelta,
        DeltaCodeExecutionResultDelta,
        DeltaURLContextCallDelta,
        DeltaURLContextResultDelta,
        DeltaGoogleSearchCallDelta,
        DeltaGoogleSearchResultDelta,
        DeltaMCPServerToolCallDelta,
        DeltaMCPServerToolResultDelta,
        DeltaFileSearchCallDelta,
        DeltaFileSearchResultDelta,
    ],
    PropertyInfo(discriminator="type"),
]


class ContentDelta(BaseModel):
    delta: Optional[Delta] = None

    event_id: Optional[str] = None
    """
    The event_id token to be used to resume the interaction stream, from this event.
    """

    event_type: Optional[Literal["content.delta"]] = None

    index: Optional[int] = None
