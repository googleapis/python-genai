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
# mypy: ignore-errors

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from .._utils import PropertyInfo
from .._models import BaseModel
from .text_content import TextContent
from .audio_content import AudioContent
from .image_content import ImageContent
from .video_content import VideoContent
from .thought_content import ThoughtContent
from .document_content import DocumentContent

__all__ = [
    "Turn",
    "ContentUnionMember1",
    "ContentUnionMember1FunctionCallContent",
    "ContentUnionMember1FunctionResultContent",
    "ContentUnionMember1CodeExecutionCallContent",
    "ContentUnionMember1CodeExecutionCallContentArguments",
    "ContentUnionMember1CodeExecutionResultContent",
    "ContentUnionMember1URLContextCallContent",
    "ContentUnionMember1URLContextCallContentArguments",
    "ContentUnionMember1URLContextResultContent",
    "ContentUnionMember1URLContextResultContentResult",
    "ContentUnionMember1GoogleSearchCallContent",
    "ContentUnionMember1GoogleSearchCallContentArguments",
    "ContentUnionMember1GoogleSearchResultContent",
    "ContentUnionMember1GoogleSearchResultContentResult",
]


class ContentUnionMember1FunctionCallContent(BaseModel):
    type: Literal["function_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[Dict[str, object]] = None
    """The arguments to pass to the function."""

    name: Optional[str] = None
    """The name of the tool to call."""


class ContentUnionMember1FunctionResultContent(BaseModel):
    type: Literal["function_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the tool call resulted in an error."""

    name: Optional[str] = None
    """The name of the tool that was called."""

    result: Union[str, object, None] = None
    """The result of the tool call."""


class ContentUnionMember1CodeExecutionCallContentArguments(BaseModel):
    code: Optional[str] = None
    """The code to be executed."""

    language: Optional[Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]] = None
    """Programming language of the `code`."""


class ContentUnionMember1CodeExecutionCallContent(BaseModel):
    type: Literal["code_execution_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[ContentUnionMember1CodeExecutionCallContentArguments] = None
    """The arguments to pass to the code execution."""


class ContentUnionMember1CodeExecutionResultContent(BaseModel):
    type: Literal["code_execution_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the code execution resulted in an error."""

    result: Optional[str] = None
    """The output of the code execution."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """A signature hash for backend validation."""


class ContentUnionMember1URLContextCallContentArguments(BaseModel):
    urls: Optional[List[str]] = None
    """The URLs to fetch."""


class ContentUnionMember1URLContextCallContent(BaseModel):
    type: Literal["url_context_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[ContentUnionMember1URLContextCallContentArguments] = None
    """The arguments to pass to the URL context."""


class ContentUnionMember1URLContextResultContentResult(BaseModel):
    status: Optional[Literal["STATUS_UNSPECIFIED", "SUCCESS", "ERROR", "PAYWALL", "UNSAFE"]] = None
    """The status of the URL retrieval."""

    url: Optional[str] = None
    """The URL that was fetched."""


class ContentUnionMember1URLContextResultContent(BaseModel):
    type: Literal["url_context_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the URL context resulted in an error."""

    result: Optional[List[ContentUnionMember1URLContextResultContentResult]] = None
    """The results of the URL context."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the URL context result."""


class ContentUnionMember1GoogleSearchCallContentArguments(BaseModel):
    queries: Optional[List[str]] = None
    """Web search queries for the following-up web search."""


class ContentUnionMember1GoogleSearchCallContent(BaseModel):
    type: Literal["google_search_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[ContentUnionMember1GoogleSearchCallContentArguments] = None
    """The arguments to pass to Google Search."""


class ContentUnionMember1GoogleSearchResultContentResult(BaseModel):
    rendered_content: Optional[str] = FieldInfo(alias="renderedContent", default=None)
    """Web content snippet that can be embedded in a web page or an app webview."""

    sdk_blob: Optional[str] = FieldInfo(alias="sdkBlob", default=None)
    """
    Base64 encoded JSON representing array of
    tuple.
    """

    title: Optional[str] = None
    """Title of the search result."""

    url: Optional[str] = None
    """URI reference of the search result."""


class ContentUnionMember1GoogleSearchResultContent(BaseModel):
    type: Literal["google_search_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the Google Search resulted in an error."""

    result: Optional[List[ContentUnionMember1GoogleSearchResultContentResult]] = None
    """The results of the Google Search."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the Google Search result."""


ContentUnionMember1: TypeAlias = Annotated[
    Union[
        TextContent,
        ImageContent,
        AudioContent,
        DocumentContent,
        VideoContent,
        ThoughtContent,
        ContentUnionMember1FunctionCallContent,
        ContentUnionMember1FunctionResultContent,
        ContentUnionMember1CodeExecutionCallContent,
        ContentUnionMember1CodeExecutionResultContent,
        ContentUnionMember1URLContextCallContent,
        ContentUnionMember1URLContextResultContent,
        ContentUnionMember1GoogleSearchCallContent,
        ContentUnionMember1GoogleSearchResultContent,
    ],
    PropertyInfo(discriminator="type"),
]


class Turn(BaseModel):
    content: Union[str, List[ContentUnionMember1], None] = None
    """The content of the turn."""

    role: Optional[str] = None
    """The originator of this turn.

    Must be user for input or model for
    model output.
    """
