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

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FixRequest", "SessionConfig", "SourceFile"]


class SessionConfig(BaseModel):
    """
    Optional session-specific configurations to override default agent
    behavior.
    """

    max_rounds: Optional[int] = None
    """
    The maximum number of interaction rounds the agent is allowed to perform before
    reaching a timeout.
    """

    pipeline_mode: Optional[Literal["scan", "verify"]] = None
    """The pipeline mode of a CodeMender session.

    It can only be used for a find session.
    """

    topology: Optional[str] = None
    """The cognitive architecture or "thinking" topology used by the agent (e.g.

    "default", "deep").
    """


class SourceFile(BaseModel):
    """Content of a single file in the codebase."""

    content: Optional[str] = None
    """The UTF-8 encoded text content of the file."""

    path: Optional[str] = None
    """The relative path of the file from the project root."""


class FixRequest(BaseModel):
    """
    Request parameters specific to FIX sessions, used for generating and
    validating security patches.
    """

    request: Literal["fix_request"]

    description: Optional[str] = None
    """
    Additional context or custom instructions provided by the user to guide the
    patch generation process.
    """

    finding_id: Optional[str] = None
    """The identifier of the specific security finding to be remediated.

    This ID maps to a previously discovered vulnerability.
    """

    session_config: Optional[SessionConfig] = None
    """Optional session-specific configurations to override default agent behavior."""

    session_id: Optional[str] = None
    """
    Parameter for grouping multiple interactions that belong to the same CodeMender
    session.
    """

    source_files: Optional[List[SourceFile]] = None
    """A list of source files providing context for the remediation.

    These files are typically the ones containing the identified vulnerability.
    """
