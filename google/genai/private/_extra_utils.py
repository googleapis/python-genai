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
"""Private extra utils for google.genai."""
# Imports all the public extra utils but change the
# public types to private types.

from .. import _extra_utils as public_extra_utils
from .._extra_utils import *  # pylint: disable=wildcard-import
from . import _mcp_utils as private_mcp_utils
from . import _transformers as private_transformers
from . import types as private_types


public_extra_utils.types = private_types
public_extra_utils.t = private_transformers
public_extra_utils._mcp_utils = private_mcp_utils  # pylint: disable=protected-access
