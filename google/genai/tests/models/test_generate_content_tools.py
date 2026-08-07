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

import collections
import logging
import os
import sys
import typing

import pydantic
import pytest

from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper


import contextlib
from unittest import mock
import pytest
from ... import _mcp_utils

try:
  from mcp import types as mcp_types
  from ... import ClientSession
except ImportError:
  mcp_types = None
  ClientSession = None

from ...models import AsyncModels

GOOGLE_HOMEPAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google_homepage.png')
)
with open(GOOGLE_HOMEPAGE_FILE_PATH, 'rb') as image_file:
  google_homepage_screenshot_bytes = image_file.read()

function_declarations = [{
    'name': 'get_current_weather',
    'description': 'Get the current weather in a city',
    'parameters': {
        'type': 'OBJECT',
        'properties': {
            'location': {
                'type': 'STRING',
                'description': 'The location to get the weather for',
            },
            'unit': {
                'type': 'STRING',
                'enum': ['C', 'F'],
            },
        },
    },
}]
computer_use_override_function_declarations = [{
    'name': 'type_text_at',
    'description': 'Types text at a certain coordinate.',
    'parameters': {
        'type': 'OBJECT',
        'properties': {
            'y': {
                'type': 'INTEGER',
                'description': 'The y-coordinate, normalized from 0 to 1000.',
            },
            'x': {
                'type': 'INTEGER',
                'description': 'The x-coordinate, normalized from 0 to 1000.',
            },
            'press_enter': {
                'type': 'BOOLEAN',
                'description': 'Whether to press enter after typing the text.'
            },
            'text': {
                'type': 'STRING',
                'description': 'The text to type.',
            },
        },
    },
}]
function_response_parts = [
    {
        'function_response': {
            'name': 'get_current_weather',
            'response': {
                'name': 'get_current_weather',
                'content': {'weather': 'super nice'},
            },
        },
    },
]
manual_function_calling_contents = [
    {'role': 'user', 'parts': [{'text': 'What is the weather in Boston?'}]},
    {
        'role': 'model',
        'parts': [{
            'function_call': {
                'name': 'get_current_weather',
                'args': {'location': 'Boston'},
            }
        }],
    },
    {'role': 'user', 'parts': function_response_parts},
]
computer_use_multi_turn_contents = [
    {
        'role': 'user',
        'parts': [{'text': 'Go to google and search nano banana'}],
    },
    {
        'role': 'model',
        'parts': [{'function_call': {'name': 'open_web_browser', 'args': {}}}],
    },
    {
        'role': 'user',
        'parts': [{
            'function_response': {
                'name': 'open_web_browser',
                'response': {
                    'url': 'http://www.google.com',
                },
                'parts': [{
                    'inline_data': {
                        'data': google_homepage_screenshot_bytes,
                        'mime_type': 'image/png',
                    }
                }],
            }
        }],
    },
]


def get_weather(city: str) -> str:
  return f'The weather in {city} is sunny and 100 degrees.'


def get_weather_declaration_only(city: str) -> str:
  """Get the current weather in a given city.

  Args:
    city: The city to get the weather for.
  """
  pass


def get_stock_price(symbol: str) -> str:
  if symbol == 'GOOG':
    return '1000'
  else:
    return '100'


def divide_integers(a: int, b: int) -> int:
  """Divide two integers."""
  return a // b


async def divide_floats_async(numerator: float, denominator: float) -> float:
  """Divide two floats."""
  return numerator / denominator


