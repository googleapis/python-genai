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


"""Tests for convert_number_values_for_function_call_args."""

from ..._extra_utils import convert_number_values_for_function_call_args


def test_integer_value():
  assert convert_number_values_for_function_call_args(1) == 1


def test_float_value():
  assert convert_number_values_for_function_call_args(1.0) == 1


def test_string_value():
  assert convert_number_values_for_function_call_args('1.0') == '1.0'


def test_boolean_value():
  assert convert_number_values_for_function_call_args(True) is True


def test_none_value():
  assert convert_number_values_for_function_call_args(None) is None


def test_float_value_with_decimal():
  assert convert_number_values_for_function_call_args(1.1) == 1.1


def test_dict_value():
  assert convert_number_values_for_function_call_args(
      {'key1': 1.0, 'key2': 1.1}
  ) == {'key1': 1, 'key2': 1.1}


def test_list_value():
  assert convert_number_values_for_function_call_args([1.0, 1.1, 1.2]) == [
      1,
      1.1,
      1.2,
  ]


def test_nested_value():
  assert convert_number_values_for_function_call_args(
      {'key1': 1.0, 'key2': {'key3': 1.0, 'key4': [1.2, 2.0]}}
  ) == {'key1': 1, 'key2': {'key3': 1, 'key4': [1.2, 2]}}
