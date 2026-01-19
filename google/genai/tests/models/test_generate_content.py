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

import os
import pathlib

from pydantic import BaseModel, ValidationError, Field, ConfigDict
from typing import Literal, List, Optional, Union, Set
from datetime import datetime
import pytest
import json
import logging
import sys
from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper
from enum import Enum

GEMINI_FLASH_LATEST = 'gemini-2.5-flash'
GEMINI_FLASH_2_0 = 'gemini-2.0-flash-001'
GEMINI_FLASH_IMAGE_LATEST = 'gemini-2.5-flash-image'

IMAGE_PNG_FILE_PATH = pathlib.Path(__file__).parent / '../data/google.png'
image_bytes = IMAGE_PNG_FILE_PATH.read_bytes()

AUDIO_WAV_FILE_PATH = pathlib.Path(__file__).parent / '../data/voice_sample.wav'
audio_bytes = AUDIO_WAV_FILE_PATH.read_bytes()


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
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('What is your name?'),
            config={
                'http_options': test_http_options,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_union_contents_is_string',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST, contents='Tell me a story in 300 words.'
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_contents_is_content',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
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
            model=GEMINI_FLASH_LATEST,
            contents=[types.Part(text='Tell me a story in 300 words.')],
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_union_contents_is_part',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=types.Part(text='Tell me a story in 300 words.'),
        ),
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_sync_content_list',
        override_replay_id='test_sync',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
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
            contents=t.t_contents('What is your name?'),
        ),
        exception_if_mldev='404',
        skip_in_api_mode='it will encounter 403 for api mode',
    ),
    pytest_helper.TestTableItem(
        name='test_system_instructions',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('high'),
            config={
                'system_instruction': t.t_content(
                    'I say high, you say low'
                )
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_labels',
        exception_if_mldev='not supported',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('What is your name?'),
            config={
                'labels': {'label1': 'value1', 'label2': 'value2'},
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_simple_shared_generation_config',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('What is your name?'),
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
        name='test_2_candidates_gemini_2_5_flash',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Tell me a story in 30 words.'),
            config={
                'candidate_count': 2,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_safety_settings_on_difference',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('What is your name?'),
            config={
                'safety_settings': safety_settings_with_method,
            },
        ),
        exception_if_mldev='method',
    ),
    pytest_helper.TestTableItem(
        name='test_penalty',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_2_0,
            contents=t.t_contents('Tell me a story in 30 words.'),
            config={
                'presence_penalty': 0.5,
                'frequency_penalty': 0.5,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_penalty_gemini_2_0_flash',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_2_0,
            contents=t.t_contents('Tell me a story in 30 words.'),
            config={
                'presence_penalty': 0.5,
                'frequency_penalty': 0.5,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_google_search_tool',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Why is the sky blue?'),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_google_maps_tool',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Find restaurants near me.'),
            config=types.GenerateContentConfig(
                tools=[{'google_maps': {}}],
                tool_config={
                    "retrieval_config": {
                        "lat_lng": {
                            "latitude": 37.421993,
                            "longitude": -122.079725,
                        }
                    }
                }
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_google_search_tool_with_time_range_filter',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('What is the QQQ stock price?'),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch(
                            time_range_filter=types.Interval(
                                start_time=datetime.fromisoformat(
                                    '2025-05-01T00:00:00Z'
                                ),
                                end_time=datetime.fromisoformat(
                                    '2025-05-03T00:00:00Z'
                                ),
                            )
                        )
                    )
                ]
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_google_search_tool_with_exclude_domains',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Why is the sky blue?'),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch(
                            exclude_domains=['amazon.com', 'facebook.com']
                        )
                    )
                ]
            ),
        ),
        exception_if_mldev='not supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_google_search_tool_with_blocking_confidence',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Why is the sky blue?'),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch(
                            blocking_confidence=types.PhishBlockThreshold.BLOCK_LOW_AND_ABOVE,
                        )
                    )
                ]
            ),
        ),
        exception_if_mldev='not supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_enterprise_web_search_tool',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Why is the sky blue?'),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        enterprise_web_search=types.EnterpriseWebSearch()
                    )
                ]
            ),
        ),
        exception_if_mldev='not supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_enterprise_web_search_tool_with_exclude_domains',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Why is the sky blue?'),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        enterprise_web_search=types.EnterpriseWebSearch(
                            exclude_domains=['amazon.com', 'facebook.com']
                        )
                    )
                ]
            ),
        ),
        exception_if_mldev='not supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_enterprise_web_search_tool_with_blocking_confidence',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('Why is the sky blue?'),
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        enterprise_web_search=types.EnterpriseWebSearch(
                            blocking_confidence=types.PhishBlockThreshold.BLOCK_LOW_AND_ABOVE,
                        )
                    )
                ]
            ),
        ),
        exception_if_mldev='not supported in',
    ),
    pytest_helper.TestTableItem(
        name='test_speech_with_config',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash-preview-tts',
            contents=t.t_contents(
                'Produce a speech response saying "Cheese"'
            ),
            config=types.GenerateContentConfig(
                response_modalities=['audio'],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='charon'
                        )
                    )
                ),
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_speech_with_multi_speaker_voice_config',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash-preview-tts',
            contents=t.t_contents(
                'Alice says "Hi", Bob replies with "what\'s up"?'
            ),
            config=types.GenerateContentConfig(
                response_modalities=['audio'],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker='Alice',
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name='leda'
                                    )
                                ),
                            ),
                            types.SpeakerVoiceConfig(
                                speaker='Bob',
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name='kore'
                                    )
                                ),
                            ),
                        ],
                    )
                ),
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_speech_error_with_speech_config_and_multi_speech_config',
        exception_if_vertex='mutually exclusive',
        exception_if_mldev='mutually exclusive',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash-preview-tts',
            contents=t.t_contents(
                'Alice says "Hi", Bob replies with "what\'s up"?'
            ),
            config=types.GenerateContentConfig(
                response_modalities=['audio'],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='puck'
                        )
                    ),
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker='Alice',
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name='leda'
                                    )
                                ),
                            ),
                            types.SpeakerVoiceConfig(
                                speaker='Bob',
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name='kore'
                                    )
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_union_speech_string_config',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash-preview-tts',
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
            model=GEMINI_FLASH_LATEST,
            contents=[
                types.Content(
                    role='user',
                    parts=[
                        types.Part(
                            file_data=types.FileData(
                                file_uri='gs://cloud-samples-data/generative-ai/audio/pixel.mp3',
                                mime_type='audio/mpeg',
                            )
                        ),
                        types.Part(
                            text="""Can you transcribe this interview, in the
                           format of timecode, speaker, caption. Use speaker A, 
                           speaker B, etc. to identify speakers."""
                        ),
                    ],
                )
            ],
            config=types.GenerateContentConfig(audio_timestamp=True),
        ),
        exception_if_mldev='not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_response_schema_with_default',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('What is your name?'),
            config={
                'response_mime_type': 'application/json',
                'response_schema': {
                    'type': 'OBJECT',
                    'properties': {
                        'name': {
                            'type': 'STRING',
                            'default': 'default_name',
                        },
                    },
                },
            },
        ),
        ignore_keys=['parsed'],
    ),
    pytest_helper.TestTableItem(
        name='test_invalid_model_parameter_path',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash/../../upload/v1beta/files',
            contents=t.t_contents('What is your name?'),
        ),
        exception_if_vertex='invalid model parameter',
        exception_if_mldev='invalid model parameter',
    ),
    pytest_helper.TestTableItem(
        name='test_invalid_model_parameter_question_mark',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash?',
            contents=t.t_contents('What is your name?'),
        ),
        exception_if_vertex='invalid model parameter',
        exception_if_mldev='invalid model parameter',
    ),
    pytest_helper.TestTableItem(
        name='test_invalid_model_parameter_ampersand',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash&',
            contents=t.t_contents('What is your name?'),
        ),
        exception_if_vertex='invalid model parameter',
        exception_if_mldev='invalid model parameter',
    ),
    pytest_helper.TestTableItem(
        name='test_enhanced_civic_answers',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents(
                'Summarize the evidence that confirms widespread voter fraud was'
                ' the reason the last national election results were'
                ' inaccurate.'
            ),
            config={
                'enable_enhanced_civic_answers': True,
            },
        ),
        exception_if_vertex='not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_model_armor_config',
        parameters=types._GenerateContentParameters(
            model=GEMINI_FLASH_LATEST,
            contents=t.t_contents('What is your name?'),
            config={
                'model_armor_config': {
                    'prompt_template_name': '',
                    'response_template_name': '',
                    # Intentionally left blank just to test that the SDK doesn't
                    # throw an exception.
                },
            },
        ),
        exception_if_mldev='not supported',
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)
pytest_plugins = ('pytest_asyncio',)


