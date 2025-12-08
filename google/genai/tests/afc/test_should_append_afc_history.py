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

"""Tests for _extra_utils.should_append_afc_history."""

from ... import types
from ..._extra_utils import should_append_afc_history


def test_should_append_afc_history_with_default_config():
  config = types.GenerateContentConfig()

  assert should_append_afc_history(config) == True


def test_should_append_afc_history_with_empty_afc_config():
  config = types.GenerateContentConfig(
      automatic_function_calling=types.AutomaticFunctionCallingConfig()
  )

  assert should_append_afc_history(config) == True


def test_should_append_afc_history_with_ignore_call_history_true():
  config = types.GenerateContentConfig(
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          ignore_call_history=True
      )
  )

  assert should_append_afc_history(config) == False


def test_should_append_afc_history_with_ignore_call_history_false():
  config = types.GenerateContentConfig(
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          ignore_call_history=False
      )
  )

  assert should_append_afc_history(config) == True
