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
"""Private live for google.genai."""
# Imports all the public live but change the
# public types to private types.

from .. import live as public_live
from ..live import *  # pylint: disable=wildcard-import
from . import _live_converters as private_live_converters
from . import _mcp_utils as private_mcp_utils
from . import _transformers as private_transformers
from . import types as private_types
from .live_music import AsyncLiveMusic as private_live_music
from .models import _Content_to_mldev as private_content_to_mldev

public_live.types = private_types
public_live.t = private_transformers
public_live.live_converters = private_live_converters
public_live._Content_to_mldev = private_content_to_mldev
public_live.mcp_utils = private_mcp_utils
public_live.AsyncLiveMusic = private_live_music
