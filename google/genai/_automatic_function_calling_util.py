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

import inspect
import sys
import types as builtin_types
import typing
from typing import _GenericAlias, Any, Callable, get_args, get_origin, Literal, Optional, Union  # type: ignore[attr-defined]

import pydantic

from . import _extra_utils
from . import types


if sys.version_info >= (3, 10):
  VersionedUnionType = builtin_types.UnionType
else:
  VersionedUnionType = typing._UnionGenericAlias  # type: ignore[attr-defined]


__all__ = [
    '_py_builtin_type_to_schema_type',
    '_raise_for_unsupported_param',
    '_handle_params_as_deferred_annotations',
    '_add_unevaluated_items_to_fixed_len_tuple_schema',
    '_is_builtin_primitive_or_compound',
    '_is_default_value_compatible',
    '_parse_schema_from_parameter',
    '_get_required_fields',
    '_get_required_fields_from_json_schema',
    'parse_function_declaration_json_schema',
]

_py_builtin_type_to_schema_type = {
    str: types.Type.STRING,
    int: types.Type.INTEGER,
    float: types.Type.NUMBER,
    bool: types.Type.BOOLEAN,
    list: types.Type.ARRAY,
    dict: types.Type.OBJECT,
    None: types.Type.NULL,
}


def _raise_for_unsupported_param(
    param: inspect.Parameter, func_name: str, exception: Union[Exception, type[Exception]]
) -> None:
  raise ValueError(
      f'Failed to parse the parameter {param} of function {func_name} for'
      ' automatic function calling.Automatic function calling works best with'
      ' simpler function signature schema, consider manually parsing your'
      f' function declaration for function {func_name}.'
  ) from exception


def _handle_params_as_deferred_annotations(param: inspect.Parameter, annotation_under_future: dict[str, Any], name: str) -> inspect.Parameter:
  """Catches the case when type hints are stored as strings."""
  if isinstance(param.annotation, str):
    param = param.replace(annotation=annotation_under_future[name])
  return param


def _add_unevaluated_items_to_fixed_len_tuple_schema(
    json_schema: dict[str, Any]
) -> dict[str, Any]:
  if (
      json_schema.get('maxItems')
      and (
          json_schema.get('prefixItems')
          and len(json_schema['prefixItems']) == json_schema['maxItems']
      )
      and json_schema.get('type') == 'array'
  ):
    json_schema['unevaluatedItems'] = False
  return json_schema


def _is_builtin_primitive_or_compound(
    annotation: inspect.Parameter.annotation,  # type: ignore[valid-type]
) -> bool:
  return annotation in _py_builtin_type_to_schema_type.keys()


def _is_default_value_compatible(
    default_value: Any, annotation: inspect.Parameter.annotation  # type: ignore[valid-type]
) -> bool:
  # None type is expected to be handled external to this function
  if _is_builtin_primitive_or_compound(annotation):
    return isinstance(default_value, annotation)

  if (
      isinstance(annotation, _GenericAlias)
      or isinstance(annotation, builtin_types.GenericAlias)
      or isinstance(annotation, VersionedUnionType)
  ):
    origin = get_origin(annotation)
    if origin in (Union, VersionedUnionType):  # type: ignore[comparison-overlap]
      return any(
          _is_default_value_compatible(default_value, arg)
          for arg in get_args(annotation)
      )

    if origin is dict:  # type: ignore[comparison-overlap]
      return isinstance(default_value, dict)

    if origin is list:  # type: ignore[comparison-overlap]
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

    if origin is Literal:  # type: ignore[comparison-overlap]
      return default_value in get_args(annotation)

  # return False for any other unrecognized annotation
  return False


