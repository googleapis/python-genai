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
    '_get_required_fields',
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


def _get_required_fields(json_schema: dict[str, Any]) -> Optional[list[str]]:
  properties = json_schema.get('properties', {})
  if not properties:
    return None
  required_fields = []
  for field_name, field_schema in properties.items():
    if not field_schema:
      continue
    if 'nullable' in field_schema and not field_schema['nullable']:
      required_fields.append(field_name)
    if 'default' not in field_schema:
      required_fields.append(field_name)
  return required_fields
