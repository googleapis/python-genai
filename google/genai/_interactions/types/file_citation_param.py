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

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

__all__ = ["FileCitationParam"]


class FileCitationParam(TypedDict, total=False):
    """A file citation annotation."""

    type: Required[Literal["file_citation"]]

    custom_metadata: Dict[str, object]
    """User provided metadata about the retrieved context."""

    document_uri: str
    """The URI of the file."""

    end_index: int
    """End of the attributed segment, exclusive."""

    file_name: str
    """The name of the file."""

    media_id: str
    """Media ID in-case of image citations, if applicable."""

    page_number: int
    """Page number of the cited document, if applicable."""

    source: str
    """Source attributed for a portion of the text."""

    start_index: int
    """Start of segment of the response that is attributed to this source.

    Index indicates the start of the segment, measured in bytes.
    """
