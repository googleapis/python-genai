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

"""Helpers for embedding the generated NextGen SDK in the Google GenAI client."""

# This bridge intentionally reuses the parent GenAI client's protected transport,
# auth, and http option internals so the NextGen resource client behaves like
# the public google-genai resource it replaces.
# pylint: disable=protected-access,too-many-arguments

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, TypeVar, Union, cast

import functools
import io
import json
import mimetypes
import os
import warnings

import httpx

from ._hooks.google_genai_auth import (
    GOOGLE_GENAI_API_REVISION as _GOOGLE_GENAI_API_REVISION,
    GoogleGenAISecurityProvider,
)
from .agents import AsyncAgents as GeneratedAsyncAgents
from .agents import Agents as GeneratedAgents
from .interactions import AsyncInteractions as GeneratedAsyncInteractions
from .interactions import Interactions as GeneratedInteractions
from .lib.compat_errors import (
    _AsyncRawResponseAccessorProxy,
    _RawResponseAccessorProxy,
    async_wrap_sdk_call,
    is_stream,
    wrap_async_stream_errors,
    wrap_sdk_call,
    wrap_stream_errors,
)
from .sdk import AsyncGenAI, GenAI
from .types import environments
from .types import credentials
from .types import interactions
from .types.security import Security
from .utils import BackoffStrategy, RetryConfig, eventstreaming
from .triggers import AsyncTriggers as GeneratedAsyncTriggers
from .triggers import Triggers as GeneratedTriggers
from .webhooks import AsyncWebhooks as GeneratedAsyncWebhooks
from .webhooks import Webhooks as GeneratedWebhooks
from .environments import AsyncEnvironments as GeneratedAsyncEnvironments
from .environments import Environments as GeneratedEnvironments
from .credentials import AsyncCredentials as GeneratedAsyncCredentials
from .credentials import Credentials as GeneratedCredentials
from .voices import AsyncVoices as GeneratedAsyncVoices
from .voices import Voices as GeneratedVoices
from .files import AsyncFiles as GeneratedAsyncFiles
from .files import Files as GeneratedFiles
from ._internal import AsyncInternal as GeneratedAsyncInternal
from ._internal import Internal as GeneratedInternal


GOOGLE_GENAI_API_REVISION = _GOOGLE_GENAI_API_REVISION
_LEGACY_LYRIA_MODELS = frozenset({'lyria-3-pro-preview', 'lyria-3-clip-preview'})
ModelT = TypeVar('ModelT')


def get_google_genai_server_url(api_client: Any) -> str:
    """Returns the server URL from the parent Google GenAI API client."""
    server_url = api_client._http_options.base_url
    if not server_url:
        raise ValueError('Base URL must be set.')
    return str(server_url).rstrip('/')


def get_google_genai_api_version(api_client: Any) -> str:
    """Returns the generated path parameter for the parent client mode."""
    api_version = api_client._http_options.api_version or ''
    if api_client.vertexai and api_client.project and api_client.location:
        return (
            f'{api_version}/projects/{api_client.project}'
            f'/locations/{api_client.location}'
        )
    return api_version


def _get_google_genai_default_headers(
    api_client: Any,
) -> Optional[dict[str, str]]:
    headers = api_client._http_options.headers
    return dict(headers) if headers else None


def _get_google_genai_user_project(api_client: Any) -> Optional[str]:
    credentials = getattr(api_client, '_credentials', None)
    return getattr(credentials, 'quota_project_id', None)


class _GoogleGenAIAccessTokenProvider:
    def __init__(self, api_client: Any) -> None:
        self._api_client = api_client

    def __call__(self) -> str:
        return self._api_client._access_token()


def _get_google_genai_security(api_client: Any) -> Optional[Any]:
    default_headers = _get_google_genai_default_headers(api_client)

    if api_client.api_key:
        return Security(
            api_key=api_client.api_key,
            default_headers=default_headers,
        )

    if api_client.vertexai and (api_client.project or api_client.location):
        return GoogleGenAISecurityProvider(
            access_token=_GoogleGenAIAccessTokenProvider(api_client),
            default_headers=default_headers,
        )

    if default_headers:
        return Security(default_headers=default_headers)

    return None


_DEFAULT_MAX_RETRIES = 2
# Default backoff shape (ms): 0.5s initial, 8s cap, base 2. Individual fields
# are overridden by the matching `retry_options` value when set.
_DEFAULT_INITIAL_INTERVAL_MS = 500
_DEFAULT_MAX_INTERVAL_MS = 8000
_DEFAULT_EXPONENT = 2
_MAX_ELAPSED_TIME_MS = 30000


def _translate_retry_config(http_options: Any) -> RetryConfig:
    """Maps parent `HttpOptions.retry_options` onto a `RetryConfig`.

    `attempts` becomes the retry count (an unset `attempts` falls back to the
    default retry count). The delay-shaping options (`initial_delay`,
    `max_delay`, `exp_base`, `jitter`) and `http_status_codes` are honored when
    provided, each defaulting to the built-in behavior when omitted.
    """
    options = getattr(http_options, 'retry_options', None)

    attempts = getattr(options, 'attempts', None) if options is not None else None
    max_retries = attempts if attempts is not None else _DEFAULT_MAX_RETRIES + 1

    initial_interval = _DEFAULT_INITIAL_INTERVAL_MS
    max_interval = _DEFAULT_MAX_INTERVAL_MS
    exponent = _DEFAULT_EXPONENT
    jitter_ms = None
    status_codes_override = None

    if options is not None:
        if options.initial_delay is not None:
            initial_interval = int(options.initial_delay * 1000)
        if options.max_delay is not None:
            max_interval = int(options.max_delay * 1000)
        if options.exp_base is not None:
            exponent = options.exp_base
        if options.jitter is not None:
            jitter_ms = int(options.jitter * 1000)
        if options.http_status_codes:
            status_codes_override = [str(code) for code in options.http_status_codes]

    return RetryConfig(
        'attempt-count-backoff',
        BackoffStrategy(
            initial_interval,
            max_interval,
            exponent,
            _MAX_ELAPSED_TIME_MS,
            jitter_ms=jitter_ms,
        ),
        True,
        max_retries=max_retries,
        status_codes_override=status_codes_override,
    )


def build_google_genai_client(
    api_client: Any, api_version: Optional[str] = None
) -> GenAI:
    """Builds a generated NextGen client from the parent GenAI client."""
    http_options = api_client._http_options
    sdk = GenAI(
        security=_get_google_genai_security(api_client),
        api_version=api_version or get_google_genai_api_version(api_client),
        user_project=_get_google_genai_user_project(api_client),
        server_url=get_google_genai_server_url(api_client),
        client=getattr(api_client, '_httpx_client', None),
        timeout_ms=http_options.timeout,
        retry_config=_translate_retry_config(http_options),
    )
    return sdk


