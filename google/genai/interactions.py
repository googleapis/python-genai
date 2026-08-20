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

# Trigger create-params define nested `Interaction` / `InteractionParam`
# TypeAliasTypes that share names with the interactions resource class.
# Star-importing those aliases into this module makes mypy keep the first
# binding (the TypeAliasType), while runtime last-binding-wins to the resource
# class — see https://github.com/googleapis/python-genai/issues/2732.
# Exclude the colliding names here; they remain available from
# `google.genai._gaos.types.triggers`.
from ._gaos.types.triggers import __all__ as _triggers_all_raw

_TRIGGERS_NAMES_EXCLUDED_FROM_INTERACTIONS = frozenset({
    'Interaction',
    'InteractionParam',
})

_triggers_all = [
    name
    for name in _triggers_all_raw
    if name not in _TRIGGERS_NAMES_EXCLUDED_FROM_INTERACTIONS
]

# Explicit imports so type checkers never bind the colliding TypeAliasTypes.
# Keep this list aligned with triggers.__all__ minus the excluded names; the
# assertion below fails if Speakeasy adds a new trigger export.
from ._gaos.types.triggers import (  # noqa: F401
    ListTriggerExecutionsResponse,
    ListTriggerExecutionsResponseTypedDict,
    ListTriggersResponse,
    ListTriggersResponseTypedDict,
    Trigger,
    TriggerCreateParams,
    TriggerCreateParamsParam,
    TriggerExecution,
    TriggerExecutionStatus,
    TriggerExecutionTypedDict,
    TriggerStatus,
    TriggerTypedDict,
    TriggerUpdate,
    TriggerUpdateParam,
    TriggerUpdateStatus,
)

_missing_trigger_exports = [
    name for name in _triggers_all if name not in globals()
]
if _missing_trigger_exports:
    raise ImportError(
        'google.genai.interactions is missing trigger exports after excluding '
        f'colliding Interaction aliases: {_missing_trigger_exports}. Update the '
        'explicit triggers import list in google/genai/interactions.py.'
    )

from ._gaos.types.environments import *  # noqa: F401,F403
from ._gaos.types.environments import __all__ as _environments_all
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
# Append interactions exports last so `Interaction` is the resource class for
# wildcard imports. Trigger Interaction aliases are intentionally omitted above.
__all__ = (
    __all__
    + list(_triggers_all)
    + list(_resources_all)
    + list(_environments_all)
    + list(_interactions_all)
)
