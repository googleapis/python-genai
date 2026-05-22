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
"""Wrapper for Fern-backed interactions to preserve Stainless signature."""

import typing
from typing import Any, Iterable, List, Optional, Union

from ._fern_interactions.core.request_options import RequestOptions
from ._fern_interactions.fern_interactions.client import AsyncFernInteractionsClient, FernInteractionsClient
from ._fern_interactions.types import CreateAgentInteractionParams, CreateModelInteractionParams


def _make_fern_request_options(
    extra_headers: Optional[dict] = None,
    extra_query: Optional[dict] = None,
    extra_body: Optional[dict] = None,
    timeout: Optional[float] = None,
) -> Optional[RequestOptions]:
    opts: RequestOptions = {}
    if extra_headers:
        opts['additional_headers'] = extra_headers
    if extra_query:
        opts['additional_query_parameters'] = extra_query
    if extra_body:
        opts['additional_body_parameters'] = extra_body
    if timeout is not None:
        opts['timeout_in_seconds'] = int(timeout)
    return opts if opts else None


class Interactions:
    """Wrapper for FernInteractionsClient to preserve Stainless signature."""

    def __init__(self, fern_client: FernInteractionsClient):
        self._fern_client = fern_client

    def create(
        self,
        *,
        input: Optional[Any] = None,
        model: Optional[str] = None,
        agent: Optional[str] = None,
        background: Optional[bool] = None,
        environment: Optional[Any] = None,
        generation_config: Optional[Any] = None,
        previous_interaction_id: Optional[str] = None,
        response_format: Optional[Any] = None,
        response_mime_type: Optional[str] = None,
        response_modalities: Optional[List[str]] = None,
        service_tier: Optional[str] = None,
        store: Optional[bool] = None,
        stream: Optional[bool] = None,
        system_instruction: Optional[str] = None,
        tools: Optional[Iterable[Any]] = None,
        webhook_config: Optional[Any] = None,
        agent_config: Optional[Any] = None,
        # Support raw request for backward compatibility
        request: Optional[Any] = None,
        request_options: Optional[Any] = None,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        if request is not None:
            if stream:
                return self._fern_client.create_stream(request=request, request_options=request_options)
            else:
                return self._fern_client.create(request=request, request_options=request_options)

        if input is None:
            raise TypeError("missing 1 required keyword-only argument: 'input'")

        if request_options is None:
            request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)

        if model is not None:
            params = {
                "model": model,
                "input": input,
                "background": background,
                "store": store,
                "stream": stream,
                "environment": environment,
                "previous_interaction_id": previous_interaction_id,
                "response_format": response_format,
                "response_mime_type": response_mime_type,
                "response_modalities": response_modalities,
                "service_tier": service_tier,
                "system_instruction": system_instruction,
                "tools": tools,
                "webhook_config": webhook_config,
                "generation_config": generation_config,
            }
            params = {k: v for k, v in params.items() if v is not None}
            req = CreateModelInteractionParams(**params)
        elif agent is not None:
            params = {
                "agent": agent,
                "input": input,
                "background": background,
                "store": store,
                "stream": stream,
                "environment": environment,
                "previous_interaction_id": previous_interaction_id,
                "response_format": response_format,
                "response_mime_type": response_mime_type,
                "response_modalities": response_modalities,
                "service_tier": service_tier,
                "system_instruction": system_instruction,
                "tools": tools,
                "webhook_config": webhook_config,
                "agent_config": agent_config,
            }
            params = {k: v for k, v in params.items() if v is not None}
            req = CreateAgentInteractionParams(**params)
        else:
            raise ValueError("Either model or agent must be specified")

        if stream:
            return self._fern_client.create_stream(request=req, request_options=request_options)
        else:
            return self._fern_client.create(request=req, request_options=request_options)

    def get(
        self,
        id: str,
        *,
        stream: Optional[bool] = None,
        include_input: Optional[bool] = None,
        last_event_id: Optional[str] = None,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)
        if stream:
            return self._fern_client.get_stream(
                id,
                stream=stream,
                last_event_id=last_event_id,
                include_input=include_input,
                request_options=request_options,
            )
        else:
            return self._fern_client.get(
                id,
                stream=stream,
                last_event_id=last_event_id,
                include_input=include_input,
                request_options=request_options,
            )

    def cancel(
        self,
        id: str,
        *,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)
        return self._fern_client.cancel(id, request_options=request_options)

    def delete(
        self,
        id: str,
        *,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)
        return self._fern_client.delete(id, request_options=request_options)


