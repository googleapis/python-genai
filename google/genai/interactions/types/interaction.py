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

from .turn import Turn
from .model import Model
from .usage import Usage
from .._utils import PropertyInfo
from .._models import BaseModel
from .text_content import TextContent
from .audio_content import AudioContent
from .image_content import ImageContent
from .video_content import VideoContent
from .thought_content import ThoughtContent
from .document_content import DocumentContent

__all__ = [
    "Interaction",
    "Error",
    "Input",
    "InputContentList",
    "InputContentListFunctionCallContent",
    "InputContentListFunctionResultContent",
    "InputContentListCodeExecutionCallContent",
    "InputContentListCodeExecutionCallContentArguments",
    "InputContentListCodeExecutionResultContent",
    "InputContentListURLContextCallContent",
    "InputContentListURLContextCallContentArguments",
    "InputContentListURLContextResultContent",
    "InputContentListURLContextResultContentResult",
    "InputContentListGoogleSearchCallContent",
    "InputContentListGoogleSearchCallContentArguments",
    "InputContentListGoogleSearchResultContent",
    "InputContentListGoogleSearchResultContentResult",
    "InputFunctionCallContent",
    "InputFunctionResultContent",
    "InputCodeExecutionCallContent",
    "InputCodeExecutionCallContentArguments",
    "InputCodeExecutionResultContent",
    "InputURLContextCallContent",
    "InputURLContextCallContentArguments",
    "InputURLContextResultContent",
    "InputURLContextResultContentResult",
    "InputGoogleSearchCallContent",
    "InputGoogleSearchCallContentArguments",
    "InputGoogleSearchResultContent",
    "InputGoogleSearchResultContentResult",
    "Output",
    "OutputFunctionCallContent",
    "OutputFunctionResultContent",
    "OutputCodeExecutionCallContent",
    "OutputCodeExecutionCallContentArguments",
    "OutputCodeExecutionResultContent",
    "OutputURLContextCallContent",
    "OutputURLContextCallContentArguments",
    "OutputURLContextResultContent",
    "OutputURLContextResultContentResult",
    "OutputGoogleSearchCallContent",
    "OutputGoogleSearchCallContentArguments",
    "OutputGoogleSearchResultContent",
    "OutputGoogleSearchResultContentResult",
]


class Error(BaseModel):
    code: Optional[int] = None
    """The HTTP status code."""

    message: Optional[str] = None
    """A human-readable error message."""

    status: Optional[str] = None
    """A string representation of the status code."""


