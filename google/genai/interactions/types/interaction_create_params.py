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

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr, Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config
from .tool_param import ToolParam
from .turn_param import TurnParam
from .model_param import ModelParam
from .tool_choice_param import ToolChoiceParam
from .text_content_param import TextContentParam
from .audio_content_param import AudioContentParam
from .image_content_param import ImageContentParam
from .speech_config_param import SpeechConfigParam
from .video_content_param import VideoContentParam
from .thinking_config_param import ThinkingConfigParam
from .thought_content_param import ThoughtContentParam
from .document_content_param import DocumentContentParam

__all__ = [
    "InteractionCreateParamsBase",
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
    "InteractionCreateParamsNonStreaming",
    "InteractionCreateParamsStreaming",
]


class InteractionCreateParamsBase(TypedDict, total=False):
    model: Required[ModelParam]
    """
    The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.
    """

    input: Input
    """The inputs for the interaction."""

    logprobs: bool
    """Input only. If true, includes log probabilities of output tokens."""

    max_output_tokens: Annotated[int, PropertyInfo(alias="maxOutputTokens")]
    """Input only. The maximum number of tokens to include in a response candidate."""

    max_tool_calls: Annotated[int, PropertyInfo(alias="maxToolCalls")]
    """Input only. The maximum number of total calls to built-in tools."""

    media_resolution: Annotated[
        Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"], PropertyInfo(alias="mediaResolution")
    ]
    """Input only. The resolution of the input media (images/video)."""

    metadata: Dict[str, object]
    """Input only.

    A set of up to 16 key-value pairs that can be attached to the object.
    """

    previous_interaction_id: Annotated[str, PropertyInfo(alias="previousInteractionId")]
    """The ID of the previous interaction, if any."""

    response_format: Annotated[Dict[str, object], PropertyInfo(alias="responseFormat")]
    """Input only. Enables Structured Outputs via JSON schema."""

    response_mime_type: Annotated[str, PropertyInfo(alias="responseMimeType")]
    """Input only.

    The mime type of the response. This is required if response_format is set.
    """

    response_modalities: Annotated[
        List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]],
        PropertyInfo(alias="responseModalities"),
    ]
    """Input only. The requested modalities of the response (TEXT, IMAGE, AUDIO)."""

    seed: int
    """Input only. Seed used in decoding for reproducibility."""

    speech_config: Annotated[Iterable[SpeechConfigParam], PropertyInfo(alias="speechConfig")]
    """Input only. Configuration for speech interaction."""

    stop_sequences: Annotated[SequenceNotStr[str], PropertyInfo(alias="stopSequences")]
    """Input only. A list of character sequences that will stop output interaction."""

    store: bool
    """
    Whether to store the generated model response and request for later
    retrieval.
    """

    system_instruction: Annotated[TextContentParam, PropertyInfo(alias="systemInstruction")]
    """A text content block."""

    temperature: float
    """Input only. Controls the randomness of the output."""

    thinking_config: Annotated[ThinkingConfigParam, PropertyInfo(alias="thinkingConfig")]
    """Input only. Configuration for thinking features."""

    tool_choice: Annotated[ToolChoiceParam, PropertyInfo(alias="toolChoice")]
    """Input only. The tool choice for the interaction."""

    tools: Iterable[ToolParam]
    """Input only. A list of tool declarations the model may call during interaction."""

    top_logprobs: Annotated[int, PropertyInfo(alias="topLogprobs")]
    """Input only.

    If logprobs is true, specifies the number of most likely tokens to return.
    """

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Input only.

    The maximum cumulative probability of tokens to consider when sampling.
    """

    truncation: str
    """Input only.

    The truncation strategy for model input if the context exceeds the window
    size.
    """


class InputContentListFunctionCallContent(TypedDict, total=False):
    type: Required[Literal["function_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Dict[str, object]
    """The arguments to pass to the function."""

    name: str
    """The name of the tool to call."""


class InputContentListFunctionResultContent(TypedDict, total=False):
    type: Required[Literal["function_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the tool call resulted in an error."""

    name: str
    """The name of the tool that was called."""

    result: Union[str, object]
    """The result of the tool call."""


class InputContentListCodeExecutionCallContentArguments(TypedDict, total=False):
    code: str
    """The code to be executed."""

    language: Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]
    """Programming language of the `code`."""


