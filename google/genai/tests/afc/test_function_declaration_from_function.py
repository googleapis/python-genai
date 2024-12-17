# Copyright 2024 Google LLC
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


import copy
import sys
import typing
from typing import Optional
import pydantic
import pytest
from ... import types


class FakeClient:

  def __init__(self, vertexai=False) -> None:
    self.vertexai = vertexai


mldev_client = FakeClient()
vertex_client = FakeClient(vertexai=True)


def test_empty_function():
  def func_under_test():
    """test empty function."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      description='test empty function.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_built_in_primitives_and_compounds():

  def func_under_test(
      a: int,
      b: float,
      c: bool,
      d: str,
      e: list,
      f: dict,
  ):
    """test built in primitives and compounds."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='INTEGER'),
              'b': types.Schema(type='NUMBER'),
              'c': types.Schema(type='BOOLEAN'),
              'd': types.Schema(type='STRING'),
              'e': types.Schema(type='ARRAY'),
              'f': types.Schema(type='OBJECT'),
          },
      ),
      description='test built in primitives and compounds.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.parameters.required = [
      'a',
      'b',
      'c',
      'd',
      'e',
      'f',
  ]

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_default_value_not_compatible_built_in_type():
  def func_under_test(a: str, b: int = '1', c: list = []):
    """test default value not compatible built in type."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(vertex_client, func_under_test)


def test_default_value_built_in_type():
  def func_under_test(a: str, b: int = 1, c: list = []):
    """test default value."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='STRING'),
              'b': types.Schema(type='INTEGER', default=1),
              'c': types.Schema(type='ARRAY', default=[]),
          },
          required=['a'],
      ),
      description='test default value.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)

  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )
  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_unsupported_built_in_primitives_compounds():
  def func_under_test1(a: bytes):
    pass

  def func_under_test2(a: set):
    pass

  def func_under_test3(a: frozenset):
    pass

  def func_under_test4(a: type(None)):
    pass

  def func_under_test5(a: int | bytes):
    pass

  def func_under_test6(a: int | set):
    pass

  def func_under_test7(a: int | frozenset):
    pass

  def func_under_test8(a: typing.Union[int, bytes]):
    pass

  def func_under_test9(a: typing.Union[int, set]):
    pass

  def func_under_test10(a: typing.Union[int, frozenset]):
    pass

  all_func_under_test = [
      func_under_test1,
      func_under_test2,
      func_under_test3,
      func_under_test4,
      func_under_test5,
      func_under_test6,
      func_under_test7,
      func_under_test8,
      func_under_test9,
      func_under_test10,
  ]
  for func_under_test in all_func_under_test:
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(mldev_client, func_under_test)
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(vertex_client, func_under_test)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_built_in_union_type():

  def func_under_test(
      a: int | str | float | bool,
      b: list | dict,
  ):
    """test built in union type."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='INTEGER'),
                      types.Schema(type='STRING'),
                      types.Schema(type='NUMBER'),
                      types.Schema(type='BOOLEAN'),
                  ],
              ),
              'b': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
              ),
          },
          required=['a', 'b'],
      ),
      description='test built in union type.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_default_value_not_compatible_built_in_union_type():
  def func_under_test(
      a: int | str = 1.1,
  ):
    """test default value not compatible built in union type."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(vertex_client, func_under_test)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_default_value_built_in_union_type():

  def func_under_test(
      a: int | str = '1',
      b: list | dict = [],
      c: list | dict = {},
  ):
    """test default value built in union type."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='INTEGER'),
                      types.Schema(type='STRING'),
                  ],
                  default='1',
              ),
              'b': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
                  default=[],
              ),
              'c': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
                  default={},
              ),
          },
          required=[],
      ),
      description='test default value built in union type.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_generic_alias_literal():

  def func_under_test(a: typing.Literal['a', 'b', 'c']):
    """test generic alias literal."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='STRING',
                  enum=['a', 'b', 'c'],
              ),
          },
      ),
      description='test generic alias literal.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.parameters.required = ['a']

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_default_value_generic_alias_literal():

  def func_under_test(a: typing.Literal['1', '2', '3'] = '1'):
    """test default value generic alias literal."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='STRING',
                  enum=['1', '2', '3'],
                  default='1',
              ),
          },
          required=[],
      ),
      description='test default value generic alias literal.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_default_value_generic_alias_literal_not_compatible():
  def func_under_test(a: typing.Literal['1', '2', 3]):
    """test default value generic alias literal not compatible."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(vertex_client, func_under_test)


