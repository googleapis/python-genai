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

from typing import Optional, Union
import pydantic
import pytest
from ... import _automatic_function_calling_util


class UserModel(pydantic.BaseModel):
  user_id: int
  name: str


class AdminModel(pydantic.BaseModel):
  admin_id: int
  role: str


def test_optional_scalar_parameters_do_not_contain_type_object():
  """Tests that optional scalar parameters (int | None, str | None) do not get type='object'."""

  def sample_tool(
      path: str,
      start_line: Optional[int] = None,
      end_line: Union[int, None] = None,
      tag: Optional[str] = None,
      verbose: Optional[bool] = None,
  ) -> str:
    """Sample tool with optional scalar parameters."""
    return f'{path}:{start_line}-{end_line}'

  decl = _automatic_function_calling_util.parse_function_declaration_json_schema(
      sample_tool, behavior=None
  )
  assert decl.parameters_json_schema is not None
  props = decl.parameters_json_schema.get('properties', {})

  # Regular string parameter should have type='string'
  assert props['path'] == {'type': 'string'}

  # Optional integer parameters should have anyOf and NO type='object'
  assert 'anyOf' in props['start_line']
  assert 'type' not in props['start_line']
  assert props['start_line']['default'] is None
  types_start = [s.get('type') for s in props['start_line']['anyOf']]
  assert 'integer' in types_start
  assert 'null' in types_start

  assert 'anyOf' in props['end_line']
  assert 'type' not in props['end_line']
  assert props['end_line']['default'] is None

  # Optional string parameter
  assert 'anyOf' in props['tag']
  assert 'type' not in props['tag']

  # Optional bool parameter
  assert 'anyOf' in props['verbose']
  assert 'type' not in props['verbose']


def test_model_unions_retain_type_object():
  """Tests that unions of Pydantic models still receive type='object'."""

  def model_union_tool(
      account: Union[UserModel, AdminModel],
      optional_user: Optional[UserModel] = None,
  ) -> str:
    """Tool accepting model unions."""
    return 'ok'

  decl = _automatic_function_calling_util.parse_function_declaration_json_schema(
      model_union_tool, behavior=None
  )
  assert decl.parameters_json_schema is not None
  props = decl.parameters_json_schema.get('properties', {})

  # Model union should retain type='object'
  assert 'anyOf' in props['account']
  assert props['account'].get('type') == 'object'

  # Optional model should retain type='object'
  assert 'anyOf' in props['optional_user']
  assert props['optional_user'].get('type') == 'object'
