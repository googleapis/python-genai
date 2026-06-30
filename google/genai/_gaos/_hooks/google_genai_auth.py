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

"""Google GenAI authentication hooks for the embedded Speakeasy SDK."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Union, cast

import httpx

from .. import types, utils
from .types import BeforeRequestContext, BeforeRequestHook


GOOGLE_GENAI_API_REVISION = "2026-05-20"
_MANAGED_BEARER_AUTH = "google_genai_managed_bearer_auth"


class GoogleGenAISecurityProvider:
    """Callable security source that keeps generated auth refreshes retry-safe."""

    def __init__(
        self,
        *,
        access_token: Callable[[], str],
        default_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._access_token = access_token
        self._default_headers = dict(default_headers or {})
        self._pending_access_token: Optional[str] = None

    def __call__(self) -> types.Security:
        if self._pending_access_token is None:
            self._pending_access_token = self._access_token()

        return types.Security(
            access_token=self._pending_access_token,
            default_headers=self._default_headers or None,
        )

    def consume(self) -> None:
        self._pending_access_token = None


class GoogleGenAIAuthHook(BeforeRequestHook):
    """Applies Google GenAI headers and custom auth before sending requests."""

    def before_request(
        self,
        hook_ctx: BeforeRequestContext,
        request: httpx.Request,
    ) -> Union[httpx.Request, Exception]:
        security = _resolve_security(hook_ctx.security_source)

        _apply_default_headers(security, request)
        _apply_api_revision(hook_ctx, request)
        _apply_user_project(hook_ctx, request)
        _apply_auth(security, request)

        return request


def _resolve_security(security_source: Any) -> Optional[types.Security]:
    security = security_source

    if callable(security_source):
        security = security_source()
        consume = getattr(security_source, "consume", None)
        if callable(consume):
            consume()

    security = utils.get_security_from_env(security, types.Security)
    if security is None:
        return None

    if isinstance(security, types.Security):
        return security

    if isinstance(security, Mapping):
        return types.Security(**security)

    return cast(types.Security, security)


def _apply_default_headers(
    security: Optional[types.Security], request: httpx.Request
) -> None:
    headers = security.default_headers if security else None
    for key, value in (headers or {}).items():
        if request.headers.get(key) is None:
            request.headers[key] = value


def _apply_api_revision(
    hook_ctx: BeforeRequestContext, request: httpx.Request
) -> None:
    if request.headers.get("Api-Revision") is not None:
        return

    api_revision = hook_ctx.config.globals.api_revision
    request.headers["Api-Revision"] = api_revision or GOOGLE_GENAI_API_REVISION


def _apply_user_project(
    hook_ctx: BeforeRequestContext, request: httpx.Request
) -> None:
    user_project = hook_ctx.config.globals.user_project
    if user_project and request.headers.get("x-goog-user-project") is None:
        request.headers["x-goog-user-project"] = user_project


def _has_auth_headers(request: httpx.Request) -> bool:
    return (
        request.headers.get("authorization") is not None
        or request.headers.get("x-goog-api-key") is not None
    )


def _has_user_auth_headers(request: httpx.Request) -> bool:
    return (
        not request.extensions.get(_MANAGED_BEARER_AUTH)
        and _has_auth_headers(request)
    )


def _apply_auth(
    security: Optional[types.Security], request: httpx.Request
) -> None:
    if security is None or _has_user_auth_headers(request):
        return

    if security.api_key:
        request.extensions.pop(_MANAGED_BEARER_AUTH, None)
        request.headers["x-goog-api-key"] = security.api_key
        return

    if security.access_token:
        request.extensions[_MANAGED_BEARER_AUTH] = True
        request.headers["Authorization"] = _bearer(security.access_token)


def _bearer(token: str) -> str:
    return token if token.lower().startswith("bearer ") else f"Bearer {token}"
