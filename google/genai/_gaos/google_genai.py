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

"""Helpers for embedding the generated NextGen SDK in the Google GenAI client."""

# This bridge intentionally reuses the parent GenAI client's protected transport,
# auth, and http option internals so the NextGen resource client behaves like
# the public google-genai resource it replaces.
# pylint: disable=protected-access,too-many-arguments

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, TypeVar, Union, cast

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
from .types import interactions
from .types.security import Security
from .utils import BackoffStrategy, RetryConfig, eventstreaming
from .triggers import AsyncTriggers as GeneratedAsyncTriggers
from .triggers import Triggers as GeneratedTriggers
from .webhooks import AsyncWebhooks as GeneratedAsyncWebhooks
from .webhooks import Webhooks as GeneratedWebhooks


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
            **body: Any,
        ) -> Union[
            interactions.Interaction,
            eventstreaming.Stream[interactions.InteractionSSEEvent],
        ]:
            if request is not None:
                if body:
                    raise TypeError(_REQUEST_AND_BODY_ERROR)
                stream = _request_stream(request)
                response = wrap_sdk_call(
                    super().create,
                    request=request,
                    api_version=api_version,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                )
                if stream:
                    if is_stream(response):
                        return wrap_stream_errors(response)
                    return response
                return _add_output_properties_if_interaction(response)

            stream = _optional_bool(body.get('stream'), default=False)
            body = _normalize_create_body(body)
            response = wrap_sdk_call(
                super().create,
                api_version=api_version,
                **cast(Any, body),
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
            if stream:
                if is_stream(response):
                    return wrap_stream_errors(response)
                return response
            return _add_output_properties_if_interaction(response)


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
            **body: Any,
        ) -> Union[
            interactions.Interaction,
            eventstreaming.AsyncStream[interactions.InteractionSSEEvent],
        ]:
            if request is not None:
                if body:
                    raise TypeError(_REQUEST_AND_BODY_ERROR)
                stream = _request_stream(request)
                response = await async_wrap_sdk_call(
                    super().create,
                    request=request,
                    api_version=api_version,
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                )
                if stream:
                    if is_stream(response):
                        return wrap_async_stream_errors(response)
                    return response
                return _add_output_properties_if_interaction(response)

            stream = _optional_bool(body.get('stream'), default=False)
            body = _normalize_create_body(body)
            response = await async_wrap_sdk_call(
                super().create,
                api_version=api_version,
                **cast(Any, body),
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
            if stream:
                if is_stream(response):
                    return wrap_async_stream_errors(response)
                return response
            return _add_output_properties_if_interaction(response)


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


def _add_output_properties_if_interaction(value: Any) -> Any:
    normalized = _normalize_interaction_shape(value)
    if normalized is None:
        return value

    steps = _get_value(normalized, 'steps')
    updates = _output_properties_from_steps(steps)
    if not updates:
        return value

    if hasattr(normalized, 'model_copy'):
        return normalized.model_copy(update=updates)
    if isinstance(normalized, dict):
        return {**normalized, **updates}

    for name, output_value in updates.items():
        setattr(normalized, name, output_value)
    return normalized


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
        if _get_value(step, 'type') == 'user_input':
            break
        if _get_value(step, 'type') != 'model_output':
            if collecting:
                break
            continue

        content = _get_value(step, 'content')
        if not isinstance(content, list):
            if collecting:
                break
            continue

        should_stop = False
        for item in reversed(content):
            if _get_value(item, 'type') == 'text':
                collecting = True
                text = _get_value(item, 'text')
                text_parts.append(text if isinstance(text, str) else '')
            elif collecting:
                should_stop = True
                break
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
    if isinstance(value, dict):
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

    return {**body, 'input': [{'type': 'user_input', 'content': input_value}]}


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
    body = (
        request.get('body')
        if isinstance(request, Mapping)
        else getattr(request, 'body', None)
    )
    stream = (
        body.get('stream')
        if isinstance(body, Mapping)
        else getattr(body, 'stream', None)
    )
    return bool(_optional_bool(stream, default=False))
