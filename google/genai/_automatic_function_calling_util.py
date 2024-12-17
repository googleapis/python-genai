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

import inspect
import types as typing_types
from typing import Any, Callable, Literal, Union, _GenericAlias, get_args, get_origin
import pydantic
from . import types

_py_builtin_type_to_schema_type = {
    str: 'STRING',
    int: 'INTEGER',
    float: 'NUMBER',
    bool: 'BOOLEAN',
    list: 'ARRAY',
    dict: 'OBJECT',
}


def _is_builtin_primitive_or_compound(
    annotation: inspect.Parameter.annotation,
) -> bool:
  return annotation in _py_builtin_type_to_schema_type.keys()


def _raise_for_any_of_if_mldev(schema: types.Schema):
  if schema.any_of:
    raise ValueError(
        'AnyOf is not supported in function declaration schema for Google AI.'
    )


def _raise_for_default_if_mldev(schema: types.Schema):
  if schema.default is not None:
    raise ValueError(
        'Default value is not supported in function declaration schema for'
        ' Google AI.'
    )


def _raise_for_nullable_if_mldev(schema: types.Schema):
  if schema.nullable:
    raise ValueError(
        'Nullable is not supported in function declaration schema for'
        ' Google AI.'
    )


def _raise_if_schema_unsupported(client, schema: types.Schema):
  if not client.vertexai:
    _raise_for_any_of_if_mldev(schema)
    _raise_for_default_if_mldev(schema)
    _raise_for_nullable_if_mldev(schema)


def _is_default_value_compatible(
    default_value: Any, annotation: inspect.Parameter.annotation
) -> bool:
  # None type is expected to be handled external to this function
  if _is_builtin_primitive_or_compound(annotation):
    return isinstance(default_value, annotation)

  if (
      isinstance(annotation, _GenericAlias)
      or isinstance(annotation, typing_types.GenericAlias)
      or isinstance(annotation, typing_types.UnionType)
  ):
    origin = get_origin(annotation)
    if origin in (Union, typing_types.UnionType):
      return any(
          _is_default_value_compatible(default_value, arg)
          for arg in get_args(annotation)
      )

    if origin is dict:
      return isinstance(default_value, dict)

    if origin is list:
      if not isinstance(default_value, list):
        return False
      # most tricky case, element in list is union type
      # need to apply any logic within all
      # see test case test_generic_alias_complex_array_with_default_value
      # a: typing.List[int | str | float | bool]
      # default_value: [1, 'a', 1.1, True]
      return all(
          any(
              _is_default_value_compatible(item, arg)
              for arg in get_args(annotation)
          )
          for item in default_value
      )

    if origin is Literal:
      return default_value in get_args(annotation)

  # return False for any other unrecognized annotation
  # let caller handle the raise
  return False


