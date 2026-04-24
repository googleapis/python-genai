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

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, TypedDict

__all__ = ["WebhookUpdateParams"]


class WebhookUpdateParams(TypedDict, total=False):
    api_version: str

    update_mask: str
    """Optional. The list of fields to update."""

    name: str
    """Optional. The user-provided name of the webhook."""

    state: Literal["enabled", "disabled", "disabled_due_to_failed_deliveries"]
    """Optional. The state of the webhook."""

    subscribed_events: List[
        Union[
            Literal[
                "batch.succeeded",
                "batch.expired",
                "batch.failed",
                "interaction.requires_action",
                "interaction.completed",
                "interaction.failed",
                "video.generated",
            ],
            str,
        ]
    ]
    """Optional. The events that the webhook is subscribed to. Available events:

    - batch.succeeded
    - batch.expired
    - batch.failed
    - interaction.requires_action
    - interaction.completed
    - interaction.failed
    - video.generated
    """

    uri: str
    """Optional. The URI to which webhook events will be sent."""
