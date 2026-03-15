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
        exception_if_vertex='is not supported in Vertex AI',
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
        exception_if_vertex='is not supported in Vertex AI',
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
        exception_if_vertex='is not supported in Vertex AI',
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
        exception_if_vertex='is not supported in Vertex AI',
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
]


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)
pytest_plugins = ('pytest_asyncio',)


# Cannot be included in test_table because json serialization fails on function.
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
  # bad request to combine function call and google search retrieval
  with pytest.raises(errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
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


@pytest.mark.skipif(
    sys.version_info >= (3, 13),
    reason=(
        'object type is dumped as <Type.OBJECT: "OBJECT"> as opposed to'
        ' "OBJECT" in Python 3.13'
    ),
)
def test_function_calling_without_implementation(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='What is the weather in Boston?',
      config={
          'tools': [get_weather_declaration_only],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )


def test_2_function(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='What is the price of GOOG? And what is the weather in Boston?',
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  assert '1000' in response.text
  assert 'Boston' in response.text
  assert 'sunny' in response.text


@pytest.mark.asyncio
async def test_2_function_async(client):
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='What is the price of GOOG? And what is the weather in Boston?',
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  assert '1000' in response.text
  assert 'Boston' in response.text
  assert 'sunny' in response.text


def test_automatic_function_calling_with_customized_math_rule(client):
  def customized_divide_integers(numerator: int, denominator: int) -> int:
    """Divide two integers with customized math rule."""
    return numerator // denominator + 1

  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [customized_divide_integers],
      },
  )
  assert '501' in response.text


def test_automatic_function_calling(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert '500' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_with_async_function(client):
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1001.0/2.0?',
      config={
          'tools': [divide_floats_async],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert '500.5' in response.text


def test_automatic_function_calling_stream(client):
  response = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  chunks = 0
  for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason


def test_disable_automatic_function_calling_stream(client):
  # If AFC is disabled, the response should contain a function call.
  response = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'disable': True},
      },
  )
  chunks = 0
  for chunk in response:
    chunks += 1
    assert chunk.parts[0].function_call is not None


def test_automatic_function_calling_no_function_response_stream(client):
  response = client.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the weather in Boston?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  chunks = 0
  for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason


@pytest.mark.asyncio
async def test_disable_automatic_function_calling_stream_async(client):
  # If AFC is disabled, the response should contain a function call.
  response = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'disable': True},
      },
  )
  chunks = 0
  async for chunk in response:
    chunks += 1
    assert chunk.parts[0].function_call is not None


@pytest.mark.asyncio
async def test_automatic_function_calling_no_function_response_stream_async(
    client,
):
  response = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the weather in Boston?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  chunks = 0
  async for chunk in response:
    chunks += 1
    assert chunk.text is not None or chunk.candidates[0].finish_reason


@pytest.mark.asyncio
async def test_automatic_function_calling_stream_async(client):
  response = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  chunks = 0
  async for chunk in response:
    chunks += 1
    assert chunk.text is not None or chunk.candidates[0].finish_reason


def test_callable_tools_user_disable_afc(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': True,
              'ignore_call_history': True,
          },
      },
  )


def test_callable_tools_user_disable_afc_with_max_remote_calls(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': True,
              'maximum_remote_calls': 2,
              'ignore_call_history': True,
          },
      },
  )


def test_callable_tools_user_disable_afc_with_max_remote_calls_negative(
    client,
):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': True,
              'maximum_remote_calls': -1,
              'ignore_call_history': True,
          },
      },
  )


def test_callable_tools_user_disable_afc_with_max_remote_calls_zero(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': True,
              'maximum_remote_calls': 0,
              'ignore_call_history': True,
          },
      },
  )


def test_callable_tools_user_enable_afc(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': False,
              'ignore_call_history': True,
          },
      },
  )


def test_callable_tools_user_enable_afc_with_max_remote_calls(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': False,
              'maximum_remote_calls': 2,
              'ignore_call_history': True,
          },
      },
  )


def test_callable_tools_user_enable_afc_with_max_remote_calls_negative(
    client,
):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': False,
              'maximum_remote_calls': -1,
              'ignore_call_history': True,
          },
      },
  )


def test_callable_tools_user_enable_afc_with_max_remote_calls_zero(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': False,
              'maximum_remote_calls': 0,
              'ignore_call_history': True,
          },
      },
  )


def test_automatic_function_calling_with_exception(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/0?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )


def test_automatic_function_calling_float_without_decimal(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000.0/2.0?',
      config={
          'tools': [divide_floats, divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert '500.0' in response.text


def test_automatic_function_calling_with_pydantic_model(client):
  class CityObject(pydantic.BaseModel):
    city_name: str

  def get_weather_pydantic_model(
      city_object: CityObject, is_winter: bool
  ) -> str:
    if is_winter:
      return f'The weather in {city_object.city_name} is cold and 10 degrees.'
    else:
      return f'The weather in {city_object.city_name} is sunny and 100 degrees.'

  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='it is winter now, what is the weather in Boston?',
      config={
          'tools': [get_weather_pydantic_model],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert 'cold' in response.text and 'Boston' in response.text


def test_automatic_function_calling_with_pydantic_model_in_list_type(client):
  class CityObject(pydantic.BaseModel):
    city_name: str

  def get_weather_from_list_of_cities(
      city_object_list: list[CityObject], is_winter: bool
  ) -> str:
    result = ''
    if is_winter:
      for city_object in city_object_list:
        result += (
            f'The weather in {city_object.city_name} is cold and 10 degrees.\n'
        )
    else:
      for city_object in city_object_list:
        result += (
            f'The weather in {city_object.city_name} is sunny and 100'
            ' degrees.\n'
        )
    return result

  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='it is winter now, what is the weather in Boston and New York?',
      config={
          'tools': [get_weather_from_list_of_cities],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert 'cold' in response.text and 'Boston' in response.text
  assert 'cold' in response.text and 'New York' in response.text


# TODO(b/397404656): modify this test to pass in api mode
def test_automatic_function_calling_with_pydantic_model_in_union_type(client):
  class AnimalObject(pydantic.BaseModel):
    name: str
    age: int
    species: str

  class PlantObject(pydantic.BaseModel):
    name: str
    height: float
    color: str

  def get_information(
      object_of_interest: typing.Union[AnimalObject, PlantObject],
  ) -> str:
    if isinstance(object_of_interest, AnimalObject):
      return (
          f'The animal is of {object_of_interest.species} species and is named'
          f' {object_of_interest.name} is {object_of_interest.age} years old'
      )
    elif isinstance(object_of_interest, PlantObject):
      return (
          f'The plant is named {object_of_interest.name} and is'
          f' {object_of_interest.height} meters tall and is'
          f' {object_of_interest.color} color'
      )
    else:
      return 'The animal is not supported'

  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=(
            'I have a one year old cat named Sundae, can you get the'
            ' information of the cat for me?'
        ),
        config={
            'system_instruction': (
                'you answer questions based on the tools provided'
            ),
            'tools': [get_information],
            'automatic_function_calling': {'ignore_call_history': True},
        },
    )
    assert 'Sundae' in response.text
    assert 'cat' in response.text


def test_automatic_function_calling_with_union_operator(client):
  class AnimalObject(pydantic.BaseModel):
    name: str
    age: int
    species: str

  def get_information(
      object_of_interest: str | AnimalObject,
  ) -> str:
    if isinstance(object_of_interest, AnimalObject):
      return (
          f'The animal is of {object_of_interest.species} species and is named'
          f' {object_of_interest.name} is {object_of_interest.age} years old'
      )
    else:
      return f'The object of interest is {object_of_interest}'

  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=(
          'I have a one year old cat named Sundae, can you get the'
          ' information of the cat for me?'
      ),
      config={
          'tools': [get_information],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  assert response.text


def test_automatic_function_calling_with_tuple_param(client):
  def output_latlng(
      latlng: tuple[float, float],
  ) -> str:
    return f'The latitude is {latlng[0]} and the longitude is {latlng[1]}'

  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=(
          'The coordinates are (51.509, -0.118). What is the latitude and longitude?'
      ),
      config={
          'tools': [output_latlng],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  assert response.text


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is only supported in Python 3.10 and above.',
)
def test_automatic_function_calling_with_union_operator_return_type(client):
  def get_cheese_age(cheese: int) -> int | float:
    """
    Retrieves data about the age of the cheese given its ID.

    Args:
        cheese_id: The ID of the cheese.

    Returns:
        An int or float of the age of the cheese.
    """
    if cheese == 1:
      return 2.5
    elif cheese == 2:
      return 3
    else:
      return 0.0

  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='How old is the cheese with id 2?',
      config={
          'tools': [get_cheese_age],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  assert '3' in response.text


def test_automatic_function_calling_with_parameterized_generic_union_type(
    client,
):
  def describe_cities(
      country: str,
      cities: typing.Optional[list[str]] = None,
  ) -> str:
    'Given a country and an optional list of cities, describe the cities.'
    if cities is None:
      return 'There are no cities to describe.'
    else:
      return (
          f'The cities in {country} are: {", ".join(cities)} and they are nice.'
      )

  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='Can you describe the city of San Francisco, USA?',
      config={
          'tools': [describe_cities],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  assert 'San Francisco' in response.text


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
  # Bad request for empty tool.
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents='What is the price of GOOG?.',
        config={
            'tools': [{}, get_stock_price],
            'automatic_function_calling': {'ignore_call_history': True},
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


def test_automatic_function_calling_with_coroutine_function(client):
  async def divide_integers(a: int, b: int) -> int:
    return a // b

  with pytest.raises(errors.UnsupportedFunctionError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents='what is the result of 1000/2?',
        config={
            'tools': [divide_integers],
            'automatic_function_calling': {'ignore_call_history': True},
        },
    )


@pytest.mark.asyncio
async def test_automatic_function_calling_with_coroutine_function_async(
    client,
):
  async def divide_integers(a: int, b: int) -> int:
    return a // b

  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert '500' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_async(client):
  def divide_integers(a: int, b: int) -> int:
    return a // b

  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert '500' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_async_with_exception(client):
  def mystery_function(a: int, b: int) -> int:
    return a // b

  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/0?',
      config={
          'tools': [divide_integers],
          'system_instruction': (
              'you must first look at the tools and then think about answers'
          ),
      },
  )
  assert response.automatic_function_calling_history
  assert (
      response.automatic_function_calling_history[-1]
      .parts[0]
      .function_response.response['error']
  )


@pytest.mark.asyncio
async def test_automatic_function_calling_async_float_without_decimal(client):
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000.0/2.0?',
      config={
          'tools': [divide_floats, divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert '500.0' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_async_with_pydantic_model(client):
  class CityObject(pydantic.BaseModel):
    city_name: str

  def get_weather_pydantic_model(
      city_object: CityObject, is_winter: bool
  ) -> str:
    if is_winter:
      return f'The weather in {city_object.city_name} is cold and 10 degrees.'
    else:
      return f'The weather in {city_object.city_name} is sunny and 100 degrees.'

  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='it is winter now, what is the weather in Boston?',
      config={
          'tools': [get_weather_pydantic_model],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  # ML Dev couldn't understand pydantic model
  if client.vertexai:
    assert 'cold' in response.text and 'Boston' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_async_with_async_function(client):
  async def get_current_weather_async(city: str) -> str:
    """Returns the current weather in the city."""

    return 'windy'

  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the weather in San Francisco?',
      config={
          'tools': [get_current_weather_async],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert 'windy' in response.text
  assert 'San Francisco' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_async_with_async_function_stream(
    client,
):
  async def get_current_weather_async(city: str) -> str:
    """Returns the current weather in the city."""

    return 'windy'

  response = await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents='what is the weather in San Francisco?',
      config={
          'tools': [get_current_weather_async],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  chunk = None
  async for chunk in response:
    if chunk.parts[0].function_call:
      assert chunk.parts[0].function_call.name == 'get_current_weather_async'
      assert chunk.parts[0].function_call.args['city'] == 'San Francisco'


def test_2_function_with_history(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='What is the price of GOOG? And what is the weather in Boston?',
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'ignore_call_history': False},
      },
  )

  actual_history = response.automatic_function_calling_history

  assert actual_history[0].role == 'user'
  assert (
      actual_history[0].parts[0].text
      == 'What is the price of GOOG? And what is the weather in Boston?'
  )

  assert actual_history[1].role == 'model'
  assert actual_history[1].parts[0].function_call.model_dump_json(
      exclude_none=True
  ) == types.FunctionCall(
      name='get_stock_price',
      args={'symbol': 'GOOG'},
  ).model_dump_json(
      exclude_none=True
  )
  assert actual_history[1].parts[1].function_call.model_dump_json(
      exclude_none=True
  ) == types.FunctionCall(
      name='get_weather',
      args={'city': 'Boston'},
  ).model_dump_json(
      exclude_none=True
  )

  assert actual_history[2].role == 'user'
  assert actual_history[2].parts[0].function_response.model_dump_json(
      exclude_none=True
  ) == types.FunctionResponse(
      name='get_stock_price', response={'result': '1000'}
  ).model_dump_json(
      exclude_none=True
  )
  assert actual_history[2].parts[1].function_response.model_dump_json(
      exclude_none=True
  ) == types.FunctionResponse(
      name='get_weather',
      response={'result': 'The weather in Boston is sunny and 100 degrees.'},
  ).model_dump_json(
      exclude_none=True
  )


@pytest.mark.asyncio
async def test_2_function_with_history_async(client):
  response = await client.aio.models.generate_content(
      model='gemini-2.5-flash',
      contents='What is the price of GOOG? And what is the weather in Boston?',
      config={
          'tools': [get_weather, get_stock_price],
          'automatic_function_calling': {'ignore_call_history': False},
      },
  )

  actual_history = response.automatic_function_calling_history

  assert actual_history[0].role == 'user'
  assert (
      actual_history[0].parts[0].text
      == 'What is the price of GOOG? And what is the weather in Boston?'
  )

  assert actual_history[1].role == 'model'
  assert actual_history[1].parts[0].function_call.model_dump_json(
      exclude_none=True
  ) == types.FunctionCall(
      name='get_stock_price',
      args={'symbol': 'GOOG'},
  ).model_dump_json(
      exclude_none=True
  )
  assert actual_history[1].parts[1].function_call.model_dump_json(
      exclude_none=True
  ) == types.FunctionCall(
      name='get_weather',
      args={'city': 'Boston'},
  ).model_dump_json(
      exclude_none=True
  )

  assert actual_history[2].role == 'user'
  assert actual_history[2].parts[0].function_response.model_dump_json(
      exclude_none=True
  ) == types.FunctionResponse(
      name='get_stock_price', response={'result': '1000'}
  ).model_dump_json(
      exclude_none=True
  )
  assert actual_history[2].parts[1].function_response.model_dump_json(
      exclude_none=True
  ) == types.FunctionResponse(
      name='get_weather',
      response={'result': 'The weather in Boston is sunny and 100 degrees.'},
  ).model_dump_json(
      exclude_none=True
  )


class FunctionHolder:
  NAME = 'FunctionHolder'

  def is_a_duck(self, number: int) -> str:
    return self.NAME + 'says isOdd: ' + str(number % 2 == 1)

  def is_a_rabbit(self, number: int) -> str:
    return self.NAME + 'says isEven: ' + str(number % 2 == 0)


def test_class_method_tools(client):
  # This test is to make sure that instance method tools can be used in
  # the generate_content request.

  function_holder = FunctionHolder()
  response = client.models.generate_content(
      model='gemini-2.0-flash-exp',
      contents=(
          'Print the verbatim output of is_a_duck and is_a_rabbit for the'
          ' number 100.'
      ),
      config={
          'tools': [function_holder.is_a_duck, function_holder.is_a_rabbit],
      },
  )
  assert 'FunctionHolder' in response.text


def test_disable_afc_in_any_mode(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config=types.GenerateContentConfig(
          tools=[divide_integers],
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
              disable=True
          ),
          tool_config=types.ToolConfig(
              function_calling_config=types.FunctionCallingConfig(mode='ANY')
          ),
      ),
  )


def test_afc_once_in_any_mode(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config=types.GenerateContentConfig(
          tools=[divide_integers],
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
              maximum_remote_calls=2
          ),
          tool_config=types.ToolConfig(
              function_calling_config=types.FunctionCallingConfig(mode='ANY')
          ),
      ),
  )


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


def test_afc_logs_to_logger_instance(client, caplog):
  caplog.set_level(logging.DEBUG, logger='google_genai.models')
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': False,
              'maximum_remote_calls': 1,
              'ignore_call_history': True,
          },
      },
  )
  for log in caplog.records:
    assert log.levelname == 'INFO'
    assert log.name == 'google_genai.models'

  assert 'AFC is enabled with max remote calls: 1' in caplog.text
  assert 'remote call 1 is done' in caplog.text
  assert 'Reached max remote calls' in caplog.text


def test_suppress_logs_with_sdk_logger(client, caplog):
  caplog.set_level(logging.DEBUG, logger='google_genai.models')
  sdk_logger = logging.getLogger('google_genai.models')
  sdk_logger.setLevel(logging.ERROR)
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {
              'disable': False,
              'maximum_remote_calls': 2,
              'ignore_call_history': True,
          },
      },
  )
  assert not caplog.text


def test_tools_chat_curation(client, caplog):
  caplog.set_level(logging.DEBUG, logger='google_genai.models')
  sdk_logger = logging.getLogger('google_genai.models')
  sdk_logger.setLevel(logging.ERROR)

  config = {
      'tools': [{'function_declarations': function_declarations}],
  }

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
      model='gemini-2.5-pro',
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
      model='gemini-2.5-pro',
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
      model='gemini-2.5-pro',
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
        model='gemini-2.5-pro',
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