def test_default_value_not_compatible_generic_alias_literal():
  def func_under_test(a: typing.Literal['a', 'b', 'c'] = 'd'):
    """test default value not compatible generic alias literal."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(vertex_client, func_under_test)


def test_generic_alias_array():

  def func_under_test(
      a: typing.List[int],
  ):
    """test generic alias array."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='ARRAY', items=types.Schema(type='INTEGER')
              ),
          },
      ),
      description='test generic alias array.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.parameters.required = ['a']

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_generic_alias_complex_array():

  def func_under_test(
      a: typing.List[int | str | float | bool],
      b: typing.List[list | dict],
  ):
    """test generic alias complex array."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='ARRAY',
                  items=types.Schema(
                      type='OBJECT',
                      any_of=[
                          types.Schema(type='INTEGER'),
                          types.Schema(type='STRING'),
                          types.Schema(type='NUMBER'),
                          types.Schema(type='BOOLEAN'),
                      ],
                  ),
              ),
              'b': types.Schema(
                  type='ARRAY',
                  items=types.Schema(
                      type='OBJECT',
                      any_of=[
                          types.Schema(type='ARRAY'),
                          types.Schema(type='OBJECT'),
                      ],
                  ),
              ),
          },
          required=['a', 'b'],
      ),
      description='test generic alias complex array.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )
  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_generic_alias_complex_array_with_default_value():

  def func_under_test(
      a: typing.List[int | str | float | bool] = [
          1,
          'a',
          1.1,
          True,
      ],
      b: list[int | str | float | bool] = [
          11,
          'aa',
          1.11,
          False,
      ],
      c: typing.List[typing.List[int] | int] = [[1], 2],
  ):
    """test generic alias complex array with default value."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='ARRAY',
                  items=types.Schema(
                      type='OBJECT',
                      any_of=[
                          types.Schema(type='INTEGER'),
                          types.Schema(type='STRING'),
                          types.Schema(type='NUMBER'),
                          types.Schema(type='BOOLEAN'),
                      ],
                  ),
                  default=[1, 'a', 1.1, True],
              ),
              'b': types.Schema(
                  type='ARRAY',
                  items=types.Schema(
                      type='OBJECT',
                      any_of=[
                          types.Schema(type='INTEGER'),
                          types.Schema(type='STRING'),
                          types.Schema(type='NUMBER'),
                          types.Schema(type='BOOLEAN'),
                      ],
                  ),
                  default=[11, 'aa', 1.11, False],
              ),
              'c': types.Schema(
                  type='ARRAY',
                  items=types.Schema(
                      type='OBJECT',
                      any_of=[
                          types.Schema(
                              type='ARRAY',
                              items=types.Schema(type='INTEGER'),
                          ),
                          types.Schema(type='INTEGER'),
                      ],
                  ),
                  default=[[1], 2],
              ),
          },
          required=[],
      ),
      description='test generic alias complex array with default value.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.9 and above.',
)
def test_generic_alias_complex_array_with_default_value_not_compatible():

  def func_under_test1(
      a: typing.List[int | str | float | bool] = [1, 'a', 1.1, True, []],
  ):
    """test generic alias complex array with default value not compatible."""
    pass

  def func_under_test2(
      a: list[int | str | float | bool] = [1, 'a', 1.1, True, []],
  ):
    """test generic alias complex array with default value not compatible."""
    pass

  for func_under_test in [func_under_test1, func_under_test2]:
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(mldev_client, func_under_test)
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(vertex_client, func_under_test)