def build_google_genai_async_client(
    api_client: Any, api_version: Optional[str] = None
) -> AsyncGenAI:
    """Builds a generated NextGen client from the parent GenAI client."""
    http_options = api_client._http_options
    sdk = AsyncGenAI(
        security=_get_google_genai_security(api_client),
        api_version=api_version or get_google_genai_api_version(api_client),
        user_project=_get_google_genai_user_project(api_client),
        server_url=get_google_genai_server_url(api_client),
        async_client=getattr(api_client, '_async_httpx_client', None),
        timeout_ms=http_options.timeout,
        retry_config=_translate_retry_config(http_options),
    )
    return sdk


class GeminiNextGenInteractions(GeneratedInteractions):
    """Public interactions resource backed by the NextGen client.

    Subclasses the generated resource so newly generated methods (and the
    raw/streaming response wrappers) are exposed automatically. Only the
    methods that need legacy input/output normalization are overridden.

    Each override sits inside `if not TYPE_CHECKING:` so static type checkers
    see the inherited generated signature (full overload sets) rather than the
    runtime stub here.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)


    if not TYPE_CHECKING:
        def create(
            self,
            *,
            request: Any = None,
            api_version: Optional[str] = None,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            extra_body: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
            automatic_continuation: Optional[bool] = None,
            **body: Any,
        ) -> Union[
            interactions.Interaction,
            eventstreaming.Stream[interactions.InteractionSSEEvent],
        ]:
            """Creates a new interaction.

            :param request: Optional request object (`CreateInteractionRequest`).
            :param api_version: API version for request routing.
            :param extra_headers: Additional headers to set or replace on requests.
            :param extra_query: Additional query parameters to append to requests.
            :param extra_body: Additional JSON object fields to merge into request bodies.
            :param timeout: Override the default request timeout configuration
                for this method in seconds. When `automatic_continuation=True`,
                `timeout` (as well as `http_options.timeout` and
                `http_options.retry_options`) applies per continuation request
                (hop).
            :param automatic_continuation: When `True`, automatically resumes
                decoding across multiple continuation hops whenever a response
                or stream stops at the per-request decode token limit
                (`status='continuation_required'` with a `continuation_token`)
                until the interaction completes, reaches `incomplete` (e.g.
                `max_output_tokens`), requires action, or fails.
                - For `stream=True`, events from all continuation hops are
                  yielded sequentially on the returned `Stream`.
                - For `stream=False`, the final continued `Interaction` returned
                  by the server contains the full interaction with concatenated
                  steps and accumulated token usage.
                - Timeout & retry settings (`timeout`, `http_options.timeout`,
                  and `http_options.retry_options`) apply per continuation
                  request (hop). Transient errors on a continuation hop retry
                  that hop using the latest `continuation_token` without
                  restarting from the initial request.
                - Billing note: With `background=False`, each continuation hop
                  re-prefills the conversation and generated prefix, so input
                  tokens are billed on every hop (and summed in
                  `usage.total_input_tokens`). If an unrecoverable error occurs
                  after one or more hops have completed, those completed hops
                  are still billed. For server-managed continuation without
                  client-side hop loops, use `background=True` (with
                  `store=True`).
            """
            if request is not None:
                if body:
                    raise TypeError(_REQUEST_AND_BODY_ERROR)
                is_background = _request_background(request)
                is_store_false = _request_store_false(request)
                stream = _request_stream(request)
                has_caller_token = _request_has_continuation_token(request)
                if automatic_continuation is None:
                    req_auto = _get_value(request, 'automatic_continuation')
                    if req_auto is None:
                        req_auto = _get_value(
                            _get_value(request, 'body'),
                            'automatic_continuation',
                        )
                    automatic_continuation = req_auto
            else:
                is_background = bool(
                    _optional_bool(body.get('background'), default=False)
                )
                is_store_false = _optional_bool(body.get('store')) is False
                stream = _optional_bool(body.get('stream'), default=False)
                body = _normalize_create_body(body)
                has_caller_token = bool(body.get('continuation_token'))

            if is_background and automatic_continuation is False:
                raise ValueError(_AUTO_CONTINUE_AND_BACKGROUND_ERROR)

            auto_continue = bool(
                _optional_bool(automatic_continuation, default=False)
            )

            if is_store_false and not stream and auto_continue:
                raise ValueError(_AUTO_CONTINUE_AND_STORE_FALSE_ERROR)

            call_kwargs = {
                'api_version': api_version,
                'extra_headers': extra_headers,
                'extra_query': extra_query,
                'extra_body': extra_body,
                'timeout': timeout,
            }
            send_once = functools.partial(
                self._send_create_once, request, body, call_kwargs
            )

            response = send_once()
            if stream:
                if not is_stream(response):
                    return response

                wrapped_stream = wrap_stream_errors(response)
                if not auto_continue:
                    if not has_caller_token:
                        return _wrap_stream_incomplete_warning(
                            wrapped_stream,
                        )
                    return wrapped_stream

                return _wrap_stream_continuation(
                    wrapped_stream,
                    send_once,
                )

            if auto_continue:
                return _continue_unary_interaction(
                    response,
                    send_once,
                )
            result = _add_output_properties_if_interaction(response)
            if not has_caller_token:
                _warn_if_incomplete_unary(result)
            return result

        def _send_create_once(
            self,
            request: Any,
            body: Mapping[str, Any],
            call_kwargs: Mapping[str, Any],
            token: Optional[str] = None,
        ) -> Any:
            if request is not None:
                req = (
                    request
                    if token is None
                    else _with_request_continuation_token(request, token)
                )
                return wrap_sdk_call(
                    super().create,
                    request=req,
                    **call_kwargs,
                )
            req_body = (
                body
                if token is None
                else {**body, 'continuation_token': token}
            )
            return wrap_sdk_call(
                super().create,
                **cast(Any, req_body),
                **call_kwargs,
            )


    if not TYPE_CHECKING:
        def get(
            self,
            id: str,
            *,
            api_version: Optional[str] = None,
            include_input: Any = None,
            last_event_id: Any = None,
            stream: Any = False,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
        ) -> Union[
            interactions.Interaction,
            eventstreaming.Stream[interactions.InteractionSSEEvent],
        ]:
            stream_bool = bool(_optional_bool(stream, default=False))
            response = wrap_sdk_call(
                super().get,
                id=id,
                api_version=api_version,
                include_input=_optional_bool(include_input),
                last_event_id=_optional_str(last_event_id),
                stream=stream_bool,
                extra_headers=extra_headers,
                extra_query=extra_query,
                timeout=timeout,
            )
            if stream_bool:
                if not is_stream(response):
                    return response
                return cast(
                    eventstreaming.Stream[interactions.InteractionSSEEvent],
                    wrap_stream_errors(response),
                )
            return cast(
                interactions.Interaction, _add_output_properties_if_interaction(response)
            )

    if not TYPE_CHECKING:
        def cancel(
            self,
            id: str,
            *,
            api_version: Optional[str] = None,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
        ) -> interactions.Interaction:
            return cast(
                interactions.Interaction,
                _add_output_properties_if_interaction(
                    wrap_sdk_call(
                        super().cancel,
                        id=id,
                        api_version=api_version,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        timeout=timeout,
                    )
                ),
            )

    if not TYPE_CHECKING:
        def delete(
            self,
            id: str,
            *,
            api_version: Optional[str] = None,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
        ) -> Any:
            return wrap_sdk_call(
                super().delete,
                id=id,
                api_version=api_version,
                extra_headers=extra_headers,
                extra_query=extra_query,
                timeout=timeout,
            )


class AsyncGeminiNextGenInteractions(GeneratedAsyncInteractions):
    """Async public interactions resource backed by the NextGen client."""

    def __init__(self, api_client: Any):
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)


    if not TYPE_CHECKING:
        async def create(
            self,
            *,
            request: Any = None,
            api_version: Optional[str] = None,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            extra_body: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
            automatic_continuation: Optional[bool] = None,
            **body: Any,
        ) -> Union[
            interactions.Interaction,
            eventstreaming.AsyncStream[interactions.InteractionSSEEvent],
        ]:
            """Creates a new interaction asynchronously.

            :param request: Optional request object (`CreateInteractionRequest`).
            :param api_version: API version for request routing.
            :param extra_headers: Additional headers to set or replace on requests.
            :param extra_query: Additional query parameters to append to requests.
            :param extra_body: Additional JSON object fields to merge into request bodies.
            :param timeout: Override the default request timeout configuration
                for this method in seconds. When `automatic_continuation=True`,
                `timeout` (as well as `http_options.timeout` and
                `http_options.retry_options`) applies per continuation request
                (hop).
            :param automatic_continuation: When `True`, automatically resumes
                decoding across multiple continuation hops whenever a response
                or stream stops at the per-request decode token limit
                (`status='continuation_required'` with a `continuation_token`)
                until the interaction completes, reaches `incomplete` (e.g.
                `max_output_tokens`), requires action, or fails.
                - For `stream=True`, events from all continuation hops are
                  yielded sequentially on the returned `AsyncStream`.
                - For `stream=False`, the final continued `Interaction` returned
                  by the server contains the full interaction with concatenated
                  steps and accumulated token usage.
                - Timeout & retry settings (`timeout`, `http_options.timeout`,
                  and `http_options.retry_options`) apply per continuation
                  request (hop). Transient errors on a continuation hop retry
                  that hop using the latest `continuation_token` without
                  restarting from the initial request.
                - Billing note: With `background=False`, each continuation hop
                  re-prefills the conversation and generated prefix, so input
                  tokens are billed on every hop (and summed in
                  `usage.total_input_tokens`). If an unrecoverable error occurs
                  after one or more hops have completed, those completed hops
                  are still billed. For server-managed continuation without
                  client-side hop loops, use `background=True` (with
                  `store=True`).
            """
            if request is not None:
                if body:
                    raise TypeError(_REQUEST_AND_BODY_ERROR)
                is_background = _request_background(request)
                is_store_false = _request_store_false(request)
                stream = _request_stream(request)
                has_caller_token = _request_has_continuation_token(request)
                if automatic_continuation is None:
                    req_auto = _get_value(request, 'automatic_continuation')
                    if req_auto is None:
                        req_auto = _get_value(
                            _get_value(request, 'body'),
                            'automatic_continuation',
                        )
                    automatic_continuation = req_auto
            else:
                is_background = bool(
                    _optional_bool(body.get('background'), default=False)
                )
                is_store_false = _optional_bool(body.get('store')) is False
                stream = _optional_bool(body.get('stream'), default=False)
                body = _normalize_create_body(body)
                has_caller_token = bool(body.get('continuation_token'))

            if is_background and automatic_continuation is False:
                raise ValueError(_AUTO_CONTINUE_AND_BACKGROUND_ERROR)

            auto_continue = bool(
                _optional_bool(automatic_continuation, default=False)
            )

            if is_store_false and not stream and auto_continue:
                raise ValueError(_AUTO_CONTINUE_AND_STORE_FALSE_ERROR)

            call_kwargs = {
                'api_version': api_version,
                'extra_headers': extra_headers,
                'extra_query': extra_query,
                'extra_body': extra_body,
                'timeout': timeout,
            }
            send_once = functools.partial(
                self._send_create_once, request, body, call_kwargs
            )

            response = await send_once()
            if stream:
                if not is_stream(response):
                    return response

                wrapped_stream = wrap_async_stream_errors(response)
                if not auto_continue:
                    if not has_caller_token:
                        return _wrap_async_stream_incomplete_warning(
                            wrapped_stream
                        )
                    return wrapped_stream

                return _wrap_async_stream_continuation(
                    wrapped_stream,
                    send_once,
                )

            if auto_continue:
                return await _continue_async_unary_interaction(
                    response,
                    send_once,
                )
            result = _add_output_properties_if_interaction(response)
            if not has_caller_token:
                _warn_if_incomplete_unary(result)
            return result

        async def _send_create_once(
            self,
            request: Any,
            body: Mapping[str, Any],
            call_kwargs: Mapping[str, Any],
            token: Optional[str] = None,
        ) -> Any:
            if request is not None:
                req = (
                    request
                    if token is None
                    else _with_request_continuation_token(request, token)
                )
                return await async_wrap_sdk_call(
                    super().create,
                    request=req,
                    **call_kwargs,
                )
            req_body = (
                body
                if token is None
                else {**body, 'continuation_token': token}
            )
            return await async_wrap_sdk_call(
                super().create,
                **cast(Any, req_body),
                **call_kwargs,
            )


    if not TYPE_CHECKING:
        async def get(
            self,
            id: str,
            *,
            api_version: Optional[str] = None,
            include_input: Any = None,
            last_event_id: Any = None,
            stream: Any = False,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
        ) -> Union[
            interactions.Interaction,
            eventstreaming.AsyncStream[interactions.InteractionSSEEvent],
        ]:
            stream_bool = bool(_optional_bool(stream, default=False))
            response = await async_wrap_sdk_call(
                super().get,
                id=id,
                api_version=api_version,
                include_input=_optional_bool(include_input),
                last_event_id=_optional_str(last_event_id),
                stream=stream_bool,
                extra_headers=extra_headers,
                extra_query=extra_query,
                timeout=timeout,
            )
            if stream_bool:
                if not is_stream(response):
                    return response
                return cast(
                    eventstreaming.AsyncStream[interactions.InteractionSSEEvent],
                    wrap_async_stream_errors(response),
                )
            return cast(
                interactions.Interaction, _add_output_properties_if_interaction(response)
            )

    if not TYPE_CHECKING:
        async def cancel(
            self,
            id: str,
            *,
            api_version: Optional[str] = None,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
        ) -> interactions.Interaction:
            return cast(
                interactions.Interaction,
                _add_output_properties_if_interaction(
                    await async_wrap_sdk_call(
                        super().cancel,
                        id=id,
                        api_version=api_version,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        timeout=timeout,
                    )
                ),
            )

    if not TYPE_CHECKING:
        async def delete(
            self,
            id: str,
            *,
            api_version: Optional[str] = None,
            extra_headers: Optional[Mapping[str, str]] = None,
            extra_query: Optional[Mapping[str, Any]] = None,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
        ) -> Any:
            return await async_wrap_sdk_call(
                super().delete,
                id=id,
                api_version=api_version,
                extra_headers=extra_headers,
                extra_query=extra_query,
                timeout=timeout,
            )


class GeminiNextGenWebhooks(GeneratedWebhooks):
    """Public webhooks resource backed by the NextGen client.

    Subclasses the generated resource so every public method is wrapped in
    `wrap_sdk_call`, translating per-operation `GenAiError` raises into the
    status-code `APIError` hierarchy exposed at the
    `google.genai._interactions` import surface.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)

        def create(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().create, *args, **kwargs)

        def list(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().list, *args, **kwargs)

        def get(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().get, *args, **kwargs)

        def update(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().update, *args, **kwargs)

        def delete(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().delete, *args, **kwargs)

        def rotate_signing_secret(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().rotate_signing_secret, *args, **kwargs)

        def ping(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().ping, *args, **kwargs)


