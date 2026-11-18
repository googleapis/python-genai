# Copyright 2026 Google LLC
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

"""One-time experimental warning shared by all Live Interactions entry points."""

import warnings

_LIVE_INTERACTIONS_EXPERIMENTAL_WARNING = (
    'Live Interactions usage (interactions.connect and interactions.auth_tokens)'
    ' is experimental and may change in future versions.'
)
_live_interactions_experimental_warned = False


def _warn_live_interactions_experimental(stacklevel: int = 2) -> None:
  """Emits a one-time-per-process warning on first Live Interactions usage.

  Args:
    stacklevel: Stack level of the public SDK method relative to this helper's
      caller (2 points the warning at the code that called that method).
  """
  global _live_interactions_experimental_warned
  if not _live_interactions_experimental_warned:
    _live_interactions_experimental_warned = True
    warnings.warn(
        _LIVE_INTERACTIONS_EXPERIMENTAL_WARNING,
        category=UserWarning,
        stacklevel=stacklevel + 1,
    )
