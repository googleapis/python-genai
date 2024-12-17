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


from pydantic import BaseModel, ValidationError
import pytest
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper

safety_settings_with_method = [
    {
        'category': 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'BLOCK_ONLY_HIGH',
        'method': 'SEVERITY',
    },
    {
        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'BLOCK_LOW_AND_ABOVE',
        'method': 'PROBABILITY',
    },
]

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_union_contents_is_string',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash', contents='Tell me a story in 300 words.'
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_contents_is_content',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=types.Content(
                role='user',
                parts=[types.Part(text='Tell me a story in 300 words.')],
            ),
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_contents_is_parts',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=[types.Part(text='Tell me a story in 300 words.')],
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_contents_is_part',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=types.Part(text='Tell me a story in 300 words.'),
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_sync_content_list',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=[
                types.Content(
                    role='user',
                    parts=[types.Part(text='Tell me a story in 300 words.')],
                )
            ],
        ),
    ),
    # You need to enable llama API in Vertex AI Model Garden.
    pytest_helper.TestTableItem(
        name='test_llama',
        parameters=types._GenerateContentParameters(
            model='meta/llama-3.2-90b-vision-instruct-maas',
            contents=t.t_contents(None, 'What is your name?'),
        ),
        exception_if_mldev='404',
        skip_in_api_mode='it will encounter 403 for api mode',
    ),
    pytest_helper.TestTableItem(
        name='test_system_instructions',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(None, 'high'),
            config={
                'system_instruction': t.t_content(
                    None, 'I say high, you say low'
                )
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_simple_shared_generation_config',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'max_output_tokens': 100,
                'top_k': 2,
                'temperature': 0.5,
                'top_p': 0.5,
                'response_mime_type': 'application/json',
                'stop_sequences': ['\n'],
                'candidate_count': 2,
                'seed': 42,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_2_candidates_gemini_1_5_flash',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(None, 'Tell me a story in 30 words.'),
            config={
                'candidate_count': 2,
            },
        ),
        exception_if_mldev='400',
    ),
    pytest_helper.TestTableItem(
        name='test_safety_settings_on_difference',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'safety_settings': safety_settings_with_method,
            },
        ),
        exception_if_mldev='method',
    ),
    pytest_helper.TestTableItem(
        name='test_penalty',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'Tell me a story in 30 words.'),
            config={
                'presence_penalty': 0.5,
                'frequency_penalty': 0.5,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_penalty_gemini_1_5_flash',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=t.t_contents(None, 'Tell me a story in 30 words.'),
            config={
                'presence_penalty': 0.5,
                'frequency_penalty': 0.5,
            },
        ),
        exception_if_mldev='400',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)
pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_async(client):
  response = await client.aio.models.generate_content(
      model='gemini-1.5-flash', contents='Tell me a story in 300 words.'
  )
  assert response.text


def test_sync_stream(client):
  response = client.models.generate_content_stream(
      model='gemini-1.5-flash', contents='Tell me a story in 300 words.'
  )
  chunks = 0
  for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason

  assert chunks > 2


@pytest.mark.asyncio
async def test_async_stream(client):
  chunks = 0
  async for part in client.aio.models.generate_content_stream(
      model='gemini-1.5-flash', contents='Tell me a story in 300 words.'
  ):
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason

  assert chunks > 2


def test_simple_shared_generation_config_stream(client):
  chunks = 0
  for chunk in client.models.generate_content_stream(
      model='gemini-1.5-flash',
      contents='tell me a story in 300 words',
      config={
          'max_output_tokens': 400,
          'top_k': 2,
          'temperature': 0.5,
          'top_p': 0.5,
          'response_mime_type': 'application/json',
          'stop_sequences': ['\n'],
          'seed': 42,
      },
  ):
    chunks += 1
    assert (
        chunk.text is not None or chunk.candidates[0].finish_reason
    ), f'vertexai: {client._api_client.vertexai}, {chunk.candidate[0]}'
  assert chunks >= 2


@pytest.mark.asyncio
async def test_simple_shared_generation_config_async(client):
  response = await client.aio.models.generate_content(
      model='gemini-1.5-flash',
      contents='tell me a story in 300 words',
      config={
          'max_output_tokens': 400,
          'top_k': 2,
          'temperature': 0.5,
          'top_p': 0.5,
          'response_mime_type': 'application/json',
          'stop_sequences': ['\n'],
          'seed': 42,
      },
  )


@pytest.mark.asyncio
async def test_simple_shared_generation_config_stream_async(client):
  chunks = 0
  async for part in client.aio.models.generate_content_stream(
      model='gemini-1.5-flash',
      contents='tell me a story in 300 words',
      config={
          'max_output_tokens': 400,
          'top_k': 2,
          'temperature': 0.5,
          'top_p': 0.5,
          'response_mime_type': 'application/json',
          'stop_sequences': ['\n'],
          'seed': 42,
      },
  ):
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason
  assert chunks >= 2


