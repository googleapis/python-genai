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

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FileCitation"]


class FileCitation(BaseModel):
    """A file citation annotation."""

    type: Literal["file_citation"]

    document_uri: Optional[str] = None
    """The URI of the file."""

    end_index: Optional[int] = None
    """End of the attributed segment, exclusive."""

    file_name: Optional[str] = None
    """The name of the file."""

    source: Optional[str] = None
    """Source attributed for a portion of the text."""

    start_index: Optional[int] = None
    """Start of segment of the response that is attributed to this source.

    Index indicates the start of the segment, measured in bytes.
    """