def test_generic_alias_object():

  def func_under_test(
      a: typing.Dict[str, int],
  ):
    """test generic alias object."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='OBJECT'),
          },
      ),
      description='test generic alias object.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.parameters.required = ['a']

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_uncommon_generic_alias_object():
  def func_under_test1(a: typing.OrderedDict[str, int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test2(a: typing.MutableMapping[str, int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test3(a: typing.MutableSequence[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test4(a: typing.MutableSet[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test5(a: typing.Counter[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test6(a: typing.Collection[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test7(a: typing.Iterable[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test8(a: typing.Iterator[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test9(a: typing.Container[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test10(a: typing.ChainMap[int, int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test11(a: typing.DefaultDict[int, int]):
    """test uncommon generic alias object."""
    pass

  all_func_under_test = [
      func_under_test1,
      func_under_test2,
      func_under_test3,
      func_under_test4,
      func_under_test5,
      func_under_test6,
      func_under_test7,
      func_under_test8,
      func_under_test9,
      func_under_test10,
      func_under_test11,
  ]

  for func_under_test in all_func_under_test:
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(mldev_client, func_under_test)
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(vertex_client, func_under_test)


def test_generic_alias_object_with_default_value():
  def func_under_test(a: typing.Dict[str, int] = {'a': 1}):
    """test generic alias object with default value."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='OBJECT',
                  default={'a': 1},
              ),
          },
          required=[],
      ),
      description='test generic alias object with default value.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_generic_alias_object_with_default_value_not_compatible():
  def func_under_test(a: typing.Dict[str, int] = 'a'):
    """test generic alias object with default value not compatible."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(vertex_client, func_under_test)


def test_pydantic_model():
  class MySimplePydanticModel(pydantic.BaseModel):
    a_simple: int
    b_simple: str

  class MyComplexPydanticModel(pydantic.BaseModel):
    a_complex: MySimplePydanticModel
    b_complex: list[MySimplePydanticModel]

  def func_under_test(
      a: MySimplePydanticModel,
      b: MyComplexPydanticModel,
  ):
    """test pydantic model."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='OBJECT',
                  properties={
                      'a_simple': types.Schema(type='INTEGER'),
                      'b_simple': types.Schema(type='STRING'),
                  },
              ),
              'b': types.Schema(
                  type='OBJECT',
                  properties={
                      'a_complex': types.Schema(
                          type='OBJECT',
                          properties={
                              'a_simple': types.Schema(type='INTEGER'),
                              'b_simple': types.Schema(type='STRING'),
                          },
                      ),
                      'b_complex': types.Schema(
                          type='ARRAY',
                          items=types.Schema(
                              type='OBJECT',
                              properties={
                                  'a_simple': types.Schema(type='INTEGER'),
                                  'b_simple': types.Schema(type='STRING'),
                              },
                          ),
                      ),
                  },
              ),
          },
      ),
      description='test pydantic model.',
  )

  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.parameters.required = ['a', 'b']

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_pydantic_model_in_list_type():
  class MySimplePydanticModel(pydantic.BaseModel):
    a_simple: int
    b_simple: str

  def func_under_test(
      a: list[MySimplePydanticModel],
  ):
    """test pydantic model in list type."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='ARRAY',
                  items=types.Schema(
                      type='OBJECT',
                      properties={
                          'a_simple': types.Schema(type='INTEGER'),
                          'b_simple': types.Schema(type='STRING'),
                      },
                  ),
              ),
          },
      ),
      description='test pydantic model in list type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.parameters.required = ['a']

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_pydantic_model_in_union_type():
  class CatInformationObject(pydantic.BaseModel):
    name: str
    age: int
    like_purring: bool

  class DogInformationObject(pydantic.BaseModel):
    name: str
    age: int
    like_barking: bool

  def func_under_test(
      animal: typing.Union[CatInformationObject, DogInformationObject],
  ):
    """test pydantic model in union type."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'animal': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(
                          type='OBJECT',
                          properties={
                              'name': types.Schema(type='STRING'),
                              'age': types.Schema(type='INTEGER'),
                              'like_purring': types.Schema(type='BOOLEAN'),
                          },
                      ),
                      types.Schema(
                          type='OBJECT',
                          properties={
                              'name': types.Schema(type='STRING'),
                              'age': types.Schema(type='INTEGER'),
                              'like_barking': types.Schema(type='BOOLEAN'),
                          },
                      ),
                  ],
              ),
          },
          required=['animal'],
      ),
      description='test pydantic model in union type.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_pydantic_model_with_default_value():
  class MySimplePydanticModel(pydantic.BaseModel):
    a_simple: Optional[int]
    b_simple: Optional[str]

  mySimplePydanticModel = MySimplePydanticModel(a_simple=1, b_simple='a')

  def func_under_test(a: MySimplePydanticModel = mySimplePydanticModel):
    """test pydantic model with default value."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      description='test pydantic model with default value.',
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  default=MySimplePydanticModel(a_simple=1, b_simple='a'),
                  type='OBJECT',
                  properties={
                      'a_simple': types.Schema(
                          nullable=True,
                          type='INTEGER',
                      ),
                      'b_simple': types.Schema(
                          nullable=True,
                          type='STRING',
                      ),
                  },
              )
          },
          required=[],
      ),
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_custom_class():

  class MyClass:
    a: int
    b: str

    def __init__(self, a: int):
      self.a = a
      self.b = str(a)

  def func_under_test(a: MyClass):
    """test custom class."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(vertex_client, func_under_test)


