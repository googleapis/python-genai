# Copyright 2026 Google LLC
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
# pyformat: disable
# pylint: skip-file

"""Async WebSocket connections and wire models for live Interactions API calls.

Experimental: Live Interactions SDK support is experimental and may change in
future versions.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Generator, Mapping
from datetime import datetime
from functools import partial
import json
import re
from typing import Any, Dict, List, Literal, Optional, Union, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import warnings

try:
    import httpx
except ImportError:
    import httpx2 as httpx
import pydantic
from pydantic import BaseModel as PydanticBaseModel, Discriminator, Field, Tag, TypeAdapter, ValidationError, model_serializer
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import AfterValidator, BeforeValidator, WrapValidator
from typing_extensions import Annotated, NotRequired, TypeAliasType, TypedDict
from websockets.asyncio.client import ClientConnection, connect as ws_connect
from websockets.exceptions import ConnectionClosed
from websockets.frames import CloseCode

from . import errors, models, types, utils
from ._hooks import AfterParseErrorContext, HookContext, ResponseContext
from ._hooks.google_genai_auth import GOOGLE_GENAI_API_REVISION
from .basesdk import AsyncBaseSDK, BaseSDK
from .lib.compat_errors import APIConnectionError
from .types import (
    BaseModel,
    Nullable,
    OptionalNullable,
    UNSET,
    UNSET_SENTINEL,
    UnrecognizedInt,
    UnrecognizedStr,
    current_exclude_none,
    interactions,
    serialize_with_info,
)
from .types.basemodel import (
    current_by_alias,
    current_filtered_dump,
    current_serialization_methods_dump,
)
from .types.interactions import (
    Content,
    ContentParam,
    Environment,
    EnvironmentParam,
    ErrorEvent,
    ResponseFormat,
    ResponseFormatParam,
    ResponseModality,
    ServiceTier,
    Status,
    StatusParam,
    Step,
    StepDelta,
    StepDeltaTypedDict,
    StepParam,
    StepStart,
    StepStartTypedDict,
    StepStop,
    StepStopTypedDict,
    Tool,
    ToolParam,
    WebhookConfig,
    WebhookConfigParam,
)
from .utils import (
    FieldMetadata,
    PathParamMetadata,
    RequestMetadata,
    get_discriminator,
    get_security_from_env,
    response_helpers,
    serialize_int,
    unmarshal,
    validate_const,
    validate_int,
)
from .utils.unions import (
    decline_sibling_variants,
    dispatch_open_union_members,
    parse_open_union,
)
from .utils.unmarshal_json_response import unmarshal_json_response

ContentTypedDict = ContentParam
StepTypedDict = StepParam
ResponseModalityParam = ResponseModality
ServiceTierParam = ServiceTier

# --- interactionauthtoken.py ---
class InteractionAuthTokenTypedDict(TypedDict):
    auth_token: NotRequired[str]
    r"""The auth token."""
    expires_at: NotRequired[datetime]
    r"""Expiration time of the auth token."""


class InteractionAuthToken(BaseModel):
    auth_token: Optional[str] = None
    r"""The auth token."""

    expires_at: Optional[datetime] = None
    r"""Expiration time of the auth token."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["auth_token", "expires_at"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m

# --- interactionauthtokencreateparams.py ---
class InteractionAuthTokenCreateParamsParam(TypedDict):
    expire_time: NotRequired[datetime]
    r"""Hard deadline - messages rejected after this time."""