def test_sync_with_headers(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a story in 300 words.',
  )
  assert response.sdk_http_response.headers is not None
  assert response.sdk_http_response.body is None


def test_sync_with_full_response(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a story in 300 words.',
      config={
          'should_return_http_response': True,
      },
  )
  print(response.sdk_http_response.body)
  assert response.sdk_http_response.headers is not None
  assert response.sdk_http_response.body is not None
  assert 'candidates' in response.sdk_http_response.body
  assert 'content' in response.sdk_http_response.body
  assert 'parts' in response.sdk_http_response.body
  assert 'usageMetadata' in response.sdk_http_response.body

@pytest.mark.asyncio
async def test_async(client):
  response = await client.aio.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
  )
  assert response.text


@pytest.mark.asyncio
async def test_async_with_headers(client):
  response = await client.aio.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a story in 300 words.',
  )
  assert response.sdk_http_response.headers is not None
  assert response.sdk_http_response.body is None


@pytest.mark.asyncio
async def test_async_with_full_response(client):
  response = await client.aio.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a story in 300 words.',
      config={
          'should_return_http_response': True,
      },
  )
  assert response.sdk_http_response.headers is not None
  assert response.sdk_http_response.body is not None
  assert 'candidates' in response.sdk_http_response.body
  assert 'content' in response.sdk_http_response.body
  assert 'parts' in response.sdk_http_response.body
  assert 'usageMetadata' in response.sdk_http_response.body


