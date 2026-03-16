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
from .google_maps_result import GoogleMapsResult
from .url_context_result import URLContextResult
from .google_search_result import GoogleSearchResult
from .google_maps_call_arguments import GoogleMapsCallArguments
from .url_context_call_arguments import URLContextCallArguments
from .google_search_call_arguments import GoogleSearchCallArguments
from .code_execution_call_arguments import CodeExecutionCallArguments

__all__ = [
    "ContentDelta",
    "Delta",
    "DeltaText",
    "DeltaImage",
    "DeltaAudio",
    "DeltaDocument",
    "DeltaVideo",
    "DeltaThoughtSummary",
    "DeltaThoughtSummaryContent",
    "DeltaThoughtSignature",
    "DeltaFunctionCall",
    "DeltaFunctionResult",
    "DeltaFunctionResultResult",
    "DeltaFunctionResultResultItems",
    "DeltaFunctionResultResultItemsItem",
    "DeltaCodeExecutionCall",
    "DeltaCodeExecutionResult",
    "DeltaURLContextCall",
    "DeltaURLContextResult",
    "DeltaGoogleSearchCall",
    "DeltaGoogleSearchResult",
    "DeltaMCPServerToolCall",
    "DeltaMCPServerToolResult",
    "DeltaMCPServerToolResultResult",
    "DeltaMCPServerToolResultResultItems",
    "DeltaMCPServerToolResultResultItemsItem",
    "DeltaFileSearchCall",
    "DeltaFileSearchResult",
    "DeltaGoogleMapsCall",
    "DeltaGoogleMapsResult",
]


class DeltaText(BaseModel):
    text: str

    type: Literal["text"]

    annotations: Optional[List[Annotation]] = None
    """Citation information for model-generated content."""


class DeltaImage(BaseModel):
    type: Literal["image"]

    data: Optional[str] = None

    mime_type: Optional[Literal["image/png", "image/jpeg", "image/webp", "image/heic", "image/heif"]] = None

    resolution: Optional[Literal["low", "medium", "high", "ultra_high"]] = None
    """The resolution of the media."""

    uri: Optional[str] = None


class DeltaAudio(BaseModel):
    type: Literal["audio"]

    data: Optional[str] = None

    mime_type: Optional[Literal["audio/wav", "audio/mp3", "audio/aiff", "audio/aac", "audio/ogg", "audio/flac"]] = None

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


class DeltaFunctionCall(BaseModel):
    id: str
    """A unique ID for this specific tool call."""

    arguments: Dict[str, object]

    name: str

    type: Literal["function_call"]

    signature: Optional[str] = None
    """A signature hash for backend validation."""


DeltaFunctionResultResultItemsItem: TypeAlias = Union[TextContent, ImageContent]


class DeltaFunctionResultResultItems(BaseModel):
    items: Optional[List[DeltaFunctionResultResultItemsItem]] = None


DeltaFunctionResultResult: TypeAlias = Union[DeltaFunctionResultResultItems, str, object]


class DeltaFunctionResult(BaseModel):
    call_id: str
    """ID to match the ID from the function call block."""

    result: DeltaFunctionResultResult
    """Tool call result delta."""

    type: Literal["function_result"]

    is_error: Optional[bool] = None

    name: Optional[str] = None

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaCodeExecutionCall(BaseModel):
    id: str
    """A unique ID for this specific tool call."""

    arguments: CodeExecutionCallArguments
    """The arguments to pass to the code execution."""

    type: Literal["code_execution_call"]

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaCodeExecutionResult(BaseModel):
    call_id: str
    """ID to match the ID from the function call block."""

    result: str

    type: Literal["code_execution_result"]

    is_error: Optional[bool] = None

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaURLContextCall(BaseModel):
    id: str
    """A unique ID for this specific tool call."""

    arguments: URLContextCallArguments
    """The arguments to pass to the URL context."""

    type: Literal["url_context_call"]

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaURLContextResult(BaseModel):
    call_id: str
    """ID to match the ID from the function call block."""

    result: List[URLContextResult]

    type: Literal["url_context_result"]

    is_error: Optional[bool] = None

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaGoogleSearchCall(BaseModel):
    id: str
    """A unique ID for this specific tool call."""

    arguments: GoogleSearchCallArguments
    """The arguments to pass to Google Search."""

    type: Literal["google_search_call"]

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaGoogleSearchResult(BaseModel):
    call_id: str
    """ID to match the ID from the function call block."""

    result: List[GoogleSearchResult]

    type: Literal["google_search_result"]

    is_error: Optional[bool] = None

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaMCPServerToolCall(BaseModel):
    id: str
    """A unique ID for this specific tool call."""

    arguments: Dict[str, object]

    name: str

    server_name: str

    type: Literal["mcp_server_tool_call"]

    signature: Optional[str] = None
    """A signature hash for backend validation."""


DeltaMCPServerToolResultResultItemsItem: TypeAlias = Union[TextContent, ImageContent]


class DeltaMCPServerToolResultResultItems(BaseModel):
    items: Optional[List[DeltaMCPServerToolResultResultItemsItem]] = None


DeltaMCPServerToolResultResult: TypeAlias = Union[DeltaMCPServerToolResultResultItems, str, object]


class DeltaMCPServerToolResult(BaseModel):
    call_id: str
    """ID to match the ID from the function call block."""

    result: DeltaMCPServerToolResultResult
    """Tool call result delta."""

    type: Literal["mcp_server_tool_result"]

    name: Optional[str] = None

    server_name: Optional[str] = None

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaFileSearchCall(BaseModel):
    id: str
    """A unique ID for this specific tool call."""

    type: Literal["file_search_call"]

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaFileSearchResult(BaseModel):
    call_id: str
    """ID to match the ID from the function call block."""

    type: Literal["file_search_result"]

    result: Optional[List[object]] = None

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaGoogleMapsCall(BaseModel):
    id: str
    """A unique ID for this specific tool call."""

    type: Literal["google_maps_call"]

    arguments: Optional[GoogleMapsCallArguments] = None
    """The arguments to pass to the Google Maps tool."""

    signature: Optional[str] = None
    """A signature hash for backend validation."""


class DeltaGoogleMapsResult(BaseModel):
    call_id: str
    """ID to match the ID from the function call block."""

    result: List[GoogleMapsResult]
    """The results of the Google Maps."""

    type: Literal["google_maps_result"]

    signature: Optional[str] = None
    """A signature hash for backend validation."""


Delta: TypeAlias = Annotated[
    Union[
        DeltaText,
        DeltaImage,
        DeltaAudio,
        DeltaDocument,
        DeltaVideo,
        DeltaThoughtSummary,
        DeltaThoughtSignature,
        DeltaFunctionCall,
        DeltaFunctionResult,
        DeltaCodeExecutionCall,
        DeltaCodeExecutionResult,
        DeltaURLContextCall,
        DeltaURLContextResult,
        DeltaGoogleSearchCall,
        DeltaGoogleSearchResult,
        DeltaMCPServerToolCall,
        DeltaMCPServerToolResult,
        DeltaFileSearchCall,
        DeltaFileSearchResult,
        DeltaGoogleMapsCall,
        DeltaGoogleMapsResult,
    ],
    PropertyInfo(discriminator="type"),
]


class ContentDelta(BaseModel):
    delta: Delta

    event_type: Literal["content.delta"]

    index: int

    event_id: Optional[str] = None
    """
    The event_id token to be used to resume the interaction stream, from this event.
    """
