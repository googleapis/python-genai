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
#

"""Private error classes for the Interactions API.

Shared by the public (`_gaos`) and private (`_gaos_private`) Interactions SDKs
and the hand-written Live Interactions transports. Not part of the public
`google.genai.errors` surface; `google.genai._interactions` re-exports these
through `_gaos/lib/compat_errors.py`.
"""

from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
  import httpx
  import httpx2


class GeminiNextGenAPIClientError(Exception):
  """Root of the GenAI Interactions error hierarchy."""


class APIError(GeminiNextGenAPIClientError):
  """General errors raised by the GenAI Interactions API.

  Carries `message`, `request`, `body`. Status-code subclasses add
  `response` and override `status_code` to a concrete value.
  """

  message: str
  request: Union['httpx.Request', 'httpx2.Request']
  body: object
  status_code: Optional[int] = None

  def __init__(
      self,
      message: str,
      request: Union['httpx.Request', 'httpx2.Request'],
      *,
      body: object,
  ) -> None:
    super().__init__(message)
    self.request = request
    self.message = message
    self.body = body

  def __str__(self) -> str:
    return self.message

  @classmethod
  def generate(
      cls,
      status_code: Optional[int],
      body: object,
      message: Optional[str],
      response: Optional[Union['httpx.Response', 'httpx2.Response']],
  ) -> 'APIError':
    """Returns the most specific APIError subclass for the given status."""
    target_cls = _status_class(status_code)
    msg = (
        message
        if message is not None
        else _compose_message(status_code, body)
    )
    if issubclass(target_cls, APIStatusError):
      if response is None:
        raise ValueError('APIStatusError subclasses require a response object.')
      return target_cls(msg, response=response, body=body)
    request = response.request if response is not None else None
    err = target_cls(msg, request, body=body)  # type: ignore[arg-type]
    if status_code is not None:
      err.status_code = status_code
    return err


class APIResponseValidationError(APIError):
  """Raised when data returned by the Interactions API fails schema validation."""

  response: Union['httpx.Response', 'httpx2.Response']

  def __init__(
      self,
      response: Union['httpx.Response', 'httpx2.Response'],
      body: object,
      *,
      message: Optional[str] = None,
  ) -> None:
    super().__init__(
        message or 'Data returned by API invalid for expected schema.',
        response.request,
        body=body,
    )
    self.response = response
    self.status_code = response.status_code


class APIStatusError(APIError):
  """Raised when an Interactions API response has a 4xx or 5xx status code."""

  response: Union['httpx.Response', 'httpx2.Response']

  def __init__(
      self,
      message: str,
      *,
      response: Union['httpx.Response', 'httpx2.Response'],
      body: object,
  ) -> None:
    super().__init__(message, response.request, body=body)
    self.response = response
    self.status_code = response.status_code


class APIConnectionError(APIError):
  """Raised when an Interactions API network or transport connection fails."""

  def __init__(
      self,
      *,
      message: str = 'Connection error.',
      request: Union['httpx.Request', 'httpx2.Request'],
  ) -> None:
    super().__init__(message, request, body=None)


class APITimeoutError(APIConnectionError):
  """Raised when an Interactions API request times out."""

  def __init__(
      self, request: Union['httpx.Request', 'httpx2.Request']
  ) -> None:
    super().__init__(
        message=(
            'Request timed out. This is a client-side timeout. You can '
            'increase the timeout by setting the `timeout` argument on '
            'your request or in the client http options.'
        ),
        request=request,
    )


class APIWebSocketError(APIConnectionError):
  """Raised when a live interaction WebSocket connection or frame fails."""

  close_code: Optional[int]
  http_status: Optional[int]
  server_code: Optional[str]

  def __init__(
      self,
      message: str = 'WebSocket connection error.',
      *,
      request: Any = None,
      close_code: Optional[int] = None,
      http_status: Optional[int] = None,
      server_code: Optional[str] = None,
  ) -> None:
    super().__init__(message=message, request=request)
    self.close_code = close_code
    self.http_status = http_status
    self.server_code = server_code


class BadRequestError(APIStatusError):
  status_code: int = 400  # type: ignore[assignment]


class AuthenticationError(APIStatusError):
  status_code: int = 401  # type: ignore[assignment]


class PermissionDeniedError(APIStatusError):
  status_code: int = 403  # type: ignore[assignment]


class NotFoundError(APIStatusError):
  status_code: int = 404  # type: ignore[assignment]


class ConflictError(APIStatusError):
  status_code: int = 409  # type: ignore[assignment]


class UnprocessableEntityError(APIStatusError):
  status_code: int = 422  # type: ignore[assignment]


class RateLimitError(APIStatusError):
  status_code: int = 429  # type: ignore[assignment]


class InternalServerError(APIStatusError):
  pass


_STATUS_MAP: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


def _status_class(
    status_code: Optional[int],
) -> type[APIError]:
  if status_code is None:
    return APIError
  cls = _STATUS_MAP.get(status_code)
  if cls is not None:
    return cls
  if 500 <= status_code < 600:
    return InternalServerError
  if 400 <= status_code < 500:
    return APIStatusError
  return APIError


def _compose_message(status_code: Optional[int], body: Any) -> str:
  """Builds an error message in `Error code: {status} - {body}` form."""
  if isinstance(body, (dict, list)):
    return f'Error code: {status_code} - {body}'
  if isinstance(body, str) and body.strip():
    return body.strip()
  if status_code is not None:
    return f'Error code: {status_code}'
  return 'An error occurred'
