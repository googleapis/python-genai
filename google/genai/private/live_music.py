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
"""Private live_music for google.genai."""
# Imports all the public live_music but change the
# public types to private types.

from .. import live_music as public_live_music
from ..live_music import *  # pylint: disable=wildcard-import
from . import _live_converters as private_live_converters
from . import _transformers as private_transformers
from . import types as private_types
from .models import _Content_to_mldev as private_content_to_mldev

public_live_music.types = private_types
public_live_music.t = private_transformers
public_live_music.live_converters = private_live_converters
public_live_music._Content_to_mldev = private_content_to_mldev
