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

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["WebhookConfig"]


class WebhookConfig(BaseModel):
    """Message for configuring webhook events for a request."""

    uris: Optional[List[str]] = None
    """Optional.

    If set, these webhook URIs will be used for webhook events instead of the
    registered webhooks.
    """

    user_metadata: Optional[Dict[str, object]] = None
    """Optional.

    The user metadata that will be returned on each event emission to the webhooks.
    """
