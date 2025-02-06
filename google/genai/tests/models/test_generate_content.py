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

import enum

from pydantic import BaseModel, ValidationError
from typing import Optional, Union
import pytest
import json
import sys
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper
from enum import Enum


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

test_http_options = {'api_version': 'v1', 'headers': {'test': 'headers'}}


class InstrumentEnum(Enum):
  PERCUSSION = 'Percussion'
  STRING = 'String'
  WOODWIND = 'Woodwind'
  BRASS = 'Brass'
  KEYBOARD = 'Keyboard'


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_http_options_in_method',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'http_options': test_http_options,
            },
        ),
    ),
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
        name='test_labels',
        exception_if_mldev='not supported',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash-002',
            contents=t.t_contents(None, 'What is your name?'),
            config={
                'labels': {'label1': 'value1', 'label2': 'value2'},
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
    pytest_helper.TestTableItem(
        name='test_google_search_tool',
        parameters=types._GenerateContentParameters(
            model='gemini-2.0-flash-exp',
            contents=t.t_contents(None, 'Why is the sky blue?'),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_speech_with_config',
        parameters=types._GenerateContentParameters(
            model='gemini-2.0-flash-exp',
            contents=t.t_contents(
                None, 'Produce a speech response saying "Cheese"'
            ),
            config=types.GenerateContentConfig(
                response_modalities=['audio'],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='charon'
                        )
                        )
                    )
                ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_union_speech_string_config',
        parameters=types._GenerateContentParameters(
            model='gemini-2.0-flash-exp',
            contents='Say hello!',
            config=types.GenerateContentConfig(
                response_modalities=['audio'], speech_config='charon'
            ),
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_audio_timestamp',
        parameters=types._GenerateContentParameters(
            model='gemini-1.5-flash',
            contents=[types.Content(
                role='user',
                parts=[
                    types.Part(
                        file_data=types.FileData(
                            file_uri='gs://cloud-samples-data/generative-ai/audio/pixel.mp3',
                            mime_type='audio/mpeg')),
                    types.Part(text="""Can you transcribe this interview, in the
                           format of timecode, speaker, caption. Use speaker A, 
                           speaker B, etc. to identify speakers."""),]
            )],
            config=types.GenerateContentConfig(audio_timestamp=True),
        ),
        exception_if_mldev='not supported',
    )
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
      model='gemini-1.5-flash',
      contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
  )
  assert response.text


def test_sync_stream(client):
  response = client.models.generate_content_stream(
      model='gemini-1.5-flash',
      contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
  )
  chunks = 0
  for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason

  assert chunks > 2


@pytest.mark.asyncio
async def test_async_stream(client):
  chunks = 0
  async for part in await client.aio.models.generate_content_stream(
      model='gemini-1.5-flash', contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
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
  async for part in await client.aio.models.generate_content_stream(
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
  # ML DEV discovery doc supports response_logprobs but the backend
  # does not.
  # TODO: update replay test json files when ML Dev backend is updated.
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
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


def test_safety_settings_on_difference_stream_with_lower_enum(client):
  safety_settings = [
      {
          'category': 'harm_category_hate_speech',
          'threshold': 'block_only_high',
          'method': 'severity',
      },
      {
          'category': 'harm_category_dangerous_content',
          'threshold': 'block_low_and_above',
          'method': 'probability',
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
    # We need at least one test with `title` in properties in case the schema
    # edits go wrong.
    title: str
    population: int
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


def test_pydantic_schema_with_default_value(client):
  class Restaurant(BaseModel):
    name: str
    rating: int = 0
    city: Optional[str] = 'New York'

  if client._api_client.vertexai:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Can you recommend a restaurant for me?',
        config={
            'response_mime_type': 'application/json',
            'response_schema': Restaurant,
        },
    )
    assert isinstance(response.parsed, Restaurant)
  else:
    with pytest.raises(ValueError) as e:
      client.models.generate_content(
          model='gemini-1.5-flash',
          contents='Can you recommend a restaurant for me?',
          config={
              'response_mime_type': 'application/json',
              'response_schema': Restaurant,
          },
      )
    assert 'Default value is not supported' in str(e)


def test_repeated_pydantic_schema(client):
  # This tests the defs handling on the pydantic side.
  class Person(BaseModel):
    name: str

  class Relationship(BaseModel):
    relationship: str
    person1: Person
    person2: Person

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Create a couple.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': Relationship,
      },
  )
  assert isinstance(response.parsed, Relationship)


def test_int_schema(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents="what's your favorite number?",
      config={
          'response_mime_type': 'application/json',
          'response_schema': int,
      },
  )
  assert isinstance(response.parsed, int)


def test_nested_list_of_int_schema(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents="Can you return two matrices, a 2x3 and a 3x4?",
      config={
          'response_mime_type': 'application/json',
          'response_schema': list[list[list[int]]],
      },
  )
  assert isinstance(response.parsed[0][0][0], int)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_pydantic_schema_with_none(client):
  class CountryInfo(BaseModel):
    name: str
    total_area_sq_mi: int | None = None

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': CountryInfo,
      },
  )
  assert isinstance(response.parsed, CountryInfo)
  assert type(response.parsed.total_area_sq_mi) in [int, None]


