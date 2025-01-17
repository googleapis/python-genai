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

"""Error classes for the GenAI SDK."""

from typing import Any, Optional, TYPE_CHECKING, Union

import requests


if TYPE_CHECKING:
  from .replay_api_client import ReplayResponse


class APIError(Exception):
  """General errors raised by the GenAI API."""
  code: int
  response: requests.Response

  status: Optional[str] = None
  message: Optional[str] = None
  response: Optional[Any] = None

  def __init__(
      self, code: int, response: Union[requests.Response, 'ReplayResponse']
  ):
    self.response = response

    if isinstance(response, requests.Response):
      try:
        # do not do any extra muanipulation on the response.
        # return the raw response json as is.
        response_json = response.json()
      except requests.exceptions.JSONDecodeError:
        response_json = {
            'message': response.text,
            'status': response.reason,
        }
    else:
      response_json = response.body_segments[0].get('error', {})

    self.details = response_json
    self.message = self._get_message(response_json)
    self.status = self._get_status(response_json)
    self.code = code if code else self._get_code(response_json)

    super().__init__(f'{self.code} {self.status}. {self.details}')

  def _get_status(self, response_json):
    return response_json.get(
        'status', response_json.get('error', {}).get('status', None)
    )

  def _get_message(self, response_json):
    return response_json.get(
        'message', response_json.get('error', {}).get('message', None)
    )

  def _get_code(self, response_json):
    return response_json.get(
        'code', response_json.get('error', {}).get('code', None)
    )

  def _to_replay_record(self):
    """Returns a dictionary representation of the error for replay recording.

    details is not included since it may expose internal information in the
    replay file.
    """
    return {
        'error': {
            'code': self.code,
            'message': self.message,
            'status': self.status,
        }
    }

  @classmethod
  def raise_for_response(
      cls, response: Union[requests.Response, 'ReplayResponse']
  ):
    """Raises an error with detailed error message if the response has an error status."""
    if response.status_code == 200:
      return

    status_code = response.status_code
    if 400 <= status_code < 500:
      raise ClientError(status_code, response)
    elif 500 <= status_code < 600:
      raise ServerError(status_code, response)
    else:
      raise cls(status_code, response)


class ClientError(APIError):
  """Client error raised by the GenAI API."""
  pass


class ServerError(APIError):
  """Server error raised by the GenAI API."""
  pass


class UnknownFunctionCallArgumentError(ValueError):
  """Raised when the function call argument cannot be converted to the parameter annotation."""

  pass


class UnsupportedFunctionError(ValueError):
  """Raised when the function is not supported."""


class FunctionInvocationError(ValueError):
  """Raised when the function cannot be invoked with the given arguments."""

  pass
