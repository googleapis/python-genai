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


import contextlib
import json
import os
import pathlib
from typing import Any, Optional
from pydantic import BaseModel, Field, SerializeAsAny
import pytest
import re
from .. import _common
from .. import _replay_api_client
from .. import types
from .._api_client import HttpOptions

is_api_mode = "config.getoption('--mode') == 'api'"


class TestTableItem(types.TestTableItem):
  # This is not a test suite class.
  __test__ = False

  # Overrides to support Pydantic models.
  parameters: SerializeAsAny[BaseModel] = Field(
      description="""The parameters to the test. Use pydantic models.""",
  )


def base_test_function(
    client,
    use_vertex: bool,
    replays_prefix: str,
    test_method: str,
    test_table_item: TestTableItem,
    globals_for_file: dict[str, Any],
):
  replay_id = (
      test_table_item.override_replay_id
      if test_table_item.override_replay_id
      else test_table_item.name
  )
  api_type = 'vertex' if use_vertex else 'mldev'
  replay_id = f'{replays_prefix}/{replay_id}.{api_type}'
  client._api_client.initialize_replay_session(replay_id)
  # vars().copy() provides a shallow copy of the parameters.
  parameters_dict = vars(test_table_item.parameters).copy()
  try:
    if '.' in test_method:
      method_name_parts = test_method.split('.')
      module_path_parts = method_name_parts[:-1]
      method_name = method_name_parts[-1]
      # Iterates the nested module starting from client
      current_object = client
      for part in module_path_parts:
        current_object = getattr(current_object, part)
      method = getattr(current_object, method_name)
      method(**parameters_dict)
    else:
      custom_method = globals_for_file[test_method]
      custom_method(client, test_table_item.parameters)
    # Should not reach here if expecting an exception.
    if test_table_item.exception_if_mldev and not client._api_client.vertexai:
      assert False, 'Should have raised exception in MLDev.'
    elif test_table_item.exception_if_vertex and client._api_client.vertexai:
      assert False, 'Should have raised exception in Vertex.'
    client._api_client.close()
  except Exception as e:
    if test_table_item.exception_if_mldev and not client._api_client.vertexai:
      if test_table_item.exception_if_mldev not in str(e):
        raise AssertionError(
            f"'{test_table_item.exception_if_mldev}' not in '{str(e)}'"
        ) from e
    elif test_table_item.exception_if_vertex and client._api_client.vertexai:
      if test_table_item.exception_if_vertex not in str(e):
        raise AssertionError(
            f"'{test_table_item.exception_if_vertex}' not in '{str(e)}'"
        ) from e
    else:
      raise e


def create_test_for_table_item(
    globals_for_file: dict[str, Any],
    test_method: str,
    test_table_item: TestTableItem,
):
  return lambda client, use_vertex, replays_prefix: base_test_function(
      client,
      use_vertex,
      replays_prefix,
      test_method,
      test_table_item,
      globals_for_file,
  )


def create_test_for_table(
    globals_for_file: dict[str, Any],
    test_method: str,
    test_table: list[TestTableItem],
):
  for test_table_item in test_table:
    if test_table_item.has_union:
      assert test_table_item.name.startswith('test_union_'), f"""
      test: {test_table_item.name}
      When has_union is true, it must be a test that explicitly test the
      non-canonical type in the union.
      For all other tests, use transformers to convert data to the canonical
      type of the field so it can be tested in other languages.
      If this test is truly about testing the non-canonical type of the union,
      rename the test to start with 'test_union_'. E.g.
      test_union_contents_is_string()"""
    globals_for_file[test_table_item.name] = create_test_for_table_item(
        globals_for_file, test_method, test_table_item
    )


# Sets up the test framework.
# file: Always use __file__
# globals_for_file: Always use globals()
# test_table: The test table for the file.
#     Use test table over individual tests whenever possible.
#     Tests built with test_table will run in all other languages automatically.
#     Otherwise, you will need to write tests in all other languages manually.
def setup(
    *,
    file: str,
    globals_for_file: Optional[dict[str, Any]] = None,
    test_method: Optional[str] = None,
    test_table: Optional[list[TestTableItem]] = None,
    http_options: Optional[HttpOptions] = None,
):
  """Generates parameterization for tests, run for both Vertex and MLDev."""
  replays_directory = (
      file.replace(os.path.dirname(__file__), 'tests')
      .replace('.py', '')
      .replace('/test_', '/')
  )

  is_tap_mode = False
  if os.environ.get('UNITTEST_ON_FORGE', None) is not None:
    is_tap_mode = True

  if test_table:
    create_test_for_table(globals_for_file, test_method, test_table)

  if test_table and not is_tap_mode:
    replays_root_directory = os.environ.get(
        'GOOGLE_GENAI_REPLAYS_DIRECTORY', None
    )
    if replays_root_directory is None:
      raise ValueError(
          'GOOGLE_GENAI_REPLAYS_DIRECTORY environment variable is not set'
      )
    abs_replay_directory = os.path.join(
        replays_root_directory, replays_directory
    )
    test_table_file_path = os.path.join(
        abs_replay_directory, '_test_table.json'
    )

    pathlib.Path(abs_replay_directory).mkdir(parents=True, exist_ok=True)
    assert isinstance(
        test_table[0].parameters, BaseModel
    ), f'{test_table_file_path} parameters must be a BaseModel.'
    test_table_file = types.TestTableFile(
        comment='Auto-generated. Do not edit.',
        test_method=test_method,
        parameter_names=list(test_table[0].parameters.model_fields.keys()),
        test_table=test_table,
    )
    os.makedirs(os.path.dirname(test_table_file_path), exist_ok=True)

    with open(test_table_file_path, 'w') as f:
      f.write(
          test_table_file.model_dump_json(exclude_none=True, by_alias=True, indent=2),
      )

  # Add fixture for requested client option.
  return pytest.mark.parametrize(
      'use_vertex, replays_prefix, http_options',
      [
          (True, replays_directory, http_options),
          (False, replays_directory, http_options),
      ],
  )


def exception_if_mldev(client, exception_type: type[Exception]):
  if client._api_client.vertexai:
    return contextlib.nullcontext()
  else:
    return pytest.raises(exception_type)


def exception_if_vertex(client, exception_type: type[Exception]):
  if client._api_client.vertexai:
    return pytest.raises(exception_type)
  else:
    return contextlib.nullcontext()


def snake_to_camel(snake_str: str) -> str:
  """Converts a snake_case string to CamelCase."""
  return re.sub(r'_([a-zA-Z])', lambda match: match.group(1).upper(), snake_str)


def camel_to_snake(camel_str: str) -> str:
  """Converts a CamelCase string to snake_case."""
  return re.sub(r'([A-Z])', r'_\1', camel_str).lower().lstrip('_')


def get_value_ignore_key_case(obj, key):
  """Returns the value of the key in the object, converting to camelCase or snake_case if necessary."""
  return obj.get(snake_to_camel(key), obj.get(camel_to_snake(key), None))


def camel_to_snake_all_keys(data):
  """Converts all keys in a dictionary or list to snake_case."""
  if isinstance(data, dict):
    new_dict = {}
    for key, value in data.items():
      if isinstance(key, str):
        new_key = camel_to_snake(key)
      else:
        new_key = key
      new_dict[new_key] = camel_to_snake_all_keys(value)
    return new_dict
  elif isinstance(data, list):
    return [camel_to_snake_all_keys(item) for item in data]
  else:
    return data
