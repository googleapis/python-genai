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
# pyformat: disable

"""Error-class compatibility shim.

Backs `google.genai._interactions` imports of `BadRequestError`,
`NotFoundError`, `RateLimitError`, etc.

The generated SDK raises `GenAiError` (and per-operation subclasses thereof).
The bridge layer in `google_genai.py` translates those into the status-code
classes defined here via `wrap_sdk_error` / `wrap_sdk_call`.
"""

import inspect
import json
from typing import Any, Awaitable, Callable, Optional, TypeVar, cast

import httpx

from ..errors.genaierror import GenAiError
from ..errors.no_response_error import NoResponseError
from ..errors.responsevalidationerror import ResponseValidationError
from ..utils.eventstreaming import AsyncStream, Stream


T = TypeVar("T")


class GeminiNextGenAPIClientError(Exception):
    """Root of the GenAI error hierarchy."""


class APIError(GeminiNextGenAPIClientError):
    """General errors raised by the GenAI API.

    Carries `message`, `request`, `body`. Status-code subclasses add
    `response` and override `status_code` to a concrete value.
    """

    message: str
    request: httpx.Request
    body: object
    status_code: Optional[int] = None

    def __init__(
        self,
        message: str,
        request: httpx.Request,
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
        response: Optional[httpx.Response],
    ) -> "APIError":
        """Return the most specific APIError subclass for the given status."""
        target_cls = _status_class(status_code)
        msg = message if message is not None else _compose_message(status_code, body)
        if issubclass(target_cls, APIStatusError):
            if response is None:
                raise ValueError(
                    "APIStatusError subclasses require a response object."
                )
            status_cls = cast(type[APIStatusError], target_cls)
            return status_cls(msg, response=response, body=body)
        # Plain APIError fallback (status_code None or unexpected success
        # status like 201). Attach status_code to the instance for callers
        # that need to inspect it; not part of the Stainless contract for
        # APIError but covers the unexpected-status path.
        request = response.request if response is not None else None
        err = target_cls(msg, request, body=body)  # type: ignore[arg-type]
        if status_code is not None:
            err.status_code = status_code
        return err


class APIResponseValidationError(APIError):
    response: httpx.Response

    def __init__(
        self,
        response: httpx.Response,
        body: object,
        *,
        message: Optional[str] = None,
    ) -> None:
        super().__init__(
            message or "Data returned by API invalid for expected schema.",
            response.request,
            body=body,
        )
        self.response = response
        self.status_code = response.status_code


class APIStatusError(APIError):
    """Raised when an API response has a 4xx or 5xx status code."""

    response: httpx.Response

    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response,
        body: object,
    ) -> None:
        super().__init__(message, response.request, body=body)
        self.response = response
        self.status_code = response.status_code


class APIConnectionError(APIError):
    def __init__(
        self,
        *,
        message: str = "Connection error.",
        request: httpx.Request,
    ) -> None:
        super().__init__(message, request, body=None)


class APITimeoutError(APIConnectionError):
    def __init__(self, request: httpx.Request) -> None:
        super().__init__(
            message=(
                "Request timed out. This is a client-side timeout. You can "
                "increase the timeout by setting the `timeout` argument on "
                "your request or in the client http options."
            ),
            request=request,
        )


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


_STATUS_MAP = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


def _status_class(status_code: Optional[int]) -> type[APIError]:
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


def _parse_body(body: Any) -> Any:
    """Return parsed JSON if body is a JSON string, else the original value."""
    if isinstance(body, (dict, list)):
        return body
    if not isinstance(body, str):
        return body
    text = body.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return text


def _compose_message(status_code: Optional[int], body: Any) -> str:
    """Build an error message in `Error code: {status} - {body}` form.

    JSON body → `Error code: {status} - {body}`.
    Text body → raw text.
    Empty body → `Error code: {status}`.
    """
    if isinstance(body, (dict, list)):
        return f"Error code: {status_code} - {body}"
    if isinstance(body, str) and body.strip():
        return body.strip()
    if status_code is not None:
        return f"Error code: {status_code}"
    return "An error occurred"


def _wrap_validation_error(error: ResponseValidationError) -> APIResponseValidationError:
    response = error.raw_response
    body = _parse_body(error.body)
    wrapped = APIResponseValidationError(response, body, message=error.message)
    wrapped.__cause__ = error
    return wrapped


def _wrap_no_response_error(error: NoResponseError) -> APIConnectionError:
    wrapped = APIConnectionError(
        message=error.message or "No response received.",
        request=None,  # type: ignore[arg-type]
    )
    wrapped.__cause__ = error
    return wrapped


