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

"""Google Gen AI SDK"""

import importlib
from typing import Any

from . import types
from . import version
from .client import Client


__version__ = version.__version__

__all__ = ['Client', 'credentials', 'interactions', 'types']


def __getattr__(name: str) -> Any:
  if name in ('credentials', 'interactions'):
    module = importlib.import_module(f'.{name}', __name__)
    globals()[name] = module
    return module
  raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