class AsyncGeminiNextGenWebhooks(GeneratedAsyncWebhooks):
    """Async public webhooks resource backed by the NextGen client."""

    def __init__(self, api_client: Any):
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)

        async def create(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().create, *args, **kwargs)

        async def list(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().list, *args, **kwargs)

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().get, *args, **kwargs)

        async def update(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().update, *args, **kwargs)

        async def delete(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().delete, *args, **kwargs)

        async def rotate_signing_secret(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(
                super().rotate_signing_secret, *args, **kwargs
            )

        async def ping(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().ping, *args, **kwargs)


class GeminiNextGenCredentials(GeneratedCredentials):
    """Public credentials resource backed by the NextGen client.

    Subclasses the generated resource so every public method is wrapped in
    `wrap_sdk_call`, translating per-operation `GenAiError` raises into the
    status-code `APIError` hierarchy exposed at the
    `google.genai._interactions` import surface.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)

        def create(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().create, *args, **kwargs)

        def list(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().list, *args, **kwargs)

        def get(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().get, *args, **kwargs)

        def update(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().update, *args, **kwargs)

        def delete(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().delete, *args, **kwargs)


class AsyncGeminiNextGenCredentials(GeneratedAsyncCredentials):
    """Async public credentials resource backed by the NextGen client."""

    def __init__(self, api_client: Any):
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)

        async def create(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().create, *args, **kwargs)

        async def list(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().list, *args, **kwargs)

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().get, *args, **kwargs)

        async def update(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().update, *args, **kwargs)

        async def delete(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().delete, *args, **kwargs)


class GeminiNextGenVoices(GeneratedVoices):
    """Voices resource backed by the NextGen client.

    Subclasses the generated resource so every public method is wrapped in
    `wrap_sdk_call`, translating per-operation `GenAiError` raises into the
    status-code `APIError` hierarchy exposed at the
    `google.genai._interactions` import surface.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)

        def create(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().create, *args, **kwargs)

        def list(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().list, *args, **kwargs)

        def get(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().get, *args, **kwargs)

        def delete(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().delete, *args, **kwargs)


