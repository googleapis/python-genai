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
from .interactions import AsyncInteractions as GeneratedAsyncInteractions
from .interactions import Interactions as GeneratedInteractions
from .sdk import AsyncGenAI, GenAI
from .types import interactions
from .types.security import Security
from .utils import eventstreaming


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
    )
    return sdk


def build_google_genai_async_client(
    api_client: Any, api_version: Optional[str] = None
) -> AsyncGenAI:
    """Builds an async generated NextGen client from the parent GenAI client."""
    http_options = api_client._http_options
    sdk = AsyncGenAI(
        security=_get_google_genai_security(api_client),
        api_version=api_version or get_google_genai_api_version(api_client),
        user_project=_get_google_genai_user_project(api_client),
        server_url=get_google_genai_server_url(api_client),
        async_client=getattr(api_client, '_async_httpx_client', None),
        timeout_ms=http_options.timeout,
    )
    return sdk


class GeminiNextGenInteractions(GeneratedInteractions):
    """Public interactions resource backed by the NextGen client.

    Subclasses the generated resource so newly generated methods (and the
    raw/streaming response wrappers) are exposed automatically. Only the
    methods that need legacy input/output normalization are overridden.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)


    # Runtime-only overrides: type checkers see the inherited generated
    # signatures (full overload sets) instead of hand-maintained stubs.
    if not TYPE_CHECKING:
        def create(
            self,
            *,
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
            stream = _optional_bool(body.get('stream'), default=False)
            body = _normalize_create_body(body)
            response = super().create(
                api_version=api_version,
                **cast(Any, body),
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
            if stream:
                return response
            return _add_output_properties_if_interaction(response)


    # Runtime-only overrides: type checkers see the inherited generated
    # signatures (full overload sets) instead of hand-maintained stubs.
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
            response = super().get(
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
                return cast(eventstreaming.Stream[interactions.InteractionSSEEvent], response)
            return cast(
                interactions.Interaction, _add_output_properties_if_interaction(response)
            )

    # Runtime-only overrides: type checkers see the inherited generated
    # signatures (full overload sets) instead of hand-maintained stubs.
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
                    super().cancel(
                        id=id,
                        api_version=api_version,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        timeout=timeout,
                    )
                ),
            )


class AsyncGeminiNextGenInteractions(GeneratedAsyncInteractions):
    """Async public interactions resource backed by the NextGen client.

    Subclasses the generated resource so newly generated methods (and the
    raw/streaming response wrappers) are exposed automatically. Only the
    methods that need legacy input/output normalization are overridden.
    """

    def __init__(self, api_client: Any):
        sdk = build_google_genai_async_client(api_client)
        super().__init__(sdk.sdk_configuration, parent_ref=sdk)


    # Runtime-only overrides: type checkers see the inherited generated
    # signatures (full overload sets) instead of hand-maintained stubs.
    if not TYPE_CHECKING:
        async def create(
            self,
            *,
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
            stream = _optional_bool(body.get('stream'), default=False)
            body = _normalize_create_body(body)
            response = await super().create(
                api_version=api_version,
                **cast(Any, body),
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
            if stream:
                return response
            return _add_output_properties_if_interaction(response)


    # Runtime-only overrides: type checkers see the inherited generated
    # signatures (full overload sets) instead of hand-maintained stubs.
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
            response = await super().get(
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
                return cast(eventstreaming.AsyncStream[interactions.InteractionSSEEvent], response)
            return cast(
                interactions.Interaction, _add_output_properties_if_interaction(response)
            )

    # Runtime-only overrides: type checkers see the inherited generated
    # signatures (full overload sets) instead of hand-maintained stubs.
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
                    await super().cancel(
                        id=id,
                        api_version=api_version,
                        extra_headers=extra_headers,
                        extra_query=extra_query,
                        timeout=timeout,
                    )
                ),
            )


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


def _normalize_create_body(body: dict[str, Any]) -> dict[str, Any]:
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
    return isinstance(value, dict) and not _is_step_block(value)


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