def test_sync_stream(client):
  response = client.models.generate_content_stream(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
  )
  chunks = 0
  for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason

  assert chunks >= 1


def test_sync_stream_with_should_return_http_headers(client):
  response = client.models.generate_content_stream(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
  )
  chunks = 0
  for part in response:
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason
    assert part.sdk_http_response.headers is not None
  assert chunks >= 1


def test_sync_stream_with_non_text_modality(client):
  response = client.models.generate_content_stream(
      model='gemini-2.0-flash-preview-image-generation',
      contents=(
          'Generate an image of the Eiffel tower with fireworks in the'
          ' background.'
      ),
      config={
          'response_modalities': ['IMAGE', 'TEXT'],
      },
  )
  chunks = 0
  for chunk in response:
    chunks += 1
    if chunk.candidates[0].finish_reason is not None:
      continue
    for part in chunk.parts:
      assert part.text is not None or part.inline_data is not None

  assert chunks >= 1


@pytest.mark.asyncio
async def test_async_stream(client):
  chunks = 0
  async for part in await client.aio.models.generate_content_stream(
      model=GEMINI_FLASH_LATEST, contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
  ):
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason

  assert chunks >= 1


@pytest.mark.asyncio
async def test_async_stream_with_headers(client):
  chunks = 0
  async for part in await client.aio.models.generate_content_stream(
      model=GEMINI_FLASH_LATEST, contents='Tell me a story in 300 words.',
      config={
          'http_options': test_http_options,
      },
  ):
    chunks += 1
    assert part.text is not None or part.candidates[0].finish_reason
    assert part.sdk_http_response.headers is not None

  assert chunks >= 1


@pytest.mark.asyncio
async def test_async_stream_with_non_text_modality(client):
  chunks = 0
  async for chunk in await client.aio.models.generate_content_stream(
      model=GEMINI_FLASH_IMAGE_LATEST,
      contents=(
          'Generate an image of the Eiffel tower with fireworks in the'
          ' background.'
      ),
      config={
          'response_modalities': ['IMAGE', 'TEXT'],
      },
  ):
    chunks += 1
    if chunk.candidates[0].finish_reason is not None:
      continue
    for part in chunk.parts:
      assert part.text is not None or part.inline_data is not None

  assert chunks >= 1


def test_simple_shared_generation_config_stream(client):
  chunks = 0
  for chunk in client.models.generate_content_stream(
      model=GEMINI_FLASH_LATEST,
      contents='tell me a story in 300 words',
      config={
          'max_output_tokens': 1000,
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
  assert chunks >= 1


@pytest.mark.asyncio
async def test_simple_shared_generation_config_async(client):
  response = await client.aio.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='tell me a story in 300 words',
      config={
          'max_output_tokens': 4000,
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
      model=GEMINI_FLASH_2_0,
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
  assert chunks >= 1


def test_log_probs(client):
  client.models.generate_content(
      model=GEMINI_FLASH_2_0,
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
      model=GEMINI_FLASH_LATEST,
      contents='What is your name?',
      config={
          'max_output_tokens': 300,
          'top_k': 2,
      },
  )
  assert response.text


def test_model_selection_config_dict(client):
  if not client.vertexai:
    return
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me a Taylor Swift lyric and explain its meaning.',
      config={
          'model_selection_config': {
              'feature_selection_preference': 'PRIORITIZE_COST'
          }
      },
  )
  assert response.text


def test_model_selection_config_pydantic(client):
  if not client.vertexai:
    return
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me a Taylor Swift lyric and explain its meaning.',
      config=types.GenerateContentConfig(
          model_selection_config=types.ModelSelectionConfig(
              feature_selection_preference=types.FeatureSelectionPreference.PRIORITIZE_QUALITY
          )
      ),
  )
  assert response.text


def test_sdk_logger_logs_warnings_once(client, caplog):
  from ... import types as types_module

  types_module._response_text_warning_logged = False

  caplog.set_level(logging.WARNING, logger='google_genai.types')

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a 50 word story about cheese.',
      config={
        'candidate_count': 2,
      }
  )
  assert response.text
  assert 'WARNING' in caplog.text
  assert 'there are 2 candidates' in caplog.text
  caplog_after_first_call = caplog.text
  assert len(caplog.records) == 1
  client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Tell me a 50 word story about cheese.',
      config={
        'candidate_count': 2,
      }
  )
  assert caplog.text == caplog_after_first_call
  assert len(caplog.records) == 1