class AsyncGeminiNextGenVoices(GeneratedAsyncVoices):
    """Async voices resource backed by the NextGen client."""

    def __init__(self, api_client: Any):
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)

        async def create(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().create, *args, **kwargs)

        async def list(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().list, *args, **kwargs)

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().get, *args, **kwargs)

        async def delete(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().delete, *args, **kwargs)


class GeminiNextGenAgents(GeneratedAgents):
    """Public agents resource backed by the NextGen client.

    Subclasses the generated resource so every public method is wrapped in
    `wrap_sdk_call`, translating per-operation `GenAiError` raises into the
    status-code `APIError` hierarchy exposed at the
    `google.genai._interactions` import surface.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)

        def create(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().create, *args, **kwargs)

        def list(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().list, *args, **kwargs)

        def get(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().get, *args, **kwargs)

        def delete(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().delete, *args, **kwargs)


class AsyncGeminiNextGenAgents(GeneratedAsyncAgents):
    """Async public agents resource backed by the NextGen client."""

    def __init__(self, api_client: Any):
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)

        async def create(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().create, *args, **kwargs)

        async def list(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().list, *args, **kwargs)

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().get, *args, **kwargs)

        async def delete(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().delete, *args, **kwargs)


class GeminiNextGenTriggers(GeneratedTriggers):
    """Public triggers resource backed by the NextGen client.

    Subclasses the generated resource so every public method is wrapped in
    `wrap_sdk_call`, translating per-operation `GenAiError` raises into the
    status-code `APIError` hierarchy exposed at the
    `google.genai._interactions` import surface.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)

        def create(self, *args: Any, **kwargs: Any) -> Any:
            if 'interaction' in kwargs:
                interaction = kwargs['interaction']
                if isinstance(interaction, dict):
                    kwargs['interaction'] = _normalize_create_body(interaction)
            return wrap_sdk_call(super().create, *args, **kwargs)

        def list(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().list, *args, **kwargs)

        def get(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().get, *args, **kwargs)

        def update(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().update, *args, **kwargs)

        def delete(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().delete, *args, **kwargs)

        def run(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().run, *args, **kwargs)

        def list_executions(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().list_executions, *args, **kwargs)


class AsyncGeminiNextGenTriggers(GeneratedAsyncTriggers):
    """Async public triggers resource backed by the NextGen client."""

    def __init__(self, api_client: Any):
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)

        async def create(self, *args: Any, **kwargs: Any) -> Any:
            if 'interaction' in kwargs:
                interaction = kwargs['interaction']
                if isinstance(interaction, dict):
                    kwargs['interaction'] = _normalize_create_body(interaction)
            return await async_wrap_sdk_call(super().create, *args, **kwargs)

        async def list(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().list, *args, **kwargs)

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().get, *args, **kwargs)

        async def update(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().update, *args, **kwargs)

        async def delete(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().delete, *args, **kwargs)

        async def run(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().run, *args, **kwargs)

        async def list_executions(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().list_executions, *args, **kwargs)



