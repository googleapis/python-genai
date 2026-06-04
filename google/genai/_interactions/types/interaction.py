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
from typing_extensions import Literal, TypeAlias, override

from . import environment
from .step import Step
from .tool import Tool
from .model import Model
from .usage import Usage
from .content import Content
from .._compat import PYDANTIC_V1
from .._models import BaseModel
from .text_content import TextContent
from .audio_content import AudioContent
from .image_content import ImageContent
from .video_content import VideoContent
from .._legacy_lyria import is_legacy_lyria_response_body
from .webhook_config import WebhookConfig
from .user_input_step import UserInputStep
from .document_content import DocumentContent
from .model_output_step import ModelOutputStep
from .dynamic_agent_config import DynamicAgentConfig
from .text_response_format import TextResponseFormat
from .audio_response_format import AudioResponseFormat
from .image_response_format import ImageResponseFormat
from .deep_research_agent_config import DeepResearchAgentConfig

__all__ = [
    "Interaction",
    "AgentConfig",
    "AgentConfigFindRequest",
    "AgentConfigFindRequestSessionConfig",
    "AgentConfigFindRequestSourceFile",
    "AgentConfigFixRequest",
    "AgentConfigFixRequestSessionConfig",
    "AgentConfigFixRequestSourceFile",
    "Environment",
    "Input",
    "ResponseFormat",
    "ResponseFormatResponseFormatList",
    "SafetySetting",
]


class AgentConfigFindRequestSessionConfig(BaseModel):
    """
    Optional session-specific configurations to override default agent
    behavior.
    """

    max_rounds: Optional[int] = None
    """
    The maximum number of interaction rounds the agent is allowed to perform before
    reaching a timeout.
    """

    pipeline_mode: Optional[Literal["scan", "verify"]] = None
    """The pipeline mode of a CodeMender session.

    It can only be used for a find session.
    """

    topology: Optional[str] = None
    """The cognitive architecture or "thinking" topology used by the agent (e.g.

    "default", "deep").
    """


class AgentConfigFindRequestSourceFile(BaseModel):
    """Content of a single file in the codebase."""

    content: Optional[str] = None
    """The UTF-8 encoded text content of the file."""

    path: Optional[str] = None
    """The relative path of the file from the project root."""


class AgentConfigFindRequest(BaseModel):
    """
    Request parameters specific to FIND sessions, used for discovering
    vulnerabilities in a codebase.
    """

    request: Literal["find_request"]

    description: Optional[str] = None
    """
    Additional context or custom instructions provided by the user to guide the
    vulnerability analysis.
    """

    finding_id: Optional[str] = None
    """The identifier of a specific finding to verify.

    This is primarily used in VERIFY mode to focus the agent's execution-based
    validation on a single vulnerability.
    """

    model: Optional[str] = None
    """The name of the model to use for the CodeMender agent.

    One CodeMender session will only use one model.
    """

    session_config: Optional[AgentConfigFindRequestSessionConfig] = None
    """Optional session-specific configurations to override default agent behavior."""

    session_id: Optional[str] = None
    """
    Parameter for grouping multiple interactions that belong to the same CodeMender
    session.
    """

    source_files: Optional[List[AgentConfigFindRequestSourceFile]] = None
    """A list of source files to provide as context for the scan."""


class AgentConfigFixRequestSessionConfig(BaseModel):
    """
    Optional session-specific configurations to override default agent
    behavior.
    """

    max_rounds: Optional[int] = None
    """
    The maximum number of interaction rounds the agent is allowed to perform before
    reaching a timeout.
    """

    pipeline_mode: Optional[Literal["scan", "verify"]] = None
    """The pipeline mode of a CodeMender session.

    It can only be used for a find session.
    """

    topology: Optional[str] = None
    """The cognitive architecture or "thinking" topology used by the agent (e.g.

    "default", "deep").
    """


class AgentConfigFixRequestSourceFile(BaseModel):
    """Content of a single file in the codebase."""

    content: Optional[str] = None
    """The UTF-8 encoded text content of the file."""

    path: Optional[str] = None
    """The relative path of the file from the project root."""


class AgentConfigFixRequest(BaseModel):
    """
    Request parameters specific to FIX sessions, used for generating and
    validating security patches.
    """

    request: Literal["fix_request"]

    description: Optional[str] = None
    """
    Additional context or custom instructions provided by the user to guide the
    patch generation process.
    """

    finding_id: Optional[str] = None
    """The identifier of the specific security finding to be remediated.

    This ID maps to a previously discovered vulnerability.
    """

    model: Optional[str] = None
    """The name of the model to use for the CodeMender agent.

    One CodeMender session will only use one model.
    """

    session_config: Optional[AgentConfigFixRequestSessionConfig] = None
    """Optional session-specific configurations to override default agent behavior."""

    session_id: Optional[str] = None
    """
    Parameter for grouping multiple interactions that belong to the same CodeMender
    session.
    """

    source_files: Optional[List[AgentConfigFixRequestSourceFile]] = None
    """A list of source files providing context for the remediation.

    These files are typically the ones containing the identified vulnerability.
    """


AgentConfig: TypeAlias = Union[
    DeepResearchAgentConfig, DynamicAgentConfig, AgentConfigFindRequest, AgentConfigFixRequest
]

