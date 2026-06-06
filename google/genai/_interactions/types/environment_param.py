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

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["EnvironmentParam", "Network", "NetworkAllowlist", "NetworkAllowlistAllowlist", "Source"]


class NetworkAllowlistAllowlist(TypedDict, total=False):
    """A single domain allowlist rule with optional header injection."""

    domain: Required[str]
    """Domain to allow outbound requests to.

    Supports wildcards (e.g. '_.googleapis.com'). Use '_' to allow all domains.
    """

    transform: Iterable[Dict[str, str]]
    """Headers to inject on all outbound requests matching this domain.

    Each entry is a flat {header_name: header_value} object. The egress proxy
    injects these automatically.
    """


class NetworkAllowlist(TypedDict, total=False):
    """Outbound networking configuration for the sandbox.

    When specified, restricts which external domains the sandbox can reach. Omit entirely to allow all outbound traffic with no header injection.
    """

    allowlist: Iterable[NetworkAllowlistAllowlist]
    """List of allowed outbound domains.

    Only requests to listed domains are permitted. Use [{'domain': '*'}] to allow
    all domains while still injecting headers on specific ones.
    """


Network: TypeAlias = Union[Literal["disabled"], NetworkAllowlist]


class Source(TypedDict, total=False):
    """A source to be mounted into the environment."""

    content: str
    """The inline content if `type` is `INLINE`."""

    encoding: str
    """Optional encoding for inline content (e.g. `base64`)."""

    source: str
    """
    The source of the environment. For GCS, this is the GCS path. For GitHub, this
    is the GitHub path.
    """

    target: str
    """Where the source should appear in the environment."""

    type: Literal["gcs", "inline", "repository", "skill_registry"]


class EnvironmentParam(TypedDict, total=False):
    """Configuration for a custom environment."""

    type: Required[Literal["remote"]]

    network: Network
    """Network configuration for the environment."""

    sources: Iterable[Source]