class GeminiNextGenEnvironmentFiles(GeneratedFiles):
    """Environment files resource backed by the NextGen client."""

    def __init__(
        self,
        sdk_config: Any,
        parent_ref: Optional[object] = None,
        api_client: Any = None,
    ):
        super().__init__(sdk_config, parent_ref=parent_ref)
        self._api_client = api_client
        self._internal = GeneratedInternal(sdk_config, parent_ref=parent_ref)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)

        def list(self, *args: Any, **kwargs: Any) -> Any:
            """Lists directory contents or files inside an environment workspace."""
            return wrap_sdk_call(super().list, *args, **kwargs)

    def download(
        self,
        *,
        path: str,
        environment: Optional[str] = None,
        environment_id: Optional[str] = None,
        http_options: Optional[Any] = None,
    ) -> bytes:
        """Downloads binary file content from an environment workspace."""
        if not self._api_client:
            raise AttributeError('api_client is required to download files.')
        target_env = environment or environment_id
        if not target_env:
            raise ValueError('environment or environment_id is required.')
        env_name = (
            target_env
            if target_env.startswith('environments/')
            else f'environments/{target_env}'
        )
        clean_path = path.lstrip('/')
        download_path = f'{env_name}/files/{clean_path}?alt=media'
        return self._api_client.download_file(
            download_path,
            http_options=http_options,
        )

    def upload(
        self,
        *,
        path: str,
        file: Union[str, os.PathLike[str], io.IOBase, bytes],
        environment: Optional[str] = None,
        environment_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        overwrite: Optional[bool] = None,
        extract: Optional[bool] = None,
        http_options: Optional[Any] = None,
    ) -> Union[environments.GetEnvironmentFilesResponse, Any]:
        """Uploads a file or extracts an archive inside an environment workspace."""
        if not self._api_client:
            raise AttributeError('api_client is required to upload files.')
        target_env = environment or environment_id
        if not target_env:
            raise ValueError('environment or environment_id is required.')
        clean_env = (
            target_env.removeprefix('environments/')
            if target_env.startswith('environments/')
            else target_env
        )
        clean_path = path.lstrip('/')

        file_obj: Union[str, io.IOBase]
        if isinstance(file, (bytes, bytearray)):
            file_obj = io.BytesIO(file)
            size_bytes = len(file)
        elif isinstance(file, io.IOBase):
            file_obj = file
            offset = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size_bytes = file_obj.tell() - offset
            file_obj.seek(offset, os.SEEK_SET)
        else:
            fs_path = os.fspath(file)
            if not fs_path or not os.path.isfile(fs_path):
                raise FileNotFoundError(f'{file} is not a valid file path.')
            size_bytes = os.path.getsize(fs_path)
            file_obj = fs_path
            if mime_type is None:
                mime_type, _ = mimetypes.guess_type(fs_path)

        if mime_type is None:
            mime_type = 'application/octet-stream'

        req_api_version = (
            (
                http_options.get('api_version')
                if isinstance(http_options, dict)
                else getattr(http_options, 'api_version', None)
            )
            or self._api_client._http_options.api_version
            or 'v1alpha'
        ).lstrip('/')

        handshake_res = self._internal.start_upload(
            environment=clean_env,
            path=clean_path,
            x_goog_upload_header_content_length=size_bytes,
            x_goog_upload_header_content_type=mime_type,
            api_version=req_api_version,
            extract=extract,
            overwrite=overwrite,
        )

        upload_urls = (
            handshake_res.headers.get('x-goog-upload-url')
            or handshake_res.headers.get('X-Goog-Upload-URL')
        )
        if not upload_urls:
            raise KeyError(
                'Failed to upload file: Upload URL was not returned from the upload request.'
            )
        upload_url = upload_urls[0] if isinstance(upload_urls, list) else upload_urls

        upload_response = self._api_client.upload_file(
            file_obj,
            upload_url,
            size_bytes,
            http_options=http_options,
        )

        body_text = (
            upload_response.response_stream[0]
            if upload_response and upload_response.response_stream
            else '{}'
        )
        try:
            res_json = json.loads(body_text) if body_text else {}
        except Exception:
            return body_text

        if isinstance(res_json, dict):
            if 'files' in res_json and isinstance(res_json['files'], list):
                return environments.GetEnvironmentFilesResponse.model_validate(res_json)
            elif 'name' in res_json or 'path' in res_json:
                file_obj = environments.EnvironmentFile.model_validate(res_json)
                return environments.GetEnvironmentFilesResponse(files=[file_obj])
            elif 'file' in res_json and isinstance(res_json['file'], dict):
                file_obj = environments.EnvironmentFile.model_validate(res_json['file'])
                return environments.GetEnvironmentFilesResponse(files=[file_obj])
        return res_json