class InputContentListFunctionCallContent(BaseModel):
    type: Literal["function_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[Dict[str, object]] = None
    """The arguments to pass to the function."""

    name: Optional[str] = None
    """The name of the tool to call."""


class InputContentListFunctionResultContent(BaseModel):
    type: Literal["function_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the tool call resulted in an error."""

    name: Optional[str] = None
    """The name of the tool that was called."""

    result: Union[str, object, None] = None
    """The result of the tool call."""


class InputContentListCodeExecutionCallContentArguments(BaseModel):
    code: Optional[str] = None
    """The code to be executed."""

    language: Optional[Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]] = None
    """Programming language of the `code`."""


class InputContentListCodeExecutionCallContent(BaseModel):
    type: Literal["code_execution_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[InputContentListCodeExecutionCallContentArguments] = None
    """The arguments to pass to the code execution."""


class InputContentListCodeExecutionResultContent(BaseModel):
    type: Literal["code_execution_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the code execution resulted in an error."""

    result: Optional[str] = None
    """The output of the code execution."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """A signature hash for backend validation."""


class InputContentListURLContextCallContentArguments(BaseModel):
    urls: Optional[List[str]] = None
    """The URLs to fetch."""


class InputContentListURLContextCallContent(BaseModel):
    type: Literal["url_context_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[InputContentListURLContextCallContentArguments] = None
    """The arguments to pass to the URL context."""


class InputContentListURLContextResultContentResult(BaseModel):
    status: Optional[Literal["STATUS_UNSPECIFIED", "SUCCESS", "ERROR", "PAYWALL", "UNSAFE"]] = None
    """The status of the URL retrieval."""

    url: Optional[str] = None
    """The URL that was fetched."""


class InputContentListURLContextResultContent(BaseModel):
    type: Literal["url_context_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the URL context resulted in an error."""

    result: Optional[List[InputContentListURLContextResultContentResult]] = None
    """The results of the URL context."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the URL context result."""


class InputContentListGoogleSearchCallContentArguments(BaseModel):
    queries: Optional[List[str]] = None
    """Web search queries for the following-up web search."""


class InputContentListGoogleSearchCallContent(BaseModel):
    type: Literal["google_search_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[InputContentListGoogleSearchCallContentArguments] = None
    """The arguments to pass to Google Search."""


class InputContentListGoogleSearchResultContentResult(BaseModel):
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


class InputContentListGoogleSearchResultContent(BaseModel):
    type: Literal["google_search_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the Google Search resulted in an error."""

    result: Optional[List[InputContentListGoogleSearchResultContentResult]] = None
    """The results of the Google Search."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the Google Search result."""


InputContentList: TypeAlias = Annotated[
    Union[
        TextContent,
        ImageContent,
        AudioContent,
        DocumentContent,
        VideoContent,
        ThoughtContent,
        InputContentListFunctionCallContent,
        InputContentListFunctionResultContent,
        InputContentListCodeExecutionCallContent,
        InputContentListCodeExecutionResultContent,
        InputContentListURLContextCallContent,
        InputContentListURLContextResultContent,
        InputContentListGoogleSearchCallContent,
        InputContentListGoogleSearchResultContent,
    ],
    PropertyInfo(discriminator="type"),
]


class InputFunctionCallContent(BaseModel):
    type: Literal["function_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[Dict[str, object]] = None
    """The arguments to pass to the function."""

    name: Optional[str] = None
    """The name of the tool to call."""


class InputFunctionResultContent(BaseModel):
    type: Literal["function_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the tool call resulted in an error."""

    name: Optional[str] = None
    """The name of the tool that was called."""

    result: Union[str, object, None] = None
    """The result of the tool call."""


class InputCodeExecutionCallContentArguments(BaseModel):
    code: Optional[str] = None
    """The code to be executed."""

    language: Optional[Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]] = None
    """Programming language of the `code`."""


class InputCodeExecutionCallContent(BaseModel):
    type: Literal["code_execution_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[InputCodeExecutionCallContentArguments] = None
    """The arguments to pass to the code execution."""


class InputCodeExecutionResultContent(BaseModel):
    type: Literal["code_execution_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the code execution resulted in an error."""

    result: Optional[str] = None
    """The output of the code execution."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """A signature hash for backend validation."""


class InputURLContextCallContentArguments(BaseModel):
    urls: Optional[List[str]] = None
    """The URLs to fetch."""


class InputURLContextCallContent(BaseModel):
    type: Literal["url_context_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[InputURLContextCallContentArguments] = None
    """The arguments to pass to the URL context."""


class InputURLContextResultContentResult(BaseModel):
    status: Optional[Literal["STATUS_UNSPECIFIED", "SUCCESS", "ERROR", "PAYWALL", "UNSAFE"]] = None
    """The status of the URL retrieval."""

    url: Optional[str] = None
    """The URL that was fetched."""


class InputURLContextResultContent(BaseModel):
    type: Literal["url_context_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the URL context resulted in an error."""

    result: Optional[List[InputURLContextResultContentResult]] = None
    """The results of the URL context."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the URL context result."""


class InputGoogleSearchCallContentArguments(BaseModel):
    queries: Optional[List[str]] = None
    """Web search queries for the following-up web search."""


class InputGoogleSearchCallContent(BaseModel):
    type: Literal["google_search_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[InputGoogleSearchCallContentArguments] = None
    """The arguments to pass to Google Search."""


class InputGoogleSearchResultContentResult(BaseModel):
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


class InputGoogleSearchResultContent(BaseModel):
    type: Literal["google_search_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the Google Search resulted in an error."""

    result: Optional[List[InputGoogleSearchResultContentResult]] = None
    """The results of the Google Search."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the Google Search result."""


Input: TypeAlias = Union[
    str,
    List[InputContentList],
    List[Turn],
    TextContent,
    ImageContent,
    AudioContent,
    DocumentContent,
    VideoContent,
    ThoughtContent,
    InputFunctionCallContent,
    InputFunctionResultContent,
    InputCodeExecutionCallContent,
    InputCodeExecutionResultContent,
    InputURLContextCallContent,
    InputURLContextResultContent,
    InputGoogleSearchCallContent,
    InputGoogleSearchResultContent,
]


class OutputFunctionCallContent(BaseModel):
    type: Literal["function_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[Dict[str, object]] = None
    """The arguments to pass to the function."""

    name: Optional[str] = None
    """The name of the tool to call."""


class OutputFunctionResultContent(BaseModel):
    type: Literal["function_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the tool call resulted in an error."""

    name: Optional[str] = None
    """The name of the tool that was called."""

    result: Union[str, object, None] = None
    """The result of the tool call."""


class OutputCodeExecutionCallContentArguments(BaseModel):
    code: Optional[str] = None
    """The code to be executed."""

    language: Optional[Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]] = None
    """Programming language of the `code`."""


class OutputCodeExecutionCallContent(BaseModel):
    type: Literal["code_execution_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[OutputCodeExecutionCallContentArguments] = None
    """The arguments to pass to the code execution."""


class OutputCodeExecutionResultContent(BaseModel):
    type: Literal["code_execution_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the code execution resulted in an error."""

    result: Optional[str] = None
    """The output of the code execution."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """A signature hash for backend validation."""


class OutputURLContextCallContentArguments(BaseModel):
    urls: Optional[List[str]] = None
    """The URLs to fetch."""


class OutputURLContextCallContent(BaseModel):
    type: Literal["url_context_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[OutputURLContextCallContentArguments] = None
    """The arguments to pass to the URL context."""


class OutputURLContextResultContentResult(BaseModel):
    status: Optional[Literal["STATUS_UNSPECIFIED", "SUCCESS", "ERROR", "PAYWALL", "UNSAFE"]] = None
    """The status of the URL retrieval."""

    url: Optional[str] = None
    """The URL that was fetched."""


class OutputURLContextResultContent(BaseModel):
    type: Literal["url_context_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the URL context resulted in an error."""

    result: Optional[List[OutputURLContextResultContentResult]] = None
    """The results of the URL context."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the URL context result."""


class OutputGoogleSearchCallContentArguments(BaseModel):
    queries: Optional[List[str]] = None
    """Web search queries for the following-up web search."""


class OutputGoogleSearchCallContent(BaseModel):
    type: Literal["google_search_call"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Optional[OutputGoogleSearchCallContentArguments] = None
    """The arguments to pass to Google Search."""


class OutputGoogleSearchResultContentResult(BaseModel):
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


class OutputGoogleSearchResultContent(BaseModel):
    type: Literal["google_search_result"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Optional[bool] = FieldInfo(alias="isError", default=None)
    """Whether the Google Search resulted in an error."""

    result: Optional[List[OutputGoogleSearchResultContentResult]] = None
    """The results of the Google Search."""

    result_signature: Optional[str] = FieldInfo(alias="resultSignature", default=None)
    """The signature of the Google Search result."""


Output: TypeAlias = Annotated[
    Union[
        TextContent,
        ImageContent,
        AudioContent,
        DocumentContent,
        VideoContent,
        ThoughtContent,
        OutputFunctionCallContent,
        OutputFunctionResultContent,
        OutputCodeExecutionCallContent,
        OutputCodeExecutionResultContent,
        OutputURLContextCallContent,
        OutputURLContextResultContent,
        OutputGoogleSearchCallContent,
        OutputGoogleSearchResultContent,
    ],
    PropertyInfo(discriminator="type"),
]


class Interaction(BaseModel):
    model: Model
    """
    The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.
    """

    id: Optional[str] = None
    """Output only. A unique identifier for the interaction completion."""

    created: Optional[float] = None
    """Output only. The time at which the response was created."""

    error: Optional[Error] = None
    """Output only. The error message for the interaction, if any."""

    input: Optional[Input] = None
    """The inputs for the interaction."""

    object: Optional[Literal["interaction"]] = None
    """Output only. The object type of the interaction. Always set to `interaction`."""

    outputs: Optional[List[Output]] = None
    """Output only. Candidate responses from the model."""

    previous_interaction_id: Optional[str] = FieldInfo(alias="previousInteractionId", default=None)
    """The ID of the previous interaction, if any."""

    role: Optional[str] = None
    """Output only. The role of the interaction."""

    status: Optional[
        Literal[
            "UNSPECIFIED",
            "QUEUED",
            "IN_PROGRESS",
            "REQUIRES_ACTION",
            "COMPLETED",
            "INCOMPLETE",
            "FAILED",
            "CANCELLED",
            "CANCELLING",
            "EXPIRED",
        ]
    ] = None
    """Output only. The status of the interaction."""

    store: Optional[bool] = None
    """
    Whether to store the generated model response and request for later
    retrieval.
    """

    updated: Optional[float] = None
    """Output only. The time at which the response was last updated."""

    usage: Optional[Usage] = None
    """Output only. Statistics on the interaction request's token usage."""
