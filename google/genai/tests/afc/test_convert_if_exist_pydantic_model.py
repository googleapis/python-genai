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


"""Test convert_if_exist_pydantic_model."""

import inspect
from typing import Optional, Union
import pydantic
import pytest
import sys
from ... import errors
from ..._extra_utils import convert_if_exist_pydantic_model


def test_builtin_types():
  assert convert_if_exist_pydantic_model(1, int, 'param_name', 'func_name') == 1
  assert (
      convert_if_exist_pydantic_model(1.0, float, 'param_name', 'func_name')
      == 1.0
  )
  assert (
      convert_if_exist_pydantic_model('1.0', str, 'param_name', 'func_name')
      == '1.0'
  )
  assert (
      convert_if_exist_pydantic_model(True, bool, 'param_name', 'func_name')
      is True
  )
  assert convert_if_exist_pydantic_model(
      [1], list, 'param_name', 'func_name'
  ) == [1]
  assert convert_if_exist_pydantic_model(
      {'key1': 1}, dict, 'param_name', 'func_name'
  ) == {'key1': 1}
  assert convert_if_exist_pydantic_model(
      {'key1': 1, 'key2': 2}, dict[str, int], 'param_name', 'func_name'
  ) == {'key1': 1, 'key2': 2}


def test_value_int_annotation_float():
  assert (
      convert_if_exist_pydantic_model(1, float, 'param_name', 'func_name')
      == 1.0
  )


def test_union_types():
  assert (
      convert_if_exist_pydantic_model(
          1, Union[int, float], 'param_name', 'func_name'
      )
      == 1
  )
  assert (
      convert_if_exist_pydantic_model(
          1.0, Union[int, float], 'param_name', 'func_name'
      )
      == 1.0
  )
  assert (
      convert_if_exist_pydantic_model(
          '1.0', Union[str, float], 'param_name', 'func_name'
      )
      == '1.0'
  )
  assert (
      convert_if_exist_pydantic_model(
          True, Union[bool, str], 'param_name', 'func_name'
      )
      is True
  )

  # | in 3.10+
  if sys.version_info >= (3, 10):
    assert (
        convert_if_exist_pydantic_model(1, int | float, 'param_name', 'func_name')
        == 1
    )


def test_nested_pydantic_model():
  class SimpleModel(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  class ComplexModel(pydantic.BaseModel):
    key1_complex: SimpleModel
    key2_complex: list[SimpleModel]
    key3_complex: dict[str, SimpleModel]

  def foo(_: ComplexModel):
    pass

  annotation = inspect.signature(foo).parameters['_'].annotation
  original_args = {
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

  converted_args = convert_if_exist_pydantic_model(
      original_args, annotation, 'param_name', 'func_name'
  )
  assert isinstance(converted_args, ComplexModel)
  assert isinstance(converted_args.key1_complex, SimpleModel)
  assert isinstance(converted_args.key2_complex[0], SimpleModel)
  assert isinstance(converted_args.key2_complex[1], SimpleModel)
  assert isinstance(converted_args.key3_complex['key1_simple'], SimpleModel)
  assert isinstance(converted_args.key3_complex['key2_simple'], SimpleModel)
  assert converted_args.model_dump() == original_args


def test_pydantic_model_in_list_union_type():
  class SimpleModel(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  def foo(_: list[Union[int, SimpleModel]]):
    pass

  annotation = inspect.signature(foo).parameters['_'].annotation
  original_args = [1, {'key1_simple': 1, 'key2_simple': 1.0}]

  converted_args = convert_if_exist_pydantic_model(
      original_args, annotation, 'param_name', 'func_name'
  )

  assert isinstance(converted_args, list)
  assert len(converted_args) == 2
  assert isinstance(converted_args[0], int)
  assert isinstance(converted_args[1], SimpleModel)
  assert converted_args[0] == original_args[0]
  assert converted_args[1].model_dump() == original_args[1]


def test_generic_list_type():
  def foo(_: Optional[list[Union[int, float]]]):
    pass

  annotation = inspect.signature(foo).parameters['_'].annotation
  original_args = [1, 1.5]

  converted_args = convert_if_exist_pydantic_model(
      original_args, annotation, 'param_name', 'func_name'
  )

  assert isinstance(converted_args, list)
  assert len(converted_args) == 2
  assert isinstance(converted_args[0], int)
  assert isinstance(converted_args[1], float)
  assert converted_args[0] == original_args[0]


@pytest.mark.skipif(sys.version_info < (3, 10), reason='need python 3.10+')
def test_pydantic_model_with_union_and_generic_type():
  class Model1(pydantic.BaseModel):
    arg1: Union[int, float]
    arg2: list[str]
    arg3: int | float  # python 3.9+
    arg4: Union[list[str], str]

  def foo(_: Optional[list[Union[int, Model1]]]):
    pass

  annotation = inspect.signature(foo).parameters['_'].annotation
  original_args = [1, {'arg1': 1, 'arg2': ['a'], 'arg3': 1.0, 'arg4': '1.0'}]

  converted_args = convert_if_exist_pydantic_model(
      original_args, annotation, 'param_name', 'func_name'
  )

  assert isinstance(converted_args, list)
  assert len(converted_args) == 2
  assert isinstance(converted_args[0], int)
  assert isinstance(converted_args[1], Model1)
  assert converted_args[0] == original_args[0]


def test_unknown_pydantic_model_argument_error():
  class SimpleModel(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  def foo(_: SimpleModel):
    pass

  annotation = inspect.signature(foo).parameters['_'].annotation
  original_args = {'key3_simple': 1, 'key2_simple': 1.0}

  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        original_args, annotation, 'param_name', 'func_name'
    )


def test_unknown_pydantic_model_argument_error_with_union_type():
  class SimpleModel1(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  class SimpleModel2(pydantic.BaseModel):
    key3_simple: str
    key4_simple: float

  def foo(_: Union[SimpleModel1, SimpleModel2]):
    pass

  annotation = inspect.signature(foo).parameters['_'].annotation
  original_args = {'key5_simple': 1, 'key4_simple': 1.0}

  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        original_args, annotation, 'param_name', 'func_name'
    )


def test_unknown_pydantic_model_argument_error_with_union_type_and_builtin_type():
  class SimpleModel1(pydantic.BaseModel):
    key1_simple: int
    key2_simple: float

  def foo(_: Union[SimpleModel1, int]):
    pass

  annotation = inspect.signature(foo).parameters['_'].annotation
  original_args = {'key5_simple': 1, 'key4_simple': 1.0}

  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        original_args, annotation, 'param_name', 'func_name'
    )


def test_incompatible_value_and_annotation():
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        {'key1_simple': 1, 'key2_simple': 1.0},
        int,
        'param_name',
        'func_name',
    )
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        {'key1_simple': 1, 'key2_simple': 1.0},
        float,
        'param_name',
        'func_name',
    )
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        1,
        str,
        'param_name',
        'func_name',
    )
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        1.0,
        str,
        'param_name',
        'func_name',
    )
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        True,
        str,
        'param_name',
        'func_name',
    )
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        [1],
        str,
        'param_name',
        'func_name',
    )
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        {'key1': 1},
        str,
        'param_name',
        'func_name',
    )
  with pytest.raises(errors.UnknownFunctionCallArgumentError):
    convert_if_exist_pydantic_model(
        {'key1': 1, 'key2': 2},
        str,
        'param_name',
        'func_name',
    )
