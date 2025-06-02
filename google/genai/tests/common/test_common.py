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


"""Tests tools in the _common module."""

import warnings
import inspect
import typing

import pytest

from ... import _common
from ... import errors


def test_warn_once():
  @_common.experimental_warning('Warning!')
  def func():
    pass

  with warnings.catch_warnings(record=True) as w:
    func()
    func()

  assert len(w) == 1
  assert w[0].category == errors.ExperimentalWarning

def test_warn_at_call_line():
  @_common.experimental_warning('Warning!')
  def func():
    pass

  with warnings.catch_warnings(record=True) as captured_warnings:
    call_line = inspect.currentframe().f_lineno + 1
    func()

  assert captured_warnings[0].lineno == call_line


def test_is_struct_type():
  assert _common._is_struct_type(list[dict[str, typing.Any]])
  assert _common._is_struct_type(typing.List[typing.Dict[str, typing.Any]])
  assert not _common._is_struct_type(list[dict[str, int]])
  assert not _common._is_struct_type(list[dict[int, typing.Any]])
  assert not _common._is_struct_type(list[str])
  assert not _common._is_struct_type(dict[str, typing.Any])
  assert not _common._is_struct_type(typing.List[typing.Dict[str, int]])
  assert not _common._is_struct_type(typing.List[typing.Dict[int, typing.Any]])
  assert not _common._is_struct_type(typing.List[str])
  assert not _common._is_struct_type(typing.Dict[str, typing.Any])