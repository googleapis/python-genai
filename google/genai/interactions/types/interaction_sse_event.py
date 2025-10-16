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

from typing import Union
from typing_extensions import TypeAlias

from .interaction_event import InteractionEvent
from .content_block_stop import ContentBlockStop
from .content_block_delta import ContentBlockDelta
from .content_block_start import ContentBlockStart
from .interaction_status_update import InteractionStatusUpdate

__all__ = ["InteractionSSEEvent"]

InteractionSSEEvent: TypeAlias = Union[
    InteractionEvent, InteractionStatusUpdate, ContentBlockStart, ContentBlockDelta, ContentBlockStop
]