class AsyncGeminiNextGenEnvironmentFiles(GeneratedAsyncFiles):
    """Async environment files resource backed by the NextGen client."""

    def __init__(
        self,
        sdk_config: Any,
        parent_ref: Optional[object] = None,
        api_client: Any = None,
    ):
        super().__init__(sdk_config, parent_ref=parent_ref)
        self._api_client = api_client
        self._internal = GeneratedAsyncInternal(sdk_config, parent_ref=parent_ref)

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)

        async def list(self, *args: Any, **kwargs: Any) -> Any:
            """Lists directory contents or files inside an environment workspace."""
            return await async_wrap_sdk_call(super().list, *args, **kwargs)

    async def download(
        self,
        *,
        path: str,
        environment: Optional[str] = None,
        environment_id: Optional[str] = None,
        http_options: Optional[Any] = None,
    ) -> bytes:
        """Downloads binary file content from an environment workspace."""
        if not self._api_client:
            raise AttributeError('api_client is required to download files.')
        target_env = environment or environment_id
        if not target_env:
            raise ValueError('environment or environment_id is required.')
        env_name = (
            target_env
            if target_env.startswith('environments/')
            else f'environments/{target_env}'
        )
        clean_path = path.lstrip('/')
        download_path = f'{env_name}/files/{clean_path}?alt=media'
        return await self._api_client.async_download_file(
            download_path,
            http_options=http_options,
        )

    async def upload(
        self,
        *,
        path: str,
        file: Union[str, os.PathLike[str], io.IOBase, bytes],
        environment: Optional[str] = None,
        environment_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        overwrite: Optional[bool] = None,
        extract: Optional[bool] = None,
        http_options: Optional[Any] = None,
    ) -> Union[environments.GetEnvironmentFilesResponse, Any]:
        """Uploads a file or extracts an archive inside an environment workspace."""
        if not self._api_client:
            raise AttributeError('api_client is required to upload files.')
        target_env = environment or environment_id
        if not target_env:
            raise ValueError('environment or environment_id is required.')
        clean_env = (
            target_env.removeprefix('environments/')
            if target_env.startswith('environments/')
            else target_env
        )
        clean_path = path.lstrip('/')

        file_obj: Union[str, io.IOBase]
        if isinstance(file, (bytes, bytearray)):
            file_obj = io.BytesIO(file)
            size_bytes = len(file)
        elif isinstance(file, io.IOBase):
            file_obj = file
            offset = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size_bytes = file_obj.tell() - offset
            file_obj.seek(offset, os.SEEK_SET)
        else:
            fs_path = os.fspath(file)
            if not fs_path or not os.path.isfile(fs_path):
                raise FileNotFoundError(f'{file} is not a valid file path.')
            size_bytes = os.path.getsize(fs_path)
            file_obj = fs_path
            if mime_type is None:
                mime_type, _ = mimetypes.guess_type(fs_path)

        if mime_type is None:
            mime_type = 'application/octet-stream'

        req_api_version = (
            (
                http_options.get('api_version')
                if isinstance(http_options, dict)
                else getattr(http_options, 'api_version', None)
            )
            or self._api_client._http_options.api_version
            or 'v1alpha'
        ).lstrip('/')

        handshake_res = await self._internal.start_upload(
            environment=clean_env,
            path=clean_path,
            x_goog_upload_header_content_length=size_bytes,
            x_goog_upload_header_content_type=mime_type,
            api_version=req_api_version,
            extract=extract,
            overwrite=overwrite,
        )

        upload_urls = (
            handshake_res.headers.get('x-goog-upload-url')
            or handshake_res.headers.get('X-Goog-Upload-URL')
        )
        if not upload_urls:
            raise KeyError(
                'Failed to upload file: Upload URL was not returned from the upload request.'
            )
        upload_url = upload_urls[0] if isinstance(upload_urls, list) else upload_urls

        upload_response = await self._api_client.async_upload_file(
            file_obj,
            upload_url,
            size_bytes,
            http_options=http_options,
        )

        body_text = (
            upload_response.response_stream[0]
            if upload_response and upload_response.response_stream
            else '{}'
        )
        try:
            res_json = json.loads(body_text) if body_text else {}
        except Exception:
            return body_text

        if isinstance(res_json, dict):
            if 'files' in res_json and isinstance(res_json['files'], list):
                return environments.GetEnvironmentFilesResponse.model_validate(res_json)
            elif 'name' in res_json or 'path' in res_json:
                file_obj = environments.EnvironmentFile.model_validate(res_json)
                return environments.GetEnvironmentFilesResponse(files=[file_obj])
            elif 'file' in res_json and isinstance(res_json['file'], dict):
                file_obj = environments.EnvironmentFile.model_validate(res_json['file'])
                return environments.GetEnvironmentFilesResponse(files=[file_obj])
        return res_json


class GeminiNextGenEnvironments(GeneratedEnvironments):
    """Public environments resource backed by the NextGen client."""

    files: GeminiNextGenEnvironmentFiles

    def __init__(self, api_client: Any):
        self._api_client = api_client
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    def _init_sdks(self) -> None:
        self.files = GeminiNextGenEnvironmentFiles(
            self.sdk_configuration,
            parent_ref=self.parent_ref,
            api_client=self._api_client,
        )

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _RawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _RawResponseAccessorProxy(super().with_streaming_response)

        def create_environment(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().create_environment, *args, **kwargs)

        def create(self, *args: Any, **kwargs: Any) -> Any:
            return self.create_environment(*args, **kwargs)

        def list_environments(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().list_environments, *args, **kwargs)

        def list(self, *args: Any, **kwargs: Any) -> Any:
            return self.list_environments(*args, **kwargs)

        def get_environment(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().get_environment, *args, **kwargs)

        def get(self, *args: Any, **kwargs: Any) -> Any:
            return self.get_environment(*args, **kwargs)

        def delete_environment(self, *args: Any, **kwargs: Any) -> Any:
            return wrap_sdk_call(super().delete_environment, *args, **kwargs)

        def delete(self, *args: Any, **kwargs: Any) -> Any:
            return self.delete_environment(*args, **kwargs)


class AsyncGeminiNextGenEnvironments(GeneratedAsyncEnvironments):
    """Async public environments resource backed by the NextGen client."""

    files: AsyncGeminiNextGenEnvironmentFiles

    def __init__(self, api_client: Any):
        self._api_client = api_client
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)

    def _init_sdks(self) -> None:
        self.files = AsyncGeminiNextGenEnvironmentFiles(
            self.sdk_configuration,
            parent_ref=self.parent_ref,
            api_client=self._api_client,
        )

    if not TYPE_CHECKING:
        @property
        def with_raw_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_raw_response)

        @property
        def with_streaming_response(self):
            return _AsyncRawResponseAccessorProxy(super().with_streaming_response)

        async def create_environment(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().create_environment, *args, **kwargs)

        async def create(self, *args: Any, **kwargs: Any) -> Any:
            return await self.create_environment(*args, **kwargs)

        async def list_environments(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().list_environments, *args, **kwargs)

        async def list(self, *args: Any, **kwargs: Any) -> Any:
            return await self.list_environments(*args, **kwargs)

        async def get_environment(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().get_environment, *args, **kwargs)

        async def get(self, *args: Any, **kwargs: Any) -> Any:
            return await self.get_environment(*args, **kwargs)

        async def delete_environment(self, *args: Any, **kwargs: Any) -> Any:
            return await async_wrap_sdk_call(super().delete_environment, *args, **kwargs)

        async def delete(self, *args: Any, **kwargs: Any) -> Any:
            return await self.delete_environment(*args, **kwargs)


def _add_output_properties_if_interaction(value: Any) -> Any:
    normalized = _normalize_interaction_shape(value)
    if normalized is None:
        return value

    steps = _get_value(normalized, 'steps')
    updates = _output_properties_from_steps(steps)
    if not updates:
        return normalized

    return _set_or_copy(normalized, updates)


def _normalize_interaction_shape(value: Any) -> Optional[Any]:
    steps = _get_value(value, 'steps')
    if isinstance(steps, list):
        return value

    model = _get_value(value, 'model')
    if not isinstance(model, str) or model not in _LEGACY_LYRIA_MODELS:
        return None

    outputs = _get_value(value, 'outputs')
    if not isinstance(outputs, list):
        outputs = []

    steps = [{'type': 'model_output', 'content': outputs}] if outputs else []
    if hasattr(value, 'model_copy'):
        return value.model_copy(update={'steps': steps, 'outputs': None})
    if isinstance(value, dict):
        normalized = {**value, 'steps': steps}
        normalized.pop('outputs', None)
        return normalized

    setattr(value, 'steps', steps)
    if hasattr(value, 'outputs'):
        setattr(value, 'outputs', None)
    return value


