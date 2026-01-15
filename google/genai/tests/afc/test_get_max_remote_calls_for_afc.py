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


"""Tests for get_max_remote_calls_for_afc."""

from ... import types
from ..._extra_utils import get_max_remote_calls_afc
import pytest


def test_config_is_none():
  assert get_max_remote_calls_afc(None) == 10


def test_afc_unset_max_unset():
  assert get_max_remote_calls_afc(types.GenerateContentConfig()) == 10


def test_afc_unset_max_set():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  maximum_remote_calls=20,
              ),
          )
      )
      == 20
  )


def test_afc_disabled_max_unset():
  with pytest.raises(ValueError):
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=True,
              ),
          )
      )


def test_afc_disabled_max_set():
  with pytest.raises(ValueError):
    get_max_remote_calls_afc(
        types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True,
                maximum_remote_calls=20,
            ),
        )
    )


def test_afc_d_max_unset():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=False,
              ),
          )
      )
      == 10
  )


def test_afc_d_max_set():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=False,
                  maximum_remote_calls=5,
              ),
          )
      )
      == 5
  )


def test_afc_enabled_max_set_to_zero():
  with pytest.raises(ValueError):
    get_max_remote_calls_afc(
        types.GenerateContentConfig(
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=0,
            ),
        )
    )


def test_afc_enabled_max_set_to_negative():
  with pytest.raises(ValueError):
    get_max_remote_calls_afc(
        types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=-1,
            ),
        )
    )


def test_afc_enabled_max_set_to_float():
  assert (
      get_max_remote_calls_afc(
          types.GenerateContentConfig(
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=False,
                  maximum_remote_calls=5.0,
              ),
          )
      )
      == 5
  )
