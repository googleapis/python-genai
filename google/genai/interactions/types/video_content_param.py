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

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config

__all__ = ["VideoContentParam"]


class VideoContentParam(TypedDict, total=False):
    type: Required[Literal["video"]]
    """Used as the OpenAPI type discriminator for the content oneof."""

    data: Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]

    file_uri: Annotated[str, PropertyInfo(alias="fileUri")]

    mime_type: Annotated[str, PropertyInfo(alias="mimeType")]
    """The video content."""


set_pydantic_config(VideoContentParam, {"arbitrary_types_allowed": True})
