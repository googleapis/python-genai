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

import importlib
from typing import Optional, TYPE_CHECKING, Union
import warnings

from typing_extensions import Literal, Required, TypedDict

# Only the interactions namespace is exported directly from this module. Other
# namespaces (agents, environments, triggers, webhooks, ...) are exported from
# their own modules (e.g. `google.genai.agents`).
# The resources wildcard import must come after the types wildcard import, so
# that resource classes (e.g. `Interaction`) win over same-named types.
# pyformat: disable
from ._gaos.types.interactions import *  # noqa: F401,F403
from ._gaos.types.interactions import __all__ as _interactions_all
from ._gaos.resources.interactions import *  # noqa: F401,F403
from ._gaos.resources.interactions import __all__ as _resources_all
# pyformat: enable
from ._gaos.types.interactions import (
    CreateAgentInteractionParam,
    CreateModelInteractionParam,
)
from ._gaos.types.interactions.model import Model as ModelParam

if TYPE_CHECKING:
    # Deprecated names. At runtime, `__getattr__` below resolves them and emits a
    # `DeprecationWarning`. These imports keep them visible to type checkers.
    # pylint: disable=g-import-not-at-top,g-bad-import-order,unused-import
    # pyformat: disable
    from ._gaos.models.listagents import ListAgentsRequestParam as AgentListParams
    from ._gaos.models.listwebhooks import ListWebhooksRequestParam as WebhookListParams
    from ._gaos.types.agents.agent import Agent, AgentParam as AgentCreateParams
    from ._gaos.types.agents.agentlistresponse import AgentListResponse
    from ._gaos.types.environments import (
        CreateEnvironmentRequest,
        CreateEnvironmentRequestNetworkEnum,
        CreateEnvironmentRequestNetworkUnion,
        CreateEnvironmentRequestNetworkUnionParam,
        CreateEnvironmentRequestParam,
        EnvironmentFile,
        EnvironmentFileTypedDict,
        EnvironmentNetworkEnum,
        EnvironmentNetworkUnion,
        EnvironmentNetworkUnionTypedDict,
        EnvironmentTypedDict,
        GetEnvironmentFilesResponse,
        GetEnvironmentFilesResponseTypedDict,
        ListEnvironmentsResponse,
        ListEnvironmentsResponseTypedDict,
        Type,
    )
    from ._gaos.types.interactions.empty import Empty as AgentDeleteResponse
    from ._gaos.types.interactions.empty import Empty as WebhookDeleteResponse
    from ._gaos.types.triggers import (
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
    from ._gaos.types.webhooks.pingwebhookrequest import PingWebhookRequestParam as WebhookPingParams
    from ._gaos.types.webhooks.rotatesigningsecretrequest import RotateSigningSecretRequestParam as WebhookRotateSigningSecretParams
    from ._gaos.types.webhooks.signingsecret import SigningSecret
    from ._gaos.types.webhooks.webhook import Webhook, WebhookInputParam as WebhookCreateParams
    from ._gaos.types.webhooks.webhooklistresponse import WebhookListResponse
    from ._gaos.types.webhooks.webhookpingresponse import WebhookPingResponse
    from ._gaos.types.webhooks.webhookupdate import WebhookUpdateParam as WebhookUpdateParams
    # pyformat: enable
    # pylint: enable=g-import-not-at-top,g-bad-import-order,unused-import

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


# Names that this module exported before only the interactions namespace was
# exported here. This list is frozen: do not add names to it. Access to these
# names emits a `DeprecationWarning`. They will be removed in a future release.
# Each value is (source module, source attribute, replacement public module).
_DEPRECATED_NAMES: dict[str, tuple[str, str, Optional[str]]] = {
    # Agent aliases.
    "Agent": ("._gaos.types.agents.agent", "Agent", "google.genai.agents"),
    "AgentCreateParams": (
        "._gaos.types.agents.agent",
        "AgentParam",
        "google.genai.agents",
    ),
    "AgentDeleteResponse": (
        "._gaos.types.interactions.empty",
        "Empty",
        "google.genai.agents",
    ),
    "AgentListParams": (
        "._gaos.models.listagents",
        "ListAgentsRequestParam",
        "google.genai.agents",
    ),
    "AgentListResponse": (
        "._gaos.types.agents.agentlistresponse",
        "AgentListResponse",
        "google.genai.agents",
    ),
    # Environments namespace.
    "CreateEnvironmentRequest": (
        "._gaos.types.environments",
        "CreateEnvironmentRequest",
        "google.genai.environments",
    ),
    "CreateEnvironmentRequestNetworkEnum": (
        "._gaos.types.environments",
        "CreateEnvironmentRequestNetworkEnum",
        "google.genai.environments",
    ),
    "CreateEnvironmentRequestNetworkUnion": (
        "._gaos.types.environments",
        "CreateEnvironmentRequestNetworkUnion",
        "google.genai.environments",
    ),
    "CreateEnvironmentRequestNetworkUnionParam": (
        "._gaos.types.environments",
        "CreateEnvironmentRequestNetworkUnionParam",
        "google.genai.environments",
    ),
    "CreateEnvironmentRequestParam": (
        "._gaos.types.environments",
        "CreateEnvironmentRequestParam",
        "google.genai.environments",
    ),
    "EnvironmentFile": (
        "._gaos.types.environments",
        "EnvironmentFile",
        "google.genai.environments",
    ),
    "EnvironmentFileTypedDict": (
        "._gaos.types.environments",
        "EnvironmentFileTypedDict",
        None,
    ),
    "EnvironmentNetworkEnum": (
        "._gaos.types.environments",
        "EnvironmentNetworkEnum",
        "google.genai.environments",
    ),
    "EnvironmentNetworkUnion": (
        "._gaos.types.environments",
        "EnvironmentNetworkUnion",
        "google.genai.environments",
    ),
    "EnvironmentNetworkUnionTypedDict": (
        "._gaos.types.environments",
        "EnvironmentNetworkUnionTypedDict",
        "google.genai.environments",
    ),
    "EnvironmentTypedDict": (
        "._gaos.types.environments",
        "EnvironmentTypedDict",
        None,
    ),
    "GetEnvironmentFilesResponse": (
        "._gaos.types.environments",
        "GetEnvironmentFilesResponse",
        "google.genai.environments",
    ),
    "GetEnvironmentFilesResponseTypedDict": (
        "._gaos.types.environments",
        "GetEnvironmentFilesResponseTypedDict",
        None,
    ),
    "ListEnvironmentsResponse": (
        "._gaos.types.environments",
        "ListEnvironmentsResponse",
        "google.genai.environments",
    ),
    "ListEnvironmentsResponseTypedDict": (
        "._gaos.types.environments",
        "ListEnvironmentsResponseTypedDict",
        None,
    ),
    "Type": ("._gaos.types.environments", "Type", "google.genai.environments"),
    # Triggers namespace.
    "ListTriggerExecutionsResponse": (
        "._gaos.types.triggers",
        "ListTriggerExecutionsResponse",
        "google.genai.triggers",
    ),
    "ListTriggerExecutionsResponseTypedDict": (
        "._gaos.types.triggers",
        "ListTriggerExecutionsResponseTypedDict",
        None,
    ),
    "ListTriggersResponse": (
        "._gaos.types.triggers",
        "ListTriggersResponse",
        "google.genai.triggers",
    ),
    "ListTriggersResponseTypedDict": (
        "._gaos.types.triggers",
        "ListTriggersResponseTypedDict",
        None,
    ),
    "Trigger": ("._gaos.types.triggers", "Trigger", "google.genai.triggers"),
    "TriggerCreateParams": (
        "._gaos.types.triggers",
        "TriggerCreateParams",
        "google.genai.triggers",
    ),
    "TriggerCreateParamsParam": (
        "._gaos.types.triggers",
        "TriggerCreateParamsParam",
        "google.genai.triggers",
    ),
    "TriggerExecution": (
        "._gaos.types.triggers",
        "TriggerExecution",
        "google.genai.triggers",
    ),
    "TriggerExecutionStatus": (
        "._gaos.types.triggers",
        "TriggerExecutionStatus",
        "google.genai.triggers",
    ),
    "TriggerExecutionTypedDict": (
        "._gaos.types.triggers",
        "TriggerExecutionTypedDict",
        None,
    ),
    "TriggerStatus": (
        "._gaos.types.triggers",
        "TriggerStatus",
        "google.genai.triggers",
    ),
    "TriggerTypedDict": ("._gaos.types.triggers", "TriggerTypedDict", None),
    "TriggerUpdate": (
        "._gaos.types.triggers",
        "TriggerUpdate",
        "google.genai.triggers",
    ),
    "TriggerUpdateParam": (
        "._gaos.types.triggers",
        "TriggerUpdateParam",
        "google.genai.triggers",
    ),
    "TriggerUpdateStatus": (
        "._gaos.types.triggers",
        "TriggerUpdateStatus",
        "google.genai.triggers",
    ),
    # Webhook aliases.
    "SigningSecret": (
        "._gaos.types.webhooks.signingsecret",
        "SigningSecret",
        "google.genai.webhooks",
    ),
    "Webhook": (
        "._gaos.types.webhooks.webhook",
        "Webhook",
        "google.genai.webhooks",
    ),
    "WebhookCreateParams": (
        "._gaos.types.webhooks.webhook",
        "WebhookInputParam",
        "google.genai.webhooks",
    ),
    "WebhookDeleteResponse": (
        "._gaos.types.interactions.empty",
        "Empty",
        "google.genai.webhooks",
    ),
    "WebhookListParams": (
        "._gaos.models.listwebhooks",
        "ListWebhooksRequestParam",
        "google.genai.webhooks",
    ),
    "WebhookListResponse": (
        "._gaos.types.webhooks.webhooklistresponse",
        "WebhookListResponse",
        "google.genai.webhooks",
    ),
    "WebhookPingParams": (
        "._gaos.types.webhooks.pingwebhookrequest",
        "PingWebhookRequestParam",
        "google.genai.webhooks",
    ),
    "WebhookPingResponse": (
        "._gaos.types.webhooks.webhookpingresponse",
        "WebhookPingResponse",
        "google.genai.webhooks",
    ),
    "WebhookRotateSigningSecretParams": (
        "._gaos.types.webhooks.rotatesigningsecretrequest",
        "RotateSigningSecretRequestParam",
        "google.genai.webhooks",
    ),
    "WebhookUpdateParams": (
        "._gaos.types.webhooks.webhookupdate",
        "WebhookUpdateParam",
        "google.genai.webhooks",
    ),
}


def __getattr__(name: str) -> object:
    """Resolves deprecated names and emits a `DeprecationWarning`."""
    try:
        module_name, attr_name, replacement = _DEPRECATED_NAMES[name]
    except KeyError:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        ) from None
    message = (
        f"`{__name__}.{name}` is deprecated and will be removed in a future"
        " release."
    )
    if replacement is not None:
        message += f" Import it from `{replacement}` instead."
    warnings.warn(message, DeprecationWarning, stacklevel=2)
    return getattr(importlib.import_module(module_name, __package__), attr_name)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_DEPRECATED_NAMES))


__all__ = [
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
]
# Deprecated names stay in `__all__` so that wildcard imports keep working.
__all__ = sorted(
    set(__all__)
    | set(_resources_all)
    | set(_interactions_all)
    | set(_DEPRECATED_NAMES)
)