Environment: TypeAlias = Union[str, environment.Environment]

Input: TypeAlias = Union[
    str, List[Step], List[Content], TextContent, ImageContent, AudioContent, DocumentContent, VideoContent
]

ResponseFormatResponseFormatList: TypeAlias = Union[
    AudioResponseFormat, TextResponseFormat, ImageResponseFormat, object
]

ResponseFormat: TypeAlias = Union[
    List[ResponseFormatResponseFormatList], AudioResponseFormat, TextResponseFormat, ImageResponseFormat, object
]


class SafetySetting(BaseModel):
    """A safety setting that affects the safety-blocking behavior.

    A SafetySetting consists of a
    harm category and a
    threshold for that
    category.
    """

    category: Literal[
        "hate_speech",
        "dangerous_content",
        "harassment",
        "sexually_explicit",
        "civic_integrity",
        "image_hate",
        "image_dangerous_content",
        "image_harassment",
        "image_sexually_explicit",
        "jailbreak",
    ]
    """Required. The harm category to be blocked."""

    threshold: Literal["block_low_and_above", "block_medium_and_above", "block_only_high", "block_none", "off"]
    """Required.

    The threshold for blocking content. If the harm probability exceeds this
    threshold, the content will be blocked.
    """

    method: Optional[Literal["severity", "probability"]] = None
    """Optional.

    The method for blocking content. If not specified, the default behavior is to
    use the probability score.
    """


class Interaction(BaseModel):
    """The Interaction resource."""

    id: str
    """Required. Output only. A unique identifier for the interaction completion."""

    created: datetime
    """Required.

    Output only. The time at which the response was created in ISO 8601 format
    (YYYY-MM-DDThh:mm:ssZ).
    """

    status: Literal[
        "in_progress", "requires_action", "completed", "failed", "cancelled", "incomplete", "budget_exceeded"
    ]
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
            "deep-research-pro-preview-12-2025",
            "deep-research-preview-04-2026",
            "deep-research-max-preview-04-2026",
            "antigravity-preview-05-2026",
        ],
        str,
        None,
    ] = None
    """The name of the `Agent` used for generating the interaction."""

    agent_config: Optional[AgentConfig] = None
    """Configuration parameters for the agent interaction."""

    cached_content: Optional[str] = None
    """
    The name of the cached content used as context to serve the prediction. Note:
    only used in explicit caching, where users can have control over caching (e.g.
    what content to cache) and enjoy guaranteed cost savings. Format:
    `projects/{project}/locations/{location}/cachedContents/{cachedContent}`
    """

    environment: Optional[Environment] = None
    """The environment configuration for the interaction.

    Can be an object specifying remote environment sources or a string referencing
    an existing environment ID.
    """

    environment_id: Optional[str] = None
    """Output only.

    The environment ID for the interaction. Only populated if environment config is
    set in the request.
    """

    input: Optional[Input] = None
    """The input for the interaction."""

    labels: Optional[Dict[str, str]] = None
    """Optional.

    The labels with user-defined metadata for the request. It is used for billing
    and reporting only.

    Label keys and values can be no longer than 63 characters (Unicode codepoints)
    and can only contain lowercase letters, numeric characters, underscores, and
    dashes. International characters are allowed. Label values are optional. Label
    keys must start with a letter.
    """

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

    safety_settings: Optional[List[SafetySetting]] = None
    """Safety settings for the interaction."""

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

    @property
    def output_text(self) -> str:
        """The last consecutive run of text from the trailing model output steps.

        Scans backwards through the steps (stopping at any UserInputStep) and
        skips non-text content until the first text item is found, then
        continues collecting text until a non-text item is encountered.
        Returns an empty string when no text content is present.
        """
        parts: List[str] = []
        collecting = False
        for step in reversed(self.steps or []):
            if isinstance(step, UserInputStep):
                break
            if not isinstance(step, ModelOutputStep) or not step.content:
                if collecting:
                    break
                continue
            for content in reversed(step.content):
                if isinstance(content, TextContent):
                    collecting = True
                    parts.append(content.text)
                elif collecting:
                    # Hit a non-text barrier after we started collecting.
                    parts.reverse()
                    return "".join(parts)
        parts.reverse()
        return "".join(parts)

    @property
    def output_image(self) -> Optional[ImageContent]:
        """The last image generated by the model in response to the current request."""
        for step in reversed(self.steps):
            if isinstance(step, UserInputStep):
                break
            if isinstance(step, ModelOutputStep) and step.content:
                for content in reversed(step.content):
                    if isinstance(content, ImageContent):
                        return content
        return None

    @property
    def output_audio(self) -> Optional[AudioContent]:
        """The last audio generated by the model in response to the current request."""
        for step in reversed(self.steps):
            if isinstance(step, UserInputStep):
                break
            if isinstance(step, ModelOutputStep) and step.content:
                for content in reversed(step.content):
                    if isinstance(content, AudioContent):
                        return content
        return None

    @property
    def output_video(self) -> Optional[VideoContent]:
        """The last video generated by the model in response to the current request."""
        for step in reversed(self.steps):
            if isinstance(step, UserInputStep):
                break
            if isinstance(step, ModelOutputStep) and step.content:
                for content in reversed(step.content):
                    if isinstance(content, VideoContent):
                        return content
        return None
