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
from unittest import mock
import pytest
from ... import _api_client
from ... import _extra_utils
from ... import client
from ... import models
from ... import types


TEST_NO_AFC_PART = types.Part(
    text=(
        'Okay, here is the weather in San Francisco'
        ' as of approximately  8:10 pm PST on May'
        ' 10, 2023. Please note that the weather'
        ' can change rapidly.'
    )
)

TEST_FUNCTION_CALL_PART = types.Part(
    function_call=types.FunctionCall(
        name='get_current_weather',
        args={'location': 'San Francisco'},
    )
)

TEST_FUNCTION_RESPONSE_PART = types.Part(
    function_response=types.FunctionResponse(
        name='get_current_weather',
        response={'result': 'sunny'},
    )
)

TEST_AFC_TEXT_PART = types.Part(text='San Francisco weather is sunny.')

TEST_NO_AFC_CONTENT = types.Content(
    parts=[TEST_NO_AFC_PART],
    role='model',
)

TEST_FUNCTION_CALL_CONTENT = types.Content(
    parts=[TEST_FUNCTION_CALL_PART],
    role='model',
)

TEST_FUNCTION_RESPONSE_CONTENT = types.Content(
    parts=[TEST_FUNCTION_RESPONSE_PART],
    role='user',
)

TEST_AFC_TEXT_CONTENT = types.Content(
    parts=[TEST_AFC_TEXT_PART],
    role='model',
)

TEST_AFC_HISTORY = [
    types.Content(
        parts=[types.Part(text='what is the weather in San Francisco?')],
        role='user',
    ),
    TEST_FUNCTION_CALL_CONTENT,
    TEST_FUNCTION_RESPONSE_CONTENT,
]


def get_current_weather(location: str) -> str:
  """Returns the current weather.

  Args:
    location: The location of a city and state, e.g. "San Francisco, CA".
  """
  return 'windy'


async def get_current_weather_async(location: str) -> str:
  """Returns the current weather.

  Args:
    location: The location of a city and state, e.g. "San Francisco, CA".
  """
  return 'windy'


def get_aqi_from_city(location: str) -> str:
  """Returns the aqi index of a city.

  Args:
    location: The city and State, e.g. San Francisco, CA.
  """
  return None


@pytest.fixture
def mock_api_client(vertexai=False):
  api_client = mock.MagicMock(spec=client.ApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}  # Ensure headers exist
  api_client.vertexai = vertexai
  return api_client


@pytest.fixture
def mock_get_function_response_parts_none():
  with mock.patch.object(
      _extra_utils,
      'get_function_response_parts',
  ) as mock_get_function_response_parts_none:
    mock_get_function_response_parts_none.return_value = None
    yield mock_get_function_response_parts_none


@pytest.fixture
def mock_get_function_response_parts_none_async():
  with mock.patch.object(
      _extra_utils,
      'get_function_response_parts_async',
  ) as mock_get_function_response_parts_none_async:
    mock_get_function_response_parts_none_async.return_value = None
    yield mock_get_function_response_parts_none_async


@pytest.fixture
def mock_get_function_response_parts() -> list[types.Part]:
  with mock.patch.object(
      _extra_utils, 'get_function_response_parts'
  ) as mock_get_function_response_parts:
    mock_get_function_response_parts.side_effect = [
        [TEST_FUNCTION_RESPONSE_PART],
        [],  # Breaks when the function response is not returned.
    ]
    yield mock_get_function_response_parts


@pytest.fixture
def mock_get_function_response_parts_async() -> list[types.Part]:
  with mock.patch.object(
      _extra_utils, 'get_function_response_parts_async'
  ) as mock_get_function_response_parts_async:
    mock_get_function_response_parts_async.side_effect = [
        [TEST_FUNCTION_RESPONSE_PART],
        [],  # Breaks when the function response is not returned.
    ]
    yield mock_get_function_response_parts_async


@pytest.fixture
def mock_generate_content_stream_no_afc():
  with mock.patch.object(
      models.Models, '_generate_content_stream'
  ) as mock_stream_no_afc:
    mock_stream_no_afc.return_value = [
        types.GenerateContentResponse(
            candidates=[types.Candidate(content=TEST_NO_AFC_CONTENT)]
        )
    ]
    yield mock_stream_no_afc


@pytest.fixture
def mock_generate_content_stream_with_afc():
  with mock.patch.object(
      models.Models, '_generate_content_stream'
  ) as mock_stream_with_afc:
    mock_stream_with_afc.side_effect = [
        [
            types.GenerateContentResponse(
                candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
            )
        ],
        [
            types.GenerateContentResponse(
                candidates=[types.Candidate(content=TEST_AFC_TEXT_CONTENT)]
            )
        ],
    ]
    yield mock_stream_with_afc


