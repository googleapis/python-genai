# Copyright 2026 Google LLC
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

from ._gaos.models.listcredentials import (
    ListCredentialsRequestParam as CredentialListParams,
)
from ._gaos.types.credentials.credential import Credential
from ._gaos.types.credentials.credentialcreateparams import CredentialCreateParams
from ._gaos.types.credentials.credentiallistresponse import (
    CredentialListResponse,
)
from ._gaos.types.credentials.credentialupdate import (
    CredentialUpdateParam as CredentialUpdateParams,
)
from ._gaos.types.credentials.environmentvariableconfig import (
    EnvironmentVariableConfig,
    EnvironmentVariableConfigInjectionLocation,
    EnvironmentVariableConfigInjectionLocationParam,
    EnvironmentVariableConfigParam,
)
from ._gaos.types.credentials.environmentvariableupdateconfig import (
    EnvironmentVariableUpdateConfig,
    EnvironmentVariableUpdateConfigInjectionLocation,
    EnvironmentVariableUpdateConfigInjectionLocationParam,
    EnvironmentVariableUpdateConfigParam,
)
from ._gaos.types.credentials.httpbearerconfig import (
    HTTPBearerConfig,
    HTTPBearerConfigParam,
)
from ._gaos.types.credentials.httpbearerupdateconfig import (
    HTTPBearerUpdateConfig,
    HTTPBearerUpdateConfigParam,
)
from ._gaos.types.credentials.injectionlocation_enum import (
    InjectionLocationEnum,
)
from ._gaos.types.credentials.oauth2config import (
    OAuth2Config,
    OAuth2ConfigParam,
)
from ._gaos.types.credentials.oauth2updateconfig import (
    OAuth2UpdateConfig,
    OAuth2UpdateConfigParam,
)
from ._gaos.types.interactions.empty import Empty as CredentialDeleteResponse

__all__ = [
    "Credential",
    "CredentialCreateParams",
    "CredentialDeleteResponse",
    "CredentialListParams",
    "CredentialListResponse",
    "CredentialUpdateParams",
    "EnvironmentVariableConfig",
    "EnvironmentVariableConfigInjectionLocation",
    "EnvironmentVariableConfigInjectionLocationParam",
    "EnvironmentVariableConfigParam",
    "EnvironmentVariableUpdateConfig",
    "EnvironmentVariableUpdateConfigInjectionLocation",
    "EnvironmentVariableUpdateConfigInjectionLocationParam",
    "EnvironmentVariableUpdateConfigParam",
    "HTTPBearerConfig",
    "HTTPBearerConfigParam",
    "HTTPBearerUpdateConfig",
    "HTTPBearerUpdateConfigParam",
    "InjectionLocationEnum",
    "OAuth2Config",
    "OAuth2ConfigParam",
    "OAuth2UpdateConfig",
    "OAuth2UpdateConfigParam",
]
