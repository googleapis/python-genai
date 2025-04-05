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


class SubPart(types.Part):
  pass


def test_factory_method_from_uri_part():

  my_part = SubPart.from_uri(
      file_uri='gs://generativeai-downloads/images/scones.jpg',
      mime_type='image/jpeg',
  )
  assert (
      my_part.file_data.file_uri
      == 'gs://generativeai-downloads/images/scones.jpg'
  )
  assert my_part.file_data.mime_type == 'image/jpeg'
  assert isinstance(my_part, SubPart)


def test_factory_method_from_text_part():
  my_part = SubPart.from_text(text='What is your name?')
  assert my_part.text == 'What is your name?'
  assert isinstance(my_part, SubPart)


def test_factory_method_from_bytes_part():
  my_part = SubPart.from_bytes(data=b'123', mime_type='text/plain')
  assert my_part.inline_data.data == b'123'
  assert my_part.inline_data.mime_type == 'text/plain'
  assert isinstance(my_part, SubPart)


def test_factory_method_from_function_call_part():
  my_part = SubPart.from_function_call(name='func', args={'arg': 'value'})
  assert my_part.function_call.name == 'func'
  assert my_part.function_call.args == {'arg': 'value'}
  assert isinstance(my_part, SubPart)


def test_factory_method_from_function_response_part():
  my_part = SubPart.from_function_response(
      name='func', response={'response': 'value'}
  )
  assert my_part.function_response.name == 'func'
  assert my_part.function_response.response == {'response': 'value'}
  assert isinstance(my_part, SubPart)


def test_factory_method_from_video_metadata_part():
  my_part = SubPart.from_video_metadata(start_offset='10s', end_offset='20s')
  assert my_part.video_metadata.end_offset == '20s'
  assert my_part.video_metadata.start_offset == '10s'
  assert isinstance(my_part, SubPart)


def test_factory_method_from_executable_code_part():
  my_part = SubPart.from_executable_code(
      code='print("hello")', language='PYTHON'
  )
  assert my_part.executable_code.code == 'print("hello")'
  assert my_part.executable_code.language == 'PYTHON'
  assert isinstance(my_part, SubPart)


def test_factory_method_from_code_execution_result_part():
  my_part = SubPart.from_code_execution_result(
      outcome='OUTCOME_OK', output='print("hello")'
  )
  assert my_part.code_execution_result.outcome == 'OUTCOME_OK'
  assert my_part.code_execution_result.output == 'print("hello")'
  assert isinstance(my_part, SubPart)


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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
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

  expected_schema = types.FunctionDeclaration(
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
          required=['a', 'b', 'c', 'd', 'e', 'f'],
      ),
      description='test built in primitives and compounds.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema


def test_default_value_not_compatible_built_in_type():
  def func_under_test(a: str, b: int = '1', c: list = []):
    """test default value not compatible built in type."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
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
      types.FunctionDeclaration.from_callable(
          client=mldev_client, callable=func_under_test
      )
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=vertex_client, callable=func_under_test
      )


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
def test_built_in_union_type():

  def func_under_test(
      a: int | str | float | bool,
      b: list | dict,
  ):
    """test built in union type."""
    pass

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_built_in_union_type_all_py_versions():

  def func_under_test(
      a: typing.Union[int, str, float, bool],
      b: typing.Union[list, dict],
  ):
    """test built in union type."""
    pass

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
def test_default_value_not_compatible_built_in_union_type():
  def func_under_test(
      a: int | str = 1.1,
  ):
    """test default value not compatible built in union type."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


def test_default_value_not_compatible_built_in_union_type_all_py_versions():
  def func_under_test(
      a: typing.Union[int, str] = 1.1,
  ):
    """test default value not compatible built in union type."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_default_value_built_in_union_type_all_py_versions():

  def func_under_test(
      a: typing.Union[int, str] = '1',
      b: typing.Union[list, dict] = [],
      c: typing.Union[list, dict] = {},
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_generic_alias_literal():

  def func_under_test(a: typing.Literal['a', 'b', 'c']):
    """test generic alias literal."""
    pass

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='STRING',
                  enum=['a', 'b', 'c'],
              ),
          },
          required=['a'],
      ),
      description='test generic alias literal.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema


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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_default_value_generic_alias_literal_not_compatible():
  def func_under_test(a: typing.Literal['1', '2', 3]):
    """test default value generic alias literal not compatible."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