def test_response_create_time_and_response_id(client):
  if client.vertexai:
    response = client.models.generate_content(
        model=GEMINI_FLASH_LATEST,
        contents='What is your name?',
        config={
            'max_output_tokens': 300,
            'top_k': 2,
        },
    )
    # create_time and response_id are not supported in mldev
    assert response.create_time
    assert response.response_id
    assert isinstance(response.create_time, datetime)


def test_safety_settings(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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
        model=GEMINI_FLASH_LATEST,
        contents='What is your name?',
        config={
            'safety_settings': safety_settings,
        },
    ):
      pass
  else:
    with pytest.raises(ValueError) as e:
      for part in client.models.generate_content_stream(
          model=GEMINI_FLASH_LATEST,
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
        model=GEMINI_FLASH_LATEST,
        contents='What is your name?',
        config={
            'safety_settings': safety_settings,
        },
    ):
      pass
  else:
    with pytest.raises(ValueError) as e:
      for part in client.models.generate_content_stream(
          model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': CountryInfo,
      },
  )
  assert isinstance(response.parsed, CountryInfo)

def test_json_schema_fields(client):
  class UserRole(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"
  class Address(BaseModel):
    street: str
    city: str
  class UserProfile(BaseModel):
    username: str = Field(description="User's unique name")
    age: Optional[int] = Field(ge=0, le=20)
    roles: Set[UserRole] = Field(min_items=1)
    contact: Union[Address, str]

    model_config = ConfigDict(
        title="User Schema", description="A user profile"
    )  # This is the title of the schema

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_json_schema': UserProfile.model_json_schema(),
      },
  )
  print(response.parsed)
  assert response.parsed != None


def test_pydantic_schema_orders_properties(client):
  class Restaurant(BaseModel):
    name: str
    rating: int
    fun_fact: str

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me information about a restaurant in Boston.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': Restaurant,
      },
  )
  response_text_json = json.loads(response.text)
  response_keys = list(response_text_json.keys())
  assert response_keys[0] == 'name'
  assert response_keys == list(Restaurant.model_fields.keys())


def test_pydantic_schema_with_default_value(client):
  class Restaurant(BaseModel):
    name: str
    rating: int = 0
    city: Optional[str] = 'New York'

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Can you recommend a restaurant for me?',
      config={
          'response_mime_type': 'application/json',
          'response_schema': Restaurant,
      },
  )
  assert isinstance(response.parsed, Restaurant)


def test_repeated_pydantic_schema(client):
  # This tests the defs handling on the pydantic side.
  class Person(BaseModel):
    name: str

  class Relationship(BaseModel):
    relationship: str
    person1: Person
    person2: Person

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Create a couple.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': Relationship,
      },
  )
  assert isinstance(response.parsed, Relationship)


def test_int_schema(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents="what's your favorite number?",
      config={
          'response_mime_type': 'application/json',
          'response_schema': int,
      },
  )
  assert isinstance(response.parsed, int)


def test_nested_list_of_int_schema(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents="Can you return two matrices, a 2x3 and a 3x4?",
      config={
          'response_mime_type': 'application/json',
          'response_schema': list[list[list[int]]],
      },
  )
  assert isinstance(response.parsed[0][0][0], int)


def test_literal_schema(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Which ice cream flavor should I order?',
      config={
          'response_mime_type': 'application/json',
          'response_schema': Literal['chocolate', 'vanilla', 'cookie dough'],
      },
  )

  allowed_values = ['chocolate', 'vanilla', 'cookie dough']
  assert isinstance(response.parsed, str)
  assert response.parsed in allowed_values