class InputContentListCodeExecutionCallContent(TypedDict, total=False):
    type: Required[Literal["code_execution_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: InputContentListCodeExecutionCallContentArguments
    """The arguments to pass to the code execution."""


class InputContentListCodeExecutionResultContent(TypedDict, total=False):
    type: Required[Literal["code_execution_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the code execution resulted in an error."""

    result: str
    """The output of the code execution."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """A signature hash for backend validation."""


class InputContentListURLContextCallContentArguments(TypedDict, total=False):
    urls: SequenceNotStr[str]
    """The URLs to fetch."""


class InputContentListURLContextCallContent(TypedDict, total=False):
    type: Required[Literal["url_context_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: InputContentListURLContextCallContentArguments
    """The arguments to pass to the URL context."""


class InputContentListURLContextResultContentResult(TypedDict, total=False):
    status: Literal["STATUS_UNSPECIFIED", "SUCCESS", "ERROR", "PAYWALL", "UNSAFE"]
    """The status of the URL retrieval."""

    url: str
    """The URL that was fetched."""


class InputContentListURLContextResultContent(TypedDict, total=False):
    type: Required[Literal["url_context_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the URL context resulted in an error."""

    result: Iterable[InputContentListURLContextResultContentResult]
    """The results of the URL context."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """The signature of the URL context result."""


class InputContentListGoogleSearchCallContentArguments(TypedDict, total=False):
    queries: SequenceNotStr[str]
    """Web search queries for the following-up web search."""


class InputContentListGoogleSearchCallContent(TypedDict, total=False):
    type: Required[Literal["google_search_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: InputContentListGoogleSearchCallContentArguments
    """The arguments to pass to Google Search."""


class InputContentListGoogleSearchResultContentResult(TypedDict, total=False):
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


set_pydantic_config(InputContentListGoogleSearchResultContentResult, {"arbitrary_types_allowed": True})


class InputContentListGoogleSearchResultContent(TypedDict, total=False):
    type: Required[Literal["google_search_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the Google Search resulted in an error."""

    result: Iterable[InputContentListGoogleSearchResultContentResult]
    """The results of the Google Search."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """The signature of the Google Search result."""


InputContentList: TypeAlias = Union[
    TextContentParam,
    ImageContentParam,
    AudioContentParam,
    DocumentContentParam,
    VideoContentParam,
    ThoughtContentParam,
    InputContentListFunctionCallContent,
    InputContentListFunctionResultContent,
    InputContentListCodeExecutionCallContent,
    InputContentListCodeExecutionResultContent,
    InputContentListURLContextCallContent,
    InputContentListURLContextResultContent,
    InputContentListGoogleSearchCallContent,
    InputContentListGoogleSearchResultContent,
]


class InputFunctionCallContent(TypedDict, total=False):
    type: Required[Literal["function_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: Dict[str, object]
    """The arguments to pass to the function."""

    name: str
    """The name of the tool to call."""


class InputFunctionResultContent(TypedDict, total=False):
    type: Required[Literal["function_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the tool call resulted in an error."""

    name: str
    """The name of the tool that was called."""

    result: Union[str, object]
    """The result of the tool call."""


class InputCodeExecutionCallContentArguments(TypedDict, total=False):
    code: str
    """The code to be executed."""

    language: Literal["LANGUAGE_UNSPECIFIED", "PYTHON"]
    """Programming language of the `code`."""


class InputCodeExecutionCallContent(TypedDict, total=False):
    type: Required[Literal["code_execution_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: InputCodeExecutionCallContentArguments
    """The arguments to pass to the code execution."""


class InputCodeExecutionResultContent(TypedDict, total=False):
    type: Required[Literal["code_execution_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the code execution resulted in an error."""

    result: str
    """The output of the code execution."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """A signature hash for backend validation."""


class InputURLContextCallContentArguments(TypedDict, total=False):
    urls: SequenceNotStr[str]
    """The URLs to fetch."""


class InputURLContextCallContent(TypedDict, total=False):
    type: Required[Literal["url_context_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: InputURLContextCallContentArguments
    """The arguments to pass to the URL context."""


class InputURLContextResultContentResult(TypedDict, total=False):
    status: Literal["STATUS_UNSPECIFIED", "SUCCESS", "ERROR", "PAYWALL", "UNSAFE"]
    """The status of the URL retrieval."""

    url: str
    """The URL that was fetched."""


class InputURLContextResultContent(TypedDict, total=False):
    type: Required[Literal["url_context_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the URL context resulted in an error."""

    result: Iterable[InputURLContextResultContentResult]
    """The results of the URL context."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """The signature of the URL context result."""


class InputGoogleSearchCallContentArguments(TypedDict, total=False):
    queries: SequenceNotStr[str]
    """Web search queries for the following-up web search."""


class InputGoogleSearchCallContent(TypedDict, total=False):
    type: Required[Literal["google_search_call"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    arguments: InputGoogleSearchCallContentArguments
    """The arguments to pass to Google Search."""


class InputGoogleSearchResultContentResult(TypedDict, total=False):
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


set_pydantic_config(InputGoogleSearchResultContentResult, {"arbitrary_types_allowed": True})


class InputGoogleSearchResultContent(TypedDict, total=False):
    type: Required[Literal["google_search_result"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    is_error: Annotated[bool, PropertyInfo(alias="isError")]
    """Whether the Google Search resulted in an error."""

    result: Iterable[InputGoogleSearchResultContentResult]
    """The results of the Google Search."""

    result_signature: Annotated[str, PropertyInfo(alias="resultSignature")]
    """The signature of the Google Search result."""


Input: TypeAlias = Union[
    str,
    Iterable[InputContentList],
    Iterable[TurnParam],
    TextContentParam,
    ImageContentParam,
    AudioContentParam,
    DocumentContentParam,
    VideoContentParam,
    ThoughtContentParam,
    InputFunctionCallContent,
    InputFunctionResultContent,
    InputCodeExecutionCallContent,
    InputCodeExecutionResultContent,
    InputURLContextCallContent,
    InputURLContextResultContent,
    InputGoogleSearchCallContent,
    InputGoogleSearchResultContent,
]


class InteractionCreateParamsNonStreaming(InteractionCreateParamsBase, total=False):
    stream: Literal[False]
    """Input only. Whether the interaction will be streamed."""


class InteractionCreateParamsStreaming(InteractionCreateParamsBase):
    stream: Required[Literal[True]]
    """Input only. Whether the interaction will be streamed."""


InteractionCreateParams = Union[InteractionCreateParamsNonStreaming, InteractionCreateParamsStreaming]
