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


"""Tests for generate_content_part."""

import base64
import os

from pydantic import ValidationError
import pytest

from ... import _transformers as t
from ... import errors
from ... import types
from .. import pytest_helper


IMAGE_PNG_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.png')
)
IMAGE_JPEG_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.jpg')
)
APPLICATION_PDF_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/story.pdf')
)
VIDEO_MP4_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/animal.mp4')
)
AUDIO_MP3_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/pixel.m4a')
)
with open(IMAGE_PNG_FILE_PATH, 'rb') as image_file:
  image_bytes = image_file.read()
  image_string = base64.b64encode(image_bytes).decode('utf-8')
with open(APPLICATION_PDF_FILE_PATH, 'rb') as pdf_file:
  pdf_bytes = pdf_file.read()
with open(VIDEO_MP4_FILE_PATH, 'rb') as video_file:
  video_bytes = video_file.read()
with open(AUDIO_MP3_FILE_PATH, 'rb') as audio_file:
  audio_bytes = audio_file.read()

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_image_uri',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content('What is this image about?'),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'gs://generativeai-downloads/images/scones.jpg'
                                    ),
                                    'mime_type': 'image/jpeg',
                                }
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_mldev='400',
    ),
    pytest_helper.TestTableItem(
        name='test_external_file_uri',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content('What is this image about?'),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'https://storage.googleapis.com/cloud-samples-data/generative-ai/image/scones.jpg'
                                    ),
                                    'mime_type': 'image/jpeg',
                                }
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_mldev='400',
    ),
    pytest_helper.TestTableItem(
        name='test_image_png_file_uri',
        skip_in_api_mode=(
            'Name of the file is hardcoded, only supporting replay mode.'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content('What is this image about?'),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'https://generativelanguage.googleapis.com/v1beta/files/864z7ft4m14h'
                                    ),
                                    'mime_type': 'image/png',
                                }
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_vertex='403',
    ),
    pytest_helper.TestTableItem(
        name='test_image_jpg_file_uri',
        skip_in_api_mode=(
            'Name of the file is hardcoded, only supporting replay mode.'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content('What is this image about?'),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'https://generativelanguage.googleapis.com/v1beta/files/22xab9a8jp0v'
                                    ),
                                    'mime_type': 'image/jpeg',
                                }
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_vertex='403',
    ),
    pytest_helper.TestTableItem(
        name='test_image_inline_part_media_resolution',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content('What is this image about?'),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.Part(
                                inline_data=types.Blob(
                                    data=image_string, mime_type='image/png'
                                ),
                                media_resolution={'level': 'MEDIA_RESOLUTION_LOW'}
                            )
                        ],
                    },
                ),
            ],
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_application_pdf_file_uri',
        skip_in_api_mode=(
            'Name of the file is hardcoded, only supporting replay mode.'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content(
                    'Summarize the pdf in concise and professional tone.'
                ),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'https://generativelanguage.googleapis.com/v1beta/files/9tnpjy0re13a'
                                    ),
                                    'mime_type': 'application/pdf',
                                }
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_vertex='403',
    ),
    pytest_helper.TestTableItem(
        name='test_video_mp4_file_uri',
        skip_in_api_mode=(
            'Name of the file is hardcoded, only supporting replay mode.'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content(
                    """
                    summarize the video in concise and professional tone.
                    the summary should include all important information said in the video.
                    """,
                ),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'https://generativelanguage.googleapis.com/v1beta/files/i2ojhd8z99uk'
                                    ),
                                    'mime_type': 'video/mp4',
                                }
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_vertex='403',
    ),
    pytest_helper.TestTableItem(
        name='test_audio_m4a_file_uri',
        skip_in_api_mode=(
            'Name of the file is hardcoded, only supporting replay mode.'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content(
                    """
                    Provide a summary for the audio in the beginning of the transcript.
                    Provide concise chapter titles with timestamps.
                    Do not make up any information that is not part of the audio.
                """,
                ),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'https://generativelanguage.googleapis.com/v1beta/files/0o9iyit198g1'
                                    ),
                                    'mime_type': 'audio/mp4',
                                }
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_vertex='403',
    ),
    pytest_helper.TestTableItem(
        name='test_mldev_video_offset_and_fps',
        skip_in_api_mode=(
            'Name of the file is hardcoded, only supporting replay mode.'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                types.Content(
                    role='user',
                    parts=[
                        types.Part(text='summarize this video'),
                        types.Part(
                            file_data=types.FileData(
                                file_uri='https://generativelanguage.googleapis.com/v1beta/files/fq9r5ftyqrho',
                                mime_type= 'video/mp4',
                            ),
                            video_metadata=types.VideoMetadata(
                                    start_offset='0s',
                                    end_offset= '5s',
                                    fps= 3,
                            )
                        )
                    ]
                ),
            ],
        ),
        exception_if_vertex='403',
    ),
    pytest_helper.TestTableItem(
        name='test_video_gcs_file_uri',
        skip_in_api_mode=(
            'Name of the file is hardcoded, only supporting replay mode.'
        ),
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content('what is the video about?'),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.PartDict({
                                'file_data': {
                                    'file_uri': (
                                        'gs://generativeai-downloads/videos/Big_Buck_Bunny.mp4'
                                    ),
                                    'mime_type': 'video/mp4',
                                },
                                'video_metadata': {
                                    'start_offset': '0s',
                                    'end_offset': '10s',
                                    'fps': 3,
                                },
                            })
                        ],
                    },
                ),
            ],
        ),
        exception_if_mldev='400',
    ),
    pytest_helper.TestTableItem(
        name='test_image_base64',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                t.t_content('What is this image about?'),
                t.t_content(
                    {
                        'role': 'user',
                        'parts': [
                            types.Part(
                                inline_data=types.Blob(
                                    data=image_string, mime_type='image/png'
                                )
                            )
                        ],
                    },
                ),
            ],
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_union_none_part',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[],
        ),
        exception_if_mldev='contents',
        exception_if_vertex='contents',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_dict_content',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=t.t_contents(
                types.ContentDict(
                    {'role': 'user', 'parts': [{'text': 'what is your name?'}]}
                ),
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_union_part_list',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=['What is your name?'],
        ),
        has_union=True,
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)
pytest_plugins = ('pytest_asyncio',)