def test_pydantic_schema_with_optional_none(client):
  class CountryInfo(BaseModel):
    name: str
    total_area_sq_mi: Optional[int] = None

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information of the United States but don\'t include the total area.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': CountryInfo,
      },
  )
  assert isinstance(response.parsed, CountryInfo)
  assert response.parsed.total_area_sq_mi is None


def test_pydantic_schema_from_json(client):
  class CountryInfo(BaseModel):
    name: str
    pupulation: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

  schema = types.Schema.model_validate(CountryInfo.model_json_schema())

  print(schema)

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information of the United States.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=schema,
      ),
  )

  print(response.text)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_schema_with_union_type(client):
  # TODO(b/392920967): any_of is not supported in mldev
  with pytest_helper.exception_if_mldev(client, ValueError):
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Give me a random number, either as an integers or written out as words.',
        config=types.GenerateContentConfig.model_validate(dict(
            response_mime_type='application/json',
            response_schema=int | str,
        ))
    )
    assert type(response.parsed) in (int, str)


def test_schema_with_union_type_all_py_versions(client):
  # TODO(b/392920967): any_of is not supported in mldev
  with pytest_helper.exception_if_mldev(client, ValueError):
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents="Give me a random number, either an integer or a float.",
        config={
            'response_mime_type': 'application/json',
            'response_schema': Union[int, float],
        },
    )
    assert type(response.parsed) in (int, float)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_list_schema_with_union_type(client):
  if client._api_client.vertexai:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Give me a list of 5 random numbers, including some integers and some written out as words.',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=list[int | str],
        )
    )
    for item in response.parsed:
      assert isinstance(item, int) or isinstance(item, str)
  else:
    with pytest.raises(ValueError) as e:
      client.models.generate_content(
          model='gemini-1.5-flash',
          contents='Give me a random number, either as an integers or written out as words.',
          config=types.GenerateContentConfig(
              response_mime_type='application/json',
              response_schema=list[int | str],
          )
      )
    assert 'AnyOf is not supported' in str(e)


def test_list_schema_with_union_type_all_py_versions(client):
  if client._api_client.vertexai:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Give me a list of 5 random numbers, including some integers and some written out as words.',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=list[Union[int, str]],
        )
    )
    for item in response.parsed:
      assert isinstance(item, int) or isinstance(item, str)
  else:
    with pytest.raises(ValueError) as e:
      client.models.generate_content(
          model='gemini-1.5-flash',
          contents='Give me a random number, either as an integers or written out as words.',
          config=types.GenerateContentConfig(
              response_mime_type='application/json',
              response_schema=list[Union[int, str]],
          )
      )
    assert 'AnyOf is not supported' in str(e)


def test_list_of_pydantic_schema(client):
  class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information for the United States, Canada, and Mexico.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=list[CountryInfo],
      )
  )
  assert isinstance(response.parsed, list)
  assert len(response.parsed) == 3
  assert isinstance(response.parsed[0], CountryInfo)


def test_nested_list_of_pydantic_schema(client):
  class Recipe(BaseModel):
    name: str
    cook_time: str

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents="I\'m writing three recipe books, one each for United States, Canada, and Mexico. "
               "Can you give some recipe ideas, at least 2 per book?",
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=list[list[Recipe]],
      )
  )
  assert isinstance(response.parsed, list)
  assert len(response.parsed) == 3
  assert isinstance(response.parsed[0][0], Recipe)


def test_list_of_pydantic_schema_with_dict_config(client):
  class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information for the United States, Canada, and Mexico.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': list[CountryInfo],
      }
  )
  assert isinstance(response.parsed, list)
  assert len(response.parsed) == 3
  assert isinstance(response.parsed[0], CountryInfo)


