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
"""Expose Google GenAI interaction types."""

from __future__ import annotations

from typing import Union

from typing_extensions import Literal, Required, TypedDict

from ._gaos.types.interactions import *  # noqa: F401,F403
from ._gaos.types.interactions import __all__ as _interactions_all
from ._gaos.models.listagents import ListAgentsRequestParam as AgentListParams
from ._gaos.models.listwebhooks import ListWebhooksRequestParam as WebhookListParams
from ._gaos.resources.interactions import *  # noqa: F401,F403
from ._gaos.resources.interactions import __all__ as _resources_all
from ._gaos.types.agents.agent import Agent, AgentParam as AgentCreateParams
from ._gaos.types.agents.agentlistresponse import AgentListResponse
from ._gaos.types.interactions.empty import Empty as AgentDeleteResponse
from ._gaos.types.interactions import (
    CreateAgentInteractionParam,
    CreateModelInteractionParam,
)
from ._gaos.types.interactions.model import Model as ModelParam
from ._gaos.types.webhooks.pingwebhookrequest import (
    PingWebhookRequestParam as WebhookPingParams,
)
from ._gaos.types.webhooks.rotatesigningsecretrequest import (
    RotateSigningSecretRequestParam as WebhookRotateSigningSecretParams,
)
from ._gaos.types.webhooks.signingsecret import SigningSecret
from ._gaos.types.webhooks.webhook import Webhook, WebhookInputParam as WebhookCreateParams
from ._gaos.types.webhooks.webhooklistresponse import WebhookListResponse
from ._gaos.types.webhooks.webhookpingresponse import WebhookPingResponse
from ._gaos.types.webhooks.webhookupdate import WebhookUpdateParam as WebhookUpdateParams

WebhookDeleteResponse = AgentDeleteResponse

# Legacy flat operation parameter typed dicts that generation cannot express
# yet: the get-params dicts exclude the positional `id` path parameter, and
# the create-params split into the four legacy streaming variants. These are
# static-typing artifacts only.


class CreateModelInteractionParamsNonStreaming(
    CreateModelInteractionParam, total=False
):
    stream: Literal[False]


class CreateModelInteractionParamsStreaming(CreateModelInteractionParam):
    stream: Required[Literal[True]]


class CreateAgentInteractionParamsNonStreaming(
    CreateAgentInteractionParam, total=False
):
    stream: Literal[False]


class CreateAgentInteractionParamsStreaming(CreateAgentInteractionParam):
    stream: Required[Literal[True]]


InteractionCreateParams = Union[
    CreateModelInteractionParamsNonStreaming,
    CreateModelInteractionParamsStreaming,
    CreateAgentInteractionParamsNonStreaming,
    CreateAgentInteractionParamsStreaming,
]


class InteractionGetParamsBase(TypedDict, total=False):
    api_version: str
    include_input: bool
    last_event_id: str


class InteractionGetParamsNonStreaming(InteractionGetParamsBase, total=False):
    stream: Literal[False]


class InteractionGetParamsStreaming(InteractionGetParamsBase):
    stream: Required[Literal[True]]


InteractionGetParams = Union[
    InteractionGetParamsNonStreaming,
    InteractionGetParamsStreaming,
]


__all__ = [
    "Agent",
    "AgentCreateParams",
    "AgentDeleteResponse",
    "AgentListParams",
    "AgentListResponse",
    "CreateAgentInteractionParamsNonStreaming",
    "CreateAgentInteractionParamsStreaming",
    "CreateModelInteractionParamsNonStreaming",
    "CreateModelInteractionParamsStreaming",
    "InteractionCreateParams",
    "InteractionGetParams",
    "InteractionGetParamsBase",
    "InteractionGetParamsNonStreaming",
    "InteractionGetParamsStreaming",
    "ModelParam",
    "SigningSecret",
    "Webhook",
    "WebhookCreateParams",
    "WebhookDeleteResponse",
    "WebhookListParams",
    "WebhookListResponse",
    "WebhookPingParams",
    "WebhookPingResponse",
    "WebhookRotateSigningSecretParams",
    "WebhookUpdateParams",
]
__all__ = __all__ + list(_interactions_all) + list(_resources_all)
