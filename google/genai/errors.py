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

from typing import Callable, Optional, TYPE_CHECKING, Union
import httpx
import json


if TYPE_CHECKING:
  from .replay_api_client import ReplayResponse


class APIError(Exception):
  """General errors raised by the GenAI API."""
  code: int
  response: Union['ReplayResponse', httpx.Response]

  status: Optional[str] = None
  message: Optional[str] = None

  def __init__(
      self,
      code: int,
      response: Union['ReplayResponse', httpx.Response],
  ):
    self.response = response
    message = None
    if isinstance(response, httpx.Response):
      try:
        response_json = response.json()
      except (json.decoder.JSONDecodeError):
        message = response.text
        response_json = {
            'message': message,
            'status': response.reason_phrase,
        }
      except httpx.ResponseNotRead:
        message = 'Response not read'
        response_json = {
            'message': message,
            'status': response.reason_phrase,
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
      cls, response: Union['ReplayResponse', httpx.Response]
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


def _if_exception_type(
    *exception_types: type[Exception],
) -> Callable[[Exception], bool]:
  """Creates a predicate to check if the exception is of a given type.

  Args:
      *exception_types: The exception types to check for.

  Returns:
      Callable[Exception]: A predicate that returns True if the provided
      exception is of the given type(s).
  """

  def if_exception_type_predicate(exception: Exception) -> bool:
    """Bound predicate for checking an exception type."""
    return isinstance(exception, exception_types)

  return if_exception_type_predicate


def is_retriable(exception: Exception)-> bool:
  """Returns true if the exception is retrieable."""
  if isinstance(exception, APIError):
    # The following list [429, 500, 503] are the default retryable HTTP errors
    # in google/api-core.
    # https://github.com/googleapis/python-api-core/blob/ab22afdf311a2d87493c29833b35ef3b3ca8f246/google/api_core/retry/retry_base.py#L87-L90
    #
    # More errors can be added in a similar way if needed:
    # 408 Request Timeout
    # 429 Too Many Requests, it depends, should not be retried too fast.
    # 500 Internal Server Error, it depends.
    # 502 Bad Gateway, it depends.
    # 503 Service Unavailable
    # 504 Gateway Timeout
    return exception.code in [429, 500, 503]
  if _if_exception_type(httpx.ConnectError, httpx.TimeoutException)(exception):
    return True
  return False


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


class ExperimentalWarning(Warning):
  """Warning for experimental features."""