def divide_floats(a: float, b: float) -> float:
  """Divide two floats."""
  return a / b


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_google_search',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('Why is the sky blue?'),
            config={'tools': [{'google_search': {}}]},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_vai_search',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('what is vertex ai search?'),
            config={
                'tools': [{
                    'retrieval': {
                        'vertex_ai_search': {
                            'datastore': (
                                'projects/vertex-sdk-dev/locations/global/collections/default_collection/dataStores/yvonne_1728691676574'
                            )
                        }
                    }
                }]
            },
        ),
        exception_if_mldev='retrieval',
    ),
    pytest_helper.TestTableItem(
        name='test_vai_google_search',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('why is the sky blue?'),
            config={
                'tools': [
                    types.Tool(
                        retrieval=types.Retrieval(
                            vertex_ai_search=types.VertexAISearch(
                                datastore='projects/vertex-sdk-dev/locations/global/collections/default_collection/dataStores/yvonne_1728691676574'
                            )
                        ),
                        google_search_retrieval=types.GoogleSearchRetrieval(),
                    ),
                ]
            },
        ),
        exception_if_mldev='retrieval',
        exception_if_vertex='400',
    ),
    pytest_helper.TestTableItem(
        name='test_vai_search_engine',
        parameters=types._GenerateContentParameters(
            model='gemini-2.0-flash-001',
            contents=t.t_contents('why is the sky blue?'),
            config={
                'tools': [
                    types.Tool(
                        retrieval=types.Retrieval(
                            vertex_ai_search=types.VertexAISearch(
                                engine='projects/862721868538/locations/global/collections/default_collection/engines/teamfood-v11_1720671063545'
                            )
                        )
                    ),
                ]
            },
        ),
        exception_if_mldev='retrieval',
    ),
    pytest_helper.TestTableItem(
        name='test_rag_model_old',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'How much gain or loss did Google get in the Motorola Mobile'
                ' deal in 2014?',
            ),
            config={
                'tools': [
                    types.Tool(
                        retrieval=types.Retrieval(
                            vertex_rag_store=types.VertexRagStore(
                                rag_resources=[
                                    types.VertexRagStoreRagResource(
                                        rag_corpus='projects/964831358985/locations/us-central1/ragCorpora/3379951520341557248'
                                    )
                                ],
                                similarity_top_k=3,
                            )
                        ),
                    ),
                ]
            },
        ),
        exception_if_mldev='retrieval',
    ),
    pytest_helper.TestTableItem(
        name='test_rag_model_ga',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'How much gain or loss did Google get in the Motorola Mobile'
                ' deal in 2014?',
            ),
            config={
                'tools': [
                    types.Tool(
                        retrieval=types.Retrieval(
                            vertex_rag_store=types.VertexRagStore(
                                rag_resources=[
                                    types.VertexRagStoreRagResource(
                                        rag_corpus='projects/964831358985/locations/us-central1/ragCorpora/3379951520341557248'
                                    )
                                ],
                                rag_retrieval_config=types.RagRetrievalConfig(
                                    top_k=3,
                                    filter=types.RagRetrievalConfigFilter(
                                        vector_similarity_threshold=0.5,
                                    ),
                                ),
                            )
                        ),
                    ),
                ]
            },
        ),
        exception_if_mldev='retrieval',
    ),
    pytest_helper.TestTableItem(
        name='test_file_search',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'can you tell me the author of "A Survey of Modernist Poetry"?',
            ),
            config={
                'tools': [
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[
                                'fileSearchStores/5en07ei3kojo-yo8sjqgvx2xf'
                            ]
                        ),
                    ),
                ],
            },
        ),
        exception_if_vertex='is only supported in Gemini Developer API mode',
    ),
    pytest_helper.TestTableItem(
        name='test_file_search_non_existent_file_search_store',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'can you tell me the author of "A Survey of Modernist Poetry"?',
            ),
            config={
                'tools': [
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[
                                'fileSearchStores/test-non-existent-rag-store'
                            ],
                        ),
                    ),
                ],
            },
        ),
        exception_if_mldev='not exist',
        exception_if_vertex='is only supported in Gemini Developer API mode',
    ),
    pytest_helper.TestTableItem(
        name='test_file_search_with_metadata_filter',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'can you tell me the author of "A Survey of Modernist Poetry"?',
            ),
            config={
                'tools': [
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[
                                'fileSearchStores/5en07ei3kojo-yo8sjqgvx2xf'
                            ],
                            metadata_filter='tag=science',
                        ),
                    ),
                ],
            },
        ),
        exception_if_vertex='is only supported in Gemini Developer API mode',
    ),
    pytest_helper.TestTableItem(
        name='test_file_search_with_metadata_filter_and_top_k',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'can you tell me the author of "A Survey of Modernist Poetry"',
            ),
            config={
                'tools': [
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[
                                'fileSearchStores/5en07ei3kojo-yo8sjqgvx2xf'
                            ],
                            metadata_filter='tag=science',
                            top_k=1,
                        ),
                    ),
                ],
            },
        ),
        exception_if_vertex='is only supported in Gemini Developer API mode',
    ),
    pytest_helper.TestTableItem(
        name='test_function_call',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=manual_function_calling_contents,
            config={
                'tools': [{'function_declarations': function_declarations}]
            },
        ),
    ),
    pytest_helper.TestTableItem(
        # TODO(b/382547236) add the test back in api mode when the code
        # execution is supported.
        skip_in_api_mode=(
            'Model gemini-2.5-flash-001 does not support code execution for'
            ' Vertex API.'
        ),
        name='test_code_execution',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'What is the sum of the first 50 prime numbers? '
                + 'Generate and run code for the calculation, and make sure you'
                ' get all 50.',
            ),
            config={'tools': [{'code_execution': {}}]},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_function_google_search_with_long_lat',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('what is the price of GOOG?'),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch(),
                    ),
                ],
                tool_config=types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLngDict(
                            latitude=37.7749, longitude=-122.4194
                        )
                    )
                ),
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_url_context',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'what are the top headlines on https://news.google.com'
            ),
            config={'tools': [{'url_context': {}}]},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_url_context_paywall_status',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'Read the content of this URL:'
                ' https://unsplash.com/photos/portrait-of-an-adorable-golden-retriever-puppy-studio-shot-isolated-on-black-yRYCnnQASnc'
            ),
            config={'tools': [{'url_context': {}}]},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_url_context_unsafe_status',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                'Fetch the content of http://0k9.me/test.html'
            ),
            config={'tools': [{'url_context': {}}]},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_computer_use',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-computer-use-preview-10-2025',
            contents=t.t_contents('Go to google and search nano banana'),
            config={'tools': [{'computer_use': {}}]},
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_computer_use_with_browser_environment',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-computer-use-preview-10-2025',
            contents=t.t_contents('Go to google and search nano banana'),
            config={
                'tools': [
                    {'computer_use': {'environment': 'ENVIRONMENT_BROWSER'}}
                ]
            },
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_computer_use_with_disabled_safety_policies',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-computer-use-preview-10-2025',
            contents=t.t_contents('Go to google and search nano banana'),
            config={
                'tools': [{
                    'computer_use': {
                        'environment': 'ENVIRONMENT_BROWSER',
                        'disabled_safety_policies': [
                            'FINANCIAL_TRANSACTIONS',
                            'COMMUNICATION_TOOL',
                        ],
                    }
                }]
            },
        ),
        exception_if_vertex='only supported in Gemini Developer API mode',
        skip_in_private=(
            'disabled_safety_policies parameter is supported on Vertex AI in'
            ' Private SDK'
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_computer_use_multi_turn',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-computer-use-preview-10-2025',
            contents=computer_use_multi_turn_contents,
            config={
                'tools': [
                    {'computer_use': {'environment': 'ENVIRONMENT_BROWSER'}}
                ]
            },
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_computer_use_exclude_predefined_functions',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-computer-use-preview-10-2025',
            contents='cheapest flight to NYC on Mar 18 2025 on Google Flights',
            config={
                'tools': [
                    {
                        'computer_use': {
                            'environment': 'ENVIRONMENT_BROWSER',
                            'excluded_predefined_functions': ['click_at'],
                        },
                    },
                ]
            },
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        name='test_computer_use_override_default_function',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-computer-use-preview-10-2025',
            contents=computer_use_multi_turn_contents,
            config={
                'tools': [
                    {
                        'computer_use': {
                            'environment': 'ENVIRONMENT_BROWSER',
                            'excluded_predefined_functions': ['type_text_at'],
                        },
                    },
                    {
                        'function_declarations': (
                            computer_use_override_function_declarations
                        )
                    },
                ]
            },
        ),
        exception_if_vertex='404',
    ),
    pytest_helper.TestTableItem(
        # https://github.com/googleapis/python-genai/issues/830
        # - models started returning empty thought in response to queries
        #   containing tools.
        # - The API needs to accept any Content response it sends (otherwise
        #   chat breaks)
        # - MLDev is not returning the, so it's okay that MLDev doesn't accept
        #   them?
        # - This is also important to configm forward compatibility.
        #   when the models start returning thought_signature, those will get
        #   dropped by the SDK leaving a `{'thought: True}` part.
        name='test_chat_tools_empty_thoughts',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                types.Content.model_validate(item)
                for item in [
                    {
                        'parts': [{'text': 'Who won the 1955 world cup?'}],
                        'role': 'user',
                    },
                    {
                        'parts': [
                            {'thought': True},
                            {
                                'text': (
                                    'The FIFA World Cup is held every four'
                                    ' years. The 1954 FIFA World Cup was won by'
                                    ' West Germany, who defeated Hungary in the'
                                    ' final.'
                                )
                            },
                        ],
                        'role': 'model',
                    },
                    {
                        'parts': [{
                            'text': 'What was the population of canada in 1955?'
                        }],
                        'role': 'user',
                    },
                ]
            ],
            config={
                'tools': [{'function_declarations': function_declarations}],
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_function_calling_config_validated_mode',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('How is the weather in Kirkland?'),
            config={
                'tools': [{'function_declarations': function_declarations}],
                'tool_config': {
                    'function_calling_config': {'mode': 'VALIDATED'}
                },
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_google_maps_with_enable_widget',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents('What is the nearest airport to Seattle?'),
            config={'tools': [{'google_maps': {'enable_widget': True}}]},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_google_maps_places_routing',
        parameters=types._GenerateContentParameters(
            model='gemini-3.5-flash',
            contents=t.t_contents(
                'How long does it take to drive from SFO to LAX?'
            ),
            config={
                'tools': [{'google_maps': {'grounding_types': {'places': {}}}}]
            },
        ),
        exception_if_mldev='only supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_google_maps_routing',
        parameters=types._GenerateContentParameters(
            model='gemini-3.5-flash',
            contents=t.t_contents(
                'Give me directions from SFO to LAX.'
            ),
            config={
                'tools': [{'google_maps': {'grounding_types': {'routing': {}}}}]
            },
        ),
        exception_if_mldev='only supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_include_server_side_tool_invocations',
        parameters=types._GenerateContentParameters(
            model='gemini-3.1-pro-preview',
            contents=t.t_contents(
                'Use Google Search to tell me about the 1970 world cup match'
            ),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch(),
                    ),
                ],
                tool_config=types.ToolConfig(
                    include_server_side_tool_invocations=True,
                ),
            ),
        ),
        exception_if_vertex=(
            'parameter is only supported in Gemini Developer API mode'
        ),
        skip_in_private=(
            'include_server_side_tool_invocations parameter is supported on'
            ' Vertex AI in Private SDK'
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_include_server_side_tool_invocations_with_tool_call_echo',
        parameters=types._GenerateContentParameters(
            model='gemini-3.1-pro-preview',
            contents=[
                types.Content.model_validate(item)
                for item in [
                    {
                        'role': 'user',
                        'parts': [{'text': 'Why is the sky blue?'}],
                    },
                    {
                        'role': 'model',
                        'parts': [
                            {
                                'tool_call': {
                                    'tool_type': 'GOOGLE_SEARCH',
                                    'args': {
                                        'query': 'why is the sky blue',
                                    },
                                },
                            },
                            {
                                'tool_response': {
                                    'tool_type': 'GOOGLE_SEARCH',
                                    'response': {
                                        'result': (
                                            'The sky is blue because of'
                                            ' Rayleigh scattering.'
                                        ),
                                    },
                                },
                            },
                            {
                                'text': (
                                    'The sky is blue due to a phenomenon called'
                                    ' Rayleigh scattering.'
                                ),
                            },
                        ],
                    },
                    {
                        'role': 'user',
                        'parts': [{'text': 'What about Mars?'}],
                    },
                ]
            ],
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch(),
                    ),
                ],
                tool_config=types.ToolConfig(
                    include_server_side_tool_invocations=True,
                ),
            ),
        ),
        exception_if_vertex=(
            'parameter is only supported in Gemini Developer API mode'
        ),
    ),
]


