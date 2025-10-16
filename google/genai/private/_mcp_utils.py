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
"""Private mcp utils for google.genai."""
# Imports all the public transformers but change the
# public types to private types.

from .. import _mcp_utils as public_mcp_utils
from .._mcp_utils import *  # pylint: disable=wildcard-import
from . import types as private_types


public_mcp_utils.types = private_types