def test_literal_schema_with_non_string_types_raises(client):
  with pytest.raises(ValueError) as e:
    client.models.generate_content(
        model=GEMINI_FLASH_LATEST,
        contents='Which ice cream flavor should I order?',
        config={
            'response_mime_type': 'application/json',
            'response_schema': Literal['chocolate', 'vanilla', 1],
        },
    )
  assert 'validation error' in str(e)


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_pydantic_schema_with_literal(client):
  class Movie(BaseModel):
    name: str
    genre: Literal['action', 'comedy', 'drama']

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me information about the movie "Mean Girls"',
      config={
          'response_mime_type': 'application/json',
          'response_schema': Movie,
      },
  )
  assert isinstance(response.parsed, Movie)
  assert isinstance(response.parsed.genre, str)
  assert response.parsed.genre in ['action', 'comedy', 'drama']


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_pydantic_schema_with_single_value_literal(client):
  class Movie(BaseModel):
    name: str
    genre: Literal['action']

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me information about the movie "The Matrix"',
      config={
          'response_mime_type': 'application/json',
          'response_schema': Movie,
      },
  )
  assert isinstance(response.parsed, Movie)
  assert response.parsed.genre == 'action'


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_pydantic_schema_with_none(client):
  class CountryInfo(BaseModel):
    name: str
    total_area_sq_mi: int | None = None

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me information of the United States.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=schema,
      ),
  )

  assert response.text


@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason='| is not supported in Python 3.9',
)
def test_schema_with_union_type(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me a random number, either as an integers or written out as words.',
      config=types.GenerateContentConfig.model_validate(dict(
          response_mime_type='application/json',
          response_schema=int | str,
      ))
  )
  assert type(response.parsed) in (int, str)


def test_schema_with_union_type_all_py_versions(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me a list of 5 random numbers, including some integers and some written out as words.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=list[int | str],
      )
  )
  for item in response.parsed:
    assert isinstance(item, int) or isinstance(item, str)


def test_list_schema_with_union_type_all_py_versions(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me a list of 5 random numbers, including some integers and some written out as words.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=list[Union[int, str]],
      )
  )
  for item in response.parsed:
    assert isinstance(item, int) or isinstance(item, str)


def test_pydantic_schema_with_optional_generic_alias(client):
  class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_languages: Optional[List[str]]
    total_area_sq_mi: int

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': CountryInfo,
      },
  )
  assert isinstance(response.parsed, CountryInfo)
  assert isinstance(response.parsed.official_languages, list) or response.parsed.official_languages is None


def test_pydantic_schema_with_optional_pydantic(client):
  class TestPerson(BaseModel):
    first_name: Optional[str] = Field(
        description='First name of the person', default=None
    )
    last_name: Optional[str] = Field(
        description='Last name of the person', default=None
    )

  class TestDocument(BaseModel):
    case_number: Optional[str] = Field(
        description='Case number assigned to the claim', default=None
    )
    filed_by: Optional[TestPerson] = Field(
        description='Name of the party that filed or submitted the statement',
        default=None,
    )

  test_prompt = """
  Carefully examine the following document and extract the metadata.
  Be sure to include the party that filed the document.

  Document Text:
  --------------
  Case Number: 20-12345
  File by: John Doe
  """

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents=test_prompt,
      config={
          'response_mime_type': 'application/json',
          'response_schema': TestDocument,
      },
  )
  assert isinstance(response.parsed, TestDocument)
  assert isinstance(response.parsed.filed_by, TestPerson)


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
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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


def test_response_schema_with_dict_of_pydantic_schema(client):
  class CountryInfo(BaseModel):
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

  if not client.vertexai:
    with pytest.raises(ValueError) as e:
      client.models.generate_content(
          model=GEMINI_FLASH_LATEST,
          contents='Give me information for the United States, Canada, and Mexico.',
          config=types.GenerateContentConfig(
              response_mime_type='application/json',
              response_schema=dict[str, CountryInfo],
          )
      )
  else:
    response = client.models.generate_content(
        model=GEMINI_FLASH_LATEST,
        contents='Give me information for the United States, Canada, and Mexico.',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=dict[str, CountryInfo],
        )
    )
    assert response.text


def test_schema_with_unsupported_type_raises(client):
  with pytest.raises(ValueError) as e:
    client.models.generate_content(
        model=GEMINI_FLASH_LATEST,
        contents='Give me information for the United States, Canada, and Mexico.',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=types.Schema(),
        )
    )
  assert 'Unsupported schema type' in str(e)


def test_enum_schema_with_enum_mime_type(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_2_0,
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
        model=GEMINI_FLASH_2_0,
        contents='What instrument plays single note at once?',
        config={
            'response_mime_type': 'text/x.enum',
            'response_schema': list[InstrumentEnum],
        },
    )
  assert '400' in str(e)


