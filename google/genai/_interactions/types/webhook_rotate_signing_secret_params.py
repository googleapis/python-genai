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

from typing_extensions import Literal, TypedDict

__all__ = ["WebhookRotateSigningSecretParams"]


class WebhookRotateSigningSecretParams(TypedDict, total=False):
    api_version: str

    revocation_behavior: Literal["revoke_previous_secrets_after_h24", "revoke_previous_secrets_immediately"]
    """Optional. The revocation behavior for previous signing secrets."""
