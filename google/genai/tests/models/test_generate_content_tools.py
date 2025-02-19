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

import logging
import sys
import typing
import pydantic
import pytest
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper

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


def divide_floats(a: float, b: float) -> float:
  """Divide two floats."""
  return a / b


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_google_search_retrieval',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(None, 'Why is the sky blue?'),
            config={'tools': [{'google_search_retrieval': {}}]},
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_vai_search',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(None, 'what is vertex ai search?'),
            config={
                'tools': [{
                    'retrieval': {
                        'vertex_ai_search': {
                            'datastore': 'projects/vertex-sdk-dev/locations/global/collections/default_collection/dataStores/yvonne_1728691676574'
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
            model='gemini-1.5-flash',
            contents=t.t_contents(None, 'why is the sky blue?'),
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
        name='test_rag_model',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(
                None,
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
        name='test_function_call',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
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
            'Model gemini-1.5-flash-001 does not support code execution for'
            ' Vertex API.'
        ),
        name='test_code_execution',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(
                None,
                'What is the sum of the first 50 prime numbers? '
                + 'Generate and run code for the calculation, and make sure you'
                ' get all 50.',
            ),
            config={'tools': [{'code_execution': {}}]},
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
def test_function_google_search_retrieval(client):
  contents = 'What is the price of GOOG?.'
  config = types.GenerateContentConfig(
      tools=[
          types.Tool(
              google_search_retrieval=types.GoogleSearchRetrieval(
                  dynamic_retrieval_config=types.DynamicRetrievalConfig(
                      mode='MODE_UNSPECIFIED'
                  )
              )
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
        model='gemini-1.5-flash',
        contents=contents,
        config=config,
    )


def test_google_search_retrieval_stream(client):
  for part in client.models.generate_content_stream(
      model='gemini-1.5-flash',
      contents=types.Content(
          role='user',
          parts=[types.Part(text='Why is the sky blue?')],
      ),
      config=types.GenerateContentConfig(
          tools=[types.ToolDict({'google_search_retrieval': {}})],
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
      model='gemini-1.5-flash',
      contents='What is the weather in Boston?',
      config={
          'tools': [get_weather_declaration_only],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )


def test_2_function(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [customized_divide_integers],
      },
  )
  assert '501' in response.text


def test_automatic_function_calling(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert '500' in response.text


def test_automatic_function_calling_stream(client):
  response = client.models.generate_content_stream(
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'disable': True},
      },
  )
  chunks = 0
  for part in response:
    chunks += 1
    assert part.candidates[0].content.parts[0].function_call is not None


def test_automatic_function_calling_no_function_response_stream(client):
  response = client.models.generate_content_stream(
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'disable': True},
      },
  )
  chunks = 0
  async for part in response:
    chunks += 1
    assert part.candidates[0].content.parts[0].function_call is not None


@pytest.mark.asyncio
async def test_automatic_function_calling_no_function_response_stream_async(client):
  response = await client.aio.models.generate_content_stream(
      model='gemini-1.5-flash',
      contents='what is the weather in Boston?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  chunks = 0
  async for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason


@pytest.mark.asyncio
async def test_automatic_function_calling_stream_async(client):
  response = await client.aio.models.generate_content_stream(
      model='gemini-1.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )
  chunks = 0
  async for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason


def test_callable_tools_user_disable_afc(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
      contents='what is the result of 1000/0?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )


def test_automatic_function_calling_float_without_decimal(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
      contents='it is winter now, what is the weather in Boston?',
      config={
          'tools': [get_weather_pydantic_model],
          'automatic_function_calling': {'ignore_call_history': True}
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
      model='gemini-1.5-flash',
      contents='it is winter now, what is the weather in Boston and New York?',
      config={'tools': [get_weather_from_list_of_cities],
              'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  assert 'cold' in response.text and 'Boston' in response.text
  assert 'cold' in response.text and 'New York' in response.text


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

  with pytest_helper.exception_if_mldev(client, ValueError):
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=(
            'I have a one year old cat named Sundae, can you get the'
            ' information of the cat for me?'
        ),
        config={
            'tools': [get_information],
            'automatic_function_calling': {'ignore_call_history': True}
        },
    )
    assert 'Sundae' in response.text
    assert 'cat' in response.text


def test_automatic_function_calling_with_parameterized_generic_union_type(client):
  def describe_cities(
      country: str,
      cities: typing.Optional[list[str]] = None,
  ) -> str:
    if cities is None:
      return 'There are no cities to describe.'
    else:
      return f'The cities in {country} are: {", ".join(cities)} and they are nice.'

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents=('Can you describe the city of San Francisco?'),
      config={
          'tools': [describe_cities],
          'automatic_function_calling': {'ignore_call_history': True}
      },
  )
  assert 'San Francisco' in response.text


@pytest.mark.asyncio
async def test_google_search_retrieval_async(client):
  await client.aio.models.generate_content(
      model='gemini-1.5-flash',
      contents=[
          types.ContentDict(
              {'role': 'user', 'parts': [{'text': 'Why is the sky blue?'}]}
          )
      ],
      config={'tools': [{'google_search_retrieval': {}}]},
  )


def test_empty_tools(client):
  client.models.generate_content(
      model='gemini-1.5-flash',
      contents='What is the price of GOOG?.',
      config={'tools': []},
  )


def test_with_1_empty_tool(client):
  # Bad request for empty tool.
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='What is the price of GOOG?.',
        config={
            'tools': [{}, get_stock_price],
            'automatic_function_calling': {'ignore_call_history': True}
        },
    )


@pytest.mark.asyncio
async def test_google_search_retrieval_stream_async(client):
  async for part in await client.aio.models.generate_content_stream(
      model='gemini-1.5-flash',
      contents='Why is the sky blue?',
      config={'tools': [{'google_search_retrieval': {}}]},
  ):
    pass


@pytest.mark.asyncio
async def test_vai_search_stream_async(client):
  if client._api_client.vertexai:
    async for part in await client.aio.models.generate_content_stream(
        model='gemini-1.5-flash',
        contents='what is vertex ai search?',
        config={
            'tools': [{
                'retrieval': {
                    'vertex_ai_search': {
                        'datastore': 'projects/vertex-sdk-dev/locations/global/collections/default_collection/dataStores/yvonne_1728691676574'
                    }
                }
            }]
        },
    ):
      pass
  else:
    with pytest.raises(ValueError) as e:
      async for part in await client.aio.models.generate_content_stream(
          model='gemini-1.5-flash',
          contents='Why is the sky blue?',
          config={
              'tools': [{
                  'retrieval': {
                      'vertex_ai_search': {
                          'datastore': 'projects/vertex-sdk-dev/locations/global/collections/default_collection/dataStores/yvonne_1728691676574'
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
        model='gemini-1.5-flash',
        contents='what is the result of 1000/2?',
        config={
            'tools': [divide_integers],
            'automatic_function_calling': {'ignore_call_history': True}
        },
    )


@pytest.mark.asyncio
async def test_automatic_function_calling_with_coroutine_function_async(
    client,
):
  async def divide_integers(a: int, b: int) -> int:
    return a // b

  with pytest.raises(errors.UnsupportedFunctionError):
    await client.aio.models.generate_content(
        model='gemini-1.5-flash',
        contents='what is the result of 1000/2?',
        config={
            'tools': [divide_integers],
            'automatic_function_calling': {'ignore_call_history': True}
        },
    )


@pytest.mark.asyncio
async def test_automatic_function_calling_async(client):
  def divide_integers(a: int, b: int) -> int:
    return a // b

  response = await client.aio.models.generate_content(
      model='gemini-1.5-flash',
      contents='what is the result of 1000/2?',
      config={
          'tools': [divide_integers],
          'automatic_function_calling': {'ignore_call_history': True}
      },
  )

  assert '500' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_async_with_exception(client):
  def divide_integers(a: int, b: int) -> int:
    return a // b

  response = await client.aio.models.generate_content(
      model='gemini-1.5-flash',
      contents='what is the result of 1000/0?',
      config={'tools': [divide_integers]},
  )

  assert 'undefined' in response.text


@pytest.mark.asyncio
async def test_automatic_function_calling_async_float_without_decimal(client):
  response = await client.aio.models.generate_content(
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
      contents='it is winter now, what is the weather in Boston?',
      config={
          'tools': [get_weather_pydantic_model],
          'automatic_function_calling': {'ignore_call_history': True},
      },
  )

  # ML Dev couldn't understand pydantic model
  if client.vertexai:
    assert 'cold' in response.text and 'Boston' in response.text


def test_2_function_with_history(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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
      model='gemini-1.5-flash',
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

  assert 'def is_prime' in response.executable_code
  assert 'primes=' in response.code_execution_result


def test_afc_logs_to_logger_instance(client, caplog):
  caplog.set_level(logging.DEBUG, logger='google_genai.models')
  client.models.generate_content(
      model='gemini-1.5-flash',
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
  for log in caplog.records:
    assert log.levelname == 'INFO'
    assert log.name == 'google_genai.models'

  assert 'AFC is enabled with max remote calls: 2' in caplog.text
  assert 'remote call 1 is done' in caplog.text
  assert 'remote call 2 is done' in caplog.text
  assert 'Reached max remote calls' in caplog.text


def test_suppress_logs_with_sdk_logger(client, caplog):
  caplog.set_level(logging.DEBUG, logger='google_genai.models')
  sdk_logger = logging.getLogger('google_genai.models')
  sdk_logger.setLevel(logging.ERROR)
  client.models.generate_content(
      model='gemini-1.5-flash',
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