class AsyncInteractions:
    """Wrapper for AsyncFernInteractionsClient to preserve Stainless signature."""

    def __init__(self, fern_client: AsyncFernInteractionsClient):
        self._fern_client = fern_client

    async def create(
        self,
        *,
        input: Optional[Any] = None,
        model: Optional[str] = None,
        agent: Optional[str] = None,
        background: Optional[bool] = None,
        environment: Optional[Any] = None,
        generation_config: Optional[Any] = None,
        previous_interaction_id: Optional[str] = None,
        response_format: Optional[Any] = None,
        response_mime_type: Optional[str] = None,
        response_modalities: Optional[List[str]] = None,
        service_tier: Optional[str] = None,
        store: Optional[bool] = None,
        stream: Optional[bool] = None,
        system_instruction: Optional[str] = None,
        tools: Optional[Iterable[Any]] = None,
        webhook_config: Optional[Any] = None,
        agent_config: Optional[Any] = None,
        # Support raw request for backward compatibility
        request: Optional[Any] = None,
        request_options: Optional[Any] = None,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        if request is not None:
            if stream:
                return self._fern_client.create_stream(request=request, request_options=request_options)
            else:
                return await self._fern_client.create(request=request, request_options=request_options)

        if input is None:
            raise TypeError("missing 1 required keyword-only argument: 'input'")

        if request_options is None:
            request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)

        if model is not None:
            params = {
                "model": model,
                "input": input,
                "background": background,
                "store": store,
                "stream": stream,
                "environment": environment,
                "previous_interaction_id": previous_interaction_id,
                "response_format": response_format,
                "response_mime_type": response_mime_type,
                "response_modalities": response_modalities,
                "service_tier": service_tier,
                "system_instruction": system_instruction,
                "tools": tools,
                "webhook_config": webhook_config,
                "generation_config": generation_config,
            }
            params = {k: v for k, v in params.items() if v is not None}
            req = CreateModelInteractionParams(**params)
        elif agent is not None:
            params = {
                "agent": agent,
                "input": input,
                "background": background,
                "store": store,
                "stream": stream,
                "environment": environment,
                "previous_interaction_id": previous_interaction_id,
                "response_format": response_format,
                "response_mime_type": response_mime_type,
                "response_modalities": response_modalities,
                "service_tier": service_tier,
                "system_instruction": system_instruction,
                "tools": tools,
                "webhook_config": webhook_config,
                "agent_config": agent_config,
            }
            params = {k: v for k, v in params.items() if v is not None}
            req = CreateAgentInteractionParams(**params)
        else:
            raise ValueError("Either model or agent must be specified")

        if stream:
            return self._fern_client.create_stream(request=req, request_options=request_options)
        else:
            return await self._fern_client.create(request=req, request_options=request_options)

    async def get(
        self,
        id: str,
        *,
        stream: Optional[bool] = None,
        include_input: Optional[bool] = None,
        last_event_id: Optional[str] = None,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)
        if stream:
            return self._fern_client.get_stream(
                id,
                stream=stream,
                last_event_id=last_event_id,
                include_input=include_input,
                request_options=request_options,
            )
        else:
            return await self._fern_client.get(
                id,
                stream=stream,
                last_event_id=last_event_id,
                include_input=include_input,
                request_options=request_options,
            )

    async def cancel(
        self,
        id: str,
        *,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)
        return await self._fern_client.cancel(id, request_options=request_options)

    async def delete(
        self,
        id: str,
        *,
        extra_headers: Optional[dict] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        request_options = _make_fern_request_options(extra_headers, extra_query, extra_body, timeout)
        return await self._fern_client.delete(id, request_options=request_options)
