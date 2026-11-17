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
# pylint: skip-file

"""Error-class compatibility shim.

Backs `google.genai._interactions` imports of `BadRequestError`,
`NotFoundError`, `RateLimitError`, etc.

The generated SDK raises `GenAiError` (and per-operation subclasses thereof).
The bridge layer in `google_genai.py` translates those into the status-code
classes re-exported here from `google.genai._interactions_errors` via
`wrap_sdk_error` / `wrap_sdk_call`.
"""

import inspect
import json
from typing import Any, Awaitable, Callable, Optional, TypeVar

try:
    import httpx2
except ImportError:
    httpx2 = None

try:
    import httpx
except ImportError:
    import httpx2 as httpx

_HTTPX_TIMEOUT_ERRORS = (
    (httpx.TimeoutException,)
    if httpx2 is None
    else (httpx.TimeoutException, httpx2.TimeoutException)
)
_HTTPX_HTTP_ERRORS = (
    (httpx.HTTPError,)
    if httpx2 is None
    else (httpx.HTTPError, httpx2.HTTPError)
)

from ..._interactions_errors import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    APIWebSocketError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    GeminiNextGenAPIClientError,
    APIError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
    _compose_message,
    _status_class,
)
from ..errors.genaierror import GenAiError
from ..errors.no_response_error import NoResponseError
from ..errors.responsevalidationerror import ResponseValidationError
from ..utils.eventstreaming import AsyncStream, Stream


T = TypeVar("T")


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
    if isinstance(error, _HTTPX_TIMEOUT_ERRORS):
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
    if isinstance(error, _HTTPX_HTTP_ERRORS):
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


_WRAP_EXCEPTIONS = (
    (GenAiError, NoResponseError, httpx.HTTPError)
    if httpx2 is None
    else (GenAiError, NoResponseError, httpx.HTTPError, httpx2.HTTPError)
)


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


async def _wrap_async_response_parse(response: Any) -> Any:
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
            response = await _wrap_async_response_parse(response)
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
                        return await _wrap_async_response_parse(response)
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
    "APIWebSocketError",
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