def _output_properties_from_steps(steps: list[Any]) -> dict[str, Any]:
    text_parts: list[str] = []
    collecting = False

    for step in reversed(steps):
        step_type = _get_value(step, 'type')
        if step_type == 'user_input':
            break
        if step_type == 'thought':
            continue
        if step_type != 'model_output':
            if collecting:
                break
            continue

        content = _get_value(step, 'content')
        if not isinstance(content, list):
            continue

        should_stop = False
        for item in reversed(content):
            item_type = _get_value(item, 'type')
            if item_type != 'text':
                if collecting:
                    should_stop = True
                    break
                continue
            collecting = True
            text = _get_value(item, 'text')
            text_parts.append(text if isinstance(text, str) else '')
        if should_stop:
            break

    updates: dict[str, Any] = {}
    output_text = ''.join(reversed(text_parts))
    if output_text:
        updates['output_text'] = output_text

    output_image = None
    output_audio = None
    output_video = None

    for step in reversed(steps):
        if _get_value(step, 'type') == 'user_input':
            break
        if _get_value(step, 'type') != 'model_output':
            continue

        content = _get_value(step, 'content')
        if not isinstance(content, list):
            continue

        for item in reversed(content):
            content_type = _get_value(item, 'type')
            if content_type == 'image' and output_image is None:
                output_image = item
            if content_type == 'audio' and output_audio is None:
                output_audio = item
            if content_type == 'video' and output_video is None:
                output_video = item

    if output_image is not None:
        updates['output_image'] = output_image
    if output_audio is not None:
        updates['output_audio'] = output_audio
    if output_video is not None:
        updates['output_video'] = output_video

    return updates


def _get_value(value: Any, name: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


# Allowed create() body keys, derived from the generated request models so the
# set tracks the schema; output-only fields are excluded.
_CREATE_BODY_KEYS = frozenset(
    field.alias or name
    for model in (
        interactions.CreateModelInteraction,
        interactions.CreateAgentInteraction,
    )
    for name, field in model.model_fields.items()
)


_REQUEST_AND_BODY_ERROR = (
    'create() accepts either request=... or individual body keyword arguments, '
    'not both.'
)


def _normalize_create_body(body: dict[str, Any]) -> dict[str, Any]:
    unknown = set(body) - _CREATE_BODY_KEYS
    if unknown:
        raise TypeError(
            'create() got unexpected keyword argument(s): '
            + ', '.join(sorted(unknown))
            + '. Use extra_body=... to send additional request body fields.'
        )

    input_value = body.get('input')
    if not _is_content_list(input_value):
        return body

    normalized_content = [_normalize_content_block(item) for item in input_value]
    return {**body, 'input': [{'type': 'user_input', 'content': normalized_content}]}


def _normalize_content_block(value: dict[str, Any]) -> dict[str, Any]:
    if 'text' in value and 'type' not in value:
        return {**value, 'type': 'text'}
    return value



def _is_content_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(_is_content_block(item) for item in value)
    )