def test_type_union():

  def func_under_test(
      a: typing.Union[int, str],
      b: typing.Union[list, dict],
      c: typing.Union[typing.List[typing.Union[int, float]], dict],
      d: list | dict,
  ):
    """test type union."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='INTEGER'),
                      types.Schema(type='STRING'),
                  ],
              ),
              'b': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
              ),
              'c': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(
                          type='ARRAY',
                          items=types.Schema(
                              type='OBJECT',
                              any_of=[
                                  types.Schema(type='INTEGER'),
                                  types.Schema(type='NUMBER'),
                              ],
                          ),
                      ),
                      types.Schema(
                          type='OBJECT',
                      ),
                  ],
              ),
              'd': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
              ),
          },
          required=['a', 'b', 'c', 'd'],
      ),
      description='test type union.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_type_union_with_default_value():

  def func_under_test(
      a: typing.Union[int, str] = 1,
      b: typing.Union[list, dict] = [1],
      c: typing.Union[typing.List[typing.Union[int, float]], dict] = {},
      d: list | dict = [1, 2, 3],
  ):
    """test type union with default value."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='INTEGER'),
                      types.Schema(type='STRING'),
                  ],
                  default=1,
              ),
              'b': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
                  default=[1],
              ),
              'c': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(
                          type='ARRAY',
                          items=types.Schema(
                              type='OBJECT',
                              any_of=[
                                  types.Schema(type='INTEGER'),
                                  types.Schema(type='NUMBER'),
                              ],
                          ),
                      ),
                      types.Schema(
                          type='OBJECT',
                      ),
                  ],
                  default={},
              ),
              'd': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
                  default=[1, 2, 3],
              ),
          },
          required=[],
      ),
      description='test type union with default value.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)

  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_type_union_with_default_value_not_compatible():

  def func_under_test1(
      a: typing.Union[typing.List[typing.Union[int, float]], dict] = 1,
  ):
    """test type union with default value not compatible."""
    pass

  def func_under_test2(
      a: list | dict = 1,
  ):
    """test type union with default value not compatible."""
    pass

  all_func_under_test = [func_under_test1, func_under_test2]

  for func_under_test in all_func_under_test:
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(mldev_client, func_under_test)
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(vertex_client, func_under_test)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_type_nullable():

  def func_under_test(
      a: int | float | None,
      b: typing.Union[list, None],
      c: typing.Union[list, dict, None],
      d: typing.Optional[int] = None,
  ):
    """test type nullable."""
    pass

  expected_schema_vertex = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='INTEGER'),
                      types.Schema(type='NUMBER'),
                  ],
                  nullable=True,
              ),
              'b': types.Schema(
                  type='ARRAY',
                  nullable=True,
              ),
              'c': types.Schema(
                  type='OBJECT',
                  any_of=[
                      types.Schema(type='ARRAY'),
                      types.Schema(type='OBJECT'),
                  ],
                  nullable=True,
              ),
              'd': types.Schema(
                  type='INTEGER',
                  nullable=True,
                  default=None,
              ),
          },
          required=[],
      ),
      description='test type nullable.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_function(mldev_client, func_under_test)
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_empty_function_with_return_type():
  def func_under_test() -> int:
    """test empty function with return type."""
    return 1

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      description='test empty function with return type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.response = types.Schema(type='INTEGER')

  acutal_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert acutal_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_simple_function_with_return_type():
  def func_under_test(a: int) -> str:
    """test return type."""
    return ''

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='INTEGER'),
          },
      ),
      description='test return type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.response = types.Schema(type='STRING')
  expected_schema_vertex.parameters.required = ['a']

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_builtin_union_return_type():

  def func_under_test() -> int | str | float | bool | list | dict | None:
    """test builtin union return type."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      description='test builtin union return type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.response = types.Schema(
      type='OBJECT',
      any_of=[
          types.Schema(type='INTEGER'),
          types.Schema(type='STRING'),
          types.Schema(type='NUMBER'),
          types.Schema(type='BOOLEAN'),
          types.Schema(type='ARRAY'),
          types.Schema(type='OBJECT'),
      ],
      nullable=True,
  )

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_typing_union_return_type():

  def func_under_test() -> (
      typing.Union[int, str, float, bool, list, dict, None]
  ):
    """test typing union return type."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      description='test typing union return type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.response = types.Schema(
      type='OBJECT',
      any_of=[
          types.Schema(type='INTEGER'),
          types.Schema(type='STRING'),
          types.Schema(type='NUMBER'),
          types.Schema(type='BOOLEAN'),
          types.Schema(type='ARRAY'),
          types.Schema(type='OBJECT'),
      ],
      nullable=True,
  )

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_return_type_optional():
  def func_under_test() -> typing.Optional[int]:
    """test return type optional."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      description='test return type optional.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.response = types.Schema(
      type='INTEGER',
      nullable=True,
  )

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_return_type_pydantic_model():
  class MySimplePydanticModel(pydantic.BaseModel):
    a_simple: int
    b_simple: str

  class MyComplexPydanticModel(pydantic.BaseModel):
    a_complex: MySimplePydanticModel
    b_complex: list[MySimplePydanticModel]

  def func_under_test() -> MyComplexPydanticModel:
    """test return type pydantic model."""
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name='func_under_test',
      description='test return type pydantic model.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.response = types.Schema(
      type='OBJECT',
      properties={
          'a_complex': types.Schema(
              type='OBJECT',
              properties={
                  'a_simple': types.Schema(type='INTEGER'),
                  'b_simple': types.Schema(type='STRING'),
              },
          ),
          'b_complex': types.Schema(
              type='ARRAY',
              items=types.Schema(
                  type='OBJECT',
                  properties={
                      'a_simple': types.Schema(type='INTEGER'),
                      'b_simple': types.Schema(type='STRING'),
                  },
              ),
          ),
      },
  )

  actual_schema_mldev = types.FunctionDeclaration.from_function(
      mldev_client, func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_function(
      vertex_client, func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_function_with_return_type_not_supported():
  def func_under_test1() -> set:
    pass

  def func_under_test2() -> frozenset[int]:
    pass

  def func_under_test3() -> typing.Set[int]:
    pass

  def func_under_test4() -> typing.FrozenSet[int]:
    pass

  def func_under_test5() -> typing.Collection[int]:
    pass

  def func_under_test6() -> typing.Iterable[int]:
    pass

  def func_under_test7() -> typing.Iterator[int]:
    pass

  def func_under_test8() -> typing.Container[int]:
    pass

  def func_under_test9() -> bytes:
    pass

  def func_under_test10() -> typing.OrderedDict[str, int]:
    pass

  def func_under_test11() -> typing.MutableMapping[str, int]:
    pass

  def func_under_test12() -> typing.MutableSequence[int]:
    pass

  def func_under_test13() -> typing.MutableSet[int]:
    pass

  def func_under_test14() -> typing.Counter[int]:
    pass

  class MyClass:
    a: int
    b: str

  def func_under_test15() -> MyClass:
    pass

  all_func_under_test = [
      func_under_test1,
      func_under_test2,
      func_under_test3,
      func_under_test4,
      func_under_test5,
      func_under_test6,
      func_under_test7,
      func_under_test8,
      func_under_test9,
      func_under_test10,
      func_under_test11,
      func_under_test12,
      func_under_test13,
      func_under_test14,
      func_under_test15,
  ]
  for i, func_under_test in enumerate(all_func_under_test):
    expected_schema_mldev = types.FunctionDeclaration(
        name=f'func_under_test{i+1}',
        description=None,
    )
    actual_schema_mldev = types.FunctionDeclaration.from_function(
        mldev_client, func_under_test
    )
    assert actual_schema_mldev == expected_schema_mldev
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_function(vertex_client, func_under_test)
