# Copyright 2026 Google LLC
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

import base64

import pytest

from ..._interactions._utils import async_maybe_transform
from ..._interactions._utils import maybe_transform
from ..._interactions._utils._json import openapi_dumps
from ..._interactions.types import interaction_create_params


@pytest.mark.parametrize(
    'content_type,mime_type',
    [
        ('image', 'image/png'),
        ('audio', 'audio/wav'),
        ('video', 'video/mp4'),
        ('document', 'application/pdf'),
    ],
)
def test_media_input_bytes_are_base64_encoded(content_type, mime_type):
  body = maybe_transform(
      {
          'input': {
              'type': content_type,
              'data': b'media-bytes',
              'mime_type': mime_type,
          },
          'model': 'gemini-2.5-flash',
      },
      interaction_create_params.CreateModelInteractionParamsNonStreaming,
  )

  assert body['input']['data'] == base64.b64encode(b'media-bytes').decode(
      'ascii'
  )
  assert openapi_dumps(body)


@pytest.mark.parametrize(
    'content_type,mime_type',
    [
        ('image', 'image/png'),
        ('audio', 'audio/wav'),
        ('video', 'video/mp4'),
        ('document', 'application/pdf'),
    ],
)
@pytest.mark.asyncio
async def test_media_input_bytes_are_base64_encoded_async(
    content_type, mime_type
):
  body = await async_maybe_transform(
      {
          'input': {
              'type': content_type,
              'data': b'media-bytes',
              'mime_type': mime_type,
          },
          'model': 'gemini-2.5-flash',
      },
      interaction_create_params.CreateModelInteractionParamsNonStreaming,
  )

  assert body['input']['data'] == base64.b64encode(b'media-bytes').decode(
      'ascii'
  )
  assert openapi_dumps(body)