def test_list_of_enum_schema_with_json_mime_type(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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


def test_optional_enum_in_pydantic_schema_with_json_mime_type(client):
  class InstrumentInfo(BaseModel):
    instrument: Optional[InstrumentEnum]
    fun_fact: str

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='What instrument plays single note at once? Include the name of the instrument in your response.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': InstrumentInfo,
      },
  )

  assert isinstance(response.parsed, InstrumentInfo)
  assert isinstance(response.parsed.instrument, InstrumentEnum)


def test_enum_schema_with_json_mime_type(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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

  response =client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='What instrument plays multiple notes at once?',
      config={
          'response_mime_type': 'text/x.enum',
          'response_schema': IntegerEnum,
      },
  )

  instrument_values = {str(member.value) for member in IntegerEnum}

  assert response.text in instrument_values


def test_json_schema(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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
      model=GEMINI_FLASH_LATEST,
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


def test_json_schema_with_any_of(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me a fruit basket.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': {
              'type': 'OBJECT',
              'title': 'Fruit Basket',
              'description': 'A structured representation of a fruit basket',
              'required': ['fruit'],
              'properties': {
                  'fruit': {
                      'type': 'ARRAY',
                      'description': (
                          'An ordered list of the fruit in the basket'
                      ),
                      'items': {
                          'description': 'A piece of fruit',
                          'any_of': [
                              {
                                  'title': 'Apple',
                                  'description': 'Describes an apple',
                                  'type': 'OBJECT',
                                  'properties': {
                                      'type': {
                                          'type': 'STRING',
                                          'description': "Always 'apple'",
                                      },
                                      'color': {
                                          'type': 'STRING',
                                          'description': (
                                              'The color of the apple (e.g.,'
                                              " 'red')"
                                          ),
                                      },
                                  },
                                  'property_ordering': ['type', 'color'],
                                  'required': ['type', 'color'],
                              },
                              {
                                  'title': 'Orange',
                                  'description': 'Describes an orange',
                                  'type': 'OBJECT',
                                  'properties': {
                                      'type': {
                                          'type': 'STRING',
                                          'description': "Always 'orange'",
                                      },
                                      'size': {
                                          'type': 'STRING',
                                          'description': (
                                              'The size of the orange (e.g.,'
                                              " 'medium')"
                                          ),
                                      },
                                  },
                                  'property_ordering': ['type', 'size'],
                                  'required': ['type', 'size'],
                              },
                          ],
                      },
                  }
              },
          },
      },
  )
  assert isinstance(response.parsed, dict)
  assert 'fruit' in response.parsed
  assert isinstance(response.parsed['fruit'], list)
  assert 'type' in response.parsed['fruit'][0]


def test_schema_with_any_of(client):
  response_schema=types.Schema(
      type=types.Type.OBJECT,
      title='Fruit Basket',
      description='A structured representation of a fruit basket',
      properties={
          'fruit': types.Schema(
              type=types.Type.ARRAY,
              description='An ordered list of the fruit in the basket',
              items=types.Schema(
                  any_of=[
                      types.Schema(
                          title='Apple',
                          description='Describes an apple',
                          type=types.Type.OBJECT,
                          properties={
                              'type': types.Schema(type=types.Type.STRING, description='Always "apple"'),
                              'variety': types.Schema(
                                  type=types.Type.STRING,
                                  description='The variety of apple (e.g., "Granny Smith")',
                              ),
                          },
                          property_ordering=['type', 'variety'],
                          required=['type', 'variety'],
                      ),
                      types.Schema(
                          title='Orange',
                          description='Describes an orange',
                          type=types.Type.OBJECT,
                          properties={
                              'type': types.Schema(type=types.Type.STRING, description='Always "orange"'),
                              'variety': types.Schema(
                                  type=types.Type.STRING,
                                  description='The variety of orange (e.g.,"Navel orange")',
                              ),
                          },
                          property_ordering=['type', 'variety'],
                          required=['type', 'variety'],
                      ),
                  ],
              ),
          ),
      },
      required=['fruit'],
  )
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Give me a fruit basket.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=response_schema,
      ),
  )
  assert isinstance(response.parsed, dict)
  assert 'fruit' in response.parsed
  assert isinstance(response.parsed['fruit'], list)
  assert 'type' in response.parsed['fruit'][0]


def test_replicated_voice_config(client):
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
      client.models.generate_content(
          model='gemini-2.5-flash-preview-tts-voice-replication-rev22-2025-10-28',
          contents=t.t_contents(
              'Produce a speech response saying "Cheese"'
          ),
          config=types.GenerateContentConfig(
              response_modalities=['audio'],
              speech_config=types.SpeechConfig(
                  voice_config=types.VoiceConfig(
                      replicated_voice_config=types.ReplicatedVoiceConfig(
                          voice_sample_audio=audio_bytes,
                          mime_type='audio/wav',
                      )
                  )
              ),
          ),
      )


