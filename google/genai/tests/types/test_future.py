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

# !Please DO NOT combine the test in this file with other tests. This file is
# used to test the future annotation, which is the first line of import.
from __future__ import annotations

import copy
import pydantic

from ... import types


class ComplexType(pydantic.BaseModel):
  param_x: str
  param_y: int


class FakeClient:

  def __init__(self, vertexai=False) -> None:
    self.vertexai = vertexai


mldev_client = FakeClient()
vertex_client = FakeClient(vertexai=True)


def test_future_annotation_simple_type():
  def func_under_test(param_1: str, param_2: int) -> str:
    return '123'

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters_json_schema={
          'type': 'object',
          'properties': {
              'param_1': {'type': 'string'},
              'param_2': {'type': 'integer'},
          },
          'required': ['param_1', 'param_2'],
      },
      response_json_schema={
          'type': 'string',
      },
  )
  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema


def test_future_annotation_complex_type():
  def func_under_test(param_1: ComplexType, param_2: int) -> str:
    return '123'

  expected_schema = types.FunctionDeclaration(
      name='func_under_test',
      parameters_json_schema={
          'type': 'object',
          'properties': {
              'param_1': {
                  'properties': {
                      'param_x': {
                          'title': 'Param X',
                          'type': 'string',
                      },
                      'param_y': {
                          'title': 'Param Y',
                          'type': 'integer',
                      },
                  },
                  'required': ['param_x', 'param_y'],
                  'title': 'ComplexType',
                  'type': 'object',
              },
              'param_2': {'type': 'integer'},
          },
          'required': ['param_1', 'param_2'],
      },
      response_json_schema={
          'type': 'string',
      },
  )

  actual_schema_mldev = types.FunctionDeclaration.from_callable(
      client=mldev_client, callable=func_under_test
  )
  actual_schema_vertex = types.FunctionDeclaration.from_callable(
      client=vertex_client, callable=func_under_test
  )
  assert actual_schema_mldev == expected_schema
  assert actual_schema_vertex == expected_schema
