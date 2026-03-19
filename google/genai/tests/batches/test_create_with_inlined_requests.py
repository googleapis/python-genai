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


"""Tests for batches.create() with inlined requests."""
import base64
import copy
import datetime
import os

import pytest
from unittest import mock

from ... import batches as batches_module
from ... import _transformers as t
from ... import types
from .. import pytest_helper

_GEMINI_MODEL = 'gemini-2.5-flash'
_DISPLAY_NAME = 'test_batch'

_MLDEV_GEMINI_MODEL = 'gemini-2.5-flash'

_SAFETY_SETTINGS = [
    {
        'category': 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'BLOCK_ONLY_HIGH',
    },
    {
        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'BLOCK_LOW_AND_ABOVE',
    },
]

_INLINED_REQUESTS = [
    {
        'contents': [{
            'parts': [{
                'text': 'what is the number after 1? return just the number.',
            }],
            'role': 'user',
        }],
        'metadata': {
            'key': 'request-1',
        },
        'config': {
            'safety_settings': _SAFETY_SETTINGS,
        },
    },
    {
        'contents': [{
            'parts': [{
                'text': 'what is the number after 2? return just the number.',
            }],
            'role': 'user',
        }],
        'metadata': {
            'key': 'request-2',
        },
        'config': {
            'safety_settings': _SAFETY_SETTINGS,
        },
    },
]
_INLINED_TEXT_REQUEST_UNION = {
    'contents': [{
        'parts': [{
            'text': 'high',
        }],
        'role': 'user',
    }],
    'config': {
        'response_modalities': ['TEXT'],
        'system_instruction': 'I say high, you say low',
        'thinking_config': {
            'include_thoughts': True,
            'thinking_budget': 4000,
        },
    },
}
_INLINED_TEXT_REQUEST = copy.deepcopy(_INLINED_TEXT_REQUEST_UNION)
_INLINED_TEXT_REQUEST['config']['system_instruction'] = t.t_content(
    'I say high, you say low'
)
_INLINED_TEXT_REQUEST['config']['tools'] = [{'google_search': {}}]
_INLINED_TEXT_REQUEST['config']['tool_config'] = {
    'retrieval_config': {'lat_lng': {'latitude': 37.422, 'longitude': -122.084}}
}

_INLINED_IMAGE_REQUEST = {
    'contents': [{
        'parts': [
            {'text': 'What is in this image?'},
            {
                'file_data': {
                    'file_uri': (
                        'https://generativelanguage.googleapis.com/v1beta/files/kje1wewvo85z'
                    ),
                    'mime_type': 'image/jpeg',
                },
            },
        ],
        'role': 'user',
    }],
    'config': {
        'temperature': 0.7,
        'top_p': 0.9,
        'top_k': 10,
    },
}
_INLINED_VIDEO_REQUEST = {
    'contents': [{
        'parts': [
            {
                'text': 'Summerize this video.',
            },
            {
                'file_data': {
                    'file_uri': (
                        'https://generativelanguage.googleapis.com/v1beta/files/tyvaih24jwje'
                    ),
                    'mime_type': 'video/mp4',
                },
                'video_metadata': {
                    'start_offset': '0s',
                    'end_offset': '5s',
                    'fps': 3,
                },
            },
        ],
        'role': 'user',
    }],
}
_IMAGE_PNG_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../data/google.png')
)
with open(_IMAGE_PNG_FILE_PATH, 'rb') as image_file:
  image_bytes = image_file.read()
  image_string = base64.b64encode(image_bytes).decode('utf-8')
_INLINED_IMAGE_BLOB_REQUEST = types.InlinedRequest(
    contents=[
        types.Content(
            parts=[
                types.Part(text='What is this image about?'),
                types.Part(
                    inline_data=types.Blob(
                        data=image_string,
                        mime_type='image/png',
                    ),
                ),
            ],
            role='user',
        )
    ]
)

# All tests will be run for both Vertex and MLDev.
test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_union_with_inlined_request',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src=_INLINED_REQUESTS,
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported in Vertex',
        has_union=True,
    ),
    pytest_helper.TestTableItem(
        name='test_with_inlined_request',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'inlined_requests': _INLINED_REQUESTS},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_with_inlined_request_config',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'inlined_requests': _INLINED_REQUESTS},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_union_with_inlined_request_system_instruction',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'inlined_requests': [_INLINED_TEXT_REQUEST_UNION]},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        has_union=True,
        exception_if_vertex='not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_with_image_file',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'inlined_requests': [_INLINED_IMAGE_REQUEST]},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_with_image_blob',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'inlined_requests': [_INLINED_IMAGE_BLOB_REQUEST]},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported',
    ),
    pytest_helper.TestTableItem(
        name='test_with_video_file',
        parameters=types._CreateBatchJobParameters(
            model=_MLDEV_GEMINI_MODEL,
            src={'inlined_requests': [_INLINED_VIDEO_REQUEST]},
            config={
                'display_name': _DISPLAY_NAME,
            },
        ),
        exception_if_vertex='not supported',
    ),
]