pytestmark = [
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
        test_method='models.generate_content',
        test_table=test_table,
    ),
]
pytest_plugins = ('pytest_asyncio',)


def test_function_google_search(client):
  contents = 'What is the price of GOOG?.'
  config = types.GenerateContentConfig(
      tools=[
          types.Tool(
              google_search=types.GoogleSearch(),
          ),
          get_stock_price,
      ],
      tool_config=types.ToolConfig(
          function_calling_config=types.FunctionCallingConfig(mode='AUTO')
      ),
  )
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-3.1-pro-preview',
        contents=contents,
        config=config,
    )


@pytest.mark.skipif(
    "config.getoption('--private')",
    reason="include_server_side_tool_invocations is supported on Vertex AI in Private SDK",
)
def test_function_google_search_server_side_tool_invocations(client):
  contents = (
      'What is the weather in Buenos Aires? If it is raining, schedule a'
      ' meeting.'
  )
  schedule_meeting = {
      'name': 'schedule_meeting',
      'description': 'Schedule a meeting',
      'parameters': {
          'type': 'object',
          'properties': {'reason': {'type': 'string'}},
          'required': ['reason'],
      },
  }
  config = types.GenerateContentConfig(
      tools=[
          types.Tool(
              google_search=types.GoogleSearch(),
          ),
          types.Tool(
              function_declarations=[schedule_meeting],
          ),
      ],
      tool_config=types.ToolConfig(
          include_server_side_tool_invocations=True,
      ),
  )
  with pytest_helper.exception_if_vertex(client, ValueError):
    client.models.generate_content(
        model='gemini-3.5-flash',
        contents=contents,
        config=config,
    )


