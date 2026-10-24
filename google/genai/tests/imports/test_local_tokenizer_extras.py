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
"""Tests for the local tokenizer install extras declared in pyproject.toml."""

import importlib
import os
import pathlib
import re
import sys

import pytest

# tomllib is standard from Python 3.11 and the project supports 3.10.
_TOMLLIB = (
    importlib.import_module('tomllib') if sys.version_info >= (3, 11) else None
)

_TRANSFORMERS_STACK = frozenset(
    {'pillow', 'torch', 'torchvision', 'transformers'}
)

pytestmark = pytest.mark.skipif(
    _TOMLLIB is None, reason='tomllib requires Python 3.11'
)


def _pyproject_path() -> pathlib.Path:
  """Finds pyproject.toml, which the public export moves to the repository root."""
  candidates = []
  srcdir = os.environ.get('TEST_SRCDIR')
  if srcdir:
    candidates.append(
        pathlib.Path(srcdir)
        / 'google3/third_party/py/google/genai/packaging/pyproject.toml'
    )
  for parent in pathlib.Path(__file__).resolve().parents:
    candidates.append(parent / 'packaging' / 'pyproject.toml')
    candidates.append(parent / 'pyproject.toml')
  for candidate in candidates:
    if candidate.is_file():
      return candidate
  raise FileNotFoundError('cannot find pyproject.toml')


def _extra_packages(extra_name: str) -> set[str]:
  """Returns the distribution names listed in one pyproject.toml extra."""
  with _pyproject_path().open('rb') as pyproject_file:
    pyproject = _TOMLLIB.load(pyproject_file)
  extras = pyproject['project']['optional-dependencies']
  return {re.split(r'[<>=!~;\[ ]', spec)[0] for spec in extras[extra_name]}


def test_local_tokenizer_extra_excludes_transformers_stack():
  """A SentencePiece model installs without Transformers and PyTorch."""
  packages = _extra_packages('local-tokenizer')

  assert 'sentencepiece' in packages
  assert 'protobuf' in packages
  assert (packages & _TRANSFORMERS_STACK) == set()


def test_local_tokenizer_transformers_extra_has_full_stack():
  """The Gemma 4 extra stays a superset of the SentencePiece extra."""
  packages = _extra_packages('local-tokenizer-transformers')

  assert packages >= {'sentencepiece', 'protobuf'} | _TRANSFORMERS_STACK