def test_pydantic_schema_with_nested_class(client):
  class CurrencyInfo(BaseModel):
    name: str

  class CountryInfo(BaseModel):
    name: str
    currency: CurrencyInfo

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information for the United States',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=CountryInfo,
      )
  )
  assert isinstance(response.parsed, CountryInfo)
  assert isinstance(response.parsed.currency, CurrencyInfo)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_pydantic_schema_with_union_type(client):

  class CountryInfo(BaseModel):
    name: str
    restaurants_per_capita: int | float

  with pytest_helper.exception_if_mldev(client, ValueError):
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Give me information for the United States',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=CountryInfo,
        )
    )
    assert isinstance(response.parsed, CountryInfo)
    assert type(response.parsed.restaurants_per_capita) in (int, float)


def test_pydantic_schema_with_union_type_all_py_versions(client):

  class CountryInfo(BaseModel):
    name: str
    restaurants_per_capita: Union[int, float]

  with pytest_helper.exception_if_mldev(client, ValueError):
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Give me information for the United States',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=CountryInfo,
        )
    )
    assert isinstance(response.parsed, CountryInfo)
    assert type(response.parsed.restaurants_per_capita) in (int, float)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_union_of_pydantic_schema(client):

  class SongLyric(BaseModel):
    song_name: str
    lyric: str
    artist: str

  class FunFact(BaseModel):
    fun_fact: str

  with pytest_helper.exception_if_mldev(client, ValueError):
      response = client.models.generate_content(
          model='gemini-1.5-flash',
          contents='Can you give me a Taylor Swift song lyric or a fun fact?',
          config=types.GenerateContentConfig(
              response_mime_type='application/json',
              response_schema=SongLyric | FunFact,
          )
      )
      assert type(response.parsed) in (SongLyric, FunFact)


def test_union_of_pydantic_schema_all_py_versions(client):

  class SongLyric(BaseModel):
    song_name: str
    lyric: str
    artist: str

  class FunFact(BaseModel):
    fun_fact: str

  with pytest_helper.exception_if_mldev(client, ValueError):
      response = client.models.generate_content(
          model='gemini-1.5-flash',
          contents='Can you give me a Taylor Swift song lyric or a fun fact?',
          config=types.GenerateContentConfig(
              response_mime_type='application/json',
              response_schema=Union[SongLyric, FunFact],
          )
      )
      assert type(response.parsed) in (SongLyric, FunFact)


def test_pydantic_schema_with_nested_enum(client):
  class Continent(Enum):
    ASIA = 'Asia'
    AFRICA = 'Africa'
    ANTARCTICA = 'Antarctica'
    EUROPE = 'Europe'
    NORTH_AMERICA = 'North America'
    SOUTH_AMERICA = 'South America'
    AUSTRALIA = 'Australia'

  class CountryInfo(BaseModel):
    name: str
    continent: Continent

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information for the United States',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=CountryInfo,
      )
  )
  assert isinstance(response.parsed, CountryInfo)
  assert isinstance(response.parsed.continent, Continent)


def test_pydantic_schema_with_nested_list_class(client):
  class CurrencyInfo(BaseModel):
    name: str

  class CountryInfo(BaseModel):
    name: str
    currency: list[CurrencyInfo]

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information for the United States.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=CountryInfo,
      )
  )
  assert isinstance(response.parsed, CountryInfo)
  assert isinstance(response.parsed.currency[0], CurrencyInfo)


def test_list_of_pydantic_schema_with_nested_class(client):
  class CurrencyInfo(BaseModel):
    name: str
    code: str
    symbol: str

  class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int
    currency: CurrencyInfo

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information for the United States, Canada, and Mexico.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=list[CountryInfo],
      )
  )
  assert isinstance(response.parsed, list)
  assert isinstance(response.parsed[0], CountryInfo)
  assert isinstance(response.parsed[0].currency, CurrencyInfo)


def test_list_of_pydantic_schema_with_nested_list_class(client):
  class CurrencyInfo(BaseModel):
    name: str
    code: str
    symbol: str

  class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int
    currency: list[CurrencyInfo]

  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information for the United States, Canada, and Mexico.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=list[CountryInfo],
      )
  )
  assert isinstance(response.parsed, list)
  assert isinstance(response.parsed[0], CountryInfo)
  assert isinstance(response.parsed[0].currency, list)
  assert isinstance(response.parsed[0].currency[0], CurrencyInfo)