def test_default_value_not_compatible_generic_alias_literal():
  def func_under_test(a: typing.Literal['a', 'b', 'c'] = 'd'):
    """test default value not compatible generic alias literal."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


def test_generic_alias_array():

  def func_under_test(
      a: typing.List[int],
  ):
    """test generic alias array."""
    pass

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(
                  type='ARRAY', items=types.Schema(type='INTEGER')
              ),
          },
          required=['a'],
      ),
      description='test generic alias array.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
def test_generic_alias_complex_array():

  def func_under_test(
      a: typing.List[int | str | float | bool],
      b: typing.List[list | dict],
  ):
    """test generic alias complex array."""
    pass

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_generic_alias_complex_array_all_py_versions():

  def func_under_test(
      a: typing.List[typing.Union[int, str, float, bool]],
      b: typing.List[typing.Union[list, dict]],
  ):
    """test generic alias complex array."""
    pass

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_generic_alias_complex_array_with_default_value_all_py_versions():

  def func_under_test(
      a: typing.List[typing.Union[int, str, float, bool]] = [
          1,
          'a',
          1.1,
          True,
      ],
      b: list[typing.Union[int, str, float, bool]] = [
          11,
          'aa',
          1.11,
          False,
      ],
      c: typing.List[typing.Union[typing.List[int], int]] = [[1], 2],
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
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
      types.FunctionDeclaration.from_callable(
          client=mldev_client, callable=func_under_test
      )
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=vertex_client, callable=func_under_test
      )


def test_generic_alias_complex_array_with_default_value_not_compatible_all_py_versions():

  def func_under_test1(
      a: typing.List[typing.Union[int, str, float, bool]] = [
          1,
          'a',
          1.1,
          True,
          [],
      ],
  ):
    """test generic alias complex array with default value not compatible."""
    pass

  def func_under_test2(
      a: list[typing.Union[int, str, float, bool]] = [1, 'a', 1.1, True, []],
  ):
    """test generic alias complex array with default value not compatible."""
    pass

  for func_under_test in [func_under_test1, func_under_test2]:
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=mldev_client, callable=func_under_test
      )
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=vertex_client, callable=func_under_test
      )


def test_generic_alias_object():

  def func_under_test(
      a: typing.Dict[str, int],
  ):
    """test generic alias object."""
    pass

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='OBJECT'),
          },
          required=['a']
      ),
      description='test generic alias object.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema


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
      types.FunctionDeclaration.from_callable(
          client=mldev_client, callable=func_under_test
      )
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=vertex_client, callable=func_under_test
      )


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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_generic_alias_object_with_default_value_not_compatible():
  def func_under_test(a: typing.Dict[str, int] = 'a'):
    """test generic alias object with default value not compatible."""
    pass

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


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

  expected_schema = types.FunctionDeclaration(
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
                  required=['a_simple', 'b_simple'],
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
                          required=['a_simple', 'b_simple'],
                      ),
                      'b_complex': types.Schema(
                          type='ARRAY',
                          items=types.Schema(
                              type='OBJECT',
                              properties={
                                  'a_simple': types.Schema(type='INTEGER'),
                                  'b_simple': types.Schema(type='STRING'),
                              },
                              required=['a_simple', 'b_simple'],
                          ),
                      ),
                  },
                  required=['a_complex', 'b_complex'],
              ),
          },
          required=['a', 'b'],
      ),
      description='test pydantic model.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema


def test_pydantic_model_in_list_type():
  class MySimplePydanticModel(pydantic.BaseModel):
    a_simple: int
    b_simple: str

  def func_under_test(
      a: list[MySimplePydanticModel],
  ):
    """test pydantic model in list type."""
    pass

  expected_schema = types.FunctionDeclaration(
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
                      required=['a_simple', 'b_simple'],
                  ),
              ),
          },
          required=['a'],
      ),
      description='test pydantic model in list type.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema


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

  expected_schema = types.FunctionDeclaration(
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
  expected_schema.parameters.properties['animal'].any_of[0].required = [
      'name',
      'age',
      'like_purring',
  ]
  expected_schema.parameters.properties['animal'].any_of[1].required = [
      'name',
      'age',
      'like_barking',
  ]

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_pydantic_model_with_default_value():
  class MySimplePydanticModel(pydantic.BaseModel):
    a_simple: typing.Optional[int] = 1
    b_simple: typing.Optional[str] = 'a'

  mySimplePydanticModel = MySimplePydanticModel()

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
                  default=mySimplePydanticModel,
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
                  required=[],
              )
          },
          required=[],
      ),
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
def test_type_union():

  def func_under_test(
      a: typing.Union[int, str],
      b: typing.Union[list, dict],
      c: typing.Union[typing.List[typing.Union[int, float]], dict],
      d: list | dict,
  ):
    """test type union."""
    pass

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_type_union_all_py_versions():

  def func_under_test(
      a: typing.Union[int, str],
      b: typing.Union[list, dict],
      c: typing.Union[typing.List[typing.Union[int, float]], dict],
  ):
    """test type union."""
    pass

  expected_schema = types.FunctionDeclaration(
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
          },
          required=['a', 'b', 'c'],
      ),
      description='test type union.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_type_optional_with_list():

  def func_under_test(
      a: str,
      b: typing.Optional[list[str]] = None,
  ):
    """test type optional with list."""
    pass

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='STRING'),
              'b': types.Schema(
                  nullable=True, type='ARRAY', items=types.Schema(type='STRING')
              ),
          },
          required=['a'],
      ),
      description='test type optional with list.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_type_union_with_default_value_all_py_versions():

  def func_under_test(
      a: typing.Union[int, str] = 1,
      b: typing.Union[list, dict] = [1],
      c: typing.Union[typing.List[typing.Union[int, float]], dict] = {},
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
          },
          required=[],
      ),
      description='test type union with default value.',
  )

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
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
      types.FunctionDeclaration.from_callable(
          client=mldev_client, callable=func_under_test
      )
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=vertex_client, callable=func_under_test
      )


def test_type_union_with_default_value_not_compatible_all_py_versions():

  def func_under_test1(
      a: typing.Union[typing.List[typing.Union[int, float]], dict] = 1,
  ):
    """test type union with default value not compatible."""
    pass

  def func_under_test2(
      a: typing.Union[list, dict] = 1,
  ):
    """test type union with default value not compatible."""
    pass

  all_func_under_test = [func_under_test1, func_under_test2]

  for func_under_test in all_func_under_test:
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=mldev_client, callable=func_under_test
      )
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=vertex_client, callable=func_under_test
      )


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

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_type_nullable_all_py_versions():

  def func_under_test(
      b: typing.Union[list, None],
      c: typing.Union[list, dict, None],
      d: typing.Optional[int] = None,
  ):
    """test type nullable."""
    pass

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
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
          required=['a'],
      ),
      description='test return type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema_mldev)
  expected_schema_vertex.response = types.Schema(type='STRING')

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_builtin_union_return_type_all_py_versions():

  def func_under_test() -> (
      typing.Union[int, str, float, bool, list, dict, None]
  ):
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
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

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
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
              required=['a_simple', 'b_simple'],
          ),
          'b_complex': types.Schema(
              type='ARRAY',
              items=types.Schema(
                  type='OBJECT',
                  properties={
                      'a_simple': types.Schema(type='INTEGER'),
                      'b_simple': types.Schema(type='STRING'),
                  },
                  required=['a_simple', 'b_simple'],
              ),
          ),
      },
      required=['a_complex', 'b_complex'],
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
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
    actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
    assert actual_schema_mldev == expected_schema_mldev
    with pytest.raises(ValueError):
      types.FunctionDeclaration.from_callable(
          client=vertex_client, callable=func_under_test
      )


def test_function_with_options_gemini_api(monkeypatch):
  api_key = 'google_api_key'
  monkeypatch.setenv('GOOGLE_API_KEY', api_key)

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
          required=['a'],
      ),
      description='test return type.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev


def test_function_gemini_api(monkeypatch):
  api_key = 'google_api_key'
  monkeypatch.setenv('GOOGLE_API_KEY', api_key)

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
          required=['a'],
      ),
      description='test return type.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev


def test_function_with_option_gemini_api(monkeypatch):

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
          required=['a'],
      ),
      description='test return type.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable_with_api_option(
      callable=func_under_test, api_option='GEMINI_API'
  )

  assert actual_schema_mldev == expected_schema_mldev


def test_function_with_option_unset(monkeypatch):

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
          required=['a'],
      ),
      description='test return type.',
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable_with_api_option(
      callable=func_under_test
  )

  assert actual_schema_mldev == expected_schema_mldev


def test_function_with_option_unsupported_api_option():

  def func_under_test(a: int) -> str:
    """test return type."""
    return ''

  with pytest.raises(ValueError):
    types.FunctionDeclaration.from_callable_with_api_option(
        callable=func_under_test, api_option='UNSUPPORTED_API_OPTION'
    )


def test_function_vertex():

  def func_under_test(a: int) -> str:
    """test return type."""
    return ''

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='INTEGER'),
          },
      ),
      description='test return type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema)
  expected_schema_vertex.response = types.Schema(type='STRING')
  expected_schema_vertex.parameters.required = ['a']

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_function_with_option_vertex(monkeypatch):

  def func_under_test(a: int) -> str:
    """test return type."""
    return ''

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters=types.Schema(
          type='OBJECT',
          properties={
              'a': types.Schema(type='INTEGER'),
          },
      ),
      description='test return type.',
  )
  expected_schema_vertex = copy.deepcopy(expected_schema)
  expected_schema_vertex.response = types.Schema(type='STRING')
  expected_schema_vertex.parameters.required = ['a']

  actual_schema_vertex = (
      types.FunctionDeclaration.from_callable_with_api_option(
          callable=func_under_test, api_option='VERTEX_AI'
      )
  )

  assert actual_schema_vertex == expected_schema_vertex


def test_case_insensitive_enum():
  """Tests that Type enum handles case insensitivity."""
  assert types.Type('STRING') == types.Type.STRING
  assert types.Type('string') == types.Type.STRING
  assert types.Type('NuLl') == types.Type.NULL


def test_case_insensitive_enum_with_pydantic_model():
  class TestModel(pydantic.BaseModel):
    test_enum: types.Type

  assert TestModel(test_enum='STRING').test_enum == types.Type.STRING
  assert TestModel(test_enum='string').test_enum == types.Type.STRING


def test_unknown_enum_value():
  """Tests behavior with invalid type values."""
  with pytest.warns(Warning, match='is not a valid'):
    enum_instance = types.Type('float')
    assert enum_instance.name == 'float'
    assert enum_instance.value == 'float'

  with pytest.raises(ValueError):
    types.Type('invalid type')

def test_enum_with_complex_type():
  """Tests enum with non-string values."""
  schema = types.Schema(
    type='OBJECT',
    properties={
      'status': {
        'type': 'INTEGER',
        'enum': [1, 2, 3]
      }
    }
  )
  assert schema.properties['status'].enum == [1, 2, 3]

def test_unknown_enum_value_in_nested_dict():
  schema = types.SafetyRating._from_response(
      response={'category': 'NEW_CATEGORY'}, kwargs=None
  )
  assert schema.category.name == 'NEW_CATEGORY'
  assert schema.category.value == 'NEW_CATEGORY'

def test_nested_property_conversion():
  schema = types.Schema(
    type='OBJECT',
    properties={
      'user': {
        'type': 'OBJECT',
        'properties': {
          'age': {'type': 'INTEGER', 'nullable': True}
        }
      }
    }
  )
  assert schema.properties['user'].properties['age'].type == ['integer', 'null']

def test_array_conversion():
  schema = types.Schema(
    type='ARRAY',
    items={
      'type': 'INTEGER',
      'format': 'int32'
    }
  )
  assert schema.items.type == 'integer'
  assert schema.items.format == 'int32'

def test_nullable_conversion():
  """Tests nullable field conversion to type array."""
  schema = types.Schema(type='STRING', nullable=True)
  assert schema.type == ['string', 'null']

def test_int_conversion():
  """Tests int32/int64 format conversion to min/max."""
  schema = types.Schema(type='INTEGER', format='int32')
  assert schema.minimum == -2147483648
  assert schema.maximum == 2147483647
  assert schema.type == 'integer'
  assert 'format' not in schema.model_dump()

def test_anyof_with_nullable():
  schema = types.Schema(
    anyOf=[{
      'type': 'STRING',
      'nullable': True
    }]
  )
  assert {'type': 'null'} in schema.anyOf
  assert {'type': 'string'} in schema.anyOf

def test_nested_anyof_allof():
  """Tests nested anyOf/allOf with multiple levels."""
  schema = types.Schema(
    anyOf=[
      {
        "allOf": [
                  {"type": "STRING", "maxLength": 10},
                  {"type": "STRING", "minLength": 5}
        ]
      },
      {
        "type": "INTEGER",
        "minimum": 1,
        "maximum": 100
      }
    ]
  )
  assert len(schema.anyOf) == 2
  assert len(schema.anyOf[0].allOf) == 2

def test_nested_combiners():
  schema = types.Schema(
    allOf=[
      {
        'anyOf': [
          {
            'type': 'INTEGER',
            'format': 'int32'
          },
          {
            'type': 'INTEGER',
            'format': 'int64' 
          }
        ]
      },
      {
        'type': 'STRING',
        'nullable': True
      }
    ]
  )
  assert schema.allOf[0].anyOf[0].minimum == -2147483648
  assert schema.allOf[0].anyOf[1].minimum == -9223372036854775808
  assert schema.allOf[0].anyOf[0].maximum == 2147483647
  assert schema.allOf[0].anyOf[1].maximum == 9223372036854775807
  assert schema.allOf[1].type == 'string'
  assert schema.allOf[1].nullable

def test_recursive_schema_definition():
  """Tests recursive schema references itself."""
  schema = types.Schema({
    "type": 'OBJECT',
    "properties": {
      "name": {
        "type": "STRING"
      },
      "children": {
        "type": "ARRAY",
        "items": {
          "$ref": "#" # Referencing the same schema
        }
      }
    }
  })
  
  with pytest.raises(ValueError):
    types.Schema(**schema)


def test_invalid_types():
  with pytest.raises(ValueError, match='Invalid type value'):
    types.Schema(type=['INVALID_TYPE'])
  with pytest.raises(ValueError, match='Invalid type value'):
    types.Schema(type=['string', 'null', 'INVALID_TYPE'])

def test_empty_type_array():
  with pytest.raises(ValueError, match='type array cannot be empty'):
    types.Schema(type=[])

def test_invalid_type_combinations():
  with pytest.raises(ValueError, match='May only combine with one other type'):
    types.Schema(type=['INTEGER', 'NULL', 'STRING'])

def test_legacy_type_unspecified():
  """Tests TYPE_UNSPECIFIED conversion."""
  with pytest.warns(Warning, match='Legacy type unspecified'):
    schema = types.Schema(type='TYPE_UNSPECIFIED')
    assert schema.type is None

def test_legacy_type_unspecified_with_pydantic():
  with pytest.warns(Warning, match='Legacy type unspecified'):
    class MyModel(pydantic.BaseModel):
      config: types.GenerationConfigDict

    model = MyModel(config=types.GenerationConfigDict(type='TYPE_UNSPECIFIED'))
    assert model.config.type is None

def test_uppercase_property_names():
  """Tests normalization of uppercase property names."""
  schema = types.Schema(
    PROPERTIES={
      'NAME': {
        'type': 'STRING'
      }
    }
  )
  assert 'properties' in schema.model_dump()
  assert 'name' in schema.properties
  assert schema.properties['name'].type == 'string'

def test_full_schema_conversion():
  """Tests complete schema conversion from legacy(OPENAPI) to modern(JSON Schema) format."""
  legacy_schema = {
    'type': 'OBJECT',
    'properties': {
      'user': {
        'type': 'OBJECT',
        'properties': {
          'name': {'type': 'STRING'},
          'age': {'type': 'INTEGER', 'format': 'int32'}
        }
      }
    }
  }

  schema = types.Schema(**legacy_schema)
  assert schema.type == 'object'
  assert schema.properties['user'].type == 'object'
  assert schema.properties['user'].properties['name'].type == 'string'
  assert schema.properties['user'].properties['age'].type == 'integer'
  assert schema.properties['user'].properties['age'].format == 'int32'
  assert schema.properties['user'].properties['age'].minimum == -2147483648
  assert schema.properties['user'].properties['age'].maximum == 2147483647
  
def test_function_with_converted_schema():
  """Tests function declaration with converted schema types."""
  def sample_function(a: int, b: str=None) -> bool:
    return True
  
  expected_schema = types.FunctionDeclaration(
    name='sample_function',
    properties={
      'a': types.Schema(type='integer'),
      'b': types.Schema(type=['string', 'null'])
    },
    required=['a'],
    
    return_type=types.Schema(type='boolean'),
    description='Sample function to test schema conversion'
  )
  
  actual_schema = types.FunctionDeclaration.from_callable(sample_function)
  assert actual_schema.model_dump_json(exclude_none=True) == expected_schema.model_dump_json(exclude_none=True)

def test_typed_dict_pydantic_field():
  from pydantic import BaseModel

  class MyConfig(BaseModel):
    config: types.GenerationConfigDict


def test_model_content_list_part_from_uri():
  expected_model_content = types.Content(
      role='model',
      parts=[
          types.Part(text='what is this image about?'),
          types.Part(
              file_data=types.FileData(
                  file_uri='gs://generativeai-downloads/images/scones.jpg',
                  mime_type='image/jpeg',
              )
          ),
      ],
  )

  actual_model_content = types.ModelContent(
      parts=[
          'what is this image about?',
          types.Part.from_uri(
              file_uri='gs://generativeai-downloads/images/scones.jpg',
              mime_type='image/jpeg',
          ),
      ]
  )

  assert expected_model_content.model_dump_json(
      exclude_none=True
  ) == actual_model_content.model_dump_json(exclude_none=True)


def test_model_content_part_from_uri():
  expected_model_content = types.Content(
      role='model',
      parts=[
          types.Part(
              file_data=types.FileData(
                  file_uri='gs://generativeai-downloads/images/scones.jpg',
                  mime_type='image/jpeg',
              )
          )
      ],
  )

  actual_model_content = types.ModelContent(
      parts=types.Part.from_uri(
          file_uri='gs://generativeai-downloads/images/scones.jpg',
          mime_type='image/jpeg',
      )
  )

  assert expected_model_content.model_dump_json(
      exclude_none=True
  ) == actual_model_content.model_dump_json(exclude_none=True)


def test_model_content_from_string():
  expected_model_content = types.Content(
      role='model',
      parts=[types.Part(text='why is the sky blue?')],
  )

  actual_model_content = types.ModelContent('why is the sky blue?')

  assert expected_model_content.model_dump_json(
      exclude_none=True
  ) == actual_model_content.model_dump_json(exclude_none=True)


def test_model_content_unsupported_type():
  with pytest.raises(ValueError):
    types.ModelContent(123)


def test_model_content_empty_list():
  with pytest.raises(ValueError):
    types.ModelContent([])


def test_model_content_unsupported_type_in_list():
  with pytest.raises(ValueError):
    types.ModelContent(['hi', 123])


def test_model_content_unsupported_role():
  with pytest.raises(TypeError):
    types.ModelContent(role='user', parts=['hi'])


def test_model_content_modify_role():
  model_content = types.ModelContent(['hi'])
  with pytest.raises(pydantic.ValidationError):
    model_content.role = 'user'


def test_model_content_modify_parts():
  expected_model_content = types.Content(
      role='model',
      parts=[types.Part(text='hello')],
  )
  model_content = types.ModelContent(['hi'])
  model_content.parts = [types.Part(text='hello')]

  assert expected_model_content.model_dump_json(
      exclude_none=True
  ) == model_content.model_dump_json(exclude_none=True)


def test_user_content_unsupported_type():
  with pytest.raises(ValueError):
    types.UserContent(123)


def test_user_content_modify_role():
  user_content = types.UserContent(['hi'])
  with pytest.raises(pydantic.ValidationError):
    user_content.role = 'model'


def test_user_content_modify_parts():
  expected_user_content = types.Content(
      role='user',
      parts=[types.Part(text='hello')],
  )
  user_content = types.UserContent(['hi'])
  user_content.parts = [types.Part(text='hello')]

  assert expected_user_content.model_dump_json(
      exclude_none=True
  ) == user_content.model_dump_json(exclude_none=True)


def test_user_content_empty_list():
  with pytest.raises(ValueError):
    types.UserContent([])


def test_user_content_unsupported_type_in_list():
  with pytest.raises(ValueError):
    types.UserContent(['hi', 123])


def test_user_content_unsupported_role():
  with pytest.raises(TypeError):
    types.UserContent(role='model', parts=['hi'])
