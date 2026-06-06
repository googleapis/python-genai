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

"""Tests for t_tools."""

import typing
from typing import Any
import pytest
from ... import _transformers as t
from ... import client as google_genai_client_module
from ... import types

_is_mcp_imported = False
if typing.TYPE_CHECKING:
  from mcp import ClientSession as McpClientSession
  from mcp import types as mcp_types

  _is_mcp_imported = True
else:
  try:
    from mcp import ClientSession as McpClientSession
    from mcp import types as mcp_types

    _is_mcp_imported = True
  except ImportError:
    _is_mcp_imported = False


@pytest.fixture
def client(use_vertex):
  if use_vertex:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, project='test-project', location='test-location'
    )
  else:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, api_key='test-api-key'
    )


@pytest.mark.usefixtures('client')
def test_empty(client):
  assert t.t_tools(client, []) == []


@pytest.mark.usefixtures('client')
def test_function(client):
  def test_func(arg1: str, arg2: int):
    pass

  assert t.t_tools(client, [test_func]) == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='test_func',
                  parameters=types.Schema(
                      type='OBJECT',
                      properties={
                          'arg1': types.Schema(type='STRING'),
                          'arg2': types.Schema(type='INTEGER'),
                      },
                      required=['arg1', 'arg2'],
                  ),
              )
          ]
      )
  ]


@pytest.mark.usefixtures('client')
def test_tool(client):
  tool = types.Tool(
      function_declarations=[
          types.FunctionDeclaration(
              name='tool',
              description='tool-description',
              parameters=types.Schema(
                  type='OBJECT',
                  properties={
                      'key1': types.Schema(type='STRING'),
                      'key2': types.Schema(type='NUMBER'),
                  },
              ),
          )
      ]
  )
  assert t.t_tools(client, [tool]) == [tool]


@pytest.mark.usefixtures('client')
def test_mcp_tool(client):
  if not _is_mcp_imported:
    return

  mcp_tool = mcp_types.Tool(
      name='tool',
      description='tool-description',
      inputSchema={
          'type': 'object',
          'properties': {
              'key1': {
                  'type': 'string',
              },
              'key2': {
                  'type': 'number',
              },
          },
      },
  )
  assert t.t_tools(client, [mcp_tool]) == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      properties={
                          'key1': types.Schema(type='STRING'),
                          'key2': types.Schema(type='NUMBER'),
                      },
                  ),
              )
          ]
      )
  ]


@pytest.mark.usefixtures('client')
def test_multiple_tools(client):
  if not _is_mcp_imported:
    return

  mcp_tool1 = mcp_types.Tool(
      name='tool1',
      description='tool1-description',
      inputSchema={
          'type': 'object',
          'properties': {
              'key1': {
                  'type': 'string',
              },
          },
      },
  )
  mcp_tool2 = mcp_types.Tool(
      name='tool2',
      description='tool2-description',
      inputSchema={
          'type': 'object',
          'properties': {
              'key1': {
                  'type': 'number',
              },
          },
      },
  )
  assert t.t_tools(client, [mcp_tool1, mcp_tool2]) == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool1',
                  description='tool1-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      properties={
                          'key1': types.Schema(type='STRING'),
                      },
                  ),
              ),
              types.FunctionDeclaration(
                  name='tool2',
                  description='tool2-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      properties={
                          'key1': types.Schema(type='NUMBER'),
                      },
                  ),
              ),
          ]
      ),
  ]
