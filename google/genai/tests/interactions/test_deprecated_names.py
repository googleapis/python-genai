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
"""Tests for deprecated names in `google.genai.interactions`."""

import importlib
import warnings

import pytest

from ... import environments
from ... import interactions

# pylint: disable=protected-access
_DEPRECATED_NAMES = sorted(interactions._DEPRECATED_NAMES)
# pylint: enable=protected-access


@pytest.mark.parametrize("name", _DEPRECATED_NAMES)
def test_deprecated_name_warns(name: str) -> None:
  with pytest.warns(DeprecationWarning, match=f"interactions.{name}`"):
    getattr(interactions, name)


@pytest.mark.parametrize("name", _DEPRECATED_NAMES)
def test_deprecated_name_matches_replacement(name: str) -> None:
  """The deprecated name is the same object as in its replacement module."""
  # pylint: disable=protected-access
  _, _, replacement = interactions._DEPRECATED_NAMES[name]
  # pylint: enable=protected-access
  if replacement is None:
    pytest.skip(f"{name} has no public replacement")
  with pytest.warns(DeprecationWarning, match=f"`{replacement}`"):
    value = getattr(interactions, name)
  # Resolve the replacement module relative to the package that holds
  # `interactions`. The package is not always importable as `google.genai`
  # (for example, in the open source test run).
  replacement_module = importlib.import_module(
      "." + replacement.rsplit(".", 1)[-1], interactions.__package__
  )
  assert value is getattr(replacement_module, name)


@pytest.mark.parametrize("name", _DEPRECATED_NAMES)
def test_deprecated_name_in_all_and_dir(name: str) -> None:
  assert name in interactions.__all__
  assert name in dir(interactions)


def test_from_import_warns() -> None:
  with pytest.warns(DeprecationWarning, match="google.genai.agents"):
    # pylint: disable=g-import-not-at-top,unused-import
    from ...interactions import Agent  # noqa: F401
    # pylint: enable=g-import-not-at-top,unused-import


def test_interactions_names_do_not_warn() -> None:
  with warnings.catch_warnings():
    warnings.simplefilter("error", DeprecationWarning)
    # Use the names that `interactions` itself imports. The `--private` test
    # run rewrites `_gaos` imports in tests to `_gaos_private`, which has
    # names that the public `interactions` module does not export.
    # pylint: disable-next=protected-access
    for name in interactions._interactions_all:
      getattr(interactions, name)
    assert interactions.Interaction is not None
    assert interactions.ModelParam is not None


def test_shadowed_names_resolve_to_interactions_types() -> None:
  """Names in both namespaces keep the interactions type."""
  assert interactions.Environment is not environments.Environment
  assert interactions.Status is not environments.Status


def test_unknown_name_raises_attribute_error() -> None:
  with pytest.raises(AttributeError, match="NotARealName"):
    getattr(interactions, "NotARealName")
