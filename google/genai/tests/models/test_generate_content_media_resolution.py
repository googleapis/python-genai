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


from ... import types
from .. import pytest_helper

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_video_audio_uri_with_media_resolution',
        parameters=types._GenerateContentParameters(
            model='gemini-2.5-flash',
            contents=[
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_text(
                            text=(
                                'Is the audio related to the video? '
                                'If so, how? '
                                'What are the common themes? '
                                'What are the different emphases?'
                            )
                        )
                    ],
                ),
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_uri(
                            file_uri='gs://cloud-samples-data/generative-ai/video/pixel8.mp4',
                            mime_type='video/mp4',
                        )
                    ],
                ),
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_uri(
                            file_uri='gs://cloud-samples-data/generative-ai/audio/pixel.mp3',
                            mime_type='audio/mpeg',
                        )
                    ],
                ),
            ],
            config={
                'system_instruction': types.Content(
                    role='user',
                    parts=[
                        types.Part.from_text(
                            text=(
                                'you are a helpful assistant for people with '
                                'visual and hearing disabilities.'
                            )
                        )
                    ],
                ),
                'media_resolution': 'MEDIA_RESOLUTION_LOW',
            },
        ),
        exception_if_mldev='400',
    )
]


def test_low_media_resolution(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/google.png')
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[file, 'Describe the image.'],
        config=types.GenerateContentConfig(
            media_resolution='MEDIA_RESOLUTION_LOW',
            http_options= types.HttpOptions(api_version='v1alpha', base_url='https://generativelanguage.googleapis.com')
            ),
        )
    assert response.text


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.generate_content',
    test_table=test_table,
)