class InteractionAuthTokenCreateParams(BaseModel):
    expire_time: Optional[datetime] = None
    r"""Hard deadline - messages rejected after this time."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["expire_time"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m

# --- inputdeliverymode.py ---
InputDeliveryMode = Literal[
    "queue",
    "immediate",
    "silent",
    "blocking",
]

# --- audiostream.py ---
class AudioStreamParam(TypedDict):
    r"""Definition of an audio input stream."""

    id: NotRequired[str]
    r"""Stream identifier (e.g. \"mic\", \"screen\"). Defaults to \"default\" (index
    0).
    """
    mime_type: NotRequired[str]
    r"""Audio format/encoding (e.g. \"audio/pcm\", \"audio/l16\")."""


class AudioStream(BaseModel):
    r"""Definition of an audio input stream."""

    id: Optional[str] = None
    r"""Stream identifier (e.g. \"mic\", \"screen\"). Defaults to \"default\" (index
    0).
    """

    mime_type: Optional[str] = None
    r"""Audio format/encoding (e.g. \"audio/pcm\", \"audio/l16\")."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["id", "mime_type"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m

# --- audioconfig.py ---
VadMode = Union[
    Literal[
        "auto",
        "manual",
    ],
    UnrecognizedStr,
]
r"""Voice Activity Detection mode."""


class AudioConfigParam(TypedDict):
    r"""Configuration for audio processing in interactions."""

    input_streams: NotRequired[List[AudioStreamParam]]
    r"""Active audio input streams. Defaults to a single 16kHz PCM stream if
    omitted.
    """
    vad_mode: NotRequired[VadMode]
    r"""Voice Activity Detection mode."""


class AudioConfig(BaseModel):
    r"""Configuration for audio processing in interactions."""

    input_streams: Optional[List[AudioStream]] = None
    r"""Active audio input streams. Defaults to a single 16kHz PCM stream if
    omitted.
    """

    vad_mode: Optional[VadMode] = None
    r"""Voice Activity Detection mode."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["input_streams", "vad_mode"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m

# --- audiostreamappend.py ---
class AudioStreamAppendTypedDict(TypedDict):
    r"""Audio data chunk for a continuous audio stream."""

    data: NotRequired[str]
    r"""Raw audio data."""
    event_type: Literal["input.audio.append"]
    seq_num: NotRequired[int]
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """
    stream_id: NotRequired[str]
    r"""Stream identifier (e.g. \"mic\", \"screen\"). Optional for single stream."""
    timestamp_micros: NotRequired[int]
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """


class AudioStreamAppend(BaseModel):
    r"""Audio data chunk for a continuous audio stream."""

    data: Optional[str] = None
    r"""Raw audio data."""

    event_type: Annotated[
        Annotated[
            Literal["input.audio.append"],
            AfterValidator(validate_const("input.audio.append")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "input.audio.append"

    seq_num: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """

    stream_id: Optional[str] = None
    r"""Stream identifier (e.g. \"mic\", \"screen\"). Optional for single stream."""

    timestamp_micros: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["data", "seq_num", "stream_id", "timestamp_micros"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    AudioStreamAppend.model_rebuild()
except NameError:
    pass

# --- cancelinteractionevent.py ---
class CancelInteractionEventTypedDict(TypedDict):
    r"""Permanently ends the interaction, aborting any work in flight.
    Reconnecting afterwards is supported to read the final status,
    but no further inputs or messages may be sent.
    """

    event_type: Literal["interaction.cancel"]


class CancelInteractionEvent(BaseModel):
    r"""Permanently ends the interaction, aborting any work in flight.
    Reconnecting afterwards is supported to read the final status,
    but no further inputs or messages may be sent.
    """

    event_type: Annotated[
        Annotated[
            Literal["interaction.cancel"],
            AfterValidator(validate_const("interaction.cancel")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.cancel"

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])


try:
    CancelInteractionEvent.model_rebuild()
except NameError:
    pass

# --- completeinteractionevent.py ---
class CompleteInteractionEventTypedDict(TypedDict):
    r"""Client signal to end the Interaction. Acts like a half-close, the Client will
    not send new input, but will wait for output to finish and may reconnect.
    """

    event_type: Literal["interaction.complete"]


class CompleteInteractionEvent(BaseModel):
    r"""Client signal to end the Interaction. Acts like a half-close, the Client will
    not send new input, but will wait for output to finish and may reconnect.
    """

    event_type: Annotated[
        Annotated[
            Literal["interaction.complete"],
            AfterValidator(validate_const("interaction.complete")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.complete"

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])


try:
    CompleteInteractionEvent.model_rebuild()
except NameError:
    pass

# --- createinteractionevent.py ---
CreateInteractionEventEnvironmentTypedDict = TypeAliasType(
    "CreateInteractionEventEnvironmentTypedDict", Union[EnvironmentParam, str]
)
r"""The environment configuration for the interaction."""


CreateInteractionEventEnvironment = TypeAliasType(
    "CreateInteractionEventEnvironment", Union[Environment, str]
)
r"""The environment configuration for the interaction."""


CreateInteractionEventInputTypedDict = TypeAliasType(
    "CreateInteractionEventInputTypedDict",
    Union[ContentParam, List[StepParam], List[ContentParam], str],
)
r"""The input for the interaction."""


CreateInteractionEventInput = TypeAliasType(
    "CreateInteractionEventInput",
    Annotated[
        Union[
            Annotated[
                Content,
                pydantic.WrapValidator(
                    partial(
                        decline_sibling_variants,
                        union_name="Content",
                        sibling_variants=(
                            (
                                "type",
                                frozenset(
                                    {
                                        "code_execution_call",
                                        "code_execution_result",
                                        "compaction",
                                        "file_search_call",
                                        "file_search_result",
                                        "function_call",
                                        "function_result",
                                        "google_maps_call",
                                        "google_maps_result",
                                        "google_search_call",
                                        "google_search_result",
                                        "mcp_server_tool_call",
                                        "mcp_server_tool_result",
                                        "model_output",
                                        "processing_call",
                                        "processing_result",
                                        "retrieval_call",
                                        "retrieval_result",
                                        "thought",
                                        "tool_search_call",
                                        "tool_search_result",
                                        "url_context_call",
                                        "url_context_result",
                                        "user_input",
                                    }
                                ),
                            ),
                        ),
                    )
                ),
            ],
            List[
                Annotated[
                    Step,
                    pydantic.WrapValidator(
                        partial(
                            decline_sibling_variants,
                            union_name="Step",
                            sibling_variants=(
                                (
                                    "type",
                                    frozenset(
                                        {"audio", "document", "image", "text", "video"}
                                    ),
                                ),
                            ),
                        )
                    ),
                ]
            ],
            List[
                Annotated[
                    Content,
                    pydantic.WrapValidator(
                        partial(
                            decline_sibling_variants,
                            union_name="Content",
                            sibling_variants=(
                                (
                                    "type",
                                    frozenset(
                                        {
                                            "code_execution_call",
                                            "code_execution_result",
                                            "compaction",
                                            "file_search_call",
                                            "file_search_result",
                                            "function_call",
                                            "function_result",
                                            "google_maps_call",
                                            "google_maps_result",
                                            "google_search_call",
                                            "google_search_result",
                                            "mcp_server_tool_call",
                                            "mcp_server_tool_result",
                                            "model_output",
                                            "processing_call",
                                            "processing_result",
                                            "retrieval_call",
                                            "retrieval_result",
                                            "thought",
                                            "url_context_call",
                                            "url_context_result",
                                            "user_input",
                                        }
                                    ),
                                ),
                            ),
                        )
                    ),
                ]
            ],
            str,
        ],
        pydantic.WrapValidator(
            partial(
                dispatch_open_union_members,
                members=(
                    Annotated[
                        Content,
                        pydantic.WrapValidator(
                            partial(
                                decline_sibling_variants,
                                union_name="Content",
                                sibling_variants=(
                                    (
                                        "type",
                                        frozenset(
                                            {
                                                "code_execution_call",
                                                "code_execution_result",
                                                "compaction",
                                                "file_search_call",
                                                "file_search_result",
                                                "function_call",
                                                "function_result",
                                                "google_maps_call",
                                                "google_maps_result",
                                                "google_search_call",
                                                "google_search_result",
                                                "mcp_server_tool_call",
                                                "mcp_server_tool_result",
                                                "model_output",
                                                "processing_call",
                                                "processing_result",
                                                "retrieval_call",
                                                "retrieval_result",
                                                "thought",
                                                "url_context_call",
                                                "url_context_result",
                                                "user_input",
                                            }
                                        ),
                                    ),
                                ),
                            )
                        ),
                    ],
                    List[
                        Annotated[
                            Step,
                            pydantic.WrapValidator(
                                partial(
                                    decline_sibling_variants,
                                    union_name="Step",
                                    sibling_variants=(
                                        (
                                            "type",
                                            frozenset(
                                                {
                                                    "audio",
                                                    "document",
                                                    "image",
                                                    "text",
                                                    "video",
                                                }
                                            ),
                                        ),
                                    ),
                                )
                            ),
                        ]
                    ],
                    List[
                        Annotated[
                            Content,
                            pydantic.WrapValidator(
                                partial(
                                    decline_sibling_variants,
                                    union_name="Content",
                                    sibling_variants=(
                                        (
                                            "type",
                                            frozenset(
                                                {
                                                    "code_execution_call",
                                                    "code_execution_result",
                                                    "compaction",
                                                    "file_search_call",
                                                    "file_search_result",
                                                    "function_call",
                                                    "function_result",
                                                    "google_maps_call",
                                                    "google_maps_result",
                                                    "google_search_call",
                                                    "google_search_result",
                                                    "mcp_server_tool_call",
                                                    "mcp_server_tool_result",
                                                    "model_output",
                                                    "processing_call",
                                                    "processing_result",
                                                    "retrieval_call",
                                                    "retrieval_result",
                                                    "thought",
                                                    "url_context_call",
                                                    "url_context_result",
                                                    "user_input",
                                                }
                                            ),
                                        ),
                                    ),
                                )
                            ),
                        ]
                    ],
                ),
            )
        ),
    ],
)
r"""The input for the interaction."""


CreateInteractionEventResponseFormatTypedDict = TypeAliasType(
    "CreateInteractionEventResponseFormatTypedDict",
    Union[ResponseFormatParam, List[ResponseFormatParam]],
)
r"""The response format configuration."""


CreateInteractionEventResponseFormat = TypeAliasType(
    "CreateInteractionEventResponseFormat", Union[ResponseFormat, List[ResponseFormat]]
)
r"""The response format configuration."""


class CreateInteractionEventTypedDict(TypedDict):
    r"""Starts a new Interaction."""

    background: NotRequired[bool]
    r"""Whether to run the interaction in the background."""
    environment: NotRequired[CreateInteractionEventEnvironmentTypedDict]
    r"""The environment configuration for the interaction."""
    event_type: Literal["interaction.create"]
    input: NotRequired[CreateInteractionEventInputTypedDict]
    r"""The input for the interaction."""
    model: NotRequired[str]
    r"""The name of the `Model` used for generating the completion."""
    previous_interaction_id: NotRequired[str]
    r"""The ID of a previous interaction. If set, the output from that interaction
    will be prepended to the input. That interaction must have been run with
    store=true and must be in a terminal state (e.g., COMPLETED).
    """
    response_format: NotRequired[CreateInteractionEventResponseFormatTypedDict]
    r"""The response format configuration."""
    response_modalities: NotRequired[List[ResponseModality]]
    r"""The requested modalities of the response (TEXT, IMAGE, AUDIO)."""
    service_tier: NotRequired[ServiceTier]
    store: NotRequired[bool]
    r"""Whether to store the interaction so that it can be retrieved later, e.g.
    to be referenced as the `previous_interaction_id` of a subsequent
    interaction.

    This does not enable / disable the storage needed to execute the
    interaction itself (e.g. to reconnect or to recover from a failure).
    """
    system_instruction: NotRequired[str]
    r"""System instruction for the interaction.
    Deprecated: Use developer_instructions instead.
    """
    tools: NotRequired[List[ToolParam]]
    r"""A list of tool declarations the model may call during interaction."""
    webhook_config: NotRequired[WebhookConfigParam]
    r"""Message for configuring webhook events for a request."""


class CreateInteractionEvent(BaseModel):
    r"""Starts a new Interaction."""

    background: Optional[bool] = None
    r"""Whether to run the interaction in the background."""

    environment: Optional[CreateInteractionEventEnvironment] = None
    r"""The environment configuration for the interaction."""

    event_type: Annotated[
        Annotated[
            Literal["interaction.create"],
            AfterValidator(validate_const("interaction.create")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.create"

    input: Optional[CreateInteractionEventInput] = None
    r"""The input for the interaction."""

    model: Optional[str] = None
    r"""The name of the `Model` used for generating the completion."""

    previous_interaction_id: Optional[str] = None
    r"""The ID of a previous interaction. If set, the output from that interaction
    will be prepended to the input. That interaction must have been run with
    store=true and must be in a terminal state (e.g., COMPLETED).
    """

    response_format: Optional[CreateInteractionEventResponseFormat] = None
    r"""The response format configuration."""

    response_modalities: Optional[List[ResponseModality]] = None
    r"""The requested modalities of the response (TEXT, IMAGE, AUDIO)."""

    service_tier: Optional[ServiceTier] = None

    store: Optional[bool] = None
    r"""Whether to store the interaction so that it can be retrieved later, e.g.
    to be referenced as the `previous_interaction_id` of a subsequent
    interaction.

    This does not enable / disable the storage needed to execute the
    interaction itself (e.g. to reconnect or to recover from a failure).
    """

    system_instruction: Optional[str] = None
    r"""System instruction for the interaction.
    Deprecated: Use developer_instructions instead.
    """

    tools: Optional[List[Tool]] = None
    r"""A list of tool declarations the model may call during interaction."""

    webhook_config: Optional[WebhookConfig] = None
    r"""Message for configuring webhook events for a request."""

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(
            [
                "background",
                "environment",
                "input",
                "model",
                "previous_interaction_id",
                "response_format",
                "response_modalities",
                "service_tier",
                "store",
                "system_instruction",
                "tools",
                "webhook_config",
            ]
        )
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    CreateInteractionEvent.model_rebuild()
except NameError:
    pass

# --- disconnectevent.py ---
class DisconnectEventTypedDict(TypedDict):
    r"""Requests a graceful disconnection without ending the interaction."""

    event_type: Literal["interaction.disconnect"]


class DisconnectEvent(BaseModel):
    r"""Requests a graceful disconnection without ending the interaction."""

    event_type: Annotated[
        Annotated[
            Literal["interaction.disconnect"],
            AfterValidator(validate_const("interaction.disconnect")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.disconnect"

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])


try:
    DisconnectEvent.model_rebuild()
except NameError:
    pass

# --- functioninvocation.py ---
class FunctionInvocationTypedDict(TypedDict):
    r"""A call to a client-side function."""

    arguments: NotRequired[Dict[str, Any]]
    r"""The arguments to pass to the function."""
    call_id: NotRequired[str]
    r"""The ID of this call. Must be propagated to the response."""
    event_type: Literal["function_invocation"]
    name: NotRequired[str]
    r"""The name of the tool to call."""
    seq_num: NotRequired[int]
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """
    timestamp_micros: NotRequired[int]
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """


class FunctionInvocation(BaseModel):
    r"""A call to a client-side function."""

    arguments: Optional[Dict[str, Any]] = None
    r"""The arguments to pass to the function."""

    call_id: Optional[str] = None
    r"""The ID of this call. Must be propagated to the response."""

    event_type: Annotated[
        Annotated[
            Literal["function_invocation"],
            AfterValidator(validate_const("function_invocation")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "function_invocation"

    name: Optional[str] = None
    r"""The name of the tool to call."""

    seq_num: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """

    timestamp_micros: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(
            ["arguments", "call_id", "name", "seq_num", "timestamp_micros"]
        )
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    FunctionInvocation.model_rebuild()
except NameError:
    pass

# --- functionresultevent.py ---
class FunctionResultEventTypedDict(TypedDict):
    r"""The result of executing a client-side function call."""

    call_id: NotRequired[str]
    r"""The ID of the FunctionInvocation call being responded to."""
    event_type: Literal["function_result"]
    is_error: NotRequired[bool]
    r"""Whether the tool call resulted in an error."""
    name: NotRequired[str]
    r"""The name of the tool that was called."""
    result: NotRequired[Any]
    r"""The result of the tool call."""
    seq_num: NotRequired[int]
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """
    timestamp_micros: NotRequired[int]
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """


class FunctionResultEvent(BaseModel):
    r"""The result of executing a client-side function call."""

    call_id: Optional[str] = None
    r"""The ID of the FunctionInvocation call being responded to."""

    event_type: Annotated[
        Annotated[
            Literal["function_result"],
            AfterValidator(validate_const("function_result")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "function_result"

    is_error: Optional[bool] = None
    r"""Whether the tool call resulted in an error."""

    name: Optional[str] = None
    r"""The name of the tool that was called."""

    result: Optional[Any] = None
    r"""The result of the tool call."""

    seq_num: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """

    timestamp_micros: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(
            ["call_id", "is_error", "name", "result", "seq_num", "timestamp_micros"]
        )
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    FunctionResultEvent.model_rebuild()
except NameError:
    pass

# --- inputcommitevent.py ---
class InputCommitEventTypedDict(TypedDict):
    r"""Signals turn completion in manual-VAD mode."""

    event_type: Literal["input.commit"]
    seq_num: NotRequired[int]
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """
    timestamp_micros: NotRequired[int]
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """


class InputCommitEvent(BaseModel):
    r"""Signals turn completion in manual-VAD mode."""

    event_type: Annotated[
        Annotated[
            Literal["input.commit"], AfterValidator(validate_const("input.commit"))
        ],
        pydantic.Field(alias="event_type"),
    ] = "input.commit"

    seq_num: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """

    timestamp_micros: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["seq_num", "timestamp_micros"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    InputCommitEvent.model_rebuild()
except NameError:
    pass

# --- inputevent.py ---
class InputEventTypedDict(TypedDict):
    r"""Atomic input payload — replaces user_input step on bidi wire.
    Sent by clients as a single complete input message.
    """

    content: NotRequired[List[ContentParam]]
    r"""Content parts making up the input (text, images, documents, etc.).
    Reuses the existing Content message from content.proto.
    """
    event_type: Literal["input"]
    mode: NotRequired[InputDeliveryMode]
    seq_num: NotRequired[int]
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """
    timestamp_micros: NotRequired[int]
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """


class InputEvent(BaseModel):
    r"""Atomic input payload — replaces user_input step on bidi wire.
    Sent by clients as a single complete input message.
    """

    content: Optional[List[Content]] = None
    r"""Content parts making up the input (text, images, documents, etc.).
    Reuses the existing Content message from content.proto.
    """

    event_type: Annotated[
        Annotated[Literal["input"], AfterValidator(validate_const("input"))],
        pydantic.Field(alias="event_type"),
    ] = "input"

    mode: Optional[InputDeliveryMode] = None

    seq_num: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""1-based sequence number of this event within the direction (distinct
    numbering for client vs. server). Increments by 1 for each event.
    """

    timestamp_micros: Annotated[
        Optional[int],
        BeforeValidator(validate_int),
        PlainSerializer(serialize_int(True)),
    ] = None
    r"""Strictly increasing timestamp of when the event was generated, in unix
    micros.
    """

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["content", "mode", "seq_num", "timestamp_micros"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    InputEvent.model_rebuild()
except NameError:
    pass

# --- interactionreconnectedevent.py ---
class InteractionReconnectedEventTypedDict(TypedDict):
    r"""The response when reconnecting to a live interaction.

    The server sets `next_input_seq_num` to tell the client the first input
    event it still needs (i.e., resume input from here). Additionally,
    `ack_input_seq_num` on the enclosing `ServerEventBatch` confirms
    cumulative receipt through that seq_num.
    """

    event_type: Literal["interaction.connected"]


class InteractionReconnectedEvent(BaseModel):
    r"""The response when reconnecting to a live interaction.

    The server sets `next_input_seq_num` to tell the client the first input
    event it still needs (i.e., resume input from here). Additionally,
    `ack_input_seq_num` on the enclosing `ServerEventBatch` confirms
    cumulative receipt through that seq_num.
    """

    event_type: Annotated[
        Annotated[
            Literal["interaction.connected"],
            AfterValidator(validate_const("interaction.connected")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.connected"

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])


try:
    InteractionReconnectedEvent.model_rebuild()
except NameError:
    pass

# --- liveinteractioncompletedevent.py ---
class LiveInteractionCompletedEventTypedDict(TypedDict):
    r"""Signals that the Interaction completed. Sent when the Interaction receives
    Complete/Cancel or naturally terminates. No more input can be sent to the
    Interaction after this.
    """

    created: NotRequired[str]
    r"""The time at which the response was created in ISO 8601 format
    (YYYY-MM-DDThh:mm:ssZ).
    """
    event_type: Literal["interaction.completed"]
    status: NotRequired[StatusParam]
    r"""The `Status` type defines a logical error model that is suitable for
    different programming environments, including REST APIs and RPC APIs. It is
    used by [gRPC](https://github.com/grpc). Each `Status` message contains
    three pieces of data: error code, error message, and error details.

    You can find out more about this error model and how to work with it in the
    [API Design Guide](https://cloud.google.com/apis/design/errors).
    """
    updated: NotRequired[str]
    r"""The time at which the response was last updated in ISO 8601 format
    (YYYY-MM-DDThh:mm:ssZ).
    """


class LiveInteractionCompletedEvent(BaseModel):
    r"""Signals that the Interaction completed. Sent when the Interaction receives
    Complete/Cancel or naturally terminates. No more input can be sent to the
    Interaction after this.
    """

    created: Optional[str] = None
    r"""The time at which the response was created in ISO 8601 format
    (YYYY-MM-DDThh:mm:ssZ).
    """

    event_type: Annotated[
        Annotated[
            Literal["interaction.completed"],
            AfterValidator(validate_const("interaction.completed")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.completed"

    status: Optional[Status] = None
    r"""The `Status` type defines a logical error model that is suitable for
    different programming environments, including REST APIs and RPC APIs. It is
    used by [gRPC](https://github.com/grpc). Each `Status` message contains
    three pieces of data: error code, error message, and error details.

    You can find out more about this error model and how to work with it in the
    [API Design Guide](https://cloud.google.com/apis/design/errors).
    """

    updated: Optional[str] = None
    r"""The time at which the response was last updated in ISO 8601 format
    (YYYY-MM-DDThh:mm:ssZ).
    """

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["created", "status", "updated"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    LiveInteractionCompletedEvent.model_rebuild()
except NameError:
    pass

# --- liveinteractioncreatedevent.py ---
class LiveInteractionCreatedEventTypedDict(TypedDict):
    r"""Server response confirming that a new interaction was created."""

    event_type: Literal["interaction.created"]
    interaction_id: NotRequired[str]


class LiveInteractionCreatedEvent(BaseModel):
    r"""Server response confirming that a new interaction was created."""

    event_type: Annotated[
        Annotated[
            Literal["interaction.created"],
            AfterValidator(validate_const("interaction.created")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.created"

    interaction_id: Optional[str] = None

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["interaction_id"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    LiveInteractionCreatedEvent.model_rebuild()
except NameError:
    pass

# --- reconnectinteractionevent.py ---
class ReconnectInteractionEventTypedDict(TypedDict):
    r"""Reconnects to an existing live Interaction.

    The client sets `next_output_seq_num` to tell the server the first output
    event it still needs (i.e. resume output from here). Additionally,
    `ack_output_seq_num` on the enclosing `ClientEventBatch` confirms
    cumulative receipt through that seq_num.

    The server responds with `InteractionReconnectedEvent` containing
    `next_input_seq_num`, telling the client where to resume sending input.
    If the interaction is already complete, the server will replay events
    starting from `next_output_seq_num` through completion.
    """

    background: NotRequired[bool]
    r"""When true, signals that the client intends to disconnect after sending
    this message. The server continues running in the background. The client
    is expected to close the stream after sending this message, and can
    reconnect again later to retrieve further output.
    """
    event_type: Literal["interaction.connect"]
    id: NotRequired[str]


class ReconnectInteractionEvent(BaseModel):
    r"""Reconnects to an existing live Interaction.

    The client sets `next_output_seq_num` to tell the server the first output
    event it still needs (i.e. resume output from here). Additionally,
    `ack_output_seq_num` on the enclosing `ClientEventBatch` confirms
    cumulative receipt through that seq_num.

    The server responds with `InteractionReconnectedEvent` containing
    `next_input_seq_num`, telling the client where to resume sending input.
    If the interaction is already complete, the server will replay events
    starting from `next_output_seq_num` through completion.
    """

    background: Optional[bool] = None
    r"""When true, signals that the client intends to disconnect after sending
    this message. The server continues running in the background. The client
    is expected to close the stream after sending this message, and can
    reconnect again later to retrieve further output.
    """

    event_type: Annotated[
        Annotated[
            Literal["interaction.connect"],
            AfterValidator(validate_const("interaction.connect")),
        ],
        pydantic.Field(alias="event_type"),
    ] = "interaction.connect"

    id: Optional[str] = None

    def model_post_init(self, context: Any, /) -> None:
        self.__pydantic_fields_set__.update(["event_type"])

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["background", "id"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


try:
    ReconnectInteractionEvent.model_rebuild()
except NameError:
    pass

# --- clientevent.py ---
ClientEventTypedDict = TypeAliasType(
    "ClientEventTypedDict",
    Union[
        CancelInteractionEventTypedDict,
        CompleteInteractionEventTypedDict,
        DisconnectEventTypedDict,
        InputCommitEventTypedDict,
        ReconnectInteractionEventTypedDict,
        AudioStreamAppendTypedDict,
        InputEventTypedDict,
        FunctionResultEventTypedDict,
        CreateInteractionEventTypedDict,
    ],
)
r"""Wrapper for client events to support flexible JSON payload formats."""


ClientEvent = Annotated[
    Union[
        Annotated[AudioStreamAppend, Tag("input.audio.append")],
        Annotated[CancelInteractionEvent, Tag("interaction.cancel")],
        Annotated[CompleteInteractionEvent, Tag("interaction.complete")],
        Annotated[CreateInteractionEvent, Tag("interaction.create")],
        Annotated[DisconnectEvent, Tag("interaction.disconnect")],
        Annotated[FunctionResultEvent, Tag("function_result")],
        Annotated[InputCommitEvent, Tag("input.commit")],
        Annotated[InputEvent, Tag("input")],
        Annotated[ReconnectInteractionEvent, Tag("interaction.connect")],
    ],
    Discriminator(lambda m: get_discriminator(m, "event_type", "event_type")),
]
r"""Wrapper for client events to support flexible JSON payload formats."""

# --- clienteventlist.py ---
class ClientEventListTypedDict(TypedDict):
    r"""Wrapper for a list of client events."""

    events: List[ClientEventTypedDict]
    r"""The list of client events."""


class ClientEventList(BaseModel):
    r"""Wrapper for a list of client events."""

    events: List[ClientEvent]
    r"""The list of client events."""

# --- clienteventbatch.py ---
ClientEventBatchTypedDict = TypeAliasType(
    "ClientEventBatchTypedDict", Union[ClientEventListTypedDict, ClientEventTypedDict]
)
r"""Top-level client->server wire message. Carries either a single event or a
batch of events.
"""


ClientEventBatch = TypeAliasType(
    "ClientEventBatch", Union[ClientEventList, ClientEvent]
)
r"""Top-level client->server wire message. Carries either a single event or a
batch of events.
"""

# --- serverevent.py ---
ServerEventTypedDict = TypeAliasType(
    "ServerEventTypedDict",
    Union[
        InteractionReconnectedEventTypedDict,
        LiveInteractionCreatedEventTypedDict,
        LiveInteractionCompletedEventTypedDict,
        FunctionInvocationTypedDict,
        StepStartTypedDict,
        StepDeltaTypedDict,
        StepStopTypedDict,
    ],
)
r"""Top-level server->client wire message."""


ServerEvent = Annotated[
    Union[
        Annotated[FunctionInvocation, Tag("function_invocation")],
        Annotated[InteractionReconnectedEvent, Tag("interaction.connected")],
        Annotated[LiveInteractionCompletedEvent, Tag("interaction.completed")],
        Annotated[LiveInteractionCreatedEvent, Tag("interaction.created")],
        Annotated[StepDelta, Tag("step.delta")],
        Annotated[StepStart, Tag("step.start")],
        Annotated[StepStop, Tag("step.stop")],
    ],
    Discriminator(lambda m: get_discriminator(m, "event_type", "event_type")),
]
r"""Top-level server->client wire message."""

# --- createinteractionauthtoken.py ---
class CreateInteractionAuthTokenGlobalsTypedDict(TypedDict):
    api_version: NotRequired[str]
    r"""API version for request routing."""


class CreateInteractionAuthTokenGlobals(BaseModel):
    api_version: Annotated[
        Optional[str],
        FieldMetadata(path=PathParamMetadata(style="simple", explode=False)),
    ] = None
    r"""API version for request routing."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["api_version"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


class CreateInteractionAuthTokenRequestParam(TypedDict):
    id: str
    r"""Required. interaction_id"""
    body: InteractionAuthTokenCreateParamsParam
    api_version: NotRequired[str]
    r"""API version for request routing."""


class CreateInteractionAuthTokenRequest(BaseModel):
    id: Annotated[
        str,
        pydantic.Field(alias="interactionsId"),
        FieldMetadata(path=PathParamMetadata(style="simple", explode=False)),
    ]
    r"""Required. interaction_id"""

    body: Annotated[
        InteractionAuthTokenCreateParams,
        FieldMetadata(request=RequestMetadata(media_type="application/json")),
    ]

    api_version: Annotated[
        Optional[str],
        FieldMetadata(path=PathParamMetadata(style="simple", explode=False)),
    ] = None
    r"""API version for request routing."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["api_version"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m

# --- deleteinteractionauthtoken.py ---
class DeleteInteractionAuthTokenGlobalsTypedDict(TypedDict):
    api_version: NotRequired[str]
    r"""API version for request routing."""


class DeleteInteractionAuthTokenGlobals(BaseModel):
    api_version: Annotated[
        Optional[str],
        FieldMetadata(path=PathParamMetadata(style="simple", explode=False)),
    ] = None
    r"""API version for request routing."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["api_version"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m


class DeleteInteractionAuthTokenRequestParam(TypedDict):
    id: str
    r"""Required. The interaction ID owning the auth token to revoke."""
    auth_token: str
    r"""Required. The hex token string returned by `CreateInteractionAuthToken` (the `auth_token` value without its `auth_tokens/` prefix)."""
    api_version: NotRequired[str]
    r"""API version for request routing."""


class DeleteInteractionAuthTokenRequest(BaseModel):
    id: Annotated[
        str,
        pydantic.Field(alias="interactionsId"),
        FieldMetadata(path=PathParamMetadata(style="simple", explode=False)),
    ]
    r"""Required. The interaction ID owning the auth token to revoke."""

    auth_token: Annotated[
        str,
        pydantic.Field(alias="auth_tokensId"),
        FieldMetadata(path=PathParamMetadata(style="simple", explode=False)),
    ]
    r"""Required. The hex token string returned by `CreateInteractionAuthToken` (the `auth_token` value without its `auth_tokens/` prefix)."""

    api_version: Annotated[
        Optional[str],
        FieldMetadata(path=PathParamMetadata(style="simple", explode=False)),
    ] = None
    r"""API version for request routing."""

    @model_serializer(mode="wrap")
    def _serialize_model_with_info(self, handler, info):
        return serialize_with_info(self.serialize_model, handler, info)

    def serialize_model(self, handler):
        optional_fields = set(["api_version"])
        exclude_none = current_exclude_none()
        by_alias = current_by_alias()
        use_field_names = by_alias is False
        serialization_methods_dump = current_serialization_methods_dump()
        skip_filtered = (
            serialization_methods_dump
            or exclude_none is False
            or current_filtered_dump()
        )
        serialized = handler(self)
        m = {}

        for n, f in type(self).model_fields.items():
            k = f.alias if f.alias is not None else n
            key = k if by_alias or k in serialized else n
            if key not in serialized and skip_filtered:
                continue
            val = serialized.pop(key, None)

            if val != UNSET_SENTINEL:
                if val is not None or k not in optional_fields:
                    m[n if use_field_names else k] = val
        for k, v in serialized.items():
            m[k] = v

        return m

# --- auth_tokens.py ---
class AuthTokens(BaseSDK):
    @property
    def with_raw_response(self):
        return AuthTokensWithRawResponse(self)

    @property
    def with_streaming_response(self):
        return AuthTokensWithStreamingResponse(self)

    def create(
        self,
        id: str,
        *,
        api_version: Optional[str] = None,
        expire_time: Optional[datetime] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        extra_query: Optional[Mapping[str, Any]] = None,
        extra_body: Optional[Mapping[str, Any]] = None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
    ) -> InteractionAuthToken:
        r"""Creates a short-lived auth token for client-side authentication (HTTP).

        :param id: Required. interaction_id
        :param api_version: API version for request routing.
        :param expire_time: Hard deadline - messages rejected after this time.
        :param extra_headers: Additional headers to set or replace on requests.
        :param extra_query: Additional query parameters to append to requests.
        :param extra_body: Additional JSON object fields to merge into request bodies.
        :param timeout: Override the default request timeout configuration for this method in seconds
        """
        base_url = None
        url_variables = None
        retries: OptionalNullable[utils.RetryConfig] = UNSET
        server_url = None
        http_headers = extra_headers
        timeout_ms = self._coerce_timeout_ms(timeout)
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms

        if server_url is not None:
            base_url = server_url
        else:
            base_url = self._get_url(base_url, url_variables)

        request = CreateInteractionAuthTokenRequest(
            api_version=api_version,
            id=id,
            body=InteractionAuthTokenCreateParams(
                expire_time=expire_time,
            ),
        )

        _speakeasy_response_mode, http_headers = response_helpers.consume_response_mode(
            http_headers
        )
        req = self._build_request(
            method="POST",
            path="/{api_version}/interactions/{interactionsId}/auth_tokens",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=True,
            request_has_path_params=True,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="application/json",
            http_headers=http_headers,
            extra_query_params=extra_query,
            _globals=CreateInteractionAuthTokenGlobals(
                api_version=self.sdk_configuration.globals.api_version,
            ),
            security=self.sdk_configuration.security,
            get_serialized_body=lambda: utils.serialize_request_body(
                request.body,
                False,
                False,
                "json",
                InteractionAuthTokenCreateParams,
                extra_body=extra_body,
            ),
            allow_empty_value=None,
            timeout_ms=timeout_ms,
        )

        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config
            else:
                retries = utils.RetryConfig(
                    "attempt-count-backoff",
                    utils.BackoffStrategy(500, 8000, 2, 30000),
                    True,
                    max_retries=4,
                )

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, ["408", "409", "429", "5XX"])

        def _speakeasy_parse_response(http_res):
            if utils.match_response(http_res, "4XX", "*"):
                http_res_text = utils.stream_to_text(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "5XX", "*"):
                http_res_text = utils.stream_to_text(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "default", "application/json"):
                return unmarshal_json_response(
                    InteractionAuthToken, http_res, validate=False
                )

            raise errors.GenAiDefaultError("Unexpected response received", http_res)

        _speakeasy_hook_ctx = HookContext(
            config=self.sdk_configuration,
            base_url=base_url or "",
            operation_id="CreateInteractionAuthToken",
            oauth2_scopes=None,
            security_source=get_security_from_env(
                self.sdk_configuration.security, types.Security
            ),
            tags=["interactions.auth_tokens"],
            extensions=None,
            response=ResponseContext(mode=_speakeasy_response_mode, execution="sync"),
        )
        http_res = self.do_request(
            hook_ctx=_speakeasy_hook_ctx,
            request=req,
            is_error_status_code=lambda c: utils.match_status_codes(["4XX", "5XX"], c),
            stream=_speakeasy_response_mode == "streaming",
            retry_config=retry_config,
        )
        if _speakeasy_response_mode != "parsed":
            if utils.match_status_codes(["4XX", "5XX"], http_res.status_code):
                http_res.read()
                try:
                    _speakeasy_parse_response(http_res)
                except Exception as parse_exc_:
                    response_helpers.raise_parse_error(
                        self.sdk_configuration.__dict__["_hooks"],
                        AfterParseErrorContext(_speakeasy_hook_ctx),
                        http_res,
                        parse_exc_,
                    )
            _speakeasy_response_cls = (
                response_helpers.StreamedAPIResponse
                if _speakeasy_response_mode == "streaming"
                else response_helpers.APIResponse
            )
            return cast(
                Any,
                _speakeasy_response_cls(
                    raw=http_res,
                    parser=_speakeasy_parse_response,
                    mode="buffered",
                    client_ref=self,
                    hook_ctx=AfterParseErrorContext(_speakeasy_hook_ctx),
                    hooks=self.sdk_configuration.__dict__.get("_hooks"),
                ),
            )
        try:
            return _speakeasy_parse_response(http_res)
        except Exception as parse_exc_:
            response_helpers.raise_parse_error(
                self.sdk_configuration.__dict__["_hooks"],
                AfterParseErrorContext(_speakeasy_hook_ctx),
                http_res,
                parse_exc_,
            )

    def delete(
        self,
        id: str,
        auth_token: str,
        *,
        api_version: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        extra_query: Optional[Mapping[str, Any]] = None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
    ) -> interactions.Empty:
        r"""Deletes (revokes) an interaction auth token (HTTP).

        :param id: Required. The interaction ID owning the auth token to revoke.
        :param auth_token: Required. The hex token string returned by `CreateInteractionAuthToken` (the `auth_token` value without its `auth_tokens/` prefix).
        :param api_version: API version for request routing.
        :param extra_headers: Additional headers to set or replace on requests.
        :param extra_query: Additional query parameters to append to requests.
        :param timeout: Override the default request timeout configuration for this method in seconds
        """
        base_url = None
        url_variables = None
        retries: OptionalNullable[utils.RetryConfig] = UNSET
        server_url = None
        http_headers = extra_headers
        timeout_ms = self._coerce_timeout_ms(timeout)
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms

        if server_url is not None:
            base_url = server_url
        else:
            base_url = self._get_url(base_url, url_variables)

        request = DeleteInteractionAuthTokenRequest(
            api_version=api_version,
            id=id,
            auth_token=auth_token,
        )

        _speakeasy_response_mode, http_headers = response_helpers.consume_response_mode(
            http_headers
        )
        req = self._build_request(
            method="DELETE",
            path="/{api_version}/interactions/{interactionsId}/auth_tokens/{auth_tokensId}",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=False,
            request_has_path_params=True,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="application/json",
            http_headers=http_headers,
            extra_query_params=extra_query,
            _globals=DeleteInteractionAuthTokenGlobals(
                api_version=self.sdk_configuration.globals.api_version,
            ),
            security=self.sdk_configuration.security,
            allow_empty_value=None,
            timeout_ms=timeout_ms,
        )

        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config
            else:
                retries = utils.RetryConfig(
                    "attempt-count-backoff",
                    utils.BackoffStrategy(500, 8000, 2, 30000),
                    True,
                    max_retries=4,
                )

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, ["408", "409", "429", "5XX"])

        def _speakeasy_parse_response(http_res):
            if utils.match_response(http_res, "4XX", "*"):
                http_res_text = utils.stream_to_text(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "5XX", "*"):
                http_res_text = utils.stream_to_text(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "default", "application/json"):
                return unmarshal_json_response(
                    interactions.Empty, http_res, validate=False
                )

            raise errors.GenAiDefaultError("Unexpected response received", http_res)

        _speakeasy_hook_ctx = HookContext(
            config=self.sdk_configuration,
            base_url=base_url or "",
            operation_id="DeleteInteractionAuthToken",
            oauth2_scopes=None,
            security_source=get_security_from_env(
                self.sdk_configuration.security, types.Security
            ),
            tags=["interactions.auth_tokens"],
            extensions=None,
            response=ResponseContext(mode=_speakeasy_response_mode, execution="sync"),
        )
        http_res = self.do_request(
            hook_ctx=_speakeasy_hook_ctx,
            request=req,
            is_error_status_code=lambda c: utils.match_status_codes(["4XX", "5XX"], c),
            stream=_speakeasy_response_mode == "streaming",
            retry_config=retry_config,
        )
        if _speakeasy_response_mode != "parsed":
            if utils.match_status_codes(["4XX", "5XX"], http_res.status_code):
                http_res.read()
                try:
                    _speakeasy_parse_response(http_res)
                except Exception as parse_exc_:
                    response_helpers.raise_parse_error(
                        self.sdk_configuration.__dict__["_hooks"],
                        AfterParseErrorContext(_speakeasy_hook_ctx),
                        http_res,
                        parse_exc_,
                    )
            _speakeasy_response_cls = (
                response_helpers.StreamedAPIResponse
                if _speakeasy_response_mode == "streaming"
                else response_helpers.APIResponse
            )
            return cast(
                Any,
                _speakeasy_response_cls(
                    raw=http_res,
                    parser=_speakeasy_parse_response,
                    mode="buffered",
                    client_ref=self,
                    hook_ctx=AfterParseErrorContext(_speakeasy_hook_ctx),
                    hooks=self.sdk_configuration.__dict__.get("_hooks"),
                ),
            )
        try:
            return _speakeasy_parse_response(http_res)
        except Exception as parse_exc_:
            response_helpers.raise_parse_error(
                self.sdk_configuration.__dict__["_hooks"],
                AfterParseErrorContext(_speakeasy_hook_ctx),
                http_res,
                parse_exc_,
            )


class AuthTokensWithRawResponse:
    def __init__(self, sdk: AuthTokens) -> None:
        self._sdk = sdk
        self.create = response_helpers.to_raw_response_wrapper(
            sdk.create, "extra_headers"
        )
        self.delete = response_helpers.to_raw_response_wrapper(
            sdk.delete, "extra_headers"
        )


class AuthTokensWithStreamingResponse:
    def __init__(self, sdk: AuthTokens) -> None:
        self._sdk = sdk
        self.create = response_helpers.to_streamed_response_wrapper(
            sdk.create, "extra_headers"
        )
        self.delete = response_helpers.to_streamed_response_wrapper(
            sdk.delete, "extra_headers"
        )


class AsyncAuthTokens(AsyncBaseSDK):
    @property
    def with_raw_response(self):
        return AsyncAuthTokensWithRawResponse(self)

    @property
    def with_streaming_response(self):
        return AsyncAuthTokensWithStreamingResponse(self)

    async def create(
        self,
        id: str,
        *,
        api_version: Optional[str] = None,
        expire_time: Optional[datetime] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        extra_query: Optional[Mapping[str, Any]] = None,
        extra_body: Optional[Mapping[str, Any]] = None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
    ) -> InteractionAuthToken:
        r"""Creates a short-lived auth token for client-side authentication (HTTP).

        :param id: Required. interaction_id
        :param api_version: API version for request routing.
        :param expire_time: Hard deadline - messages rejected after this time.
        :param extra_headers: Additional headers to set or replace on requests.
        :param extra_query: Additional query parameters to append to requests.
        :param extra_body: Additional JSON object fields to merge into request bodies.
        :param timeout: Override the default request timeout configuration for this method in seconds
        """
        base_url = None
        url_variables = None
        retries: OptionalNullable[utils.RetryConfig] = UNSET
        server_url = None
        http_headers = extra_headers
        timeout_ms = self._coerce_timeout_ms(timeout)
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms

        if server_url is not None:
            base_url = server_url
        else:
            base_url = self._get_url(base_url, url_variables)

        request = CreateInteractionAuthTokenRequest(
            api_version=api_version,
            id=id,
            body=InteractionAuthTokenCreateParams(
                expire_time=expire_time,
            ),
        )

        _speakeasy_response_mode, http_headers = response_helpers.consume_response_mode(
            http_headers
        )
        req = self._build_request_async(
            method="POST",
            path="/{api_version}/interactions/{interactionsId}/auth_tokens",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=True,
            request_has_path_params=True,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="application/json",
            http_headers=http_headers,
            extra_query_params=extra_query,
            _globals=CreateInteractionAuthTokenGlobals(
                api_version=self.sdk_configuration.globals.api_version,
            ),
            security=self.sdk_configuration.security,
            get_serialized_body=lambda: utils.serialize_request_body(
                request.body,
                False,
                False,
                "json",
                InteractionAuthTokenCreateParams,
                extra_body=extra_body,
            ),
            allow_empty_value=None,
            timeout_ms=timeout_ms,
        )

        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config
            else:
                retries = utils.RetryConfig(
                    "attempt-count-backoff",
                    utils.BackoffStrategy(500, 8000, 2, 30000),
                    True,
                    max_retries=4,
                )

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, ["408", "409", "429", "5XX"])

        async def _speakeasy_parse_response(http_res):
            if utils.match_response(http_res, "4XX", "*"):
                http_res_text = await utils.stream_to_text_async(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "5XX", "*"):
                http_res_text = await utils.stream_to_text_async(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "default", "application/json"):
                return unmarshal_json_response(
                    InteractionAuthToken, http_res, validate=False
                )

            raise errors.GenAiDefaultError("Unexpected response received", http_res)

        _speakeasy_hook_ctx = HookContext(
            config=self.sdk_configuration,
            base_url=base_url or "",
            operation_id="CreateInteractionAuthToken",
            oauth2_scopes=None,
            security_source=get_security_from_env(
                self.sdk_configuration.security, types.Security
            ),
            tags=["interactions.auth_tokens"],
            extensions=None,
            response=ResponseContext(mode=_speakeasy_response_mode, execution="async"),
        )
        http_res = await self.do_request_async(
            hook_ctx=_speakeasy_hook_ctx,
            request=req,
            is_error_status_code=lambda c: utils.match_status_codes(["4XX", "5XX"], c),
            stream=_speakeasy_response_mode == "streaming",
            retry_config=retry_config,
        )
        if _speakeasy_response_mode != "parsed":
            if utils.match_status_codes(["4XX", "5XX"], http_res.status_code):
                await http_res.aread()
                try:
                    await _speakeasy_parse_response(http_res)
                except Exception as parse_exc_:
                    await response_helpers.raise_parse_error_async(
                        self.sdk_configuration.__dict__.get("_async_hooks"),
                        self.sdk_configuration.__dict__.get("_hooks"),
                        AfterParseErrorContext(_speakeasy_hook_ctx),
                        http_res,
                        parse_exc_,
                    )
            _speakeasy_response_cls = (
                response_helpers.AsyncStreamedAPIResponse
                if _speakeasy_response_mode == "streaming"
                else response_helpers.AsyncAPIResponse
            )
            return cast(
                Any,
                _speakeasy_response_cls(
                    raw=http_res,
                    parser=_speakeasy_parse_response,
                    mode="buffered",
                    client_ref=self,
                    hook_ctx=AfterParseErrorContext(_speakeasy_hook_ctx),
                    hooks=self.sdk_configuration.__dict__.get("_hooks"),
                    async_hooks=self.sdk_configuration.__dict__.get("_async_hooks"),
                ),
            )
        try:
            return await _speakeasy_parse_response(http_res)
        except Exception as parse_exc_:
            await response_helpers.raise_parse_error_async(
                self.sdk_configuration.__dict__.get("_async_hooks"),
                self.sdk_configuration.__dict__.get("_hooks"),
                AfterParseErrorContext(_speakeasy_hook_ctx),
                http_res,
                parse_exc_,
            )

    async def delete(
        self,
        id: str,
        auth_token: str,
        *,
        api_version: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        extra_query: Optional[Mapping[str, Any]] = None,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
    ) -> interactions.Empty:
        r"""Deletes (revokes) an interaction auth token (HTTP).

        :param id: Required. The interaction ID owning the auth token to revoke.
        :param auth_token: Required. The hex token string returned by `CreateInteractionAuthToken` (the `auth_token` value without its `auth_tokens/` prefix).
        :param api_version: API version for request routing.
        :param extra_headers: Additional headers to set or replace on requests.
        :param extra_query: Additional query parameters to append to requests.
        :param timeout: Override the default request timeout configuration for this method in seconds
        """
        base_url = None
        url_variables = None
        retries: OptionalNullable[utils.RetryConfig] = UNSET
        server_url = None
        http_headers = extra_headers
        timeout_ms = self._coerce_timeout_ms(timeout)
        if timeout_ms is None:
            timeout_ms = self.sdk_configuration.timeout_ms

        if server_url is not None:
            base_url = server_url
        else:
            base_url = self._get_url(base_url, url_variables)

        request = DeleteInteractionAuthTokenRequest(
            api_version=api_version,
            id=id,
            auth_token=auth_token,
        )

        _speakeasy_response_mode, http_headers = response_helpers.consume_response_mode(
            http_headers
        )
        req = self._build_request_async(
            method="DELETE",
            path="/{api_version}/interactions/{interactionsId}/auth_tokens/{auth_tokensId}",
            base_url=base_url,
            url_variables=url_variables,
            request=request,
            request_body_required=False,
            request_has_path_params=True,
            request_has_query_params=True,
            user_agent_header="user-agent",
            accept_header_value="application/json",
            http_headers=http_headers,
            extra_query_params=extra_query,
            _globals=DeleteInteractionAuthTokenGlobals(
                api_version=self.sdk_configuration.globals.api_version,
            ),
            security=self.sdk_configuration.security,
            allow_empty_value=None,
            timeout_ms=timeout_ms,
        )

        if retries == UNSET:
            if self.sdk_configuration.retry_config is not UNSET:
                retries = self.sdk_configuration.retry_config
            else:
                retries = utils.RetryConfig(
                    "attempt-count-backoff",
                    utils.BackoffStrategy(500, 8000, 2, 30000),
                    True,
                    max_retries=4,
                )

        retry_config = None
        if isinstance(retries, utils.RetryConfig):
            retry_config = (retries, ["408", "409", "429", "5XX"])

        async def _speakeasy_parse_response(http_res):
            if utils.match_response(http_res, "4XX", "*"):
                http_res_text = await utils.stream_to_text_async(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "5XX", "*"):
                http_res_text = await utils.stream_to_text_async(http_res)
                raise errors.GenAiDefaultError(
                    "API error occurred", http_res, http_res_text
                )
            if utils.match_response(http_res, "default", "application/json"):
                return unmarshal_json_response(
                    interactions.Empty, http_res, validate=False
                )

            raise errors.GenAiDefaultError("Unexpected response received", http_res)

        _speakeasy_hook_ctx = HookContext(
            config=self.sdk_configuration,
            base_url=base_url or "",
            operation_id="DeleteInteractionAuthToken",
            oauth2_scopes=None,
            security_source=get_security_from_env(
                self.sdk_configuration.security, types.Security
            ),
            tags=["interactions.auth_tokens"],
            extensions=None,
            response=ResponseContext(mode=_speakeasy_response_mode, execution="async"),
        )
        http_res = await self.do_request_async(
            hook_ctx=_speakeasy_hook_ctx,
            request=req,
            is_error_status_code=lambda c: utils.match_status_codes(["4XX", "5XX"], c),
            stream=_speakeasy_response_mode == "streaming",
            retry_config=retry_config,
        )
        if _speakeasy_response_mode != "parsed":
            if utils.match_status_codes(["4XX", "5XX"], http_res.status_code):
                await http_res.aread()
                try:
                    await _speakeasy_parse_response(http_res)
                except Exception as parse_exc_:
                    await response_helpers.raise_parse_error_async(
                        self.sdk_configuration.__dict__.get("_async_hooks"),
                        self.sdk_configuration.__dict__.get("_hooks"),
                        AfterParseErrorContext(_speakeasy_hook_ctx),
                        http_res,
                        parse_exc_,
                    )
            _speakeasy_response_cls = (
                response_helpers.AsyncStreamedAPIResponse
                if _speakeasy_response_mode == "streaming"
                else response_helpers.AsyncAPIResponse
            )
            return cast(
                Any,
                _speakeasy_response_cls(
                    raw=http_res,
                    parser=_speakeasy_parse_response,
                    mode="buffered",
                    client_ref=self,
                    hook_ctx=AfterParseErrorContext(_speakeasy_hook_ctx),
                    hooks=self.sdk_configuration.__dict__.get("_hooks"),
                    async_hooks=self.sdk_configuration.__dict__.get("_async_hooks"),
                ),
            )
        try:
            return await _speakeasy_parse_response(http_res)
        except Exception as parse_exc_:
            await response_helpers.raise_parse_error_async(
                self.sdk_configuration.__dict__.get("_async_hooks"),
                self.sdk_configuration.__dict__.get("_hooks"),
                AfterParseErrorContext(_speakeasy_hook_ctx),
                http_res,
                parse_exc_,
            )


class AsyncAuthTokensWithRawResponse:
    def __init__(self, sdk: AsyncAuthTokens) -> None:
        self._sdk = sdk
        self.create = response_helpers.async_to_raw_response_wrapper(
            sdk.create, "extra_headers"
        )
        self.delete = response_helpers.async_to_raw_response_wrapper(
            sdk.delete, "extra_headers"
        )


class AsyncAuthTokensWithStreamingResponse:
    def __init__(self, sdk: AsyncAuthTokens) -> None:
        self._sdk = sdk
        self.create = response_helpers.async_to_streamed_response_wrapper(
            sdk.create, "extra_headers"
        )
        self.delete = response_helpers.async_to_streamed_response_wrapper(
            sdk.delete, "extra_headers"
        )

# --- live_interactions.py ---
_LIVE_INTERACTIONS_EXPERIMENTAL_WARNING = (
    "Live Interactions usage is experimental and may change in future versions."
)
_live_interactions_experimental_warned = False


def _warn_live_interactions_experimental(stacklevel: int = 2) -> None:
    """Emit a one-time-per-process warning on first Live Interactions usage."""
    global _live_interactions_experimental_warned
    if not _live_interactions_experimental_warned:
        _live_interactions_experimental_warned = True
        warnings.warn(
            _LIVE_INTERACTIONS_EXPERIMENTAL_WARNING,
            category=UserWarning,
            stacklevel=stacklevel + 1,
        )


class APIWebSocketError(APIConnectionError):
    """Raised when a live interaction WebSocket connection or frame fails."""

    close_code: Optional[int]
    http_status: Optional[int]
    server_code: Optional[str]

    def __init__(
        self,
        message: str = "WebSocket connection error.",
        *,
        request: Any = None,
        close_code: Optional[int] = None,
        http_status: Optional[int] = None,
        server_code: Optional[str] = None,
    ) -> None:
        super().__init__(message=message, request=request)
        self.close_code = close_code
        self.http_status = http_status
        self.server_code = server_code


def _closed_websocket_error(close_code: Optional[int]) -> APIWebSocketError:
    """Return an ``APIWebSocketError`` describing a closed connection."""
    detail = "The live interaction connection closed."
    if close_code is not None:
        detail = f"The live interaction connection closed with code {close_code}."
    return APIWebSocketError(detail, close_code=close_code)


_LIVE_INTERACTIONS_PATH = "interactions/live"
_TERMINAL_EVENTS = frozenset({
    "interaction.completed",
    "interaction.canceled",
    "interaction.cancelled",
    "reconnection_required",
})


def _decode_frame_text(raw: Any) -> Any:
    """Decode raw bytes to UTF-8 text, raising ``APIWebSocketError`` on failure."""
    if not isinstance(raw, bytes):
        return raw
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise APIWebSocketError(
            "Live interaction server frames must contain UTF-8 JSON text."
        ) from None


def _require_server_event_dict(event: Any) -> dict[str, Any]:
    """Validate that a decoded event is a dict with a non-empty ``event_type`` string."""
    if (
        not isinstance(event, dict)
        or not isinstance(event.get("event_type"), str)
        or not event["event_type"]
    ):
        raise APIWebSocketError(
            "Live interaction server events must have an event_type."
        )
    return event


def _frame_events(raw: Any) -> list[dict[str, Any]]:
    """Decode a server frame into its events in wire order."""
    text = _decode_frame_text(raw)
    try:
        payload = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        raise APIWebSocketError(
            "Live interaction server frames must contain valid JSON."
        ) from None
    candidates = (
        payload["events"]
        if isinstance(payload, dict) and isinstance(payload.get("events"), list)
        else [payload]
    )
    return [_require_server_event_dict(event) for event in candidates]


def _to_json_value(value: Any) -> Any:
    """Recursively convert Pydantic models and mappings to plain JSON-serializable values."""
    if isinstance(value, PydanticBaseModel):
        return value.model_dump(
            mode="json",
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
        )
    if isinstance(value, Mapping):
        return {key: _to_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_value(item) for item in value]
    return value


def _serialize_client_event(event: Any) -> dict[str, Any]:
    """Serialize a single client event (Pydantic model or mapping) to a JSON-ready dict."""
    if isinstance(event, PydanticBaseModel):
        return event.model_dump(
            mode="json",
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
        )
    if isinstance(event, Mapping):
        return {key: _to_json_value(value) for key, value in event.items()}
    raise ValueError("Live client events must be mappings or Pydantic models.")


def _serialize_client_payload(input: Any) -> dict[str, Any]:
    """Normalize ``send()`` input (text, single event, or event list) into a wire payload dict."""
    if isinstance(input, str):
        return {
            "event_type": "input",
            "content": [{"type": "text", "text": input}],
        }
    if isinstance(input, (list, tuple)):
        return {"events": [_serialize_client_event(item) for item in input]}
    return _serialize_client_event(input)


def _payload_has_cancel(payload: Mapping[str, Any]) -> bool:
    """Return whether the serialized payload contains an ``interaction.cancel`` event."""
    if payload.get("event_type") == "interaction.cancel":
        return True
    events = payload.get("events")
    if not isinstance(events, list):
        return False
    return any(
        isinstance(item, Mapping)
        and item.get("event_type") == "interaction.cancel"
        for item in events
    )


def _safe_close_code(error: ConnectionClosed) -> int:
    """Return a close code without exposing the peer's close reason."""
    close = error.rcvd if error.rcvd is not None else error.sent
    if close is None:
        return int(CloseCode.ABNORMAL_CLOSURE)
    return close.code


def _parse_server_event(payload: dict[str, Any]) -> Any:
    """Unmarshal a raw server event dict into a typed ``ServerEvent`` or ``ErrorEvent``."""
    target_type: Any = (
        ErrorEvent
        if payload.get("event_type") == "error"
        else ServerEvent
    )
    try:
        return unmarshal(
            payload, target_type, allow_unknown_union_variants=True
        )
    except ValidationError:
        return BaseModel.model_validate(payload)


def _interaction_id(value: Any) -> str:
    """Validate and return a non-empty interaction ID string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A non-empty interaction ID is required to connect.")
    return value


def _websocket_url(
    api_client: Any,
    api_version: Optional[str],
) -> str:
    """Build the WebSocket URL from the parent client's HTTP options."""
    if getattr(api_client, "vertexai", False):
        raise ValueError("Live Interactions is currently Gemini API only.")
    http_options = getattr(api_client, "_http_options")
    parts = urlsplit(str(http_options.base_url).rstrip("/"))
    scheme = "ws" if parts.scheme in {"http", "ws"} else "wss"
    version = api_version or http_options.api_version or ""
    path = "/".join(
        part.strip("/")
        for part in (parts.path, version, _LIVE_INTERACTIONS_PATH)
        if part.strip("/")
    )
    return urlunsplit((scheme, parts.netloc, f"/{path}", parts.query, ""))


def _websocket_transport_kwargs(api_client: Any) -> dict[str, Any]:
    """Return additional keyword arguments for the ``websockets`` transport layer."""
    transport_kwargs = getattr(api_client, "_websocket_ssl_ctx", None)
    if isinstance(transport_kwargs, Mapping):
        return dict(transport_kwargs)
    return {}


def _set_header(headers: dict[str, str], name: str, value: str) -> None:
    """Set ``name`` on ``headers``, replacing any case-insensitive match."""
    for candidate in [k for k in headers if k.lower() == name.lower()]:
        del headers[candidate]
    headers[name] = value


async def _websocket_headers(
    api_client: Any,
    extra_headers: Optional[Mapping[str, str]],
) -> dict[str, str]:
    """Build the WebSocket handshake headers, including auth and API revision."""
    headers = {"api-revision": GOOGLE_GENAI_API_REVISION}
    credentials = getattr(api_client, "_credentials", None)
    user_project = getattr(credentials, "quota_project_id", None)
    if user_project:
        headers["x-goog-user-project"] = user_project
    api_key = getattr(api_client, "api_key", None)
    if api_key:
        headers["x-goog-api-key"] = api_key
    for source in (getattr(api_client, "_http_options").headers, extra_headers):
        for name, value in (source or {}).items():
            _set_header(headers, name, value)
    if isinstance(api_key, str) and api_key.startswith("auth_tokens/"):
        for name in [k for k in headers if k.lower() == "authorization"]:
            del headers[name]
        _set_header(headers, "x-goog-api-key", api_key)
    return headers


class InteractionWebSocketConnection:
    """An active asynchronous live interaction WebSocket connection.

    Experimental: Live Interactions SDK support is experimental and may change
    in future versions.
    """

    def __init__(
        self,
        websocket: ClientConnection,
        interaction_id: Optional[str] = None,
    ) -> None:
        """Initialize the connection wrapper around an open WebSocket."""
        self._websocket = websocket
        self.id = interaction_id
        self._terminal = False
        self._detached = False
        self._receiving = False
        self._connection_error = False
        self._socket_closed = False
        self._recv_task: Optional[asyncio.Future[Any]] = None
        self._recv_cancelled_by_session = False
        self._pending_events: deque[dict[str, Any]] = deque()

    async def _close_socket_only(self) -> None:
        """Close the underlying WebSocket without marking the session detached or clearing buffered events."""
        if self._socket_closed:
            return
        self._socket_closed = True
        try:
            await self._websocket.close()
        except Exception:
            pass

    def _end_receive_wait(self) -> None:
        """Cancel an in-flight WebSocket recv task when the session terminates or detaches."""
        if self._recv_task is not None and not self._recv_task.done():
            self._recv_cancelled_by_session = True
            self._recv_task.cancel()
    async def _send_payload(self, payload: dict[str, Any]) -> None:
        """Send a JSON-serialized payload dict over the WebSocket."""
        try:
            await self._websocket.send(
                json.dumps(payload, separators=(",", ":"))
            )
        except ConnectionClosed as error:
            await self._close_socket_only()
            raise self._redacted_connection_error(error) from None

    async def _send_event(
        self,
        event: BaseModel,
    ) -> None:
        """Serialize and send a single typed client event."""
        await self._send_payload(_serialize_client_event(event))

    def _redacted_connection_error(
        self, error: ConnectionClosed
    ) -> APIWebSocketError:
        """Wrap a ``ConnectionClosed`` exception into an ``APIWebSocketError`` without leaking the close reason."""
        self._connection_error = True
        return _closed_websocket_error(_safe_close_code(error))

    def _ensure_active(self) -> None:
        """Raise ``RuntimeError`` if the interaction is terminal or detached."""
        if self._terminal:
            raise RuntimeError("This live interaction is already terminal.")
        if self._detached:
            raise RuntimeError("This live interaction is detached.")

    async def send(self, input: Any) -> None:
        """Send text, one ClientEvent, or a list of ClientEvents."""
        self._ensure_active()
        payload = _serialize_client_payload(input)
        if payload.get("events") == []:
            raise ValueError("Empty client event batch.")
        await self._send_payload(payload)
        if _payload_has_cancel(payload):
            self._terminal = True
            self._end_receive_wait()
            await self._close_socket_only()

    async def _fill_pending_events(self) -> bool:
        """Read WebSocket frames into ``_pending_events`` until at least one event is queued, returning ``False`` when the stream has ended."""
        while not self._pending_events:
            if self._terminal or self._detached:
                return False
            recv_task = asyncio.ensure_future(self._websocket.recv())
            self._recv_task = recv_task
            self._recv_cancelled_by_session = False
            try:
                raw = await recv_task
            except asyncio.CancelledError:
                current_task = asyncio.current_task()
                if (
                    self._recv_cancelled_by_session
                    and (self._terminal or self._detached)
                    and getattr(current_task, "cancelling", lambda: 0)() == 0
                ):
                    return False
                raise
            except ConnectionClosed as error:
                self._connection_error = True
                await self._close_socket_only()
                if self._terminal or self._detached:
                    return False
                raise self._redacted_connection_error(error) from None
            finally:
                self._recv_task = None
            if self._terminal or self._detached:
                return False
            self._pending_events.extend(_frame_events(raw))
        return True

    async def receive(self) -> AsyncIterator[Any]:
        """Yield generated server events until the interaction completes or detaches."""
        try:
            while not self._detached:
                if self._receiving:
                    raise RuntimeError("Only one receive iterator may be active at a time.")
                # Scope to _fill_pending_events(): Python async-for break/anext() does not synchronously close generators.
                self._receiving = True
                try:
                    has_events = await self._fill_pending_events()
                finally:
                    self._receiving = False
                if not has_events:
                    return
                event = self._pending_events.popleft()
                terminal = event["event_type"] in _TERMINAL_EVENTS
                if terminal:
                    self._terminal = True
                    self._pending_events.clear()
                    await self._close_socket_only()
                yield _parse_server_event(event)
                if terminal or self._detached:
                    return
        except APIWebSocketError as error:
            if error.close_code is None:
                self._pending_events.clear()
                await self._close_transport()
            raise

    async def complete(self) -> None:
        """Request completion while leaving the socket open for acknowledgement."""
        if self._terminal:
            return
        if self._detached:
            raise RuntimeError("This live interaction is detached.")
        await self._send_event(
            CompleteInteractionEvent(event_type="interaction.complete")
        )

    async def cancel(self) -> None:
        """Cancel inference on the server."""
        if self._terminal:
            return
        if self._detached:
            raise RuntimeError("This live interaction is detached.")
        await self._send_event(
            CancelInteractionEvent(event_type="interaction.cancel")
        )
        self._terminal = True
        self._end_receive_wait()
        await self._close_socket_only()

    async def _close_transport(self) -> None:
        """Mark the connection as detached, clear buffered events, and close the WebSocket."""
        self._detached = True
        self._pending_events.clear()
        self._end_receive_wait()
        await self._close_socket_only()

    async def detach(self) -> None:
        """Gracefully detach from the interaction without completing it."""
        if self._detached:
            return
        send_disconnect = not self._terminal and not self._connection_error
        self._detached = True
        self._pending_events.clear()
        self._end_receive_wait()
        if send_disconnect:
            try:
                await self._send_event(
                    DisconnectEvent(
                        event_type="interaction.disconnect"
                    )
                )
            except Exception:
                pass
        await self._close_socket_only()


class InteractionWebSocketConnectionContext(Awaitable[InteractionWebSocketConnection]):
    """Async context manager that connects to an existing live interaction.

    Experimental: Live Interactions SDK support is experimental and may change
    in future versions.

    Exiting ``async with`` detaches the local WebSocket without ending the
    server-side interaction. Call ``complete()`` (and drain ``receive()`` for
    ``interaction.completed``) or ``cancel()`` to finish or abort the
    interaction on the server.
    """

    def __init__(
        self,
        api_client: Any,
        id: str,
        *,
        api_version: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        timeout: float = 30.0,
    ) -> None:
        """Configure the context manager with connection parameters and validate inputs."""
        _warn_live_interactions_experimental(stacklevel=2)
        if getattr(api_client, "vertexai", False) is True:
            raise ValueError("Live Interactions is currently Gemini API only.")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout < float("inf"):
            raise ValueError("timeout must be positive and finite.")
        interaction_id = _interaction_id(id)
        self._timeout = timeout
        self._api_client = api_client
        self._initial_event = ReconnectInteractionEvent(
            event_type="interaction.connect", id=interaction_id
        )
        self._interaction_id = interaction_id
        self._api_version = api_version
        self._extra_headers = extra_headers
        if "additional_headers" in _websocket_transport_kwargs(api_client):
            raise ValueError(
                "WebSocket client arguments cannot supply 'additional_headers'; "
                "use extra_headers to add request headers."
            )
        self._connection: Any = None
        self._session: Optional[InteractionWebSocketConnection] = None

    async def _connect(self) -> ClientConnection:
        """Open the underlying ``websockets`` connection and return the ``ClientConnection``."""
        url = _websocket_url(self._api_client, self._api_version)
        kwargs = _websocket_transport_kwargs(self._api_client)
        if not url.startswith("wss://"):
            kwargs.pop("ssl", None)
        kwargs.setdefault("open_timeout", self._timeout)
        kwargs["additional_headers"] = await _websocket_headers(
            self._api_client,
            self._extra_headers,
        )
        self._connection = ws_connect(url, **kwargs)
        return await self._connection.__aenter__()

    async def _open(self) -> InteractionWebSocketConnection:
        """Establish the WebSocket connection, send the initial event, and return the session."""
        if self._session is not None:
            return self._session
        session = None
        failure = None

        async def establish():
            nonlocal session
            websocket = await self._connect()
            session = InteractionWebSocketConnection(
                websocket,
                self._interaction_id,
            )
            await session._send_event(self._initial_event)

        try:
            await asyncio.wait_for(establish(), timeout=self._timeout)
            self._session = session
            return session
        except (asyncio.CancelledError, ValueError):
            raise
        except APIWebSocketError as error:
            failure = (
                APIWebSocketError(
                    "The connection closed during live setup.",
                    close_code=error.close_code,
                )
                if error.close_code is not None
                else error
            )
        except ConnectionClosed as error:
            failure = APIWebSocketError(
                "The connection closed during live setup.",
                close_code=_safe_close_code(error),
            )
        except asyncio.TimeoutError:
            failure = APIWebSocketError(
                "Timed out establishing live interaction connection."
            )
        except Exception as error:
            response = getattr(error, "response", None)
            status = getattr(response, "status_code", None)
            failure = APIWebSocketError(
                "The live interaction setup failed.",
                http_status=status if isinstance(status, int) else None,
            )
        finally:
            if self._session is None:
                if session is not None:
                    await session._close_transport()
                if self._connection is not None:
                    try:
                        await self._connection.__aexit__(None, None, None)
                    except Exception:
                        pass
                    self._connection = None
        raise failure from None

    def __await__(self) -> Generator[Any, None, InteractionWebSocketConnection]:
        """Allow ``await context`` as a shorthand for ``await context._open()``."""
        return self._open().__await__()

    async def __aenter__(self) -> InteractionWebSocketConnection:
        """Enter the async context manager by opening the connection."""
        return await self._open()

    async def __aexit__(self, exc_type, exc, traceback) -> Optional[bool]:
        """Exit the async context manager by detaching from the interaction."""
        if self._session is not None:
            await self._session.detach()

        if self._connection is not None:
            return await self._connection.__aexit__(exc_type, exc, traceback)
        return False