@pytest.mark.skipif(
    "config.getoption('--private')",
    reason="include_server_side_tool_invocations is supported on Vertex AI in Private SDK",
)
def test_function_google_search_server_side_tool_invocations_one_tool(client):
  contents = (
      'What is the weather in Buenos Aires? If it is raining, schedule a'
      ' meeting.'
  )
  schedule_meeting = {
      'name': 'schedule_meeting',
      'description': 'Schedule a meeting',
      'parameters': {
          'type': 'object',
          'properties': {'reason': {'type': 'string'}},
          'required': ['reason'],
      },
  }
  config = types.GenerateContentConfig(
      tools=[
          types.Tool(
              google_search=types.GoogleSearch(),
              function_declarations=[schedule_meeting],
          ),
      ],
      tool_config=types.ToolConfig(
          include_server_side_tool_invocations=True,
      ),
  )
  with pytest_helper.exception_if_vertex(client, ValueError):
    client.models.generate_content(
        model='gemini-3.5-flash',
        contents=contents,
        config=config,
    )


def test_google_search_stream(client):
  for part in client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents=types.Content(
          role='user',
          parts=[types.Part(text='Why is the sky blue?')],
      ),
      config=types.GenerateContentConfig(
          tools=[types.ToolDict({'google_search': {}})],
      ),
  ):
    pass


