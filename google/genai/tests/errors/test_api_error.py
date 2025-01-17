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


"""Unit Tests for the APIError class.

End to end tests should be in models/test_generate_content.py.
"""


from typing import cast

import requests

from ... import errors


def test_constructor_code_none_error_in_json_code_in_error():
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'error': {
              'code': 400,
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          }
      }

  actual_error = errors.APIError(
      None,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'code': 400,
          'error': {
              'code': (
                  500
              ),  # differentiate from the code in the outer level for test purpose.
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          },
      }

  actual_error = errors.APIError(
      None,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'error': {
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          }
      }

  actual_error = errors.APIError(
      None,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'error': {
              'code': 400,
              'message': 'error message',
              'status': 'INVALID_ARGUMENT',
          }
      }

  actual_error = errors.APIError(
      400,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'message': 'error message',
          'status': 'INVALID_ARGUMENT',
          'code': 400,
      }

  actual_error = errors.APIError(
      400,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'status': 'OUTER_INVALID_ARGUMENT_STATUS',
          'error': {
              'code': 400,
              'message': 'error message',
              'status': 'INNER_INVALID_ARGUMENT_STATUS',
          },
      }

  actual_error = errors.APIError(
      400,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'error': {
              'code': 400,
              'message': 'error message',
          }
      }

  actual_error = errors.APIError(
      400,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'message': 'OUTER_ERROR_MESSAGE',
          'error': {
              'code': 400,
              'message': 'INNER_ERROR_MESSAGE',
              'status': 'INVALID_ARGUMENT',
          },
      }

  actual_error = errors.APIError(
      400,
      FakeResponse(),
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
  class FakeResponse(requests.Response):

    def json(self):
      return {
          'error': {
              'code': 400,
              'status': 'INVALID_ARGUMENT',
          }
      }

  actual_error = errors.APIError(
      400,
      FakeResponse(),
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


def test_constructor_code_exist_json_decoder_error():
  class FakeResponse(requests.Response):

    def json(self):
      raise requests.exceptions.JSONDecodeError(
          'json decode error', 'json string', 10
      )

  actual_error = errors.APIError(
      400,
      FakeResponse(),
  )
  assert actual_error.code == 400
  assert (
      actual_error.message == ''
  )  # response.text defaults to '' in requests.Response.
  assert actual_error.status is None
  assert actual_error.details == {
      'message': '',
      'status': None,
  }


def test_constructor_code_none_json_decoder_error():
  class FakeResponse(requests.Response):

    def json(self):
      raise requests.exceptions.JSONDecodeError(
          'json decode error', 'json string', 10
      )

  actual_error = errors.APIError(
      None,
      FakeResponse(),
  )
  assert actual_error.code is None
  assert (
      actual_error.message == ''
  )  # response.text defaults to '' in requests.Response.
  assert actual_error.status is None
  assert actual_error.details == {
      'message': '',
      'status': None,
  }