def _is_content_block(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if _is_step_block(value):
        return False
    if 'role' in value or 'content' in value:
        return False
    return True


def _is_step_block(value: dict[str, Any]) -> bool:
    return value.get('type') in {
        'user_input',
        'model_output',
        'thought',
        'function_call',
        'code_execution_call',
        'url_context_call',
        'mcp_server_tool_call',
        'google_search_call',
        'file_search_call',
        'google_maps_call',
        'function_result',
        'code_execution_result',
        'url_context_result',
        'google_search_result',
        'mcp_server_tool_result',
        'file_search_result',
        'google_maps_result',
    }


def _optional_bool(value: Any, default: Optional[bool] = None) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    return default


def _optional_str(value: Any) -> Optional[str]:
    if isinstance(value, str):
        return value
    return None


def _request_stream(request: Any) -> bool:
    stream = _get_value(_get_value(request, 'body'), 'stream')
    return bool(_optional_bool(stream, default=False))


_AUTO_CONTINUE_AND_BACKGROUND_ERROR = (
    'automatic_continuation=False cannot be used with background=True.'
)

_AUTO_CONTINUE_AND_STORE_FALSE_ERROR = (
    'automatic_continuation=True cannot be used with store=False in unary mode.'
    ' Use store=True, stream=True, or background=True for automatic'
    ' continuation to work.'
)


def _request_background(request: Any) -> bool:
    background = _get_value(_get_value(request, 'body'), 'background')
    return bool(_optional_bool(background, default=False))


def _request_store_false(request: Any) -> bool:
    store = _get_value(_get_value(request, 'body'), 'store')
    return _optional_bool(store) is False


def _with_request_continuation_token(request: Any, token: str) -> Any:
    body = _get_value(request, 'body')
    if isinstance(body, Mapping):
        new_body = {**body, 'continuation_token': token}
    elif hasattr(body, 'model_copy'):
        new_body = body.model_copy(update={'continuation_token': token})
    else:
        new_body = body

    if isinstance(request, Mapping):
        return {**request, 'body': new_body}
    if hasattr(request, 'model_copy'):
        return request.model_copy(update={'body': new_body})
    return request


def _request_has_continuation_token(request: Any) -> bool:
    token = _get_value(_get_value(request, 'body'), 'continuation_token')
    return bool(isinstance(token, str) and token)


def _extract_hop_continuation_state(
    event: Any,
    hop_status: Optional[str],
    hop_continuation_token: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    if _get_value(event, 'event_type') == 'error':
        return 'error', None

    interaction = _get_value(event, 'interaction')
    if interaction is not None:
        status = _get_value(interaction, 'status')
        if isinstance(status, str) and status:
            hop_status = status
        token = _get_value(interaction, 'continuation_token')
        if isinstance(token, str) and token:
            hop_continuation_token = token

    direct_status = _get_value(event, 'status')
    if isinstance(direct_status, str) and direct_status:
        hop_status = direct_status
    direct_token = _get_value(event, 'continuation_token')
    if isinstance(direct_token, str) and direct_token:
        hop_continuation_token = direct_token

    return hop_status, hop_continuation_token


_RESUMABLE_STREAM_HOP_STATUSES = frozenset({
    None,
    'in_progress',
    'continuation_required',
})


def _can_resume_stream_hop(
    hop_status: Optional[str],
    hop_continuation_token: Optional[str],
) -> bool:
    return bool(
        hop_continuation_token
        and hop_status in _RESUMABLE_STREAM_HOP_STATUSES
    )


_INCOMPLETE_CONTINUATION_WARNING = (
    "Interaction stopped before completion (status='continuation_required') "
    "with a continuation_token because the per-request decode token limit was "
    "reached. To resume decoding automatically, pass "
    "automatic_continuation=True (note: each continuation hop re-prefills and "
    "bills input tokens), or use background=True (the most cost-efficient "
    "option for server-managed continuation), or pass continuation_token to "
    "interactions.create()."
)

_incomplete_continuation_warned = False


def _warn_incomplete_continuation(*, stacklevel: int = 3) -> None:
    global _incomplete_continuation_warned
    if not _incomplete_continuation_warned:
        _incomplete_continuation_warned = True
        warnings.warn(
            _INCOMPLETE_CONTINUATION_WARNING,
            category=UserWarning,
            stacklevel=stacklevel,
        )


def _warn_if_incomplete_unary(interaction: Any) -> None:
    if _should_continue_unary(interaction):
        _warn_incomplete_continuation(stacklevel=4)


def _wrap_stream_incomplete_warning(stream: Any) -> Any:
    current_gen = stream.generator

    def _warning_gen():
        hop_status: Optional[str] = None
        hop_continuation_token: Optional[str] = None
        try:
            for event in current_gen:
                hop_status, hop_continuation_token = (
                    _extract_hop_continuation_state(
                        event,
                        hop_status,
                        hop_continuation_token,
                    )
                )
                yield event
            if (
                hop_status == 'continuation_required'
                and hop_continuation_token
            ):
                _warn_incomplete_continuation(stacklevel=3)
        finally:
            if hasattr(current_gen, 'close'):
                current_gen.close()

    warning_gen = _warning_gen()
    stream.generator = warning_gen

    orig_close = stream.close

    def _close() -> None:
        try:
            warning_gen.close()
        finally:
            orig_close()

    stream.close = _close
    return stream


def _wrap_async_stream_incomplete_warning(stream: Any) -> Any:
    current_gen = stream.generator

    async def _warning_agen():
        hop_status: Optional[str] = None
        hop_continuation_token: Optional[str] = None
        try:
            async for event in current_gen:
                hop_status, hop_continuation_token = (
                    _extract_hop_continuation_state(
                        event,
                        hop_status,
                        hop_continuation_token,
                    )
                )
                yield event
            if (
                hop_status == 'continuation_required'
                and hop_continuation_token
            ):
                _warn_incomplete_continuation(stacklevel=3)
        finally:
            if hasattr(current_gen, 'aclose'):
                await current_gen.aclose()

    warning_agen = _warning_agen()
    stream.generator = warning_agen

    orig_close = stream.close

    async def _close() -> None:
        try:
            await warning_agen.aclose()
        finally:
            await orig_close()

    stream.close = _close
    return stream


def _wrap_stream_continuation(
    stream: Any,
    create_next_stream: Any,
) -> Any:
    current_gen = stream.generator
    current_stream = stream

    def _continuation_gen():
        nonlocal current_gen, current_stream
        try:
            while True:
                hop_status: Optional[str] = None
                hop_continuation_token: Optional[str] = None
                it = iter(current_gen)
                while True:
                    try:
                        event = next(it)
                    except StopIteration:
                        break
                    except Exception:
                        if not _can_resume_stream_hop(
                            hop_status, hop_continuation_token
                        ):
                            raise
                        break
                    hop_status, hop_continuation_token = (
                        _extract_hop_continuation_state(
                            event,
                            hop_status,
                            hop_continuation_token,
                        )
                    )
                    yield event

                if not _can_resume_stream_hop(
                    hop_status, hop_continuation_token
                ):
                    break

                if hasattr(current_stream, 'response'):
                    current_stream.response.close()

                next_stream = create_next_stream(hop_continuation_token)
                if not is_stream(next_stream):
                    break
                next_stream = wrap_stream_errors(next_stream)
                current_stream = next_stream
                current_gen = next_stream.generator
                if hasattr(stream, 'response') and hasattr(
                    next_stream, 'response'
                ):
                    stream.response = next_stream.response
        finally:
            if hasattr(current_gen, 'close'):
                current_gen.close()
            if current_stream is not stream and hasattr(
                current_stream, 'close'
            ):
                current_stream.close()

    continuation_gen = _continuation_gen()
    stream.generator = continuation_gen

    orig_close = stream.close

    def _close() -> None:
        try:
            continuation_gen.close()
        finally:
            orig_close()

    stream.close = _close
    return stream


def _wrap_async_stream_continuation(
    stream: Any,
    create_next_stream: Any,
) -> Any:
    current_gen = stream.generator
    current_stream = stream

    async def _continuation_agen():
        nonlocal current_gen, current_stream
        try:
            while True:
                hop_status: Optional[str] = None
                hop_continuation_token: Optional[str] = None
                it = current_gen.__aiter__()
                while True:
                    try:
                        event = await it.__anext__()
                    except StopAsyncIteration:
                        break
                    except Exception:
                        if not _can_resume_stream_hop(
                            hop_status, hop_continuation_token
                        ):
                            raise
                        break
                    hop_status, hop_continuation_token = (
                        _extract_hop_continuation_state(
                            event,
                            hop_status,
                            hop_continuation_token,
                        )
                    )
                    yield event

                if not _can_resume_stream_hop(
                    hop_status, hop_continuation_token
                ):
                    break

                if hasattr(current_stream, 'response'):
                    await current_stream.response.aclose()

                next_stream = await create_next_stream(hop_continuation_token)
                if not is_stream(next_stream):
                    break
                next_stream = wrap_async_stream_errors(next_stream)
                current_stream = next_stream
                current_gen = next_stream.generator
                if hasattr(stream, 'response') and hasattr(
                    next_stream, 'response'
                ):
                    stream.response = next_stream.response
        finally:
            if hasattr(current_gen, 'aclose'):
                await current_gen.aclose()
            if current_stream is not stream:
                await current_stream.close()

    continuation_agen = _continuation_agen()
    stream.generator = continuation_agen

    orig_close = stream.close

    async def _close() -> None:
        try:
            await continuation_agen.aclose()
        finally:
            await orig_close()

    stream.close = _close
    return stream


def _set_or_copy(target: Any, updates: dict[str, Any]) -> Any:
    if hasattr(target, 'model_copy'):
        return target.model_copy(update=updates)
    if isinstance(target, dict):
        return {**target, **updates}
    for name, value in updates.items():
        setattr(target, name, value)
    return target


def _should_continue_unary(interaction: Any) -> Optional[str]:
    if _get_value(interaction, 'status') != 'continuation_required':
        return None
    token = _get_value(interaction, 'continuation_token')
    if not isinstance(token, str) or not token:
        return None
    return token


def _continue_unary_interaction(
    initial_response: Any,
    create_next: Any,
) -> Any:
    current = initial_response
    while True:
        token = _should_continue_unary(current)
        if not token:
            return _add_output_properties_if_interaction(current)
        current = create_next(token)


async def _continue_async_unary_interaction(
    initial_response: Any,
    create_next: Any,
) -> Any:
    current = initial_response
    while True:
        token = _should_continue_unary(current)
        if not token:
            return _add_output_properties_if_interaction(current)
        current = await create_next(token)