pytestmark = [
    pytest.mark.usefixtures('mock_timestamped_unique_name'),
    pytest_helper.setup(
        file=__file__,
        globals_for_file=globals(),
        test_method='batches.create',
        test_table=test_table,
    ),
]


def test_inlined_requests_include_internal_order_metadata(
    use_vertex, replays_prefix, http_options
):
  del use_vertex, replays_prefix, http_options
  request_payload = {
      'inlined_requests': [
          {'contents': [{'parts': [{'text': 'first'}], 'role': 'user'}]},
          {
              'contents': [{'parts': [{'text': 'second'}], 'role': 'user'}],
              'metadata': {'caller': 'external'},
          },
      ]
  }

  converted = batches_module._BatchJobSource_to_mldev(
      mock.MagicMock(), request_payload
  )
  requests = converted['requests']['requests']
  key = batches_module._INLINED_REQUEST_ORDER_METADATA_KEY

  assert requests[0]['metadata'][key] == '0'
  assert requests[1]['metadata'][key] == '1'
  assert requests[1]['metadata']['caller'] == 'external'


def test_inlined_requests_internal_order_metadata_overrides_reserved_key(
    use_vertex, replays_prefix, http_options
):
  del use_vertex, replays_prefix, http_options
  key = batches_module._INLINED_REQUEST_ORDER_METADATA_KEY
  request_payload = {
      'inlined_requests': [
          {
              'contents': [{'parts': [{'text': 'first'}], 'role': 'user'}],
              'metadata': {key: '999', 'caller': 'external'},
          },
      ]
  }

  converted = batches_module._BatchJobSource_to_mldev(
      mock.MagicMock(), request_payload
  )
  request = converted['requests']['requests'][0]

  assert request['metadata'][key] == '0'
  assert request['metadata']['caller'] == 'external'


def test_inlined_responses_are_reordered_by_internal_order_metadata(
    use_vertex, replays_prefix, http_options
):
  del use_vertex, replays_prefix, http_options
  key = batches_module._INLINED_REQUEST_ORDER_METADATA_KEY
  response_payload = {
      'inlinedResponses': {
          'inlinedResponses': [
              {
                  'metadata': {'request_key': 'two', key: '2'},
                  'response': {'candidates': []},
              },
              {
                  'metadata': {'request_key': 'zero', key: '0'},
                  'response': {'candidates': []},
              },
              {
                  'metadata': {'request_key': 'one', key: '1'},
                  'response': {'candidates': []},
              },
          ]
      }
  }

  converted = batches_module._BatchJobDestination_from_mldev(response_payload)
  responses = converted['inlined_responses']

  assert [item['metadata']['request_key'] for item in responses] == [
      'zero',
      'one',
      'two',
  ]
  assert all(key not in item['metadata'] for item in responses)


def test_inlined_responses_keep_input_order_when_metadata_missing(
    use_vertex, replays_prefix, http_options
):
  del use_vertex, replays_prefix, http_options
  key = batches_module._INLINED_REQUEST_ORDER_METADATA_KEY
  response_payload = {
      'inlinedResponses': {
          'inlinedResponses': [
              {
                  'metadata': {'request_key': 'two', key: '2'},
                  'response': {'candidates': []},
              },
              {
                  'metadata': {'request_key': 'zero'},
                  'response': {'candidates': []},
              },
              {
                  'metadata': {'request_key': 'one', key: '1'},
                  'response': {'candidates': []},
              },
          ]
      }
  }

  converted = batches_module._BatchJobDestination_from_mldev(response_payload)
  responses = converted['inlined_responses']

  assert [item['metadata']['request_key'] for item in responses] == [
      'two',
      'zero',
      'one',
  ]
  assert responses[0]['metadata'][key] == '2'
  assert key not in responses[1]['metadata']
  assert responses[2]['metadata'][key] == '1'


def test_inlined_responses_keep_input_order_when_metadata_non_numeric(
    use_vertex, replays_prefix, http_options
):
  del use_vertex, replays_prefix, http_options
  key = batches_module._INLINED_REQUEST_ORDER_METADATA_KEY
  response_payload = {
      'inlinedResponses': {
          'inlinedResponses': [
              {
                  'metadata': {'request_key': 'two', key: '2'},
                  'response': {'candidates': []},
              },
              {
                  'metadata': {'request_key': 'bad', key: 'not-a-number'},
                  'response': {'candidates': []},
              },
              {
                  'metadata': {'request_key': 'one', key: '1'},
                  'response': {'candidates': []},
              },
          ]
      }
  }

  converted = batches_module._BatchJobDestination_from_mldev(response_payload)
  responses = converted['inlined_responses']

  assert [item['metadata']['request_key'] for item in responses] == [
      'two',
      'bad',
      'one',
  ]
  assert responses[0]['metadata'][key] == '2'
  assert responses[1]['metadata'][key] == 'not-a-number'
  assert responses[2]['metadata'][key] == '1'


@pytest.mark.asyncio
async def test_async_create(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    batch_job = await client.aio.batches.create(
        model=_GEMINI_MODEL,
        src=_INLINED_REQUESTS,
    )
    assert batch_job.name.startswith('batches/')
    assert (
        batch_job.model == 'models/' + _GEMINI_MODEL
    )  # Converted to Gemini full name.
