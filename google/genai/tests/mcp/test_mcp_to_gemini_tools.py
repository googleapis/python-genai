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
from unittest import mock

import pytest

from ... import _mcp_utils
from ... import types
from ..._api_client import BaseApiClient


try:
  from mcp import types as mcp_types
except ImportError as e:
  import sys

  if sys.version_info < (3, 10):
    raise ImportError(
        'MCP Tool requires Python 3.10 or above. Please upgrade your Python'
        ' version.'
    ) from e
  else:
    raise e


def test_empty_mcp_tools_list():
  """Test conversion of empty MCP tools list to Gemini tools list."""
  result = _mcp_utils.mcp_to_gemini_tools([])

  assert result == []


def test_unknown_field_conversion():
  """Test conversion of MCP tools with unknown fields to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'object',
              'properties': {},
              'unknown_field': 'unknownField',
              'unknown_object': {},
          },
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      properties={},
                  ),
              ),
          ],
      ),
  ]


def test_items_conversion():
  """Test conversion of MCP tools with items to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'array',
              'items': {
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
          },
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='ARRAY',
                      items=types.Schema(
                          type='OBJECT',
                          properties={
                              'key1': types.Schema(type='STRING'),
                              'key2': types.Schema(type='NUMBER'),
                          },
                      ),
                  ),
              ),
          ],
      ),
  ]


def test_any_of_conversion():
  """Test conversion of MCP tools with any_of to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
          name='tool',
          description='tool-description',
          inputSchema={
              'type': 'object',
              'any_of': [
                  {
                      'type': 'string',
                  },
                  {
                      'type': 'number',
                  },
              ],
          },
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
      types.Tool(
          function_declarations=[
              types.FunctionDeclaration(
                  name='tool',
                  description='tool-description',
                  parameters=types.Schema(
                      type='OBJECT',
                      any_of=[
                          types.Schema(type='STRING'),
                          types.Schema(type='NUMBER'),
                      ],
                  ),
              ),
          ],
      ),
  ]


def test_properties_conversion():
  """Test conversion of MCP tools with properties to Gemini tools."""
  mcp_tools = [
      mcp_types.Tool(
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
      ),
  ]
  result = _mcp_utils.mcp_to_gemini_tools(mcp_tools)
  assert result == [
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
              ),
          ],
      ),
  ]


def test_defs_conversion():
    """Test conversion of MCP tools with shared definitions ($defs)."""
    mcp_tools = [
        mcp_types.Tool(
            name='create_endpoint',
            description='Creates an endpoint',
            inputSchema={
                'type': 'object',
                'properties': {
                    'machine_spec': {'$ref': '#/$defs/MachineSpec'}
                },
                '$defs': {
                    'MachineSpec': {
                        'type': 'object',
                        'properties': {'machine_type': {'type': 'string'}}
                    }
                }
            },
        ),
    ]

    result = _mcp_utils.mcp_to_gemini_tools(mcp_tools, is_agent_platform=True)

    schema = result[0].function_declarations[0].parameters_json_schema
    assert '$defs' in schema
    assert 'MachineSpec' in schema['$defs']


def test_create_endpoint_one_of_conversion():
    """Test oneOf translation for Vertex create_endpoint resource selection."""

    mcp_tools = [
        mcp_types.Tool(
            name='create_endpoint',
            description='Creates a Vertex AI Endpoint resource.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'endpoint': {
                        'type': 'object',
                        'oneOf': [
                            {'title': 'dedicated_resources', 'type': 'object'},
                            {'title': 'automatic_resources', 'type': 'object'},
                        ],
                    }
                },
            },
        ),
    ]
    result = _mcp_utils.mcp_to_gemini_tools(mcp_tools, is_agent_platform=True)
    schema = result[0].function_declarations[0].parameters_json_schema
    endpoint_schema = schema['properties']['endpoint']

    assert 'oneOf' in endpoint_schema
    assert len(endpoint_schema['oneOf']) == 2


def test_update_endpoint_labels_conversion():
    """Test additionalProperties translation for Vertex resource labels."""

    mcp_tools = [
        mcp_types.Tool(
            name='update_endpoint',
            description='Updates a Vertex AI Endpoint resource.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'endpoint': {
                        'type': 'object',
                        'properties': {
                            'labels': {
                                'type': 'object',
                                'additionalProperties': {'type': 'string'}
                            }
                        }
                    }
                }
            },
        ),
    ]
    result = _mcp_utils.mcp_to_gemini_tools(mcp_tools, is_agent_platform=True)
    schema = result[0].function_declarations[0].parameters_json_schema
    labels_schema = schema['properties']['endpoint']['properties']['labels']

    assert 'additionalProperties' in labels_schema


def test_agent_platform_preserves_unknown_fields():
    """Test that Agent Platform translation passes all schema fields directly
    to the backend.
    """
    mcp_tools = [
        mcp_types.Tool(
            name='tool',
            description='tool-description',
            inputSchema={
                'type': 'object',
                'properties': {},
                # A new unknown field
                'some_new_future_field': 'value',
            },
        ),
    ]

    result = _mcp_utils.mcp_to_gemini_tools(mcp_tools, is_agent_platform=True)
    schema = result[0].function_declarations[0].parameters_json_schema

    # Verify the entire schema is passed through intact, including the unknown field
    assert 'some_new_future_field' in schema
    assert schema['some_new_future_field'] == 'value'


@pytest.mark.asyncio
@mock.patch('httpx.AsyncClient')
@mock.patch.object(_mcp_utils, 'streamable_http_client')
@mock.patch.object(_mcp_utils, 'McpClientSession')
@mock.patch('google.auth.default')
async def test_connect_agent_platform_mcp_url_and_headers(
    mock_auth_default, mock_session_cls, mock_streamable, mock_create_http
):
    """Tests that _mcp_utils._connect_agent_platform_mcp builds the correct
    regional URL and injects auth headers.
    """

    mock_creds = mock.Mock()
    mock_creds.token = 'fake-oauth-token'
    mock_auth_default.return_value = (mock_creds, 'fake-project')

    @contextlib.asynccontextmanager
    async def mock_streamable_ctx(*args, **kwargs):
      yield (mock.Mock(), mock.Mock(), mock.Mock())

    mock_streamable.side_effect = mock_streamable_ctx

    @contextlib.asynccontextmanager
    async def mock_session_ctx(*args, **kwargs):
      session_instance = mock.AsyncMock()
      yield session_instance

    mock_session_cls.side_effect = mock_session_ctx

    mock_http_client_instance = mock.AsyncMock()
    mock_http_client_instance.__aenter__.return_value = (
        mock_http_client_instance
    )
    mock_http_client_instance.__aexit__.return_value = None
    mock_create_http.return_value = mock_http_client_instance

    api_client = BaseApiClient(
      vertexai=True,
      project='test-project-123',
      location='europe-west4'
    )

    async with _mcp_utils._connect_agent_platform_mcp(
        api_client, 'endpoints'
    ) as session:
      session.initialize.assert_awaited_once()

    mock_streamable.assert_called_once()
    assert (
        mock_streamable.call_args.kwargs['url']
        == 'https://europe-west4-aiplatform.googleapis.com/mcp/endpoints'
    )

    mock_create_http.assert_called_once()
    called_headers = mock_create_http.call_args.kwargs['headers']

    assert called_headers['Authorization'] == 'Bearer fake-oauth-token'
    assert called_headers['X-Goog-User-Project'] == 'test-project-123'
    assert 'mcp_used' in called_headers.get('x-goog-api-client', '')