def _wrap_httpx_error(error: BaseException) -> APIConnectionError:
    """Translate an `httpx.HTTPError` into the compat connection-error class.

    `httpx.HTTPError.request` is a descriptor that raises `RuntimeError` when
    the request was never attached. Reads the underlying `_request` attribute
    directly. May pass `None` if the error was raised before request
    construction — type hint stays strict (mirrors Stainless) but runtime
    tolerates the edge case rather than fabricating a misleading stand-in.
    """
    request = getattr(error, "_request", None)
    if isinstance(error, httpx.TimeoutException):
        wrapped: APIConnectionError = APITimeoutError(request=request)  # type: ignore[arg-type]
    else:
        wrapped = APIConnectionError(
            message=str(error) or "Connection error.",
            request=request,  # type: ignore[arg-type]
        )
    wrapped.__cause__ = error
    return wrapped


def wrap_sdk_error(error: BaseException) -> BaseException:
    """Translate a generated SDK exception into an `APIError` subclass.

    Covers:
      - `ResponseValidationError` → `APIResponseValidationError`.
      - `NoResponseError` → `APIConnectionError`.
      - `httpx.TimeoutException` → `APITimeoutError`.
      - `httpx.HTTPError` → `APIConnectionError`.
      - `GenAiError` → status-code class via `APIError.generate`.

    Already-wrapped or unrelated exceptions pass through.
    """
    if isinstance(error, APIError):
        return error
    if isinstance(error, ResponseValidationError):
        return _wrap_validation_error(error)
    if isinstance(error, NoResponseError):
        return _wrap_no_response_error(error)
    if isinstance(error, httpx.HTTPError):
        return _wrap_httpx_error(error)
    if not isinstance(error, GenAiError):
        return error

    response = error.raw_response
    body = _parse_body(error.body)
    wrapped = APIError.generate(
        status_code=error.status_code,
        body=body,
        message=_compose_message(error.status_code, body),
        response=response,
    )
    wrapped.__cause__ = error
    return wrapped


_WRAP_EXCEPTIONS = (GenAiError, NoResponseError, httpx.HTTPError)


class CompatErrorHook:
    """Hook adapter that maps generated SDK exceptions to compat errors."""

    def after_error(
        self,
        hook_ctx: Any,
        response: Optional[httpx.Response],
        error: Optional[Exception],
    ) -> tuple[Optional[httpx.Response], Optional[Exception]]:
        if error is None:
            return response, error
        return response, wrap_sdk_error(error)  # type: ignore[return-value]

    def after_parse_error(
        self,
        hook_ctx: Any,
        response: httpx.Response,
        error: Exception,
    ) -> Exception:
        return wrap_sdk_error(error)  # type: ignore[return-value]