def test_function_calling_without_implementation(client):
  response = client.models.generate_content(
      model='gemini-3.1-pro-preview',
      contents='What is the weather in Boston?',
      config={
          'tools': [get_weather_declaration_only],
      },
  )


@pytest.mark.asyncio
async def test_google_search_async(client):
  await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          types.ContentDict(
              {'role': 'user', 'parts': [{'text': 'Why is the sky blue?'}]}
          )
      ],
      config={'tools': [{'google_search': {}}]},
  )


def test_empty_tools(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents='What is the price of GOOG?.',
      config={'tools': []},
  )


def test_with_1_empty_tool(client):
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-3.1-pro-preview',
        contents='What is the price of GOOG?.',
        config={
            'tools': [{}, get_stock_price],
        },
    )


@pytest.mark.asyncio
async def test_google_search_stream_async(client):
  async for part in await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='Why is the sky blue?',
      config={'tools': [{'google_search': {}}]},
  ):
    pass


@pytest.mark.asyncio
async def test_vai_search_stream_async(client):
  if client._api_client.vertexai:
    async for part in await client.aio.models.generate_content_stream(
        model='gemini-2.5-flash',
        contents='what is vertex ai search?',
        config={
            'tools': [{
                'retrieval': {
                    'vertex_ai_search': {
                        'datastore': (
                            'projects/vertex-sdk-dev/locations/global/collections/default_collection/dataStores/yvonne_1728691676574'
                        )
                    }
                }
            }]
        },
    ):
      pass
  else:
    with pytest.raises(ValueError) as e:
      async for part in await client.aio.models.generate_content_stream(
          model='gemini-2.5-flash',
          contents='Why is the sky blue?',
          config={
              'tools': [{
                  'retrieval': {
                      'vertex_ai_search': {
                          'datastore': (
                              'projects/vertex-sdk-dev/locations/global/collections/default_collection/dataStores/yvonne_1728691676574'
                          )
                      }
                  }
              }]
          },
      ):
        pass
    assert 'retrieval' in str(e)


