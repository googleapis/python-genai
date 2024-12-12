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


from ... import types
from .. import pytest_helper

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_video_audio_uri_with_media_resolution',
        parameters=types._GenerateContentParameters(
            model='gemini-2.0-flash-exp',
            contents=[
                types.Content(
                    role='user',
                    parts=[types.Part.from_text(
                        'Is the audio related to the video? '
                        'If so, how? '
                        'What are the common themes? '
                        'What are the different emphases?'
                    )],
                ),
                types.Content(
                    role='user',
                    parts=[types.Part.from_uri(
                        'gs://cloud-samples-data/generative-ai/video/pixel8.mp4',
                        'video/mp4',
                    )],
                ),
                types.Content(
                    role='user',
                    parts=[types.Part.from_uri(
                        'gs://cloud-samples-data/generative-ai/audio/pixel.mp3',
                        'audio/mpeg',
                    )],
                ),
            ],
            config={
                'system_instruction': types.Content(
                    role='user',
                    parts=[types.Part.from_text(
                        'you are a helpful assistant for people with visual '
                        'and hearing disabilities.'
                    )],
                ),
              'media_resolution': 'MEDIA_RESOLUTION_LOW',
            },
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


def test_video_audio_uri_with_media_resolution(client):
  with pytest_helper.exception_if_mldev(client, ValueError):
    client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=[
            """
                 Is the audio related to the video?
                 If so, how?
                 What are the common themes?
                 What are the different emphases?
                 """,
            types.Part.from_uri(
                'gs://cloud-samples-data/generative-ai/video/pixel8.mp4',
                'video/mp4',
            ),
            types.Part.from_uri(
                'gs://cloud-samples-data/generative-ai/audio/pixel.mp3',
                'audio/mpeg',
            ),
        ],
        config={
            'system_instruction': (
                'you are a helpful assistant for people with visual and hearing'
                ' disabilities.'
            ),
            'media_resolution': 'MEDIA_RESOLUTION_LOW',
        },
    )
