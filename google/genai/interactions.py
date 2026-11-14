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
from typing import Optional, Union
import warnings

from typing_extensions import Literal, Required, TypedDict

# Only the interactions namespace is exported directly from this module. Other
# namespaces (agents, environments, triggers, webhooks, ...) are exported from
# their own modules (e.g. `google.genai.agents`).
from ._gaos.types.interactions import *  # noqa: F401,F403
from ._gaos.types.interactions import __all__ as _interactions_all
from ._gaos.resources.interactions import *  # noqa: F401,F403
from ._gaos.resources.interactions import __all__ as _resources_all
from ._gaos.types.interactions import (
    CreateAgentInteractionParam,
    CreateModelInteractionParam,
)
from ._gaos.types.interactions.model import Model as ModelParam

# Deprecated names: names that this module exported before only the
# interactions namespace was exported here. The imports below are the single
# source of truth for them. Type checkers see the imports. At runtime, the
# names are removed from the module globals, so `__getattr__` below resolves
# them and emits a `DeprecationWarning`. Do not add names to this list. The
# names will be removed in a future release.
_globals_before_deprecated = set(globals())
# pylint: disable=g-import-not-at-top,g-bad-import-order,unused-import,g-multiple-import,g-importing-member
# pyformat: disable
# Agent aliases.
from ._gaos.models.listagents import ListAgentsRequestParam as AgentListParams
from ._gaos.types.agents.agent import Agent, AgentParam as AgentCreateParams
from ._gaos.types.agents.agentlistresponse import AgentListResponse
from ._gaos.types.interactions.empty import Empty as AgentDeleteResponse

# Environments namespace.
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

# Triggers namespace.
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

# Webhook aliases.
from ._gaos.models.listwebhooks import ListWebhooksRequestParam as WebhookListParams
from ._gaos.types.interactions.empty import Empty as WebhookDeleteResponse
from ._gaos.types.webhooks.pingwebhookrequest import PingWebhookRequestParam as WebhookPingParams
from ._gaos.types.webhooks.rotatesigningsecretrequest import RotateSigningSecretRequestParam as WebhookRotateSigningSecretParams
from ._gaos.types.webhooks.signingsecret import SigningSecret
from ._gaos.types.webhooks.webhook import Webhook, WebhookInputParam as WebhookCreateParams
from ._gaos.types.webhooks.webhooklistresponse import WebhookListResponse
from ._gaos.types.webhooks.webhookpingresponse import WebhookPingResponse
from ._gaos.types.webhooks.webhookupdate import WebhookUpdateParam as WebhookUpdateParams
# pyformat: enable
# pylint: enable=g-import-not-at-top,g-bad-import-order,unused-import,g-multiple-import,g-importing-member
_DEPRECATED_OBJECTS: dict[str, object] = {
    name: globals().pop(name)
    for name in set(globals())
    - _globals_before_deprecated
    - {"_globals_before_deprecated"}
}
del _globals_before_deprecated
_DEPRECATED_NAMES = frozenset(_DEPRECATED_OBJECTS)

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


# Public modules that export the deprecated names now.
_REPLACEMENT_MODULES = ("agents", "environments", "triggers", "webhooks")


def _replacement_module(name: str, value: object) -> Optional[str]:
    """Returns the public module that exports the same object, if one does."""
    for module_name in _REPLACEMENT_MODULES:
        module = importlib.import_module(f".{module_name}", __package__)
        if getattr(module, name, None) is value:
            return f"google.genai.{module_name}"
    return None


def __getattr__(name: str) -> object:
    """Resolves deprecated names and emits a `DeprecationWarning`."""
    if name not in _DEPRECATED_NAMES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = _DEPRECATED_OBJECTS[name]
    message = (
        f"`{__name__}.{name}` is deprecated and will be removed in a future"
        " release."
    )
    replacement = _replacement_module(name, value)
    if replacement is not None:
        message += f" Import it from `{replacement}` instead."
    warnings.warn(message, DeprecationWarning, stacklevel=2)
    return value


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