def wrap_sdk_call(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Execute `fn(*args, **kwargs)`, translating known SDK exceptions."""
    try:
        return fn(*args, **kwargs)
    except _WRAP_EXCEPTIONS as exc:
        raise wrap_sdk_error(exc) from exc


async def async_wrap_sdk_call(
    fn: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
) -> T:
    """Async variant of `wrap_sdk_call`."""
    try:
        return await fn(*args, **kwargs)
    except _WRAP_EXCEPTIONS as exc:
        raise wrap_sdk_error(exc) from exc


def is_stream(obj: Any) -> bool:
    """True if `obj` is a live SSE `Stream` / `AsyncStream`.

    Distinguishes the streaming iterator — which carries a `.generator` ready
    for `wrap_stream_errors` to wrap — from a `StreamedAPIResponse`, whose
    underlying stream only materializes once `.parse()` is called. Subclasses
    produced by `parse(to=MyStream)` are covered by `isinstance`.
    """
    return isinstance(obj, (Stream, AsyncStream))


def wrap_stream_errors(stream: Stream[Any]) -> Stream[Any]:
    """Wrap a `Stream` so iteration-time `GenAiError`s become `APIError`s.

    Mutates `stream.generator` in place and returns the same stream object so
    the caller's typing and identity are preserved.

    Precondition: caller ensures `is_stream(stream)` (see `_wrap_response_parse`
    and the `google_genai` bridge). A `StreamedAPIResponse` has no `.generator`.
    """
    original = stream.generator

    def _wrapped_gen():
        try:
            for chunk in original:
                yield chunk
        except _WRAP_EXCEPTIONS as exc:
            raise wrap_sdk_error(exc) from exc

    stream.generator = _wrapped_gen()
    return stream


def wrap_async_stream_errors(stream: AsyncStream[Any]) -> AsyncStream[Any]:
    """Async variant of `wrap_stream_errors`."""
    original = stream.generator

    async def _wrapped_agen():
        try:
            async for chunk in original:
                yield chunk
        except _WRAP_EXCEPTIONS as exc:
            raise wrap_sdk_error(exc) from exc

    stream.generator = _wrapped_agen()
    return stream


def _wrap_response_parse(response: Any) -> Any:
    """Shadow `response.parse` so SDK errors raised at parse-time and iteration-time become compat errors."""
    original_parse = response.parse

    def _parse(*args: Any, **kwargs: Any) -> Any:
        result = wrap_sdk_call(original_parse, *args, **kwargs)
        if is_stream(result):
            return wrap_stream_errors(result)
        return result

    response.parse = _parse  # type: ignore[method-assign]
    return response


def _wrap_async_response_parse(response: Any) -> Any:
    """Async variant of `_wrap_response_parse`."""
    original_parse = response.parse

    async def _parse(*args: Any, **kwargs: Any) -> Any:
        result = await async_wrap_sdk_call(original_parse, *args, **kwargs)
        if is_stream(result):
            return wrap_async_stream_errors(result)
        return result

    response.parse = _parse  # type: ignore[method-assign]
    return response


class _StreamingContextManagerProxy:
    """Proxy a sync `ResponseContextManager` so the entered response wraps parse."""

    __slots__ = ("_inner",)

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def __enter__(self) -> Any:
        try:
            response = self._inner.__enter__()
        except _WRAP_EXCEPTIONS as exc:
            raise wrap_sdk_error(exc) from exc
        if hasattr(response, "parse"):
            response = _wrap_response_parse(response)
        return response

    def __exit__(self, *exc_info: Any) -> Any:
        return self._inner.__exit__(*exc_info)


class _AsyncStreamingContextManagerProxy:
    """Async variant of `_StreamingContextManagerProxy`."""

    __slots__ = ("_inner",)

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    async def __aenter__(self) -> Any:
        try:
            response = await self._inner.__aenter__()
        except _WRAP_EXCEPTIONS as exc:
            raise wrap_sdk_error(exc) from exc
        if hasattr(response, "parse"):
            response = _wrap_async_response_parse(response)
        return response

    async def __aexit__(self, *exc_info: Any) -> Any:
        return await self._inner.__aexit__(*exc_info)


class _RawResponseAccessorProxy:
    """Sync proxy around the value of `with_raw_response` / `with_streaming_response`.

    Delegates attribute access to the wrapped instance. Methods are wrapped so
    that exceptions are translated via `wrap_sdk_error`, and the returned value
    is decorated based on shape:

    - `APIResponse` / `StreamedAPIResponse`: `.parse` is shadowed so parse-time
      errors are translated.
    - `ResponseContextManager` (from `with_streaming_response`): proxied so the
      response yielded by `__enter__` has `.parse` shadowed.
    """

    __slots__ = ("_inner",)

    def __init__(self, inner: Any) -> None:
        object.__setattr__(self, "_inner", inner)

    def __getattr__(self, name: str) -> Any:
        inner = object.__getattribute__(self, "_inner")
        attr = getattr(inner, name)
        if name.startswith("_") or not callable(attr):
            return attr

        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                result = attr(*args, **kwargs)
            except _WRAP_EXCEPTIONS as exc:
                raise wrap_sdk_error(exc) from exc
            if hasattr(result, "parse"):
                return _wrap_response_parse(result)
            if hasattr(result, "__enter__"):
                return _StreamingContextManagerProxy(result)
            return result

        return _wrapped


class _AsyncRawResponseAccessorProxy:
    """Async variant of `_RawResponseAccessorProxy`.

    The accessor's methods may return:
    - `Awaitable[AsyncAPIResponse]` (raw): await, then shadow `.parse`.
    - `AsyncResponseContextManager` (streaming): proxy so `__aenter__` yields a
      response with `.parse` shadowed.
    """

    __slots__ = ("_inner",)

    def __init__(self, inner: Any) -> None:
        object.__setattr__(self, "_inner", inner)

    def __getattr__(self, name: str) -> Any:
        inner = object.__getattribute__(self, "_inner")
        attr = getattr(inner, name)
        if name.startswith("_") or not callable(attr):
            return attr

        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                result = attr(*args, **kwargs)
            except _WRAP_EXCEPTIONS as exc:
                raise wrap_sdk_error(exc) from exc
            if hasattr(result, "__aenter__"):
                return _AsyncStreamingContextManagerProxy(result)
            if inspect.isawaitable(result):

                async def _await_and_wrap() -> Any:
                    try:
                        response = await result
                    except _WRAP_EXCEPTIONS as exc:
                        raise wrap_sdk_error(exc) from exc
                    if hasattr(response, "parse"):
                        return _wrap_async_response_parse(response)
                    return response

                return _await_and_wrap()
            if hasattr(result, "parse"):
                return _wrap_async_response_parse(result)
            return result

        return _wrapped


__all__ = [
    "APIConnectionError",
    "APIError",
    "APIResponseValidationError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "CompatErrorHook",
    "GeminiNextGenAPIClientError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "UnprocessableEntityError",
    "_AsyncRawResponseAccessorProxy",
    "_RawResponseAccessorProxy",
    "async_wrap_sdk_call",
    "is_stream",
    "wrap_async_stream_errors",
    "wrap_sdk_call",
    "wrap_sdk_error",
    "wrap_stream_errors",
]
