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

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr, Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config
from .text_content_param import TextContentParam
from .audio_content_param import AudioContentParam
from .image_content_param import ImageContentParam
from .video_content_param import VideoContentParam
from .thought_content_param import ThoughtContentParam
from .document_content_param import DocumentContentParam

__all__ = [
    "TurnParam",
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


class ContentUnionMember1FunctionCallContent(TypedDict, total=False):
    type: Required[Literal["function_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Dict[str, object]
    """The arguments to pass to the function."""

    name: str
    """The name of the tool to call."""


class ContentUnionMember1FunctionResultContent(TypedDict, total=False):
    type: Required[Literal["function_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the tool call resulted in an error."""

    name: str
    """The name of the tool that was called."""

    result: Union[str, object]
    """The result of the tool call."""


class ContentUnionMember1CodeExecutionCallContentArguments(TypedDict, total=False):
    code: str
    """The code to be executed."""

    language: Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]
    """Programming language of the `code`."""


class ContentUnionMember1CodeExecutionCallContent(TypedDict, total=False):
    type: Required[Literal["code_execution_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: ContentUnionMember1CodeExecutionCallContentArguments
    """The arguments to pass to the code execution."""


class ContentUnionMember1CodeExecutionResultContent(TypedDict, total=False):
    type: Required[Literal["code_execution_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the code execution resulted in an error."""

    result: str
    """The output of the code execution."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """A signature hash for backend validation."""


class ContentUnionMember1URLContextCallContentArguments(TypedDict, total=False):
    urls: SequenceNotStr[str]
    """The URLs to fetch."""


class ContentUnionMember1URLContextCallContent(TypedDict, total=False):
    type: Required[Literal["url_context_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: ContentUnionMember1URLContextCallContentArguments
    """The arguments to pass to the URL context."""


class ContentUnionMember1URLContextResultContentResult(TypedDict, total=False):
    status: Literal["STATUS_UNSPECIFIED", "SUCCESS", "ERROR", "PAYWALL", "UNSAFE"]
    """The status of the URL retrieval."""

    url: str
    """The URL that was fetched."""


class ContentUnionMember1URLContextResultContent(TypedDict, total=False):
    type: Required[Literal["url_context_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the URL context resulted in an error."""

    result: Iterable[ContentUnionMember1URLContextResultContentResult]
    """The results of the URL context."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """The signature of the URL context result."""


class ContentUnionMember1GoogleSearchCallContentArguments(TypedDict, total=False):
    queries: SequenceNotStr[str]
    """Web search queries for the following-up web search."""


class ContentUnionMember1GoogleSearchCallContent(TypedDict, total=False):
    type: Required[Literal["google_search_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: ContentUnionMember1GoogleSearchCallContentArguments
    """The arguments to pass to Google Search."""


class ContentUnionMember1GoogleSearchResultContentResult(TypedDict, total=False):
    rendered_content: Annotated[str, PropertyInfo(alias="renderedContent")]
    """Web content snippet that can be embedded in a web page or an app webview."""

    sdk_blob: Annotated[Union[str, Base64FileInput], PropertyInfo(alias="sdkBlob", format="base64")]
    """
    Base64 encoded JSON representing array of
    tuple.
    """

    title: str
    """Title of the search result."""

    url: str
    """URI reference of the search result."""


set_pydantic_config(ContentUnionMember1GoogleSearchResultContentResult, {"arbitrary_types_allowed": True})


class ContentUnionMember1GoogleSearchResultContent(TypedDict, total=False):
    type: Required[Literal["google_search_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the Google Search resulted in an error."""

    result: Iterable[ContentUnionMember1GoogleSearchResultContentResult]
    """The results of the Google Search."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """The signature of the Google Search result."""


ContentUnionMember1: TypeAlias = Union[
    TextContentParam,
    ImageContentParam,
    AudioContentParam,
    DocumentContentParam,
    VideoContentParam,
    ThoughtContentParam,
    ContentUnionMember1FunctionCallContent,
    ContentUnionMember1FunctionResultContent,
    ContentUnionMember1CodeExecutionCallContent,
    ContentUnionMember1CodeExecutionResultContent,
    ContentUnionMember1URLContextCallContent,
    ContentUnionMember1URLContextResultContent,
    ContentUnionMember1GoogleSearchCallContent,
    ContentUnionMember1GoogleSearchResultContent,
]


class TurnParam(TypedDict, total=False):
    content: Union[str, Iterable[ContentUnionMember1]]
    """The content of the turn."""

    role: str
    """The originator of this turn.

    Must be user for input or model for
    model output.
    """