def test_log_probs(client):
  with pytest_helper.exception_if_mldev(client, ValueError):
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='What is your name?',
        config={
            'logprobs': 2,
            'presence_penalty': 0.5,
            'frequency_penalty': 0.5,
            'response_logprobs': True,
        },
    )


def test_simple_config(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='What is your name?',
      config={
          'max_output_tokens': 3,
          'top_k': 2,
      },
  )
  assert response.text


def test_safety_settings(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='What is your name?',
      config={
          'safety_settings': [{
              'category': 'HARM_CATEGORY_HATE_SPEECH',
              'threshold': 'BLOCK_ONLY_HIGH',
          }]
      },
  )
  assert response.text


def test_safety_settings_on_difference_stream(client):
  safety_settings = [
      {
          'category': 'HARM_CATEGORY_HATE_SPEECH',
          'threshold': 'BLOCK_ONLY_HIGH',
          'method': 'SEVERITY',
      },
      {
          'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
          'threshold': 'BLOCK_LOW_AND_ABOVE',
          'method': 'PROBABILITY',
      },
  ]
  if client._api_client.vertexai:
    for part in client.models.generate_content_stream(
        model='gemini-1.5-flash',
        contents='What is your name?',
        config={
            'safety_settings': safety_settings,
        },
    ):
      pass
  else:
    with pytest.raises(ValueError) as e:
      for part in client.models.generate_content_stream(
          model='gemini-1.5-flash',
          contents='What is your name?',
          config={
              'safety_settings': safety_settings,
          },
      ):
        pass
    assert 'method' in str(e)


def test_pydantic_schema(client):
  class CountryInfo(BaseModel):
    name: str
    pupulation: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': CountryInfo,
      },
  )
  assert isinstance(response.parsed, CountryInfo)


def test_json_schema(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': {
              'required': [
                  'name',
                  'pupulation',
                  'capital',
                  'continent',
                  'gdp',
                  'official_language',
                  'total_area_sq_mi',
              ],
              'properties': {
                  'name': {'type': 'STRING'},
                  'pupulation': {'type': 'INTEGER'},
                  'capital': {'type': 'STRING'},
                  'continent': {'type': 'STRING'},
                  'gdp': {'type': 'INTEGER'},
                  'official_language': {'type': 'STRING'},
                  'total_area_sq_mi': {'type': 'INTEGER'},
              },
              'type': 'OBJECT',
          },
      },
  )
  assert isinstance(response.parsed, dict)


def test_function(client):
  def get_weather(city: str) -> str:
    return f'The weather in {city} is sunny and 100 degrees.'

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents=(
          'What is the weather like in Sunnyvale? Answer in very short'
          ' sentence.'
      ),
      config={
          'tools': [get_weather],
      },
  )
  assert '100' in response.text


def test_invalid_input_without_transformer(client):
  with pytest.raises(ValidationError) as e:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='What is your name',
        config={
            'input_that_does_not_exist': 'what_ever_value',
        },
    )
  assert 'input_that_does_not_exist' in str(e)
  assert 'Extra inputs are not permitted' in str(e)


def test_invalid_input_with_transformer_dict(client):
  with pytest.raises(ValidationError) as e:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents={'invalid_key': 'invalid_value'},
    )
  assert 'invalid_key' in str(e.value)


def test_invalid_input_with_transformer_list(client):
  with pytest.raises(ValidationError) as e:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents=[{'invalid_key': 'invalid_value'}],
    )
  assert 'invalid_key' in str(e.value)


def test_invalid_input_for_simple_parameter(client):
  with pytest.raises(ValidationError) as e:
    client.models.generate_content(
        model=5,
        contents='What is your name?',
    )
  assert 'model' in str(e)


def test_catch_stack_trace_in_error_handling(client):
  try:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='What is your name?',
        config={
            'response_modalities': ['AUDIO']
        },
    )
  except errors.ClientError as e:
    # Note that the stack trace is truncated in replay file, therefore this is
    # the best we can do in testing error handling. In api mode, the stack trace
    # is:
    # {
    #     'error': {
    #         'code': 400,
    #         'message': 'Multi-modal output is not supported.',
    #         'status': 'INVALID_ARGUMENT',
    #         'details': [{
    #             '@type': 'type.googleapis.com/google.rpc.DebugInfo',
    #             'detail': '[ORIGINAL ERROR] generic::invalid_argument: '
    #                      'Multi-modal output is not supported. '
    #                      '[google.rpc.error_details_ext] '
    #                      '{ message: "Multi-modal output is not supported." }'
    #         }]
    #     }
    # }
    assert e.details == {'code': 400, 'message': '', 'status': 'UNKNOWN'}