@pytest.fixture
def mock_generate_content_stream_no_afc_async():
  with mock.patch.object(
      models.AsyncModels, '_generate_content_stream'
  ) as mock_stream_no_afc:

    async def async_generator():
      yield types.GenerateContentResponse(
          candidates=[types.Candidate(content=TEST_NO_AFC_CONTENT)]
      )

    mock_stream_no_afc.return_value = async_generator()
    yield mock_stream_no_afc


@pytest.fixture
def mock_generate_content_stream_with_afc_async():
  with mock.patch.object(
      models.AsyncModels, '_generate_content_stream'
  ) as mock_stream_with_afc:

    async def async_generator_1():
      yield types.GenerateContentResponse(
          candidates=[types.Candidate(content=TEST_FUNCTION_CALL_CONTENT)]
      )

    async def async_generator_2():
      yield types.GenerateContentResponse(
          candidates=[types.Candidate(content=TEST_AFC_TEXT_CONTENT)]
      )

    mock_stream_with_afc.side_effect = [
        async_generator_1(),
        async_generator_2(),
    ]
    yield mock_stream_with_afc


def test_generate_content_stream_no_function_map(
    mock_generate_content_stream_no_afc,
    mock_get_function_response_parts_none,
):
  """Test when no function tools are provided.

  Expected to answer past weather.
  """
  models_instance = models.Models(api_client_=mock_api_client)
  stream = models_instance.generate_content_stream(
      model='test_model', contents='what is the weather in San Francisco?'
  )
  for chunk in stream:
    assert chunk.text == TEST_NO_AFC_PART.text

  assert mock_generate_content_stream_no_afc.call_count == 1
  assert mock_get_function_response_parts_none.call_count == 0


def test_generate_content_stream_afc_disabled(
    mock_generate_content_stream_with_afc,
    mock_get_function_response_parts_none,
):
  """Test when function tools are provided but AFC is disabled.

  Expected to respond with function call.
  """
  models_instance = models.Models(api_client_=mock_api_client)
  stream = models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=types.GenerateContentConfig(
          tools=[get_current_weather],
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
              disable=True
          ),
      ),
  )
  for chunk in stream:
    # Work as manual function calling.
    assert chunk.candidates[0].content.parts[0].function_call

  assert mock_generate_content_stream_with_afc.call_count == 1
  assert mock_get_function_response_parts_none.call_count == 0


def test_generate_content_stream_no_function_response(
    mock_generate_content_stream_no_afc,
    mock_get_function_response_parts_none,
):
  """Test when function tools are provided and function responses are not returned.

  Expected to answer past weather.
  """
  models_instance = models.Models(api_client_=mock_api_client)
  config = types.GenerateContentConfig(tools=[get_aqi_from_city])
  stream = models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=config,
  )
  for chunk in stream:
    assert chunk.text == TEST_NO_AFC_PART.text

  assert mock_generate_content_stream_no_afc.call_count == 1
  assert mock_get_function_response_parts_none.call_count == 1


def test_generate_content_stream_with_function_tools_used(
    mock_generate_content_stream_with_afc,
    mock_get_function_response_parts,
):
  """Test when function tools are provided and function responses are returned.

  Expected to answer weather based on function response.
  """
  models_instance = models.Models(api_client_=mock_api_client)
  config = types.GenerateContentConfig(tools=[get_current_weather])
  stream = models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=config,
  )

  chunk = None
  for chunk in stream:
    assert chunk.text == TEST_AFC_TEXT_PART.text

  assert mock_generate_content_stream_with_afc.call_count == 2
  assert mock_get_function_response_parts.call_count == 2

  assert chunk is not None
  for i in range(len(chunk.automatic_function_calling_history)):
    assert chunk.automatic_function_calling_history[i].model_dump(
        exclude_none=True
    ) == TEST_AFC_HISTORY[i].model_dump(exclude_none=True)


def test_generate_content_stream_with_thought_summaries(
    mock_generate_content_stream_with_afc,
    mock_get_function_response_parts,
):
  """Test when function tools are provided and thought summaries are enabled.

  Expected to answer weather based on function response.
  """
  models_instance = models.Models(api_client_=mock_api_client)
  config = types.GenerateContentConfig(
      tools=[get_current_weather],
      thinking_config=types.ThinkingConfig(include_thoughts=True),
  )
  stream = models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=config,
  )

  chunk = None
  for chunk in stream:
    assert chunk.text == TEST_AFC_TEXT_PART.text

  assert mock_generate_content_stream_with_afc.call_count == 2
  assert mock_get_function_response_parts.call_count == 2

  assert chunk is not None
  for i in range(len(chunk.automatic_function_calling_history)):
    assert chunk.automatic_function_calling_history[i].model_dump(
        exclude_none=True
    ) == TEST_AFC_HISTORY[i].model_dump(exclude_none=True)


