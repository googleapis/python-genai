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

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["FindRequestParam", "SessionConfig", "SourceFile"]


class SessionConfig(TypedDict, total=False):
    """
    Optional session-specific configurations to override default agent
    behavior.
    """

    max_rounds: int
    """
    The maximum number of interaction rounds the agent is allowed to perform before
    reaching a timeout.
    """

    pipeline_mode: Literal["scan", "verify"]
    """The pipeline mode of a CodeMender session.

    It can only be used for a find session.
    """

    topology: str
    """The cognitive architecture or "thinking" topology used by the agent (e.g.

    "default", "deep").
    """


class SourceFile(TypedDict, total=False):
    """Content of a single file in the codebase."""

    content: str
    """The UTF-8 encoded text content of the file."""

    path: str
    """The relative path of the file from the project root."""


class FindRequestParam(TypedDict, total=False):
    """
    Request parameters specific to FIND sessions, used for discovering
    vulnerabilities in a codebase.
    """

    request: Required[Literal["find_request"]]

    description: str
    """
    Additional context or custom instructions provided by the user to guide the
    vulnerability analysis.
    """

    finding_id: str
    """The identifier of a specific finding to verify.

    This is primarily used in VERIFY mode to focus the agent's execution-based
    validation on a single vulnerability.
    """

    session_config: SessionConfig
    """Optional session-specific configurations to override default agent behavior."""

    session_id: str
    """
    Parameter for grouping multiple interactions that belong to the same CodeMender
    session.
    """

    source_files: Iterable[SourceFile]
    """A list of source files to provide as context for the scan."""
