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
# mypy: ignore-errors

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["TextContent", "Annotation"]


class Annotation(BaseModel):
    end_index: Optional[int] = FieldInfo(alias="endIndex", default=None)
    """End of the attributed segment, exclusive."""

    start_index: Optional[int] = FieldInfo(alias="startIndex", default=None)
    """Start of segment of the response that is attributed to this source.

    Index indicates the start of the segment, measured in bytes.
    """

    url: Optional[str] = None
    """URL that is attributed as a source for a portion of the text."""


class TextContent(BaseModel):
    type: Literal["text"]
    """Used as the OpenAPI type discriminator for the content oneof."""

    annotations: Optional[List[Annotation]] = None
    """Citation information for model-generated content."""

    text: Optional[str] = None
    """The text content."""