def _parse_schema_from_parameter(
    client, param: inspect.Parameter, func_name: str
) -> types.Schema:
  """parse schema from parameter.

  from the simplest case to the most complex case.
  """
  schema = types.Schema()
  default_value_error_msg = (
      f'Default value {param.default} of parameter {param} of function'
      f' {func_name} is not compatible with the parameter annotation'
      f' {param.annotation}.'
  )
  if _is_builtin_primitive_or_compound(param.annotation):
    if param.default is not inspect.Parameter.empty:
      if not _is_default_value_compatible(param.default, param.annotation):
        raise ValueError(default_value_error_msg)
      schema.default = param.default
    schema.type = _py_builtin_type_to_schema_type[param.annotation]
    _raise_if_schema_unsupported(client, schema)
    return schema
  if (
      isinstance(param.annotation, typing_types.UnionType)
      # only parse simple UnionType, example int | str | float | bool
      # complex types.UnionType will be invoked in raise branch
      and all(
          (_is_builtin_primitive_or_compound(arg) or arg is type(None))
          for arg in get_args(param.annotation)
      )
  ):
    schema.type = 'OBJECT'
    schema.any_of = []
    unique_types = set()
    for arg in get_args(param.annotation):
      if arg.__name__ == 'NoneType':  # Optional type
        schema.nullable = True
        continue
      schema_in_any_of = _parse_schema_from_parameter(
          client,
          inspect.Parameter(
              'item', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=arg
          ),
          func_name,
      )
      if (
          schema_in_any_of.model_dump_json(exclude_none=True)
          not in unique_types
      ):
        schema.any_of.append(schema_in_any_of)
        unique_types.add(schema_in_any_of.model_dump_json(exclude_none=True))
    if len(schema.any_of) == 1:  # param: list | None -> Array
      schema.type = schema.any_of[0].type
      schema.any_of = None
    if (
        param.default is not inspect.Parameter.empty
        and param.default is not None
    ):
      if not _is_default_value_compatible(param.default, param.annotation):
        raise ValueError(default_value_error_msg)
      schema.default = param.default
    _raise_if_schema_unsupported(client, schema)
    return schema
  if isinstance(param.annotation, _GenericAlias) or isinstance(
      param.annotation, typing_types.GenericAlias
  ):
    origin = get_origin(param.annotation)
    args = get_args(param.annotation)
    if origin is dict:
      schema.type = 'OBJECT'
      if param.default is not inspect.Parameter.empty:
        if not _is_default_value_compatible(param.default, param.annotation):
          raise ValueError(default_value_error_msg)
        schema.default = param.default
      _raise_if_schema_unsupported(client, schema)
      return schema
    if origin is Literal:
      if not all(isinstance(arg, str) for arg in args):
        raise ValueError(
            f'Literal type {param.annotation} must be a list of strings.'
        )
      schema.type = 'STRING'
      schema.enum = list(args)
      if param.default is not inspect.Parameter.empty:
        if not _is_default_value_compatible(param.default, param.annotation):
          raise ValueError(default_value_error_msg)
        schema.default = param.default
      _raise_if_schema_unsupported(client, schema)
      return schema
    if origin is list:
      schema.type = 'ARRAY'
      schema.items = _parse_schema_from_parameter(
          client,
          inspect.Parameter(
              'item',
              inspect.Parameter.POSITIONAL_OR_KEYWORD,
              annotation=args[0],
          ),
          func_name,
      )
      if param.default is not inspect.Parameter.empty:
        if not _is_default_value_compatible(param.default, param.annotation):
          raise ValueError(default_value_error_msg)
        schema.default = param.default
      _raise_if_schema_unsupported(client, schema)
      return schema
    if origin is Union:
      schema.any_of = []
      schema.type = 'OBJECT'
      unique_types = set()
      for arg in args:
        if arg.__name__ == 'NoneType':  # Optional type
          schema.nullable = True
          continue
        schema_in_any_of = _parse_schema_from_parameter(
            client,
            inspect.Parameter(
                'item',
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=arg,
            ),
            func_name,
        )
        if (
            schema_in_any_of.model_dump_json(exclude_none=True)
            not in unique_types
        ):
          schema.any_of.append(schema_in_any_of)
          unique_types.add(schema_in_any_of.model_dump_json(exclude_none=True))
      if len(schema.any_of) == 1:  # param: Union[List, None] -> Array
        schema.type = schema.any_of[0].type
        schema.any_of = None
      if (
          param.default is not None
          and param.default is not inspect.Parameter.empty
      ):
        if not _is_default_value_compatible(param.default, param.annotation):
          raise ValueError(default_value_error_msg)
        schema.default = param.default
      _raise_if_schema_unsupported(client, schema)
      return schema
      # all other generic alias will be invoked in raise branch
  if (
      inspect.isclass(param.annotation)
      # for user defined class, we only support pydantic model
      and issubclass(param.annotation, pydantic.BaseModel)
  ):
    if (
        param.default is not inspect.Parameter.empty
        and param.default is not None
    ):
      schema.default = param.default
    schema.type = 'OBJECT'
    schema.properties = {}
    for field_name, field_info in param.annotation.model_fields.items():
      schema.properties[field_name] = _parse_schema_from_parameter(
          client,
          inspect.Parameter(
              field_name,
              inspect.Parameter.POSITIONAL_OR_KEYWORD,
              annotation=field_info.annotation,
          ),
          func_name,
      )
    _raise_if_schema_unsupported(client, schema)
    return schema
  raise ValueError(
      f'Failed to parse the parameter {param} of function {func_name} for'
      ' automatic function calling.Automatic function calling works best with'
      ' simpler function signature schema,consider manually parse your'
      f' function declaration for function {func_name}.'
  )


def _get_required_fields(schema: types.Schema) -> list[str]:
  if not schema.properties:
    return
  return [
      field_name
      for field_name, field_schema in schema.properties.items()
      if not field_schema.nullable and field_schema.default is None
  ]
