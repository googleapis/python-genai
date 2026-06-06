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

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = ["Environment", "Network", "NetworkAllowlist", "NetworkAllowlistAllowlist", "Source"]


class NetworkAllowlistAllowlist(BaseModel):
    """A single domain allowlist rule with optional header injection."""

    domain: str
    """Domain to allow outbound requests to.

    Supports wildcards (e.g. '_.googleapis.com'). Use '_' to allow all domains.
    """

    transform: Optional[List[Dict[str, str]]] = None
    """Headers to inject on all outbound requests matching this domain.

    Each entry is a flat {header_name: header_value} object. The egress proxy
    injects these automatically.
    """


class NetworkAllowlist(BaseModel):
    """Outbound networking configuration for the sandbox.

    When specified, restricts which external domains the sandbox can reach. Omit entirely to allow all outbound traffic with no header injection.
    """

    allowlist: Optional[List[NetworkAllowlistAllowlist]] = None
    """List of allowed outbound domains.

    Only requests to listed domains are permitted. Use [{'domain': '*'}] to allow
    all domains while still injecting headers on specific ones.
    """


Network: TypeAlias = Union[Literal["disabled"], NetworkAllowlist]


class Source(BaseModel):
    """A source to be mounted into the environment."""

    content: Optional[str] = None
    """The inline content if `type` is `INLINE`."""

    encoding: Optional[str] = None
    """Optional encoding for inline content (e.g. `base64`)."""

    source: Optional[str] = None
    """
    The source of the environment. For GCS, this is the GCS path. For GitHub, this
    is the GitHub path.
    """

    target: Optional[str] = None
    """Where the source should appear in the environment."""

    type: Optional[Literal["gcs", "inline", "repository", "skill_registry"]] = None


class Environment(BaseModel):
    """Configuration for a custom environment."""

    type: Literal["remote"]

    network: Optional[Network] = None
    """Network configuration for the environment."""

    sources: Optional[List[Source]] = None
