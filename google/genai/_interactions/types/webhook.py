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
from typing_extensions import Literal

from .._models import BaseModel
from .signing_secret import SigningSecret

__all__ = ["Webhook"]


class Webhook(BaseModel):
    """A Webhook resource."""

    subscribed_events: List[
        Union[
            Literal[
                "batch.succeeded",
                "batch.cancelled",
                "batch.expired",
                "batch.failed",
                "interaction.requires_action",
                "interaction.completed",
                "interaction.failed",
                "interaction.cancelled",
                "video.generated",
            ],
            str,
        ]
    ]
    """Required. The events that the webhook is subscribed to. Available events:

    - batch.succeeded
    - batch.cancelled
    - batch.expired
    - batch.failed
    - interaction.requires_action
    - interaction.completed
    - interaction.failed
    - interaction.cancelled
    - video.generated
    """

    uri: str
    """Required. The URI to which webhook events will be sent."""

    create_time: Optional[datetime] = None
    """Output only. The timestamp when the webhook was created."""

    name: Optional[str] = None
    """Identifier. The name of the webhook. Format: `webhooks/{webhook_id}`"""

    new_signing_secret: Optional[str] = None
    """Output only. The new signing secret for the webhook. Only populated on create."""

    signing_secrets: Optional[List[SigningSecret]] = None
    """Output only. The signing secrets associated with this webhook."""

    state: Optional[Literal["enabled", "disabled", "disabled_due_to_failed_deliveries"]] = None
    """The state of the webhook."""

    update_time: Optional[datetime] = None
    """Output only. The timestamp when the webhook was last updated."""