def test_code_execution_tool(client):
  response = client.models.generate_content(
      model='gemini-2.0-flash-exp',
      contents=(
          'What is the sum of the first 50 prime numbers? Generate and run code'
          ' for the calculation, and make sure you get all 50.'
      ),
      config=types.GenerateContentConfig(
          tools=[types.Tool(code_execution=types.ToolCodeExecution)]
      ),
  )

  assert response.executable_code
  assert (
      'prime' in response.code_execution_result.lower()
      or '5117' in response.code_execution_result
  )


def test_tools_chat_curation(client, caplog):
  caplog.set_level(logging.DEBUG, logger='google_genai.models')
  sdk_logger = logging.getLogger('google_genai.models')
  sdk_logger.setLevel(logging.ERROR)

  config = types.ChatConfig(
      tools=[
          types.Tool(
              function_declarations=function_declarations,
          )
      ],
  )

  chat = client.chats.create(
      model='gemini-2.5-flash',
      config=config,
  )

  response = chat.send_message(
      message='Who won the 1955 world cup?',
  )

  response = chat.send_message(
      message='What was the population of canada in 1955?',
  )

  history = chat.get_history(curated=True)
  assert len(history) == 4


def test_function_declaration_with_callable(client):
  response = client.models.generate_content(
      model='gemini-3.1-pro-preview',
      contents=(
          'Divide 1000 by 2. And tell'
          ' me the weather in London.'
      ),
      config={
          'tools': [
              divide_integers,
              {'function_declarations': function_declarations},
          ],
      },
  )
  assert response.function_calls is not None


