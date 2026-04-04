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


import copy
import json
import sys
import typing
from typing import Optional, assert_never
import PIL.Image
import pydantic
import pytest
from ... import types

_is_mcp_imported = False
if typing.TYPE_CHECKING:
  from mcp import types as mcp_types

  _is_mcp_imported = True
else:
  try:
    from mcp import types as mcp_types

    _is_mcp_imported = True
  except ImportError:
    mcp_types = None


class SubPart(types.Part):
  pass


class SubFunctionResponsePart(types.FunctionResponsePart):
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


def test_factory_method_from_uri_inferred_mime_type_part():

  my_part = SubPart.from_uri(
      file_uri='gs://generativeai-downloads/images/scones.jpg',
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


def test_factory_method_part_from_function_response_with_multi_modal_parts():
  my_part = SubPart.from_function_response(
      name='func',
      response={'response': 'value'},
      parts=[{'inline_data': {'data': b'123', 'mime_type': 'image/png'}}],
  )
  assert my_part.function_response.name == 'func'
  assert my_part.function_response.response == {'response': 'value'}
  assert my_part.function_response.parts[0].inline_data.data == b'123'
  assert my_part.function_response.parts[0].inline_data.mime_type == 'image/png'
  assert isinstance(my_part, SubPart)


def test_factory_method_function_response_part_from_bytes():
  my_part = SubFunctionResponsePart.from_bytes(
      data=b'123', mime_type='image/png'
  )
  assert my_part.inline_data.data == b'123'
  assert my_part.inline_data.mime_type == 'image/png'
  assert isinstance(my_part, SubFunctionResponsePart)


def test_factory_method_function_response_part_from_uri():
  my_part = SubFunctionResponsePart.from_uri(
      file_uri='gs://generativeai-downloads/images/scones.jpg',
      mime_type='image/jpeg',
  )
  assert (
      my_part.file_data.file_uri
      == 'gs://generativeai-downloads/images/scones.jpg'
  )
  assert my_part.file_data.mime_type == 'image/jpeg'
  assert isinstance(my_part, SubFunctionResponsePart)


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


def test_factory_method_from_mcp_call_tool_function_response_on_error():
  if not _is_mcp_imported:
    return

  call_tool_result = mcp_types.CallToolResult(
      content=[],
      isError=True,
  )
  my_function_response = types.FunctionResponse.from_mcp_response(
      name='func_name', response=call_tool_result
  )
  assert my_function_response.name == 'func_name'
  assert my_function_response.response == {'error': 'MCP response is error.'}
  assert isinstance(my_function_response, types.FunctionResponse)


def test_factory_method_from_mcp_call_tool_function_response_text():
  if not _is_mcp_imported:
    return

  call_tool_result = mcp_types.CallToolResult(
      content=[
          mcp_types.TextContent(type='text', text='hello'),
          mcp_types.TextContent(type='text', text=' world'),
      ],
  )
  my_function_response = types.FunctionResponse.from_mcp_response(
      name='func_name', response=call_tool_result
  )
  assert my_function_response.name == 'func_name'
  assert my_function_response.response == {
      'result': [
          mcp_types.TextContent(type='text', text='hello'),
          mcp_types.TextContent(type='text', text=' world'),
      ]
  }
  assert isinstance(my_function_response, types.FunctionResponse)


def test_factory_method_from_mcp_call_tool_function_response_inline_data():
  if not _is_mcp_imported:
    return

  call_tool_result = mcp_types.CallToolResult(
      content=[
          mcp_types.ImageContent(
              type='image',
              data='MTIz',
              mimeType='text/plain',
          ),
          mcp_types.ImageContent(
              type='image',
              data='NDU2',
              mimeType='text/plain',
          ),
      ],
  )
  my_function_response = types.FunctionResponse.from_mcp_response(
      name='func_name', response=call_tool_result
  )
  assert my_function_response.name == 'func_name'
  assert my_function_response.response == {
      'result': [
          mcp_types.ImageContent(
              type='image',
              data='MTIz',
              mimeType='text/plain',
          ),
          mcp_types.ImageContent(
              type='image',
              data='NDU2',
              mimeType='text/plain',
          ),
      ]
  }
  assert isinstance(my_function_response, types.FunctionResponse)


def test_factory_method_from_mcp_call_tool_function_response_combined_content():
  if not _is_mcp_imported:
    return

  call_tool_result = mcp_types.CallToolResult(
      content=[
          mcp_types.TextContent(
              type='text',
              text='Hello',
          ),
          mcp_types.ImageContent(
              type='image',
              data='NDU2',
              mimeType='text/plain',
          ),
      ],
  )
  my_function_response = types.FunctionResponse.from_mcp_response(
      name='func_name', response=call_tool_result
  )
  assert my_function_response.name == 'func_name'
  assert my_function_response.response == {
      'result': [
          mcp_types.TextContent(
              type='text',
              text='Hello',
          ),
          mcp_types.ImageContent(
              type='image',
              data='NDU2',
              mimeType='text/plain',
          ),
      ]
  }
  assert isinstance(my_function_response, types.FunctionResponse)


def test_factory_method_from_mcp_call_tool_function_response_embedded_resource():
  if not _is_mcp_imported:
    return

  call_tool_result = mcp_types.CallToolResult(
      content=[
          mcp_types.EmbeddedResource(
              type='resource',
              resource=mcp_types.TextResourceContents(
                  uri='https://generativelanguage.googleapis.com/v1beta/files/ansa0kyotrsw',
                  text='hello',
              ),
          ),
      ],
  )
  my_function_response = types.FunctionResponse.from_mcp_response(
      name='func_name', response=call_tool_result
  )
  assert my_function_response.name == 'func_name'
  assert my_function_response.response == {
      'result': [
          mcp_types.EmbeddedResource(
              type='resource',
              resource=mcp_types.TextResourceContents(
                  uri='https://generativelanguage.googleapis.com/v1beta/files/ansa0kyotrsw',
                  text='hello',
              ),
          ),
      ]
  }
  assert isinstance(my_function_response, types.FunctionResponse)


def test_part_constructor_with_string_value():
  part = types.Part('hello')
  assert part.text == 'hello'
  assert part.file_data is None
  assert part.inline_data is None


def test_part_constructor_with_part_value():
  other_part = types.Part(text='hello from other part')
  part = types.Part(other_part)
  assert part.text == 'hello from other part'


def test_part_constructor_with_part_dict_value():
  part = types.Part({'text': 'hello from dict'})
  assert part.text == 'hello from dict'


def test_part_constructor_with_file_data_dict_value():
  part = types.Part(
      {'file_uri': 'gs://my-bucket/file-data', 'mime_type': 'text/plain'}
  )
  assert part.file_data.file_uri == 'gs://my-bucket/file-data'
  assert part.file_data.mime_type == 'text/plain'


def test_part_constructor_with_kwargs_and_value_fails():
  with pytest.raises(
      ValueError, match='Positional and keyword arguments can not be combined'
  ):
    types.Part('hello', text='world')


def test_part_constructor_with_file_value():
  f = types.File(
      uri='gs://my-bucket/my-file',
      mime_type='text/plain',
      display_name='test file',
  )
  part = types.Part(f)
  assert part.file_data.file_uri == 'gs://my-bucket/my-file'
  assert part.file_data.mime_type == 'text/plain'
  assert part.file_data.display_name == 'test file'


def test_part_constructor_with_pil_image():
  img = PIL.Image.new('RGB', (1, 1), color='red')
  part = types.Part(img)
  assert part.inline_data.mime_type == 'image/jpeg'
  assert isinstance(part.inline_data.data, bytes)


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


def test_default_value_built_in_type():
  def func_under_test(a: str, b: int = '1', c: list = []):
    """test default value not compatible built in type."""
    pass

  types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )


