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


import base64
import json
from unittest import mock

import pytest

from .. import pytest_helper

from ... import _api_client as google_genai_api_client_module
from ... import _common as common_module
from ... import client as google_genai_client_module
from ... import types


# 64 chars in url safe base64.
_BASE64_URL_SAFE = (
    '-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)
_RAW_BYTES = (
    b'\xfb\xf6\x9bq\xd7\x9f\x82\x18\xa3\x92Y\xa7\xa2\x9a\xab\xb2\xdb\xaf\xc3\x1c\xb3\x00\x10\x83\x10Q\x87'
    b' \x92\x8b0\xd3\x8fA\x14\x93QU\x97a\x9d5\xdb~9\xeb\xbf='
)
# 64 chars in normal base64 is invalid format for pydantic `val_json_bytes`.
_BASE64_NOT_URL_SAFE = (
    '+/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789==='
)
assert base64.b64decode(_BASE64_NOT_URL_SAFE) == _RAW_BYTES


@pytest.fixture
def client(use_vertex):
  if use_vertex:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, project='test-project', location='test-location'
    )
  else:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, api_key='test-api-key'
    )

@pytest.fixture
def encode_unserializable_types_method():
  with mock.patch.object(common_module, 'encode_unserializable_types', wraps=common_module.encode_unserializable_types) as method:
    yield method


pytestmark = [pytest.mark.parametrize('use_vertex', [True, False])]


@pytest.fixture
def mock_request_method():
  with mock.patch.object(
      google_genai_api_client_module.BaseApiClient, 'request'
  ) as request_method:
    yield request_method


# This test checks if user pass in valid base64 string(url safe base64)
# via pydantic type, then SDK will return the raw bytes in pydantic type.
@pytest.mark.usefixtures('client', 'mock_request_method', 'encode_unserializable_types_method')
@pytest.mark.parametrize('bytes_input', [_RAW_BYTES, _BASE64_URL_SAFE])
def test_base64_pydantic_input_success(
    client, mock_request_method, encode_unserializable_types_method, bytes_input
):
  mock_request_method.return_value = types.HttpResponse(
      headers={'header_key': 'header_value'},
      body=json.dumps({
          'candidates': [
              {'content': {'parts': [{'text': 'Hello World'}], 'role': 'model'}}
          ]
      }),
  )

  response = client.models.generate_content(
      model='gemini-2.5-flash-001',
      contents=types.Content(
          role='user',
          parts=[
              types.Part(
                  inline_data=types.Blob(
                      mime_type='image/png',
                      data=bytes_input,
                  )
              )
          ],
      ),
  )

  encode_unserializable_types_method.assert_called()
  assert mock_request_method.call_count == 1
  assert (
      pytest_helper.get_value_ignore_key_case(
          mock_request_method.call_args[0][2]['contents'][0]['parts'][0],
          'inlineData'
      )['data']
      == _BASE64_URL_SAFE
  )
  assert response.candidates[0].content == types.Content(
      role='model',
      parts=[types.Part(text='Hello World')],
  )


# This test checks if user pass in valid base64 string(url safe base64)
# via dict type, then SDK will return the raw bytes in pydantic type.
@pytest.mark.usefixtures('client', 'mock_request_method', 'encode_unserializable_types_method')
@pytest.mark.parametrize('bytes_input', [_RAW_BYTES, _BASE64_URL_SAFE])
def test_base64_dict_input_success(client, mock_request_method, encode_unserializable_types_method, bytes_input):
  mock_request_method.return_value = types.HttpResponse(
      headers={'header_key': 'header_value'},
      body = json.dumps({
          'candidates': [
              {'content': {'parts': [{'text': 'Hello World'}], 'role': 'model'}}
          ]
      }),
  )

  response = client.models.generate_content(
      model='gemini-2.5-flash-001',
      contents={
          'role': 'user',
          'parts': [
              {
                  'inlineData': {
                      'mimeType': 'image/png',
                      'data': bytes_input,
                  }
              }
          ],
      },
  )

  encode_unserializable_types_method.assert_called()
  assert mock_request_method.call_count == 1
  assert (
      pytest_helper.get_value_ignore_key_case(
          mock_request_method.call_args[0][2]['contents'][0]['parts'][0],
          'inlineData'
      )['data']
      == _BASE64_URL_SAFE
  )
  assert response.candidates[0].content == types.Content(
      role='model',
      parts=[types.Part(text='Hello World')],
  )


# This test checks if user pass in invalid base64 string(normal base64 but not
# url safe) via pydantic type, then SDK will raise ValueError.
@pytest.mark.usefixtures('client', 'mock_request_method')
def test_base64_pydantic_input_failure(client):
  with pytest.raises(ValueError, match='Data should be valid base64'):
    client.models.generate_content(
        model='gemini-2.5-flash-001',
        contents=types.Content(
            role='user',
            parts=[
                types.Part(
                    inline_data=types.Blob(
                        mime_type='image/png',
                        data=_BASE64_NOT_URL_SAFE,
                    )
                )
            ],
        ),
    )


# This test checks if user pass in invalid base64 string(normal base64 but not
# url safe) via dict type, then SDK will raise ValueError.
@pytest.mark.usefixtures('client', 'mock_request_method')
def test_base64_dict_input_failure(client):
  with pytest.raises(ValueError, match='Data should be valid base64'):
    client.models.generate_content(
        model='gemini-2.5-flash-001',
        contents={
            'role': 'user',
            'parts': [{
                'inlineData': {
                    'mimeType': 'image/png',
                    'data': _BASE64_NOT_URL_SAFE,
                }
            }],
        },
    )


# This test checks if server returns valid base64 string(url safe base64),
# then SDK will return the raw bytes in pydantic type.
@pytest.mark.usefixtures('client', 'mock_request_method',)
def test_base64_pydantic_output_success(client, mock_request_method):
  mock_request_method.return_value = types.HttpResponse(
      headers={'header_key': 'header_value'},
      body=json.dumps({
          'candidates': [{
              'content': {
                  'parts': [{
                      'inlineData': {
                          'data': _BASE64_URL_SAFE,
                          'mimeType': 'image/png',
                      }
                  }],
                  'role': 'model',
              }
          }]
      }),
  )

  response = client.models.generate_content(
      model='gemini-2.5-flash-001',
      contents=types.Content(
          role='user',
          parts=[types.Part(text='Hello World')],
      ),
  )

  assert response.candidates[0].content == types.Content(
      role='model',
      parts=[
          types.Part(
              inline_data=types.Blob(data=_RAW_BYTES, mime_type='image/png')
          )
      ],
  )


# This test checks if server returns invalid base64 string(normal base64 but
# not url safe), then SDK will raise ValueError.
@pytest.mark.usefixtures('client', 'mock_request_method')
def test_base64_pydantic_output_failure(client, mock_request_method):
  mock_request_method.return_value = types.HttpResponse(
      headers={'header_key': 'header_value'},
      body=json.dumps({
          'candidates': [{
              'content': {
                  'parts': [{
                      'inlineData': {
                          'data': _BASE64_NOT_URL_SAFE,
                          'mimeType': 'image/png',
                      }
                  }],
                  'role': 'model',
              }
          }]
      }),
  )

  with pytest.raises(ValueError, match='Data should be valid base64'):
    client.models.generate_content(
        model='gemini-2.5-flash-001',
        contents=types.Content(
            role='user',
            parts=[types.Part(text='Hello World')],
        ),
    )
