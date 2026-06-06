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


"""Unit Tests for the APIError class.

End to end tests should be in models/test_generate_content.py.
"""

import pickle

import httpx
import pytest

from ... import errors


def test_constructor_code_none_error_in_json_code_in_error():

  actual_error = errors.APIError(
      None,
      {
          'error': {
              'code': 400,
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          }
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message == 'error message'
  assert actual_error.status == 'INVALID_ARGUMENT'
  assert actual_error.details == {
      'error': {
          'code': 400,
          'message': 'error message',
          'status': 'INVALID_ARGUMENT',
      }
  }


def test_constructor_code_none_error_in_json_code_outside_error():

  actual_error = errors.APIError(
      None,
      {
          'code': 400,
          'error': {
              'code': 500,
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          },
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message == 'error message'
  assert actual_error.status == 'INVALID_ARGUMENT'
  assert actual_error.details == {
      'code': 400,
      'error': {
          'code': 500,
          'message': 'error message',
          'status': 'INVALID_ARGUMENT',
      },
  }


def test_constructor_code_not_present():

  actual_error = errors.APIError(
      None,
      {
          'error': {
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          }
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code is None
  assert actual_error.message == 'error message'
  assert actual_error.status == 'INVALID_ARGUMENT'
  assert actual_error.details == {
      'error': {
          'message': 'error message',
          'status': 'INVALID_ARGUMENT',
      }
  }


def test_constructor_code_exist_error_in_json():

  actual_error = errors.APIError(
      400,
      {
          'error': {
              'code': 400,
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          }
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message == 'error message'
  assert actual_error.status == 'INVALID_ARGUMENT'
  assert actual_error.details == {
      'error': {
          'code': 400,
          'message': 'error message',
          'status': 'INVALID_ARGUMENT',
      }
  }


def test_constructor_error_not_in_json():

  actual_error = errors.APIError(
      400,
      {
          'message': 'error message',
          'status': 'INVALID_ARGUMENT',
          'code': 400,
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message == 'error message'
  assert actual_error.status == 'INVALID_ARGUMENT'
  assert actual_error.details == {
      'message': 'error message',
      'status': 'INVALID_ARGUMENT',
      'code': 400,
  }


def test_constructor_error_in_json_status_outside_error():

  actual_error = errors.APIError(
      400,
      {
          'status': 'OUTER_INVALID_ARGUMENT_STATUS',
          'error': {
              'code': 400,
              'message': 'error message',
              'status': 'INNER_INVALID_ARGUMENT_STATUS',
          },
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message == 'error message'
  assert actual_error.status == 'OUTER_INVALID_ARGUMENT_STATUS'
  assert actual_error.details == {
      'status': 'OUTER_INVALID_ARGUMENT_STATUS',
      'error': {
          'code': 400,
          'message': 'error message',
          'status': 'INNER_INVALID_ARGUMENT_STATUS',
      },
  }


def test_constructor_status_not_present():

  actual_error = errors.APIError(
      400,
      {
          'error': {
              'code': 400,
              'message': 'error message',
          }
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message == 'error message'
  assert actual_error.status == None
  assert actual_error.details == {
      'error': {
          'code': 400,
          'message': 'error message',
      }
  }


def test_constructor_error_in_json_message_outside_error():

  actual_error = errors.APIError(
      400,
      {
          'message': 'OUTER_ERROR_MESSAGE',
          'error': {
              'code': 400,
              'message': 'INNER_ERROR_MESSAGE',
              'status': 'INVALID_ARGUMENT',
          },
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message == 'OUTER_ERROR_MESSAGE'
  assert actual_error.status == 'INVALID_ARGUMENT'
  assert actual_error.details == {
      'message': 'OUTER_ERROR_MESSAGE',
      'error': {
          'code': 400,
          'message': 'INNER_ERROR_MESSAGE',
          'status': 'INVALID_ARGUMENT',
      },
  }


def test_constructor_message_not_present():

  actual_error = errors.APIError(
      400,
      {
          'error': {
              'code': 400,
              'status': 'INVALID_ARGUMENT',
          }
      },
      httpx.Response(status_code=400),
  )

  assert actual_error.code == 400
  assert actual_error.message is None
  assert actual_error.status == 'INVALID_ARGUMENT'
  assert actual_error.details == {
      'error': {
          'code': 400,
          'status': 'INVALID_ARGUMENT',
      }
  }


def test_constructor_with_websocket_connection_closed_error():
  actual_error = errors.APIError(
      1007,
      'At most one response modality can be specified in the setup request.'
      ' To enable simultaneous transcription and audio output,',
      None,
  )
  assert actual_error.code == 1007
  assert (
      actual_error.details
      == 'At most one response modality can be specified in the setup request.'
      ' To enable simultaneous transcription and audio output,'
  )
  assert actual_error.status == None
  assert actual_error.message == None


def test_raise_for_websocket_connection_closed_error():
  try:
    errors.APIError.raise_error(
        1007,
        'At most one response modality can be specified in the setup request.'
        ' To enable simultaneous transcription and audio output,',
        None,
    )
  except errors.APIError as actual_error:
    assert actual_error.code == 1007
    assert (
        actual_error.details
        == 'At most one response modality can be specified in the setup'
        ' request.'
        ' To enable simultaneous transcription and audio output,'
    )
    assert actual_error.status == None
    assert actual_error.message == None


def test_raise_for_response_code_exist_json_decoder_error():
  class FakeResponse(httpx.Response):

    def read(self) -> bytes:
      self._content = b'{"data": {"key1": "value1", "key2"}'
      return self._content

  try:
    errors.APIError.raise_for_response(
        FakeResponse(
            status_code=503,
            extensions={'reason_phrase': b'Service Unavailable'},
        )
    )
  except errors.ServerError as actual_error:
    assert actual_error.code == 503
    assert actual_error.message == '{"data": {"key1": "value1", "key2"}'
    assert actual_error.status == 'Service Unavailable'
    assert actual_error.details == {
        'message': '{"data": {"key1": "value1", "key2"}',
        'status': 'Service Unavailable',
    }


def test_raise_for_response_client_error():
  class FakeResponse(httpx.Response):

    def read(self) -> bytes:
      self._content = (
          b'{"error": {"code": 400, "message": "error message", "status":'
          b' "INVALID_ARGUMENT"}}'
      )
      return self._content

  try:
    errors.APIError.raise_for_response(FakeResponse(status_code=400))
  except errors.ClientError as actual_error:
    assert actual_error.code == 400
    assert actual_error.message == 'error message'
    assert actual_error.status == 'INVALID_ARGUMENT'
    assert actual_error.details == {
        'error': {
            'code': 400,
            'message': 'error message',
            'status': 'INVALID_ARGUMENT',
        }
    }


def test_raise_for_response_server_error():
  class FakeResponse(httpx.Response):

    def read(self) -> bytes:
      self._content = (
          b'{"error": {"code": 500, "message": "error message", "status":'
          b' "SERVER_INTERNAL ERROR"}}'
      )
      return self._content

  try:
    errors.APIError.raise_for_response(FakeResponse(status_code=500))
  except errors.ServerError as actual_error:
    assert actual_error.code == 500
    assert actual_error.message == 'error message'
    assert actual_error.status == 'SERVER_INTERNAL ERROR'
    assert actual_error.details == {
        'error': {
            'code': 500,
            'message': 'error message',
            'status': 'SERVER_INTERNAL ERROR',
        }
    }


def test_api_error_is_picklable():
  pickled_error = pickle.loads(pickle.dumps(errors.APIError(1, {})))
  assert isinstance(pickled_error, errors.APIError)


@pytest.mark.asyncio
async def test_raise_for_async_response_client_error():
  class FakeResponse(httpx.Response):

    async def aread(self) -> bytes:
      self._content = (
          b'{"error": {"code": 400, "message": "error message", "status":'
          b' "INVALID_ARGUMENT"}}'
      )
      return self._content

  try:
    await errors.APIError.raise_for_async_response(
        FakeResponse(status_code=400)
    )
  except errors.ClientError as actual_error:
    assert actual_error.code == 400
    assert actual_error.message == 'error message'
    assert actual_error.status == 'INVALID_ARGUMENT'
    assert actual_error.details == {
        'error': {
            'code': 400,
            'message': 'error message',
            'status': 'INVALID_ARGUMENT',
        }
    }


@pytest.mark.asyncio
async def test_raise_for_async_response_server_error():
  class FakeResponse(httpx.Response):

    async def aread(self) -> bytes:
      self._content = (
          b'{"error": {"code": 500, "message": "error message", "status":'
          b' "SERVER_INTERNAL ERROR"}}'
      )
      return self._content

  try:
    await errors.APIError.raise_for_async_response(
        FakeResponse(status_code=500)
    )
  except errors.ServerError as actual_error:
    assert actual_error.code == 500
    assert actual_error.message == 'error message'
    assert actual_error.status == 'SERVER_INTERNAL ERROR'
    assert actual_error.details == {
        'error': {
            'code': 500,
            'message': 'error message',
            'status': 'SERVER_INTERNAL ERROR',
        }
    }


@pytest.mark.asyncio
async def test_raise_for_async_response_code_exist_json_decoder_error():
  class FakeResponse(httpx.Response):

    async def aread(self) -> bytes:
      self._content = b'{"data": {"key1": "value1", "key2"}'
      return self._content

  try:
    await errors.APIError.raise_for_async_response(
        FakeResponse(
            status_code=503,
            extensions={'reason_phrase': b'Service Unavailable'},
        )
    )
  except errors.ServerError as actual_error:
    assert actual_error.code == 503
    assert actual_error.message == '{"data": {"key1": "value1", "key2"}'
    assert actual_error.status == 'Service Unavailable'
    assert actual_error.details == {
        'message': '{"data": {"key1": "value1", "key2"}',
        'status': 'Service Unavailable',
    }