def test_json_schema_with_streaming(client):

  response = client.models.generate_content_stream(
      model=GEMINI_FLASH_LATEST,
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
    parts = r.parts
    for p in parts:
      assert p.text


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
      model=GEMINI_FLASH_LATEST,
      contents='Give me information of the United States.',
      config={
          'response_mime_type': 'application/json',
          'response_schema': CountryInfo
      },
  )

  for r in response:
    parts = r.parts
    for p in parts:
      assert p.text


def test_schema_from_json(client):

  class Foo(BaseModel):
    bar: str
    baz: int
    qux: list[str]

  schema = types.Schema.model_validate(Foo.model_json_schema())

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Fill in the Foo.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=schema
      ),
  )

  assert response.text


def test_schema_from_model_schema(client):

  class Foo(BaseModel):
    bar: str
    baz: int
    qux: list[str]

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='Fill in the Foo.',
      config=types.GenerateContentConfig(
          response_mime_type='application/json',
          response_schema=Foo.model_json_schema(),
      ),
  )

  response.text


def test_schema_with_additional_properties(client):

  class Foo(BaseModel):
    bar: str
    baz: int
    qux: dict[str, str]

  if client.vertexai:
    response = client.models.generate_content(
        model=GEMINI_FLASH_LATEST,
        contents='What is your name?',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=Foo,
        ),
    )
    assert response.text
  else:
    with pytest.raises(ValueError) as e:
      client.models.generate_content(
          model=GEMINI_FLASH_LATEST,
          contents='What is your name?',
          config=types.GenerateContentConfig(
              response_mime_type='application/json',
              response_schema=Foo,
          ),
      )
    assert 'additionalProperties is not supported in the Gemini API.' in str(e)


def test_function(client):
  def get_weather(city: str) -> str:
    """Returns the weather in a city."""
    return f'The weather in {city} is sunny and 100 degrees.'

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
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
        model=GEMINI_FLASH_LATEST,
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
        model=GEMINI_FLASH_LATEST,
        contents={'invalid_key': 'invalid_value'},
    )
  assert 'invalid_key' in str(e.value)


def test_invalid_input_with_transformer_list(client):
  with pytest.raises(ValidationError) as e:
    client.models.generate_content(
        model=GEMINI_FLASH_LATEST,
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
        model=GEMINI_FLASH_LATEST,
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
    if 'error' in e.details:
      details = e.details['error']
    else:
      details = e.details
    assert details['code'] == 400
    assert details['status'] == 'INVALID_ARGUMENT'


def test_multiple_strings(client):
  class SummaryResponses(BaseModel):
    summary: str
    person: str

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents=[
          "Summarize Shakespeare's life work in a few sentences",
          "Summarize Hemingway's life work",
      ],
      config={
          'response_mime_type': 'application/json',
          'response_schema': list[SummaryResponses],
      },
  )

  assert 'Shakespeare' in response.text
  assert 'Hemingway' in response.text
  assert 'Shakespeare' in response.parsed[0].person
  assert 'Hemingway' in response.parsed[1].person


def test_multiple_parts(client):
  class SummaryResponses(BaseModel):
    summary: str
    person: str

  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents=[
          types.Part(
              text="Summarize Shakespeare's life work in a few sentences"
          ),
          types.Part(text="Summarize Hemingway's life work"),
      ],
      config={
          'response_mime_type': 'application/json',
          'response_schema': list[SummaryResponses],
      },
  )

  assert 'Shakespeare' in response.text
  assert 'Hemingway' in response.text
  assert 'Shakespeare' in  response.parsed[0].person
  assert 'Hemingway' in response.parsed[1].person


def test_multiple_function_calls(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents=[
          'What is the weather in Boston?',
          'What is the stock price of GOOG?',
          types.Part.from_function_call(
              name='get_weather',
              args={'location': 'Boston'},
          ),
          types.Part.from_function_call(
              name='get_stock_price',
              args={'symbol': 'GOOG'},
          ),
          types.Part.from_function_response(
              name='get_weather',
              response={'response': 'It is sunny and 100 degrees.'},
          ),
          types.Part.from_function_response(
              name='get_stock_price',
              response={'response': 'The stock price is $100.'},
          ),
      ],
      config=types.GenerateContentConfig(
          tools=[
              types.Tool(
                  function_declarations=[
                      types.FunctionDeclaration(
                          name='get_weather',
                          description='Get the weather in a city.',
                          parameters=types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  'location': types.Schema(
                                      type=types.Type.STRING
                                  )
                              },
                          ),
                      ),
                      types.FunctionDeclaration(
                          name='get_stock_price',
                          description='Get the stock price of a symbol.',
                          parameters=types.Schema(
                              type=types.Type.OBJECT,
                              properties={
                                  'symbol': types.Schema(
                                      type=types.Type.STRING
                                  )
                              },
                          ),
                      ),
                  ]
              ),
          ]
      ),
  )

  assert 'Boston' in response.text
  assert 'sunny' in response.text
  assert '100 degrees' in response.text
  assert '$100' in response.text


