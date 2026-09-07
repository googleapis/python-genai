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
"""Expose Google GenAI credential types."""

from __future__ import annotations

from ._gaos.models.listcredentials import ListCredentialsRequestParam as CredentialListParams
from ._gaos.types.credentials import *  # noqa: F401,F403
from ._gaos.types.credentials import __all__ as _credentials_all
from ._gaos.types.credentials.credential import Credential, CredentialCreateParams
from ._gaos.types.credentials.credentiallistresponse import CredentialListResponse
from ._gaos.types.credentials.credentialupdate import CredentialUpdateParam as CredentialUpdateParams
from ._gaos.types.interactions.empty import Empty as CredentialDeleteResponse

__all__ = [
    "Credential",
    "CredentialCreateParams",
    "CredentialDeleteResponse",
    "CredentialListParams",
    "CredentialListResponse",
    "CredentialUpdateParams",
]
__all__ = __all__ + list(_credentials_all)