def _parse_schema_from_parameter(  # type: ignore[return]
    api_option: Literal['ENTERPRISE', 'GEMINI_API', 'VERTEX_AI'],
    param: inspect.Parameter,
    func_name: str,
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
    return schema
  if (
      isinstance(param.annotation, VersionedUnionType)
      # only parse simple UnionType, example int | str | float | bool
      # complex UnionType will be invoked in raise branch
      and all(
          (_is_builtin_primitive_or_compound(arg) or arg is type(None))
          for arg in get_args(param.annotation)
      )
  ):
    schema.type = _py_builtin_type_to_schema_type[dict]
    schema.any_of = []
    unique_types = set()
    for arg in get_args(param.annotation):
      if arg.__name__ == 'NoneType':  # Optional type
        schema.nullable = True
        continue
      schema_in_any_of = _parse_schema_from_parameter(
          api_option,
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
    return schema
  if isinstance(param.annotation, _GenericAlias) or isinstance(
      param.annotation, builtin_types.GenericAlias
  ):
    origin = get_origin(param.annotation)
    args = get_args(param.annotation)
    if origin is dict:
      schema.type = _py_builtin_type_to_schema_type[dict]
      if param.default is not inspect.Parameter.empty:
        if not _is_default_value_compatible(param.default, param.annotation):
          raise ValueError(default_value_error_msg)
        schema.default = param.default
      return schema
    if origin is Literal:
      if not all(isinstance(arg, str) for arg in args):
        raise ValueError(
            f'Literal type {param.annotation} must be a list of strings.'
        )
      schema.type = _py_builtin_type_to_schema_type[str]
      schema.enum = list(args)
      if param.default is not inspect.Parameter.empty:
        if not _is_default_value_compatible(param.default, param.annotation):
          raise ValueError(default_value_error_msg)
        schema.default = param.default
      return schema
    if origin is list:
      schema.type = _py_builtin_type_to_schema_type[list]
      schema.items = _parse_schema_from_parameter(
          api_option,
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
      return schema
    if origin is Union:
      schema.any_of = []
      schema.type = _py_builtin_type_to_schema_type[dict]
      unique_types = set()
      for arg in args:
        # The first check is for NoneType in Python 3.9, since the __name__
        # attribute is not available in Python 3.9
        if type(arg) is type(None) or (
            hasattr(arg, '__name__') and arg.__name__ == 'NoneType'
        ):  # Optional type
          schema.nullable = True
          continue
        schema_in_any_of = _parse_schema_from_parameter(
            api_option,
            inspect.Parameter(
                'item',
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=arg,
            ),
            func_name,
        )
        if (
            len(param.annotation.__args__) == 2
            and type(None) in param.annotation.__args__
        ):  # Optional type
          for optional_arg in param.annotation.__args__:
            if (
                hasattr(optional_arg, '__origin__')
                and optional_arg.__origin__ is list
            ):
              # Optional type with list, for example Optional[list[str]]
              schema.items = schema_in_any_of.items
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
      return schema
      # all other generic alias will be invoked in raise branch
  if (
      # for user defined class, we only support pydantic model
      _extra_utils.is_annotation_pydantic_model(param.annotation)
  ):
    if (
        param.default is not inspect.Parameter.empty
        and param.default is not None
    ):
      schema.default = param.default
    schema.type = _py_builtin_type_to_schema_type[dict]
    schema.properties = {}
    for field_name, field_info in param.annotation.model_fields.items():
      schema.properties[field_name] = _parse_schema_from_parameter(
          api_option,
          inspect.Parameter(
              field_name,
              inspect.Parameter.POSITIONAL_OR_KEYWORD,
              annotation=field_info.annotation,
          ),
          func_name,
      )
    schema.required = _get_required_fields(schema)
    return schema
  _raise_for_unsupported_param(param, func_name, ValueError)


def _get_required_fields(schema: types.Schema) -> Optional[list[str]]:
  if not schema.properties:
    return None
  return [
      field_name
      for field_name, field_schema in schema.properties.items()
      if not field_schema.nullable and field_schema.default is None
  ]


def _get_required_fields_from_json_schema(json_schema: dict[str, Any]) -> Optional[list[str]]:
  properties = json_schema.get('properties', {})
  if not properties:
    return None
  required_fields = []
  for field_name, field_schema in properties.items():
    if not field_schema:
      continue
    if 'nullable' in field_schema and not field_schema['nullable']:
      required_fields.append(field_name)
    if 'default' not in field_schema and field_name not in required_fields:
      required_fields.append(field_name)
  return required_fields


def parse_function_declaration_json_schema(
    callable: Callable[..., Any],
    behavior: Optional[types.Behavior]
    ) -> types.FunctionDeclaration:
  """Parse function declaration JSON schema from a callable."""
  annotation_under_future = typing.get_type_hints(callable)
  parameters_properties_json_schema = {}
  root_defs = {}

  for name, param in inspect.signature(callable).parameters.items():
    if param.kind in (
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.POSITIONAL_ONLY,
    ):
      try:
        param = _handle_params_as_deferred_annotations(
            param, annotation_under_future, name
        )
        json_schema_dict = {}
        if _extra_utils.is_annotation_pydantic_model(param.annotation):
          json_schema_dict = param.annotation.model_json_schema()
        else:
          param_schema_adapter = pydantic.TypeAdapter(
              param.annotation,
              config=pydantic.ConfigDict(arbitrary_types_allowed=True),
          )
          json_schema_dict = param_schema_adapter.json_schema()
          json_schema_dict = _add_unevaluated_items_to_fixed_len_tuple_schema(
              json_schema_dict
          )

        # Extract parameter-level $defs and promote to top-level root_defs
        if '$defs' in json_schema_dict:
          root_defs.update(json_schema_dict.pop('$defs'))
        if 'definitions' in json_schema_dict:
          root_defs.update(json_schema_dict.pop('definitions'))
        # pydantic doesn't assign the `type` field when the schema has 'anyOf'.
        # but Vertex requires it.
        if not 'type' in json_schema_dict and 'anyOf' in json_schema_dict:
          json_schema_dict['type'] = 'object'
        if param.default is not inspect._empty:
          json_schema_dict['default'] = param.default
        parameters_properties_json_schema[name] = json_schema_dict
      except Exception as e:
        _raise_for_unsupported_param(
            param, callable.__name__, e
        )

  declaration = types.FunctionDeclaration(
      name=callable.__name__,
      description=inspect.cleandoc(callable.__doc__)
      if callable.__doc__
      else '',
      behavior=behavior,
  )
  if parameters_properties_json_schema:
    declaration.parameters_json_schema = {
        'type': 'object',
        'properties': parameters_properties_json_schema,
    }
    if root_defs:
      declaration.parameters_json_schema['$defs'] = root_defs
    declaration.parameters_json_schema['required'] = (
        _get_required_fields_from_json_schema(
            declaration.parameters_json_schema
        )
    )
    return_annotation = inspect.signature(callable).return_annotation
    if return_annotation is inspect.Parameter.empty:
      return declaration

    return_value = inspect.Parameter(
        'return_value',
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=return_annotation,
    )
    # This snippet catches the case when type hints are stored as strings
    if isinstance(return_value.annotation, str):
      return_value = return_value.replace(
          annotation=annotation_under_future['return']
      )
    response_json_schema: dict[str, Any] = {}
    try:
      if _extra_utils.is_annotation_pydantic_model(return_value.annotation):
        response_json_schema = return_value.annotation.model_json_schema()
      else:
        return_value_schema_adapter = pydantic.TypeAdapter(
            return_value.annotation,
            config=pydantic.ConfigDict(arbitrary_types_allowed=True),
        )
        response_json_schema = return_value_schema_adapter.json_schema()
      response_json_schema = _add_unevaluated_items_to_fixed_len_tuple_schema(
          response_json_schema
      )
      # pydantic doesn't assign the `type` field when the schema has 'anyOf'.
      # but Vertex requires it.
      if 'type' not in response_json_schema and 'anyOf' in response_json_schema:
        response_json_schema['type'] = 'object'
    except Exception as e:
      _raise_for_unsupported_param(
          return_value, callable.__name__, e
      )
    declaration.response_json_schema = response_json_schema
  return declaration
