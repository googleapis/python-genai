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
"""Private adapters for google.genai."""
# Imports all the public adapters but change the
# public types to private types.

from .. import _adapters as public_adapters
from .._adapters import *  # pylint: disable=wildcard-import
from . import types as private_types


public_adapters.FunctionCall = private_types.FunctionCall
public_adapters.Tool = private_types.Tool