def test_empty_part(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=t.t_contents(['']),
  )


def test_none_list_part(client):
  # pydantic will raise ValidationError
  with pytest.raises(ValidationError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[None],
    )


def test_image_file(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          'What is this image about?',
          {'inline_data': {'data': image_bytes, 'mimeType': 'image/png'}},
      ],
  )


def test_image_jpeg(client, image_jpeg):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=['What is this image about?', image_jpeg],
  )


def test_from_uri(client):
  # gs://generativeai-downloads/images/scones.jpg isn't supported in MLDev
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'What is this image about?',
            types.Part.from_uri(
                file_uri='gs://generativeai-downloads/images/scones.jpg',
                mime_type='image/jpeg',
            ),
        ],
    )


def test_user_content_text(client):
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=types.UserContent(parts='why is the sky blue?'),
  )
  assert response.text


def test_user_content_part(client):
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=types.UserContent(
            parts=[
                'what is this image about?',
                types.Part.from_uri(
                    file_uri='gs://generativeai-downloads/images/scones.jpg',
                    mime_type='image/jpeg',
                ),
            ]
        ),
    )
    assert response.text


def test_model_content_text(client):
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.UserContent(
                parts=[
                    'what is this image about?',
                    types.Part.from_uri(
                        file_uri=(
                            'gs://generativeai-downloads/images/scones.jpg'
                        ),
                        mime_type='image/jpeg',
                    ),
                ]
            ),
            types.ModelContent(
                parts=(
                    'The image is about a cozy breakfast or brunch with'
                    ' blueberry scones, coffee, and fresh flowers.'
                )
            ),
            types.UserContent(
                parts='Is this a good environment for a family gathering?'
            ),
        ],
    )
    assert response.text


def test_from_file_input(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/story.txt')
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=file,
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'Summarize this file',
            file,
        ],
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[['Summarize this file', file]],
    )


def test_from_file_dict_input(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/story.txt')
    file_dict = file.model_dump()
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=file_dict,
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'Summarize this file',
            file_dict,
        ],
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[['Summarize this file', file_dict]],
    )


def test_from_uploaded_file_uri(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/story.txt')
    file_part = types.Part.from_uri(file_uri=file.uri, mime_type='text/plain')
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=file_part,
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'Summarize this file',
            file_part,
        ],
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[['Summarize this file', file_part]],
    )


def test_from_uri_inferred_mime_type(client):
  # gs://generativeai-downloads/images/scones.jpg isn't supported in MLDev
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'What is this image about?',
            types.Part.from_uri(
                file_uri='gs://generativeai-downloads/images/scones.jpg'
            ),
        ],
    )


