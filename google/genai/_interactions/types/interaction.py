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

from typing import TYPE_CHECKING, Any, Set, Dict, List, Tuple, Union, Optional, cast
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias, override

from .step import Step
from .tool import Tool
from .model import Model
from .usage import Usage
from .._utils import PropertyInfo
from .content import Content
from .._compat import PYDANTIC_V1
from .._models import BaseModel
from .text_content import TextContent
from .audio_content import AudioContent
from .image_content import ImageContent
from .video_content import VideoContent
from .._legacy_lyria import is_legacy_lyria_response_body
from .webhook_config import WebhookConfig
from .document_content import DocumentContent
from .dynamic_agent_config import DynamicAgentConfig
from .text_response_format import TextResponseFormat
from .audio_response_format import AudioResponseFormat
from .image_response_format import ImageResponseFormat
from .video_response_format import VideoResponseFormat
from .deep_research_agent_config import DeepResearchAgentConfig

__all__ = ["Interaction", "AgentConfig", "Input", "ResponseFormat", "ResponseFormatResponseFormatList"]

AgentConfig: TypeAlias = Annotated[
    Union[DynamicAgentConfig, DeepResearchAgentConfig], PropertyInfo(discriminator="type")
]

Input: TypeAlias = Union[
    str, List[Step], List[Content], TextContent, ImageContent, AudioContent, DocumentContent, VideoContent
]

ResponseFormatResponseFormatList: TypeAlias = Union[
    AudioResponseFormat, TextResponseFormat, ImageResponseFormat, VideoResponseFormat, object
]

ResponseFormat: TypeAlias = Union[
    List[ResponseFormatResponseFormatList],
    AudioResponseFormat,
    TextResponseFormat,
    ImageResponseFormat,
    VideoResponseFormat,
    object,
]


class Interaction(BaseModel):
    """The Interaction resource."""

    id: str
    """Required. Output only. A unique identifier for the interaction completion."""

    created: datetime
    """Required.

    Output only. The time at which the response was created in ISO 8601 format
    (YYYY-MM-DDThh:mm:ssZ).
    """

    status: Literal["in_progress", "requires_action", "completed", "failed", "cancelled", "incomplete"]
    """Required. Output only. The status of the interaction."""

    steps: List[Step]
    """Required. Output only. The steps that make up the interaction."""

    updated: datetime
    """Required.

    Output only. The time at which the response was last updated in ISO 8601 format
    (YYYY-MM-DDThh:mm:ssZ).
    """

    agent: Union[
        Literal[
            "deep-research-pro-preview-12-2025", "deep-research-preview-04-2026", "deep-research-max-preview-04-2026"
        ],
        str,
        None,
    ] = None
    """The name of the `Agent` used for generating the interaction."""

    agent_config: Optional[AgentConfig] = None
    """Configuration parameters for the agent interaction."""

    input: Optional[Input] = None
    """The input for the interaction."""

    model: Optional[Model] = None
    """The name of the `Model` used for generating the interaction."""

    previous_interaction_id: Optional[str] = None
    """The ID of the previous interaction, if any."""

    response_format: Optional[ResponseFormat] = None
    """
    Enforces that the generated response is a JSON object that complies with the
    JSON schema specified in this field.
    """

    response_mime_type: Optional[str] = None
    """The mime type of the response. This is required if response_format is set."""

    response_modalities: Optional[List[Literal["text", "image", "audio", "video", "document"]]] = None
    """The requested modalities of the response (TEXT, IMAGE, AUDIO)."""

    role: Optional[str] = None
    """Output only. The role of the interaction."""

    service_tier: Optional[Literal["flex", "standard", "priority"]] = None
    """The service tier for the interaction."""

    system_instruction: Optional[str] = None
    """System instruction for the interaction."""

    tools: Optional[List[Tool]] = None
    """A list of tool declarations the model may call during interaction."""

    usage: Optional[Usage] = None
    """Output only. Statistics on the interaction request's token usage."""

    webhook_config: Optional[WebhookConfig] = None
    """Optional.

    Webhook configuration for receiving notifications when the interaction
    completes.
    """

    @classmethod
    def _maybe_coerce_outputs(cls, data: Any) -> Tuple[Any, bool]:
        """Rewrite legacy vertex `outputs` payloads into the modern `steps` shape.

        Returns `(data, did_rewrite)` so callers (notably the `construct`
        override below) can react to whether the rewrite actually fired
        without relying on object identity.

        Triggers only when the response body identifies itself as a legacy-
        lyria payload via its top-level `model` field. The model field is
        present on every Interaction body produced by `create()`, `get()`,
        and any deferred parse via `with_raw_response.parse()`, including
        the nested `interaction` bodies inside `interaction.created` /
        `interaction.completed` SSE events.

        Skips the rewrite if `outputs` isn't a list (e.g. server emits an
        explicit `null`) so the divergence surfaces in `__pydantic_extra__`
        instead of being silently coerced into an empty step.

        On rewrite, the original `outputs` field is popped so it doesn't
        land on the parsed model as a redundant extra.
        """
        if not isinstance(data, dict):
            return data, False
        typed_data: Dict[str, Any] = cast("Dict[str, Any]", data)
        if not is_legacy_lyria_response_body(typed_data):
            return typed_data, False
        if "outputs" not in typed_data or "steps" in typed_data:
            return typed_data, False
        outputs = typed_data["outputs"]
        if not isinstance(outputs, list):
            return typed_data, False

        new_data: Dict[str, Any] = {**typed_data}
        new_data.pop("outputs")
        new_data["steps"] = [{"type": "model_output", "content": outputs}]
        return new_data, True

    @classmethod
    @override
    def construct(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls,
        _fields_set: Optional[Set[str]] = None,
        **values: Any,
    ) -> "Interaction":
        coerced, rewrote = cls._maybe_coerce_outputs(values)
        # If we rewrote `outputs` -> `steps` and the caller passed an explicit
        # _fields_set including `outputs`, swap the field name so
        # `model_dump(exclude_unset=True)` and friends report `steps` as set
        # rather than the field that no longer exists on the model.
        if rewrote and _fields_set is not None and "outputs" in _fields_set:
            _fields_set = (set(_fields_set) - {"outputs"}) | {"steps"}
        return super().construct(_fields_set=_fields_set, **coerced)  # type: ignore[return-value]

    if not TYPE_CHECKING:
        model_construct = construct

        if PYDANTIC_V1:
            from pydantic import root_validator

            @root_validator(pre=True)
            def _coerce_outputs_to_steps(cls, values: Any) -> Any:
                coerced, _ = cls._maybe_coerce_outputs(values)
                return coerced
        else:
            from pydantic import model_validator

            @model_validator(mode="before")
            @classmethod
            def _coerce_outputs_to_steps(cls, data: Any) -> Any:
                coerced, _ = cls._maybe_coerce_outputs(data)
                return coerced