def test_function_declaration_with_callable_stream_now(client):
  for chunk in client.models.generate_content_stream(
      model='gemini-3.1-pro-preview',
      contents='Divide 1000 by 2. And tell me the weather in London.',
      config={
          'tools': [
              divide_integers,
              {'function_declarations': function_declarations},
          ],
      },
  ):
    pass


@pytest.mark.asyncio
async def test_function_declaration_with_callable_async(client):
  response = await client.aio.models.generate_content(
      model='gemini-3.1-pro-preview',
      contents=(
          'Divide 1000 by 2. And tell'
          ' me the weather in London.'
      ),
      config={
          'tools': [
              divide_integers,
              {'function_declarations': function_declarations},
          ],
      },
  )
  assert response.function_calls is not None


@pytest.mark.asyncio
async def test_function_declaration_with_callable_async_stream(client):
    async for chunk in await client.aio.models.generate_content_stream(
        model='gemini-3.1-pro-preview',
        contents='Divide 1000 by 2. And tell me the weather in London.',
        config={
            'tools': [
                divide_integers,
                {'function_declarations': function_declarations},
            ],
        },
    ):
      pass


def test_server_side_mcp_only(client):
  """Test server side mcp, happy path."""
  with pytest_helper.exception_if_vertex(client, ValueError):
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=('What is the weather like in New York (NY) on 02/02/2026?'),
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                mcp_servers=[types.McpServer(
                    name='get_weather',
                    streamable_http_transport=types.StreamableHttpTransport(
                        url='https://gemini-api-demos.uc.r.appspot.com/mcp',
                        headers={'AUTHORIZATION': 'Bearer github_pat_XXXX'},
                    ),
                )]
            )]
        )
    )
    assert response.text


@pytest.mark.asyncio
async def test_server_side_mcp_only_async(client):
  """Test server side mcp, happy path."""
  with pytest_helper.exception_if_vertex(client, ValueError):
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents=(
            'What is the weather like in New York on 02/02/2026?'
        ),
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                mcp_servers=[types.McpServer(
                    name='get_weather',
                    streamable_http_transport=types.StreamableHttpTransport(
                        url='https://gemini-api-demos.uc.r.appspot.com/mcp',
                        headers={'AUTHORIZATION': 'Bearer github_pat_XXXX'},
                    ),
                )]

            )]
        )
    )
    assert response.text


def test_server_side_mcp_only_stream(client):
  """Test server side mcp, happy path."""
  with pytest_helper.exception_if_vertex(client, ValueError):
    response = client.models.generate_content_stream(
        model='gemini-2.5-pro',
        contents=('What is the weather like in New York (NY) on 02/02/2026?'),
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                mcp_servers=[types.McpServer(
                    name='get_weather',
                    streamable_http_transport=types.StreamableHttpTransport(
                        url='https://gemini-api-demos.uc.r.appspot.com/mcp',
                        headers={'AUTHORIZATION': 'Bearer github_pat_XXXX'},
                    ),
                )]
            )]
        )
    )
    for chunk in response:
      pass


@pytest.mark.asyncio
async def test_client_side_mcp_unary_async(client):
    """Test client-side MCP execution for Agent Platform."""
    if not client._api_client.vertexai:
      pytest.skip('Vertex MCP test is not applicable to MLDev.')

    if mcp_types is None:
      pytest.skip('MCP library is not installed.')

    # Need to mock this since MCP bypasses the replay client recorder
    mock_session = mock.AsyncMock(spec=ClientSession)
    mock_session.list_tools.return_value = mcp_types.ListToolsResult(
        tools=[
            mcp_types.Tool(
                name='list_endpoints',
                description='Lists endpoints',
                inputSchema={'type': 'object', 'properties': {}}
            )
        ]
    )

    mock_session.call_tool.return_value = mcp_types.CallToolResult(
        content=[
            mcp_types.TextContent(
                type='text', text='Endpoint list: [my-endpoint-123]'
            )
        ]
    )

    @contextlib.asynccontextmanager
    async def mock_connect(*args, **kwargs):
      yield mock_session

    with mock.patch.object(_mcp_utils, '_connect_agent_platform_mcp', side_effect=mock_connect):

      response = await client.aio.models.generate_content(
          model='gemini-2.5-flash',
          contents='List my endpoints.',
          config={
              'tools': [
                  types.Tool(
                      mcp_servers=[types.McpServer(name='endpoints')]
                  )
              ],
              'automatic_function_calling': {'disable': False}
          }
      )

    assert response.text is not None
    assert mock_session.list_tools.called
    assert mock_session.call_tool.called