@pytest.mark.asyncio
async def test_generate_content_stream_no_function_map_async(
    mock_generate_content_stream_no_afc,
    mock_get_function_response_parts_none,
):
  """Test when no function tools are provided.

  Expected to answer past weather.
  """
  models_instance = models.Models(api_client_=mock_api_client)
  stream = models_instance.generate_content_stream(
      model='test_model', contents='what is the weather in San Francisco?'
  )
  for chunk in stream:
    assert chunk.text == TEST_NO_AFC_PART.text

  assert mock_generate_content_stream_no_afc.call_count == 1
  assert mock_get_function_response_parts_none.call_count == 0


@pytest.mark.asyncio
async def test_generate_content_stream_afc_disabled_async(
    mock_generate_content_stream_with_afc_async,
    mock_get_function_response_parts_none,
):
  """Test when function tools are provided but AFC is disabled.

  Expected to respond with function call.
  """
  models_instance = models.AsyncModels(api_client_=mock_api_client)
  stream = await models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=types.GenerateContentConfig(
          tools=[get_current_weather],
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
              disable=True
          ),
      ),
  )
  async for chunk in stream:
    # Work as manual function calling.
    assert chunk.candidates[0].content.parts[0].function_call

  assert mock_generate_content_stream_with_afc_async.call_count == 1
  assert mock_get_function_response_parts_none.call_count == 0


@pytest.mark.asyncio
async def test_generate_content_stream_no_function_response_async(
    mock_generate_content_stream_no_afc_async,
    mock_get_function_response_parts_none_async,
):
  """Test when function tools are provided and function responses are not returned.

  Expected to answer past weather.
  """
  models_instance = models.AsyncModels(api_client_=mock_api_client)
  config = types.GenerateContentConfig(tools=[get_aqi_from_city])
  stream = await models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=config,
  )
  async for chunk in stream:
    assert chunk.text == TEST_NO_AFC_PART.text

  assert mock_generate_content_stream_no_afc_async.call_count == 1

  assert mock_get_function_response_parts_none_async.call_count == 1


@pytest.mark.asyncio
async def test_generate_content_stream_with_function_tools_used_async(
    mock_generate_content_stream_with_afc_async,
    mock_get_function_response_parts_async,
):
  """Test when function tools are provided and function responses are returned.

  Expected to answer weather based on function response.
  """
  models_instance = models.AsyncModels(api_client_=mock_api_client)
  config = types.GenerateContentConfig(tools=[get_current_weather])
  stream = await models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=config,
  )

  chunk = None
  async for chunk in stream:
    assert chunk.text == TEST_AFC_TEXT_PART.text

  assert mock_generate_content_stream_with_afc_async.call_count == 2

  assert mock_get_function_response_parts_async.call_count == 2

  assert chunk is not None
  for i in range(len(chunk.automatic_function_calling_history)):
    assert chunk.automatic_function_calling_history[i].model_dump(
        exclude_none=True
    ) == TEST_AFC_HISTORY[i].model_dump(exclude_none=True)


@pytest.mark.asyncio
async def test_generate_content_stream_with_function_async_function_used_async(
    mock_generate_content_stream_with_afc_async,
    mock_get_function_response_parts_async,
):
  """Test when function tools are provided and function responses are returned.

  Expected to answer weather based on function response.
  """
  models_instance = models.AsyncModels(api_client_=mock_api_client)
  config = types.GenerateContentConfig(tools=[get_current_weather_async])
  stream = await models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=config,
  )

  chunk = None
  async for chunk in stream:
    assert chunk.text == TEST_AFC_TEXT_PART.text

  assert mock_generate_content_stream_with_afc_async.call_count == 2

  assert mock_get_function_response_parts_async.call_count == 2

  assert chunk is not None
  for i in range(len(chunk.automatic_function_calling_history)):
    assert chunk.automatic_function_calling_history[i].model_dump(
        exclude_none=True
    ) == TEST_AFC_HISTORY[i].model_dump(exclude_none=True)


@pytest.mark.asyncio
async def test_generate_content_stream_with_thought_summaries_async(
    mock_generate_content_stream_with_afc_async,
    mock_get_function_response_parts_async,
):
  """Test when function tools are provided and thought summaries are enabled.

  Expected to answer weather based on function response.
  """
  models_instance = models.AsyncModels(api_client_=mock_api_client)
  config = types.GenerateContentConfig(
      tools=[get_current_weather],
      thinking_config=types.ThinkingConfig(include_thoughts=True),
  )
  stream = await models_instance.generate_content_stream(
      model='test_model',
      contents='what is the weather in San Francisco?',
      config=config,
  )

  chunk = None
  async for chunk in stream:
    assert chunk.text == TEST_AFC_TEXT_PART.text

  assert mock_generate_content_stream_with_afc_async.call_count == 2

  assert mock_get_function_response_parts_async.call_count == 2

  assert chunk is not None
  for i in range(len(chunk.automatic_function_calling_history)):
    assert chunk.automatic_function_calling_history[i].model_dump(
        exclude_none=True
    ) == TEST_AFC_HISTORY[i].model_dump(exclude_none=True)