def test_response_schema_with_unsupported_type_raises(client):
  class CountryInfo(BaseModel):
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

  with pytest.raises(ValueError) as e:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Give me information for the United States, Canada, and Mexico.',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=dict[str, CountryInfo],
        )
    )
    assert 'Unsupported schema type' in str(e)
    assert 'GenericAlias' in str(e)


def test_enum_schema_with_enum_mime_type(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='What instrument plays multiple notes at once?',
      config={
          'response_mime_type': 'text/x.enum',
          'response_schema': InstrumentEnum,
      },
  )

  instrument_values = {member.value for member in InstrumentEnum}

  assert response.text in instrument_values
  assert isinstance(response.parsed, InstrumentEnum)


def test_list_of_enum_schema_with_enum_mime_type(client):
  with pytest.raises(errors.ClientError) as e:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='What instrument plays single note at once?',
        config={
            'response_mime_type': 'text/x.enum',
            'response_schema': list[InstrumentEnum],
        },
    )
  assert '400' in str(e)


def test_list_of_enum_schema_with_json_mime_type(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='What instrument plays single note at once?',
      config={
          'response_mime_type': 'application/json',
          'response_schema': list[InstrumentEnum],
      },
  )

  assert isinstance(response.parsed, list)
  assert response.parsed
  for item in response.parsed:
    assert isinstance(item, InstrumentEnum)


def test_enum_schema_with_json_mime_type(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='What instrument plays multiple notes at once?',
      config={
          'response_mime_type': 'application/json',
          'response_schema': InstrumentEnum,
      },
  )
  # "application/json" returns response in double quotes.
  removed_quotes = response.text.replace('"', '')
  instrument_values = {member.value for member in InstrumentEnum}

  assert removed_quotes in instrument_values
  assert isinstance(response.parsed, InstrumentEnum)


def test_non_string_enum_schema_with_enum_mime_type(client):
  class IntegerEnum(Enum):
    PERCUSSION = 1
    STRING = 2
    WOODWIND = 3
    BRASS = 4
    KEYBOARD = 5

  with pytest.raises(TypeError) as e:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='What instrument plays multiple notes at once?',
        config={
            'response_mime_type': 'text/x.enum',
            'response_schema': IntegerEnum,
        },
    )

    assert 'value must be a string' in str(e)


def test_json_schema(client):
  response = client.models.generate_content(
      model='gemini-1.5-flash',
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': {
              'required': [
                  'name',
                  'population',
                  'capital',
                  'continent',
                  'gdp',
                  'official_language',
                  'total_area_sq_mi',
              ],
              'properties': {
                  'name': {'type': 'STRING'},
                  'population': {'type': 'INTEGER'},
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


def test_json_schema_with_lower_enum(client):
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
                  'name': {'type': 'string'},
                  'pupulation': {'type': 'integer'},
                  'capital': {'type': 'string'},
                  'continent': {'type': 'string'},
                  'gdp': {'type': 'integer'},
                  'official_language': {'type': 'string'},
                  'total_area_sq_mi': {'type': 'integer'},
              },
              'type': 'OBJECT',
          },
      },
  )
  assert isinstance(response.parsed, dict)


def test_json_schema_with_streaming(client):

  response = client.models.generate_content_stream(
      model='gemini-2.0-flash-exp',
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': {
              'properties': {
                  'name': {'type': 'STRING'},
                  'population': {'type': 'INTEGER'},
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

  for r in response:
    parts = r.candidates[0].content.parts
    for p in parts:
      print(p.text)


def test_pydantic_schema_with_streaming(client):

  class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

  response = client.models.generate_content_stream(
      model='gemini-2.0-flash-exp',
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': CountryInfo
      },
  )

  for r in response:
    parts = r.candidates[0].content.parts
    for p in parts:
      print(p.text)


def test_schema_from_json(client):

  class Foo(BaseModel):
    bar: str
    baz: int
    qux: list[str]

  schema = types.Schema.model_validate(Foo.model_json_schema())

  response = client.models.generate_content(
      model='gemini-2.0-flash-exp',
      contents='Fill in the Foo.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=schema
      ),
  )

  print(response.text)


def test_schema_from_model_schema(client):

  class Foo(BaseModel):
    bar: str
    baz: int
    qux: list[str]

  response = client.models.generate_content(
      model='gemini-2.0-flash-exp',
      contents='Fill in the Foo.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=Foo.model_json_schema(),
      ),
  )

  print(response.text)


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
        config={'response_modalities': ['AUDIO']},
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
