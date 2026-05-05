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

from typing import Union
from typing_extensions import Annotated, TypeAlias

from .._utils import PropertyInfo
from .text_content import TextContent
from .audio_content import AudioContent
from .image_content import ImageContent
from .video_content import VideoContent
from .document_content import DocumentContent

__all__ = ["Content"]

Content: TypeAlias = Annotated[
    Union[TextContent, ImageContent, AudioContent, DocumentContent, VideoContent], PropertyInfo(discriminator="type")
]
