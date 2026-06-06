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

from typing_extensions import TypedDict

__all__ = ["WebhookListParams"]


class WebhookListParams(TypedDict, total=False):
    api_version: str

    page_size: int
    """Optional.

    The maximum number of webhooks to return. The service may return fewer than this
    value. If unspecified, at most 50 webhooks will be returned. The maximum value
    is 1000.
    """

    page_token: str
    """Optional.

    A page token, received from a previous `ListWebhooks` call. Provide this to
    retrieve the subsequent page.
    """