def test_default_value_built_in_type():
  def func_under_test(a: str, b: int = 1, c: list = []):
    """test default value."""
    pass

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
def test_built_in_primitives_compounds():
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
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
def test_default_value_built_in_union_type():
  def func_under_test(
      a: int | str = 1.1,
  ):
    """test default value not compatible built in union type."""
    pass

  types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )


def test_default_value_built_in_union_type_all_py_versions():
  def func_under_test(
      a: typing.Union[int, str] = 1.1,
  ):
    """test default value not compatible built in union type."""
    pass

  types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_default_value_built_in_union_type_all_py_versions():

  def func_under_test(
      a: typing.Union[int, str] = '1',
      b: typing.Union[list, dict] = [],
      c: typing.Union[list, dict] = {},
  ):
    """test default value built in union type."""
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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


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

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_default_value_generic_alias_literal():
  def func_under_test(a: typing.Literal['1', '2', 3]):
    """test default value generic alias literal not compatible."""
    pass

  types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )


def test_default_value_generic_alias_literal_with_str_default():
  def func_under_test(a: typing.Literal['a', 'b', 'c'] = 'd'):
    """test default value not compatible generic alias literal."""
    pass

  types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
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
          required=['a'],
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


def test_supported_uncommon_generic_alias_object():
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

  def func_under_test6(a: typing.Iterable[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test7(a: typing.DefaultDict[int, int]):
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
  ]

  for func_under_test in all_func_under_test:
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


def test_unsupported_uncommon_generic_alias_object():

  def func_under_test1(a: typing.Collection[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test2(a: typing.Iterator[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test3(a: typing.Container[int]):
    """test uncommon generic alias object."""
    pass

  def func_under_test4(a: typing.ChainMap[int, int]):
    """test uncommon generic alias object."""
    pass

  all_func_under_test = [
      func_under_test1,
      func_under_test2,
      func_under_test3,
      func_under_test4,
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

  expected_schema = types.FunctionDeclaration(
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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_generic_alias_object_with_default_value_not_compatible():
  def func_under_test(a: typing.Dict[str, int] = 'a'):
    """test generic alias object with default value not compatible."""
    pass

  types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
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
    a_simple: Optional[int]
    b_simple: Optional[str]

  mySimplePydanticModel = MySimplePydanticModel(a_simple=1, b_simple='a')

  def func_under_test(a: MySimplePydanticModel = mySimplePydanticModel):
    """test pydantic model with default value."""
    pass

  expected_schema = types.FunctionDeclaration(
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
                  required=[],
              )
          },
          required=[],
      ),
  )

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


def test_type_union_with_default_value_all_py_versions():

  def func_under_test(
      a: typing.Union[int, str] = 1,
      b: typing.Union[list, dict] = [1],
      c: typing.Union[typing.List[typing.Union[int, float]], dict] = {},
  ):
    """test type union with default value."""
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

  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  assert actual_schema_vertex == expected_schema
  assert actual_schema_mldev == expected_schema


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
def test_type_union_with_default_value():

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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
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
    types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
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
  expected_schema_vertex.response_json_schema = types.Schema(
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
  expected_schema_vertex.response_json_schema = types.Schema(
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
  expected_schema_vertex.response_json_schema = types.Schema(
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


def test_function_with_return_type():
  def func_under_test1() -> set:
    pass

  def func_under_test2() -> frozenset[int]:
    pass

  def func_under_test3() -> typing.Set[int]:
    pass

  def func_under_test4() -> typing.FrozenSet[int]:
    pass

  def func_under_test5() -> typing.Iterable[int]:
    pass

  def func_under_test6() -> bytes:
    pass

  def func_under_test7() -> typing.OrderedDict[str, int]:
    pass

  def func_under_test8() -> typing.MutableMapping[str, int]:
    pass

  def func_under_test9() -> typing.MutableSequence[int]:
    pass

  def func_under_test10() -> typing.MutableSet[int]:
    pass

  def func_under_test11() -> typing.Counter[int]:
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
  for i, func_under_test in enumerate(all_func_under_test):

    expected_schema_mldev = types.FunctionDeclaration(
        name=f'func_under_test{i+1}',
        description=None,
    )
    actual_schema_mldev = types.FunctionDeclaration.from_callable(
        client=mldev_client, callable=func_under_test
    )
    assert actual_schema_mldev == expected_schema_mldev

    types.FunctionDeclaration.from_callable(
        client=vertex_client, callable=func_under_test
    )


def test_function_with_tuple_return_type():
  def func_under_test() -> tuple[int, str, str]:
    pass

  expected_schema_mldev = types.FunctionDeclaration(
      name=f'func_under_test',
      description=None,
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )

  expected_schema_vertex = types.FunctionDeclaration(
      name=f'func_under_test',
      description=None,
      response_json_schema={
          'maxItems': 3,
          'minItems': 3,
          'prefixItems': [
              {'type': 'integer'},
              {'type': 'string'},
              {'type': 'string'},
          ],
          'type': 'array',
          'unevaluatedItems': False,
      },
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  assert actual_schema_mldev == expected_schema_mldev
  assert actual_schema_vertex == expected_schema_vertex


def test_function_with_return_type_not_supported():
  def func_under_test1() -> typing.Collection[int]:
    pass

  def func_under_test2() -> typing.Iterator[int]:
    pass

  def func_under_test3() -> typing.Container[int]:
    pass

  class MyClass:
    a: int
    b: str

  def func_under_test4() -> MyClass:
    pass

  all_func_under_test = [
      func_under_test1,
      func_under_test2,
      func_under_test3,
      func_under_test4,
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

def test_function_with_tuple_contains_unevaluated_items():
  def func_under_test(a: tuple[int, int]) -> str:
    """test return type."""
    return ''

  expected_parameters_json_schema = {
      'a': {
          'maxItems': 2,
          'minItems': 2,
          'prefixItems': [{'type': 'integer'}, {'type': 'integer'}],
          'type': 'array',
          'unevaluatedItems': False,
      }
  }

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )

  assert actual_schema_mldev.parameters_json_schema == expected_parameters_json_schema
  assert actual_schema_vertex.parameters_json_schema == expected_parameters_json_schema


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
  assert types.Type('STRING') == types.Type.STRING
  assert types.Type('string') == types.Type.STRING


def test_case_insensitive_enum_with_pydantic_model():
  class TestModel(pydantic.BaseModel):
    test_enum: types.Type

  assert TestModel(test_enum='STRING').test_enum == types.Type.STRING
  assert TestModel(test_enum='string').test_enum == types.Type.STRING


def test_unknown_enum_value():
  with pytest.warns(Warning, match='is not a valid'):
    enum_instance = types.Type('float')
    assert enum_instance.name == 'float'
    assert enum_instance.value == 'float'


def test_unknown_enum_value_in_nested_dict():
  schema = types.SafetyRating._from_response(
      response={'category': 'NEW_CATEGORY'}, kwargs=None
  )
  assert schema.category.name == 'NEW_CATEGORY'
  assert schema.category.value == 'NEW_CATEGORY'


# Tests that TypedDict types from types.py are compatible with pydantic
# pydantic requires TypedDict from typing_extensions for Python <3.12
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


def test_instantiate_response_from_batch_json():
  test_batch_json = json.dumps({
      'candidates': [{
          'citationMetadata': {
              'citationSources': [{
                  'endIndex': 2009,
                  'startIndex': 1880,
                  'uri': 'http://someurl.com',
              }]
          },
          'content': {
              'parts': [{
                  'text': (
                      'This recipe makes a moist and delicious banana bread!'
                  )
              }],
              'role': 'model',
          },
          'finishReason': 'STOP',
      }],
      'modelVersion': 'gemini-1.5-flash-002@default',
  })
  parsed = types.GenerateContentResponse.model_validate_json(test_batch_json)
  assert isinstance(parsed, types.GenerateContentResponse)
  assert isinstance(parsed.candidates[0].citation_metadata, types.CitationMetadata)
  assert isinstance(
      parsed.candidates[0].citation_metadata.citations[0], types.Citation
  )
  assert(
      parsed.candidates[0].citation_metadata.citations[0].uri
      == 'http://someurl.com'
  )