@pytest.mark.asyncio
async def test_client_side_mcp_missing_name_raises(client):
    """Test that an MCP server without a name raises an error."""

    if not client._api_client.vertexai:
      pytest.skip('Vertex MCP test is not applicable to MLDev.')

    with pytest.raises(
        ValueError,
        match="Agent Platform MCP servers require a 'name' field."
    ):
      await client.aio.models.generate_content(
          model='gemini-2.5-flash',
          contents='List my endpoints.',
          config={
              'tools': [
                  types.Tool(
                      mcp_servers=[types.McpServer(name=None)]
                  )
              ]
          }
      )


@pytest.mark.asyncio
async def test_agent_platform_mcp_stream_async_unit(client):
    """Unit tests the Agent Platform MCP integration for streaming without the replay framework."""
    if not client._api_client.vertexai:
      return

    if ClientSession is None:
      pytest.skip('MCP library is not installed.')

    class MockAgentPlatformSession(ClientSession):
      def __init__(self):
        self._read_stream = None
        self._write_stream = None

      async def list_tools(self):
        return mcp_types.ListToolsResult(
            tools=[
                mcp_types.Tool(
                    name='list_endpoints',
                    description='Lists all serving Endpoints',
                    inputSchema={
                        'type': 'object',
                        'properties': {'parent': {'type': 'string'}},
                    },
                )
            ]
        )

      async def call_tool(self, name: str, arguments: dict[str, typing.Any]):
        if name == 'list_endpoints':
          return mcp_types.CallToolResult(
              content=[mcp_types.TextContent(type='text', text='["endpoint-1", "endpoint-2"]')]
          )

    @contextlib.asynccontextmanager
    async def mock_mcp_context(*args, **kwargs):
      yield MockAgentPlatformSession()

    turn_1_chunk = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role='model',
                    parts=[
                        types.Part(
                            function_call=types.FunctionCall(
                                name='list_endpoints',
                                args={'parent': 'projects/vertex-sdk-dev/locations/us-central1'}
                            )
                        )
                    ]
                )
            )
        ]
    )

    turn_2_chunk = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role='model',
                    parts=[types.Part(text='You have 2 endpoints.')]
                )
            )
        ]
    )

    async def mock_stream_1(*args, **kwargs):
      yield turn_1_chunk

    async def mock_stream_2(*args, **kwargs):
      yield turn_2_chunk

    with mock.patch.object(_mcp_utils, '_connect_agent_platform_mcp', side_effect=mock_mcp_context) as mock_connect_mcp:
      with mock.patch.object(AsyncModels, '_generate_content_stream', side_effect=[mock_stream_1(), mock_stream_2()]) as mock_generate_stream:

        response_stream = await client.aio.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents='List my endpoints.',
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        mcp_servers=[
                            types.McpServer(name='endpoints')
                        ]
                    )
                ]
            )
        )

        final_text = ''
        async for chunk in response_stream:
          if chunk.text:
            final_text += chunk.text

        assert '2 endpoints' in final_text
        mock_connect_mcp.assert_called_once_with(client._api_client, 'endpoints')
        assert mock_generate_stream.call_count == 2