def test_usage_metadata_part_types(client):
  contents = [
      'Hello world.',
      types.Part.from_bytes(
          data=image_bytes,
          mime_type='image/png',
      ),
  ]

  response = client.models.generate_content(
      model=GEMINI_FLASH_2_0, contents=contents
  )
  usage_metadata = response.usage_metadata

  assert usage_metadata.candidates_token_count
  assert usage_metadata.candidates_tokens_details
  modalities = sorted(
      [d.modality.name for d in usage_metadata.candidates_tokens_details]
  )
  assert modalities == ['TEXT']
  assert isinstance(
      usage_metadata.candidates_tokens_details[0].modality, types.MediaModality)

  assert usage_metadata.prompt_token_count
  assert usage_metadata.prompt_tokens_details
  modalities = sorted(
      [d.modality.name for d in usage_metadata.prompt_tokens_details]
  )
  assert modalities == ['IMAGE', 'TEXT']


def test_error_handling_stream(client):
  if client.vertexai:
    return

  try:
    for chunk in client.models.generate_content_stream(
        model=GEMINI_FLASH_IMAGE_LATEST,
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_bytes(
                        data=image_bytes, mime_type='image/png'
                    ),
                    types.Part.from_text(text='Make sky more beautiful.'),
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            response_mime_type='text/plain',
            response_modalities=['IMAGE', 'TEXT'],
            system_instruction='make the sky more beautiful.',
        ),
    ):
      continue

  except errors.ClientError as e:
    assert (
        e.message
        == 'Developer instruction is not enabled for'
        ' models/gemini-2.5-flash-image'
    )


def test_error_handling_unary(client):
  if client.vertexai:
    return

  try:
    client.models.generate_content(
        model=GEMINI_FLASH_IMAGE_LATEST,
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_bytes(
                        data=image_bytes, mime_type='image/png'
                    ),
                    types.Part.from_text(text='Make sky more beautiful.'),
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            response_mime_type='text/plain',
            response_modalities=['IMAGE', 'TEXT'],
            system_instruction='make the sky more beautiful.',
        ),
    )

  except errors.ClientError as e:
    assert (
        e.message
        == 'Developer instruction is not enabled for'
        ' models/gemini-2.5-flash-image'
    )


def test_provisioned_output_dedicated(client):
  response = client.models.generate_content(
      model=GEMINI_FLASH_LATEST,
      contents='What is 1 + 1?',
      config=types.GenerateContentConfig(
          http_options={'headers': {'X-Vertex-AI-LLM-Request-Type': 'dedicated'}}
      ),
  )
  if client.vertexai:
    assert response.usage_metadata.traffic_type == types.TrafficType.PROVISIONED_THROUGHPUT
  else:
    assert not response.usage_metadata.traffic_type


@pytest.mark.asyncio
async def test_error_handling_unary_async(client):
  if client.vertexai:
    return

  try:
    await client.aio.models.generate_content(
        model=GEMINI_FLASH_IMAGE_LATEST,
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_bytes(
                        data=image_bytes, mime_type='image/png'
                    ),
                    types.Part.from_text(text='Make sky more beautiful.'),
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            response_mime_type='text/plain',
            response_modalities=['IMAGE', 'TEXT'],
            system_instruction='make the sky more beautiful.',
        ),
    )

  except errors.ClientError as e:
    assert (
        e.message
        == 'Developer instruction is not enabled for'
        ' models/gemini-2.5-flash-image'
    )


@pytest.mark.asyncio
async def test_error_handling_stream_async(client):
  if client.vertexai:
    return

  try:
    async for part in await client.aio.models.generate_content_stream(
        model=GEMINI_FLASH_IMAGE_LATEST,
        contents=[
            types.Content(
                role='user',
                parts=[
                    types.Part.from_bytes(
                        data=image_bytes, mime_type='image/png'
                    ),
                    types.Part.from_text(text='Make sky more beautiful.'),
                ],
            ),
        ],
        config=types.GenerateContentConfig(
            response_mime_type='text/plain',
            response_modalities=['IMAGE', 'TEXT'],
            system_instruction='make the sky more beautiful.',
        ),
    ):
      continue

  except errors.ClientError as e:
    assert ('Developer instruction is not enabled' in e.message)
