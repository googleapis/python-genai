"""Compatibility surface for `google.genai._interactions`.

Preserves the reference Stainless module's *passive* surface: values, type aliases,
sentinels, helpers, aliases to actual runtime objects, and the legacy error-class
hierarchy (re-exported from `.core.error`). Intentionally does *not* expose private
Stainless behavioral classes whose semantics cannot be fully honored.

Skipped on purpose as it would trap callers with partial parity:
- `Client`, `AsyncClient`, `GeminiNextGenAPIClient`, `AsyncGeminiNextGenAPIClient`.
   The public `google.genai.Client` is the supported entry point.
- `APIResponse`, `AsyncAPIResponse`: omitting forces immediate `ImportError` instead of
   silent failures on `.parse()`, `.text`, `.json()`, etc.
"""

from __future__ import annotations

import os as _os
import pathlib as _pathlib
import typing as _typing
from abc import ABC, abstractmethod

import httpx as _httpx
import pydantic as _pydantic

from .. import types
from ..version import __version__
from .._gaos.utils.eventstreaming import AsyncStream, Stream
from .core.error import (
    APIConnectionError,
    APIError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    GeminiNextGenAPIClientError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)

__title__ = "google.genai._interactions"


# Type aliases mirroring Stainless `_types` re-exports.
NoneType = type(None)
Transport = _httpx.BaseTransport
ProxiesDict = _typing.Dict[
    "_typing.Union[str, _httpx.URL]",
    _typing.Union[None, str, _httpx.URL, _httpx.Proxy],
]
ProxiesTypes = _typing.Union[str, _httpx.Proxy, ProxiesDict]
Timeout = _httpx.Timeout
BaseModel = _pydantic.BaseModel


# Defaults mirroring Stainless module-level constants.
DEFAULT_TIMEOUT = _httpx.Timeout(timeout=60.0, connect=5.0)
DEFAULT_MAX_RETRIES = 2
DEFAULT_CONNECTION_LIMITS = _httpx.Limits(
    max_connections=100, max_keepalive_connections=20
)


class NotGiven:
    """Stainless `_types.NotGiven` sentinel — caller did not provide the arg (vs `None` = explicit null)."""

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = NotGiven()
not_given = NOT_GIVEN


class Omit:
    """Stainless `_types.Omit` sentinel. Strips the key from the request body."""

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "omit"


omit = Omit()


class RequestOptions(_typing.TypedDict, total=False):
    """Stainless `_types.RequestOptions` stub — importable + `**`-unpackable; not wired into bridge."""

    headers: _typing.Mapping[str, str]
    max_retries: int
    timeout: _typing.Union[float, _httpx.Timeout, None]
    params: _typing.Mapping[str, object]
    extra_json: _typing.Mapping[str, _typing.Any]
    idempotency_key: str
    follow_redirects: bool


class _BaseGeminiNextGenAPIClientAdapter(ABC):
    """Stainless adapter base — abstract hooks for project / location / auth resolution.

    Stub-only: speakeasy `Client` does not consume these. Mirrors reference
    abstract surface so user subclasses keep enforcing the same contract.
    """

    @abstractmethod
    def is_vertex_ai(self) -> bool: ...

    @abstractmethod
    def get_project(self) -> _typing.Optional[str]: ...

    @abstractmethod
    def get_location(self) -> _typing.Optional[str]: ...


class GeminiNextGenAPIClientAdapter(_BaseGeminiNextGenAPIClientAdapter):
    """Stub-only — speakeasy `Client` does not consume these hooks."""

    @abstractmethod
    def get_auth_headers(self) -> _typing.Optional[_typing.Dict[str, str]]: ...


class AsyncGeminiNextGenAPIClientAdapter(_BaseGeminiNextGenAPIClientAdapter):
    """Stub-only — speakeasy `AsyncClient` does not consume these hooks."""

    @abstractmethod
    async def async_get_auth_headers(
        self,
    ) -> _typing.Optional[_typing.Dict[str, str]]: ...


class DefaultHttpxClient(_httpx.Client):
    """Stainless `DefaultHttpxClient` — `httpx.Client` w/ SDK defaults pre-applied (timeout, limits, follow_redirects)."""

    def __init__(self, **kwargs: _typing.Any) -> None:
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        kwargs.setdefault("limits", DEFAULT_CONNECTION_LIMITS)
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)


class DefaultAsyncHttpxClient(_httpx.AsyncClient):
    """Stainless `DefaultAsyncHttpxClient` — `httpx.AsyncClient` w/ SDK defaults pre-applied."""

    def __init__(self, **kwargs: _typing.Any) -> None:
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        kwargs.setdefault("limits", DEFAULT_CONNECTION_LIMITS)
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)


try:
    from httpx_aiohttp import HttpxAiohttpClient as _HttpxAiohttpClient

    class DefaultAioHttpClient(_HttpxAiohttpClient):  # type: ignore[no-redef,misc]
        """Stainless `DefaultAioHttpClient` — `httpx.AsyncClient`-shaped via `httpx_aiohttp` w/ SDK defaults."""

        def __init__(self, **kwargs: _typing.Any) -> None:
            kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
            kwargs.setdefault("limits", DEFAULT_CONNECTION_LIMITS)
            kwargs.setdefault("follow_redirects", True)
            super().__init__(**kwargs)
except ImportError:

    class DefaultAioHttpClient(_httpx.AsyncClient):  # type: ignore[no-redef]
        """Stub when `httpx_aiohttp` absent — keeps `httpx.AsyncClient` shape; raises on construction so divergence isn't silent."""

        def __init__(self, *args: _typing.Any, **kwargs: _typing.Any) -> None:
            raise RuntimeError(
                "DefaultAioHttpClient requires the optional `httpx_aiohttp` dependency."
            )


def file_from_path(
    path: _typing.Union[str, "_os.PathLike[str]"],
) -> _typing.Tuple[str, bytes]:
    """Stainless helper: `(filename, contents_bytes)` tuple.

    Matches reference `_utils._utils.file_from_path` contract — reads the
    file eagerly and returns a `FileTypes` tuple so caller can unpack
    directly into multipart upload kwargs.
    """
    fs_path = _os.fspath(path)
    return _os.path.basename(fs_path), _pathlib.Path(fs_path).read_bytes()


__all__ = [
    "__title__",
    "__version__",
    "types",
    "NoneType",
    "Transport",
    "ProxiesTypes",
    "Timeout",
    "BaseModel",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_CONNECTION_LIMITS",
    "NotGiven",
    "NOT_GIVEN",
    "not_given",
    "Omit",
    "omit",
    "RequestOptions",
    "Stream",
    "AsyncStream",
    "GeminiNextGenAPIClientAdapter",
    "AsyncGeminiNextGenAPIClientAdapter",
    "DefaultHttpxClient",
    "DefaultAsyncHttpxClient",
    "DefaultAioHttpClient",
    "file_from_path",
    # Error classes re-exported from `.core.error` (compat hierarchy).
    "APIConnectionError",
    "APIError",
    "APIResponseValidationError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "GeminiNextGenAPIClientError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "UnprocessableEntityError",
]

for _name in (
    "APIConnectionError",
    "APIError",
    "APIResponseValidationError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "GeminiNextGenAPIClientError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "UnprocessableEntityError",
):
    globals()[_name].__module__ = "google.genai._interactions"
