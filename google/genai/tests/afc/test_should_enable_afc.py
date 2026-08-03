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


"""Tests for should_enable_afc."""

import pytest
from .. import pytest_helper
from ... import types
from ..._extra_utils import should_enable_afc

pytestmark = [
    pytest.mark.skipif(
        "config.getoption('--private')",
        reason="AFC re-written for private SDK",
    ),
]


def test_config_is_none():
  assert should_enable_afc(None) is False


def test_afc_config_unset():
  assert should_enable_afc(types.ChatConfig()) is False


def test_afc_enable_unset_max_0():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  maximum_remote_calls=0,
              ),
          )
      )
      is False
  )


def test_afc_enable_unset_max_negative():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  maximum_remote_calls=-1,
              ),
          )
      )
      is False
  )


def test_afc_enable_unset_max_1():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  maximum_remote_calls=1,
              ),
          )
      )
      is False
  )


def test_afc_enable_false_max_unset():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  enable=True,
              ),
          )
      )
      is True
  )


def test_afc_enable_false_max_0():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  enable=True,
                  maximum_remote_calls=0,
              ),
          )
      )
      is False
  )


def test_afc_enable_false():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  enable=False,
              ),
          )
      )
      is False
  )


def test_afc_enable_false_max_1():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  enable=False,
                  maximum_remote_calls=1,
              ),
          )
      )
      is False
  )


def test_afc_enable_true_max_negative():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  enable=True,
                  maximum_remote_calls=-1,
              ),
          )
      )
      is False
  )


def test_afc_enable_true_max_1():
  assert (
      should_enable_afc(
          types.ChatConfig(
              automatic_function_calling_config=types.AutomaticFunctionCallingConfig(
                  enable=True,
                  maximum_remote_calls=1,
              ),
          )
      )
      is True
  )
