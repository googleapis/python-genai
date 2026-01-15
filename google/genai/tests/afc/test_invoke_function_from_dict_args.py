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


"""Test invoke_function_from_dict_args."""

from typing import Union
import pydantic
import pytest
import sys
from ... import errors
from ..._extra_utils import invoke_function_from_dict_args


def test_builtin_primitive_types():
  def func_under_test(x: int, y: float, z: str, w: bool):
    return {
        'x': x + 1,
        'y': y + 1.0,
        'z': z + '1.0',
        'w': not w,
    }

  original_args = {
      'x': 1,
      'y': 1.0,
      'z': '1.0',
      'w': True,
  }
  expected_response = {
      'x': 2,
      'y': 2.0,
      'z': '1.01.0',
      'w': False,
  }

  actual_response = invoke_function_from_dict_args(
      original_args, func_under_test
  )

  assert actual_response == expected_response


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_builtin_compound_types():
  def func_under_test(x: list[int], y: dict[str, float]):
    return {
        'new_x': x + [3],
        'new_y': y | {'key3': 3.0},
    }

  original_args = {
      'x': [1, 2],
      'y': {'key1': 1.0, 'key2': 2.0},
  }
  expected_response = {
      'new_x': [1, 2, 3],
      'new_y': {'key1': 1.0, 'key2': 2.0, 'key3': 3.0},
  }

  actual_response = invoke_function_from_dict_args(
      original_args, func_under_test
  )

  assert actual_response == expected_response


def test_nested_pydantic_model():
  class SimpleModel(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  class ComplexModel(pydantic.BaseModel):
    key1_complex: SimpleModel
    key2_complex: list[SimpleModel]
    key3_complex: dict[str, SimpleModel]

  def func_under_test(x: ComplexModel):
    y = x.model_copy()
    y.key1_complex.key1_simple += 1
    y.key1_complex.key2_simple += 1.0
    for simple_model in y.key2_complex:
      simple_model.key1_simple += 1
      simple_model.key2_simple += 1.0
    for simple_model in y.key3_complex.values():
      simple_model.key1_simple += 1
      simple_model.key2_simple += 1.0
    return y

  original_args = {
      'x': {
          'key1_complex': {'key1_simple': 1, 'key2_simple': 1.0},
          'key2_complex': [
              {'key1_simple': 2, 'key2_simple': 2.0},
              {'key1_simple': 3, 'key2_simple': 3.0},
          ],
          'key3_complex': {
              'key1_simple': {'key1_simple': 4, 'key2_simple': 4.0},
              'key2_simple': {'key1_simple': 5, 'key2_simple': 5.0},
          },
      }
  }
  expected_response = {
      'key1_complex': {'key1_simple': 2, 'key2_simple': 2.0},
      'key2_complex': [
          {'key1_simple': 3, 'key2_simple': 3.0},
          {'key1_simple': 4, 'key2_simple': 4.0},
      ],
      'key3_complex': {
          'key1_simple': {'key1_simple': 5, 'key2_simple': 5.0},
          'key2_simple': {'key1_simple': 6, 'key2_simple': 6.0},
      },
  }

  actual_response = invoke_function_from_dict_args(
      original_args, func_under_test
  )

  assert isinstance(actual_response, ComplexModel)
  assert isinstance(actual_response.key1_complex, SimpleModel)
  assert isinstance(actual_response.key2_complex[0], SimpleModel)
  assert isinstance(actual_response.key2_complex[1], SimpleModel)
  assert isinstance(actual_response.key3_complex['key1_simple'], SimpleModel)
  assert isinstance(actual_response.key3_complex['key2_simple'], SimpleModel)
  assert actual_response.model_dump() == expected_response


def test_pydantic_model_in_list_union_type():
  class SimpleModel(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  def func_under_test(x: list[Union[int, SimpleModel]]):
    result = []
    for item in x:
      if isinstance(item, int):
        result.append(item + 1)
      elif isinstance(item, SimpleModel):
        result.append(item.model_copy())
        result[-1].key1_simple += 1
        result[-1].key2_simple += 1.0
      else:
        raise ValueError('Unsupported type: %s' % type(item))
    return result

  expected_response = [2, {'key1_simple': 2, 'key2_simple': 2.0}]
  original_args = {'x': [1, {'key1_simple': 1, 'key2_simple': 1.0}]}
  actual_response = invoke_function_from_dict_args(
      original_args, func_under_test
  )
  assert isinstance(actual_response, list)
  assert len(actual_response) == 2
  assert isinstance(actual_response[0], int)
  assert isinstance(actual_response[1], SimpleModel)
  assert actual_response[0] == expected_response[0]
  assert actual_response[1].model_dump() == expected_response[1]


def test_unknown_pydantic_model_argument():
  class SimpleModel(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  def func_under_test(x: SimpleModel):
    return x.model_copy()

  original_args = {'x': {'key3_simple': 1, 'key2_simple': 1.0}}

  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args(original_args, func_under_test)


def test_unknown_pydantic_model_argument_with_union_type():
  class SimpleModel1(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  class SimpleModel2(pydantic.BaseModel):
    key3_simple: str
    key4_simple: float

  def func_under_test(x: Union[SimpleModel1, SimpleModel2]):
    return x.model_copy()

  original_args = {'x': {'key5_simple': 1, 'key4_simple': 1.0}}

  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args(original_args, func_under_test)


def test_unknown_pydantic_model_argument_with_union_type_and_builtin_type():
  class SimpleModel1(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  def func_under_test(x: Union[SimpleModel1, int]):
    return x.model_copy()

  original_args = {'x': {'key5_simple': 1, 'key4_simple': 1.0}}

  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args(original_args, func_under_test)


def test_incompatible_value_and_annotation():
  def func_under_test(x: int):
    return x + 1

  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args({'x': {'k': 'v'}}, func_under_test)
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args({'x': 'a'}, func_under_test)
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args({'x': []}, func_under_test)
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args({'x': 1.0}, func_under_test)
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    invoke_function_from_dict_args({'x': {}}, func_under_test)


def test_function_invocation_error():
  def func_under_test(x: int):
    return x / 0

  with pytest.raises(errors.FunctionInvocationError):
    invoke_function_from_dict_args({'x': 1}, func_under_test)