def test_from_uri_invalid_inferred_mime_type(client):
  # Throws ValueError if mime_type cannot be inferred.
  with pytest.raises(ValueError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'What is this image about?',
            types.Part.from_uri(
                file_uri='uri/without/mime/type'
            ),
        ],
    )


def test_audio_uri(client):
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            """
        Provide a summary for the audio in the beginning of the transcript.
        Provide concise chapter titles with timestamps.
        Do not make up any information that is not part of the audio.
        """,
            types.Part.from_uri(
                file_uri='gs://cloud-samples-data/generative-ai/audio/pixel.mp3',
                mime_type='audio/mpeg',
            ),
        ],
        config={
            'system_instruction': (
                'You are a helpful assistant for audio transcription.'
            )
        },
    )


def test_pdf_uri(client):
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'summarize the pdf in concise and professional tone',
            types.Part.from_uri(
                file_uri='gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf',
                mime_type='application/pdf',
            ),
        ],
        config={
            'system_instruction': (
                'You are a helpful assistant for academic literature review.'
            )
        },
    )


def test_video_uri(client):
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            """
            summarize the video in concise and professional tone.
            the summary should include all important information said in the video.
            """,
            types.Part.from_uri(
                file_uri='gs://cloud-samples-data/generative-ai/video/pixel8.mp4',
                mime_type='video/mp4',
            ),
        ],
        config={
            'system_instruction': (
                'you are a helpful assistant for market research.'
            )
        },
    )


def test_video_audio_uri(client):
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            """
            Is the audio related to the video?
            If so, how?
            What are the common themes?
            What are the different emphases?
            """,
            types.Part.from_uri(
                file_uri='gs://cloud-samples-data/generative-ai/video/pixel8.mp4',
                mime_type='video/mp4',
            ),
            types.Part.from_uri(
                file_uri='gs://cloud-samples-data/generative-ai/audio/pixel.mp3',
                mime_type='audio/mpeg',
            ),
        ],
        config={
            'system_instruction': (
                'you are a helpful assistant for people with visual and hearing'
                ' disabilities.'
            )
        },
    )


def test_file(client):
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    file = types.File(
        uri='https://generativelanguage.googleapis.com/v1beta/files/8q6j6weg80ey',
        mime_type='text/plain',
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'Summarize this file',
            file,
        ],
    )


def test_file_error(client):
  # missing mime_type
  with pytest.raises(ValueError):
    file = types.File(
        uri='https://generativelanguage.googleapis.com/v1beta/files/8q6j6weg80ey',
    )
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            'Summarize this file',
            file,
        ],
    )


def test_from_text(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[types.Part.from_text(text='What is your name?')],
  )


def test_from_bytes_image(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          'What is this image about?',
          types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
      ],
  )


def test_from_bytes_image_dict(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          {'text': 'What is this image about?'},
          {'inline_data': {'data': image_bytes, 'mimeType': 'image/png'}},
      ],
  )


def test_from_bytes_image_none(client):
  with pytest.raises(errors.ClientError) as e:
    client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            {'text': 'What is this image about?'},
            {'inline_data': {'data': None, 'mimeType': 'image/png'}},
        ],
    )
  assert 'INVALID_ARGUMENT' in str(e)


def test_from_bytes_video(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          'What is this video about?',
          types.Part.from_bytes(data=video_bytes, mime_type='video/mp4'),
      ],
  )


def test_from_bytes_audio(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          'What is this audio about?',
          types.Part.from_bytes(data=audio_bytes, mime_type='audio/mpeg'),
      ],
  )


def test_from_bytes_pdf(client):
  client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          'What is this pdf about?',
          types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf'),
      ],
  )


def test_from_function_call_response(client):
  function_call = types.Part.from_function_call(
      name='get_weather', args={'location': 'Boston'}
  )
  function_response = types.Part.from_function_response(
      name='get_weather', response={'weather': 'sunny'}
  )
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=[
          'what is the weather in Boston?',
          function_call,
          function_response,
      ],
  )

  assert 'sunny' in response.text
  assert 'Boston' in response.text


@pytest.mark.asyncio
async def test_image_base64_stream_async(client):
  async for part in await client.aio.models.generate_content_stream(
      model='gemini-2.5-flash',
      contents=[
          'What is this image about?',
          {'inline_data': {'data': image_string, 'mimeType': 'image/png'}},
      ],
  ):
    pass


# function_call and function_response are tested in generate_content_tools.py
