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

from typing import Dict, List, Iterable
from typing_extensions import Literal, overload

import httpx

from ..types import interaction_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import required_args, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.tool_param import ToolParam
from ..types.interaction import Interaction
from ..types.model_param import ModelParam
from ..types.tool_choice_param import ToolChoiceParam
from ..types.text_content_param import TextContentParam
from ..types.speech_config_param import SpeechConfigParam
from ..types.interaction_sse_event import InteractionSSEEvent
from ..types.thinking_config_param import ThinkingConfigParam

__all__ = ["InteractionsResource", "AsyncInteractionsResource"]


class InteractionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InteractionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#accessing-raw-response-data-eg-headers
        """
        return InteractionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InteractionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#with_streaming_response
        """
        return InteractionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        model: ModelParam,
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        stream: Literal[False] | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction:
        """
        Internal version of CreateInteraction that generates a set of responses
        from the model using structured protos.

        Args:
          model: The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.

          input: The inputs for the interaction.

          logprobs: Input only. If true, includes log probabilities of output tokens.

          max_output_tokens: Input only. The maximum number of tokens to include in a response candidate.

          max_tool_calls: Input only. The maximum number of total calls to built-in tools.

          media_resolution: Input only. The resolution of the input media (images/video).

          metadata: Input only. A set of up to 16 key-value pairs that can be attached to the object.

          previous_interaction_id: The ID of the previous interaction, if any.

          response_format: Input only. Enables Structured Outputs via JSON schema.

          response_mime_type: Input only. The mime type of the response. This is required if response_format is set.

          response_modalities: Input only. The requested modalities of the response (TEXT, IMAGE, AUDIO).

          seed: Input only. Seed used in decoding for reproducibility.

          speech_config: Input only. Configuration for speech interaction.

          stop_sequences: Input only. A list of character sequences that will stop output interaction.

          store: Whether to store the generated model response and request for later
              retrieval.

          stream: Input only. Whether the interaction will be streamed.

          system_instruction: A text content block.

          temperature: Input only. Controls the randomness of the output.

          thinking_config: Input only. Configuration for thinking features.

          tool_choice: Input only. The tool choice for the interaction.

          tools: Input only. A list of tool declarations the model may call during interaction.

          top_logprobs: Input only. If logprobs is true, specifies the number of most likely tokens to return.

          top_p: Input only. The maximum cumulative probability of tokens to consider when sampling.

          truncation: Input only. The truncation strategy for model input if the context exceeds the window
              size.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        model: ModelParam,
        stream: Literal[True],
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[InteractionSSEEvent]:
        """
        Internal version of CreateInteraction that generates a set of responses
        from the model using structured protos.

        Args:
          model: The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.

          stream: Input only. Whether the interaction will be streamed.

          input: The inputs for the interaction.

          logprobs: Input only. If true, includes log probabilities of output tokens.

          max_output_tokens: Input only. The maximum number of tokens to include in a response candidate.

          max_tool_calls: Input only. The maximum number of total calls to built-in tools.

          media_resolution: Input only. The resolution of the input media (images/video).

          metadata: Input only. A set of up to 16 key-value pairs that can be attached to the object.

          previous_interaction_id: The ID of the previous interaction, if any.

          response_format: Input only. Enables Structured Outputs via JSON schema.

          response_mime_type: Input only. The mime type of the response. This is required if response_format is set.

          response_modalities: Input only. The requested modalities of the response (TEXT, IMAGE, AUDIO).

          seed: Input only. Seed used in decoding for reproducibility.

          speech_config: Input only. Configuration for speech interaction.

          stop_sequences: Input only. A list of character sequences that will stop output interaction.

          store: Whether to store the generated model response and request for later
              retrieval.

          system_instruction: A text content block.

          temperature: Input only. Controls the randomness of the output.

          thinking_config: Input only. Configuration for thinking features.

          tool_choice: Input only. The tool choice for the interaction.

          tools: Input only. A list of tool declarations the model may call during interaction.

          top_logprobs: Input only. If logprobs is true, specifies the number of most likely tokens to return.

          top_p: Input only. The maximum cumulative probability of tokens to consider when sampling.

          truncation: Input only. The truncation strategy for model input if the context exceeds the window
              size.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        model: ModelParam,
        stream: bool,
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction | Stream[InteractionSSEEvent]:
        """
        Internal version of CreateInteraction that generates a set of responses
        from the model using structured protos.

        Args:
          model: The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.

          stream: Input only. Whether the interaction will be streamed.

          input: The inputs for the interaction.

          logprobs: Input only. If true, includes log probabilities of output tokens.

          max_output_tokens: Input only. The maximum number of tokens to include in a response candidate.

          max_tool_calls: Input only. The maximum number of total calls to built-in tools.

          media_resolution: Input only. The resolution of the input media (images/video).

          metadata: Input only. A set of up to 16 key-value pairs that can be attached to the object.

          previous_interaction_id: The ID of the previous interaction, if any.

          response_format: Input only. Enables Structured Outputs via JSON schema.

          response_mime_type: Input only. The mime type of the response. This is required if response_format is set.

          response_modalities: Input only. The requested modalities of the response (TEXT, IMAGE, AUDIO).

          seed: Input only. Seed used in decoding for reproducibility.

          speech_config: Input only. Configuration for speech interaction.

          stop_sequences: Input only. A list of character sequences that will stop output interaction.

          store: Whether to store the generated model response and request for later
              retrieval.

          system_instruction: A text content block.

          temperature: Input only. Controls the randomness of the output.

          thinking_config: Input only. Configuration for thinking features.

          tool_choice: Input only. The tool choice for the interaction.

          tools: Input only. A list of tool declarations the model may call during interaction.

          top_logprobs: Input only. If logprobs is true, specifies the number of most likely tokens to return.

          top_p: Input only. The maximum cumulative probability of tokens to consider when sampling.

          truncation: Input only. The truncation strategy for model input if the context exceeds the window
              size.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["model"], ["model", "stream"])
    def create(
        self,
        *,
        model: ModelParam,
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction | Stream[InteractionSSEEvent]:
        return self._post(
            "/v1alpha/interactions",
            body=maybe_transform(
                {
                    "model": model,
                    "input": input,
                    "logprobs": logprobs,
                    "max_output_tokens": max_output_tokens,
                    "max_tool_calls": max_tool_calls,
                    "media_resolution": media_resolution,
                    "metadata": metadata,
                    "previous_interaction_id": previous_interaction_id,
                    "response_format": response_format,
                    "response_mime_type": response_mime_type,
                    "response_modalities": response_modalities,
                    "seed": seed,
                    "speech_config": speech_config,
                    "stop_sequences": stop_sequences,
                    "store": store,
                    "stream": stream,
                    "system_instruction": system_instruction,
                    "temperature": temperature,
                    "thinking_config": thinking_config,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "truncation": truncation,
                },
                interaction_create_params.InteractionCreateParamsStreaming
                if stream
                else interaction_create_params.InteractionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Interaction,
            stream=stream or False,
            stream_cls=Stream[InteractionSSEEvent],
        )

    def get(
        self,
        interaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction:
        """
        Retrieves the full details of a single interaction based on its `Interaction.id`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not interaction_id:
            raise ValueError(f"Expected a non-empty value for `interaction_id` but received {interaction_id!r}")
        return self._get(
            f"/v1alpha/interactions/{interaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Interaction,
        )


class AsyncInteractionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInteractionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInteractionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInteractionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/gemini-next-gen-api-python#with_streaming_response
        """
        return AsyncInteractionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        model: ModelParam,
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        stream: Literal[False] | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction:
        """
        Internal version of CreateInteraction that generates a set of responses
        from the model using structured protos.

        Args:
          model: The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.

          input: The inputs for the interaction.

          logprobs: Input only. If true, includes log probabilities of output tokens.

          max_output_tokens: Input only. The maximum number of tokens to include in a response candidate.

          max_tool_calls: Input only. The maximum number of total calls to built-in tools.

          media_resolution: Input only. The resolution of the input media (images/video).

          metadata: Input only. A set of up to 16 key-value pairs that can be attached to the object.

          previous_interaction_id: The ID of the previous interaction, if any.

          response_format: Input only. Enables Structured Outputs via JSON schema.

          response_mime_type: Input only. The mime type of the response. This is required if response_format is set.

          response_modalities: Input only. The requested modalities of the response (TEXT, IMAGE, AUDIO).

          seed: Input only. Seed used in decoding for reproducibility.

          speech_config: Input only. Configuration for speech interaction.

          stop_sequences: Input only. A list of character sequences that will stop output interaction.

          store: Whether to store the generated model response and request for later
              retrieval.

          stream: Input only. Whether the interaction will be streamed.

          system_instruction: A text content block.

          temperature: Input only. Controls the randomness of the output.

          thinking_config: Input only. Configuration for thinking features.

          tool_choice: Input only. The tool choice for the interaction.

          tools: Input only. A list of tool declarations the model may call during interaction.

          top_logprobs: Input only. If logprobs is true, specifies the number of most likely tokens to return.

          top_p: Input only. The maximum cumulative probability of tokens to consider when sampling.

          truncation: Input only. The truncation strategy for model input if the context exceeds the window
              size.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        model: ModelParam,
        stream: Literal[True],
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[InteractionSSEEvent]:
        """
        Internal version of CreateInteraction that generates a set of responses
        from the model using structured protos.

        Args:
          model: The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.

          stream: Input only. Whether the interaction will be streamed.

          input: The inputs for the interaction.

          logprobs: Input only. If true, includes log probabilities of output tokens.

          max_output_tokens: Input only. The maximum number of tokens to include in a response candidate.

          max_tool_calls: Input only. The maximum number of total calls to built-in tools.

          media_resolution: Input only. The resolution of the input media (images/video).

          metadata: Input only. A set of up to 16 key-value pairs that can be attached to the object.

          previous_interaction_id: The ID of the previous interaction, if any.

          response_format: Input only. Enables Structured Outputs via JSON schema.

          response_mime_type: Input only. The mime type of the response. This is required if response_format is set.

          response_modalities: Input only. The requested modalities of the response (TEXT, IMAGE, AUDIO).

          seed: Input only. Seed used in decoding for reproducibility.

          speech_config: Input only. Configuration for speech interaction.

          stop_sequences: Input only. A list of character sequences that will stop output interaction.

          store: Whether to store the generated model response and request for later
              retrieval.

          system_instruction: A text content block.

          temperature: Input only. Controls the randomness of the output.

          thinking_config: Input only. Configuration for thinking features.

          tool_choice: Input only. The tool choice for the interaction.

          tools: Input only. A list of tool declarations the model may call during interaction.

          top_logprobs: Input only. If logprobs is true, specifies the number of most likely tokens to return.

          top_p: Input only. The maximum cumulative probability of tokens to consider when sampling.

          truncation: Input only. The truncation strategy for model input if the context exceeds the window
              size.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        model: ModelParam,
        stream: bool,
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction | AsyncStream[InteractionSSEEvent]:
        """
        Internal version of CreateInteraction that generates a set of responses
        from the model using structured protos.

        Args:
          model: The model that will complete your prompt.\n\nSee [models](https://ai.google.dev/gemini-api/docs/models) for additional details.

          stream: Input only. Whether the interaction will be streamed.

          input: The inputs for the interaction.

          logprobs: Input only. If true, includes log probabilities of output tokens.

          max_output_tokens: Input only. The maximum number of tokens to include in a response candidate.

          max_tool_calls: Input only. The maximum number of total calls to built-in tools.

          media_resolution: Input only. The resolution of the input media (images/video).

          metadata: Input only. A set of up to 16 key-value pairs that can be attached to the object.

          previous_interaction_id: The ID of the previous interaction, if any.

          response_format: Input only. Enables Structured Outputs via JSON schema.

          response_mime_type: Input only. The mime type of the response. This is required if response_format is set.

          response_modalities: Input only. The requested modalities of the response (TEXT, IMAGE, AUDIO).

          seed: Input only. Seed used in decoding for reproducibility.

          speech_config: Input only. Configuration for speech interaction.

          stop_sequences: Input only. A list of character sequences that will stop output interaction.

          store: Whether to store the generated model response and request for later
              retrieval.

          system_instruction: A text content block.

          temperature: Input only. Controls the randomness of the output.

          thinking_config: Input only. Configuration for thinking features.

          tool_choice: Input only. The tool choice for the interaction.

          tools: Input only. A list of tool declarations the model may call during interaction.

          top_logprobs: Input only. If logprobs is true, specifies the number of most likely tokens to return.

          top_p: Input only. The maximum cumulative probability of tokens to consider when sampling.

          truncation: Input only. The truncation strategy for model input if the context exceeds the window
              size.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["model"], ["model", "stream"])
    async def create(
        self,
        *,
        model: ModelParam,
        input: interaction_create_params.Input | Omit = omit,
        logprobs: bool | Omit = omit,
        max_output_tokens: int | Omit = omit,
        max_tool_calls: int | Omit = omit,
        media_resolution: Literal["MEDIA_RESOLUTION_UNSPECIFIED", "LOW", "MEDIUM", "HIGH"] | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        previous_interaction_id: str | Omit = omit,
        response_format: Dict[str, object] | Omit = omit,
        response_mime_type: str | Omit = omit,
        response_modalities: List[Literal["RESPONSE_MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]] | Omit = omit,
        seed: int | Omit = omit,
        speech_config: Iterable[SpeechConfigParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        store: bool | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        system_instruction: TextContentParam | Omit = omit,
        temperature: float | Omit = omit,
        thinking_config: ThinkingConfigParam | Omit = omit,
        tool_choice: ToolChoiceParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        truncation: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction | AsyncStream[InteractionSSEEvent]:
        return await self._post(
            "/v1alpha/interactions",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "input": input,
                    "logprobs": logprobs,
                    "max_output_tokens": max_output_tokens,
                    "max_tool_calls": max_tool_calls,
                    "media_resolution": media_resolution,
                    "metadata": metadata,
                    "previous_interaction_id": previous_interaction_id,
                    "response_format": response_format,
                    "response_mime_type": response_mime_type,
                    "response_modalities": response_modalities,
                    "seed": seed,
                    "speech_config": speech_config,
                    "stop_sequences": stop_sequences,
                    "store": store,
                    "stream": stream,
                    "system_instruction": system_instruction,
                    "temperature": temperature,
                    "thinking_config": thinking_config,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "truncation": truncation,
                },
                interaction_create_params.InteractionCreateParamsStreaming
                if stream
                else interaction_create_params.InteractionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Interaction,
            stream=stream or False,
            stream_cls=AsyncStream[InteractionSSEEvent],
        )

    async def get(
        self,
        interaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Interaction:
        """
        Retrieves the full details of a single interaction based on its `Interaction.id`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not interaction_id:
            raise ValueError(f"Expected a non-empty value for `interaction_id` but received {interaction_id!r}")
        return await self._get(
            f"/v1alpha/interactions/{interaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Interaction,
        )


class InteractionsResourceWithRawResponse:
    def __init__(self, interactions: InteractionsResource) -> None:
        self._interactions = interactions

        self.create = to_raw_response_wrapper(
            interactions.create,
        )
        self.get = to_raw_response_wrapper(
            interactions.get,
        )


class AsyncInteractionsResourceWithRawResponse:
    def __init__(self, interactions: AsyncInteractionsResource) -> None:
        self._interactions = interactions

        self.create = async_to_raw_response_wrapper(
            interactions.create,
        )
        self.get = async_to_raw_response_wrapper(
            interactions.get,
        )


class InteractionsResourceWithStreamingResponse:
    def __init__(self, interactions: InteractionsResource) -> None:
        self._interactions = interactions

        self.create = to_streamed_response_wrapper(
            interactions.create,
        )
        self.get = to_streamed_response_wrapper(
            interactions.get,
        )


class AsyncInteractionsResourceWithStreamingResponse:
    def __init__(self, interactions: AsyncInteractionsResource) -> None:
        self._interactions = interactions

        self.create = async_to_streamed_response_wrapper(
            interactions.create,
        )
        self.get = async_to_streamed_response_wrapper(
            interactions.get,
        )
