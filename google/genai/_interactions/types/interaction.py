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

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from .step import Step
from .tool import Tool
from .model import Model
from .usage import Usage
from .._utils import PropertyInfo
from .content import Content
from .._models import BaseModel
from .text_content import TextContent
from .audio_content import AudioContent
from .image_content import ImageContent
from .video_content import VideoContent
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

    steps: Optional[List[Step]] = None
    """Output only. The steps that make up the interaction."""

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
