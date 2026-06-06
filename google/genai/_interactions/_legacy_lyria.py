# Copyright 2025 Google LLC
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

"""Compatibility shim for the legacy vertex+lyria response/event shape.

The vertex `aiplatform.googleapis.com` endpoint returns a different schema for
`lyria-3-pro-preview, lyria-3-clip-preview` than the public `generativelanguage.googleapis.com` API:
- non-streaming responses use `outputs: List[Content]` instead of the modern
  `steps: List[Step]`,
- streaming SSE events use `interaction.start`, `content.start/delta/stop`, and
  `interaction.complete` instead of the modern `interaction.created`,
  `step.start/delta/stop`, and `interaction.completed`.

Two cooperating mechanisms cover the surface:

1. **Data inspection — non-streaming.** `Interaction._maybe_coerce_outputs`
   checks whether the response body's `model` field is in `LEGACY_LYRIA_MODELS`
   and rewrites `outputs` to `steps` accordingly. The model field is present on
   every Interaction body produced by `create()`, `get()`, and any deferred
   parse via `with_raw_response.parse()`, including the nested `interaction`
   body inside `interaction.created` / `interaction.completed` SSE events.
   This helper does not consult any contextvar; data is the only signal.

2. **Stream subclass + contextvar — streaming SSE event renames.** Per-event
   `event_type` renames have to happen *before* the discriminated-union
   dispatch runs and most events don't carry a model field, so we use a
   per-iteration contextvar (`LEGACY_LYRIA_SHIM_CTX`) instead of data
   inspection. `_base_client._process_response_data` reads it to gate the
   rename helper. Two stream subclasses set the contextvar:

   - `LegacyLyriaInteractionStream` / `LegacyLyriaInteractionAsyncStream`:
     activate the contextvar unconditionally on entry. Used by `create()`'s
     streaming path, where `is_legacy_lyria_request` lets the resource layer
     pre-detect the legacy case at request time.

   - `LegacyLyriaInteractionDetectingStream` / `LegacyLyriaInteractionDetectingAsyncStream`:
     activate the contextvar lazily, only on observing the first legacy
     `event_type`. Used by `get()`'s streaming path, where the model is
     unknown until the first event arrives.

   Both pairs reset the contextvar in `finally:` so activation is scoped to
   one iteration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, TypeVar, cast
from contextvars import ContextVar
from typing_extensions import override

from ._streaming import Stream, AsyncStream

if TYPE_CHECKING:
    from collections.abc import Iterator, AsyncIterator

__all__ = [
    "LEGACY_LYRIA_SHIM_CTX",
    "LEGACY_LYRIA_MODELS",
    "is_legacy_lyria_request",
    "is_legacy_lyria_response_body",
    "maybe_remap_legacy_sse_event",
    "LegacyLyriaInteractionStream",
    "LegacyLyriaInteractionAsyncStream",
    "LegacyLyriaInteractionDetectingStream",
    "LegacyLyriaInteractionDetectingAsyncStream",
]

_T = TypeVar("_T")

# Set by the streaming subclasses below for the lifetime of one iteration. Read
# by `_base_client._process_response_data` to gate the per-SSE-event
# `event_type` rename (which must happen before discriminator-union dispatch).
# Not consulted by `Interaction._maybe_coerce_outputs` — that helper is purely
# data-gated, so a contextvar leak across yields cannot trigger spurious
# Interaction rewrites.
LEGACY_LYRIA_SHIM_CTX: ContextVar[bool] = ContextVar("legacy_lyria_shim", default=False)

# Models known to return the legacy vertex shape. Currently exactly one. Kept
# as a frozenset so additional models can be added without touching call sites.
LEGACY_LYRIA_MODELS = frozenset({"lyria-3-pro-preview", "lyria-3-clip-preview"})

# Mapping of legacy SSE event_type values to their modern equivalents in the
# `InteractionSSEEvent` discriminator union. Captured live from the vertex
# endpoint for `lyria-3-pro-preview, lyria-3-clip-preview`.
_LEGACY_EVENT_TYPE_RENAMES: Dict[str, str] = {
    "interaction.start": "interaction.created",
    "content.start": "step.start",
    "content.delta": "step.delta",
    "content.stop": "step.stop",
    "interaction.complete": "interaction.completed",
}


def is_legacy_lyria_request(*, is_vertex: bool, model: object) -> bool:
    """Return True iff the (client, model) combination needs the shim active.

    Used at request issue time (in the resource layer) to decide whether to
    pick the `LegacyLyriaInteractionStream` subclass for streaming requests.
    """
    return bool(is_vertex) and isinstance(model, str) and model in LEGACY_LYRIA_MODELS


def is_legacy_lyria_response_body(data: object) -> bool:
    """Return True iff a parsed response body identifies itself as a legacy-lyria payload.

    Used at parse time (inside `Interaction._maybe_coerce_outputs`) to gate
    the `outputs` -> `steps` rewrite. Works for any path that produces an
    Interaction body — including `get()` (where the model isn't known until
    the response arrives) and `with_raw_response.parse()` (where parsing
    happens after the resource-level detection has already returned).
    """
    if not isinstance(data, dict):
        return False
    typed_data: Dict[str, Any] = cast("Dict[str, Any]", data)
    model = typed_data.get("model")
    return isinstance(model, str) and model in LEGACY_LYRIA_MODELS


def maybe_remap_legacy_sse_event(data: Dict[str, Any]) -> Dict[str, Any]:
    """Translate one legacy SSE event dict to the modern `InteractionSSEEvent` shape.

    Returns the input unchanged if the `event_type` is not one of the legacy
    ones we know how to map. Only the `content.start` mapping is non-trivial:
    the legacy event carries a single `content: <Content>` block, while the
    modern `step.start` event expects `step: {type: "model_output", content:
    [<Content>]}`.
    """
    event_type = data.get("event_type")
    if not isinstance(event_type, str) or event_type not in _LEGACY_EVENT_TYPE_RENAMES:
        return data

    new_data: Dict[str, Any] = {**data, "event_type": _LEGACY_EVENT_TYPE_RENAMES[event_type]}

    if event_type == "content.start":
        content = new_data.pop("content", None)
        new_data["step"] = {
            "type": "model_output",
            "content": [content] if content is not None else [],
        }

    return new_data


def _is_legacy_event_dict(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    typed_data: Dict[str, Any] = cast("Dict[str, Any]", data)
    event_type = typed_data.get("event_type")
    return isinstance(event_type, str) and event_type in _LEGACY_EVENT_TYPE_RENAMES


class LegacyLyriaInteractionStream(Stream[_T]):
    """Sync stream subclass that activates the legacy-lyria shim eagerly.

    Used by `create(stream=True)` where the resource layer pre-detects the
    legacy case via `is_legacy_lyria_request(...)`. The contextvar is set on
    iteration start and reset in `finally`, so even an unrecognized first
    event won't disable the shim — every event runs through the rename helper
    (which is a no-op for unrecognized event_types).
    """

    @override
    def __stream__(self) -> "Iterator[_T]":
        token = LEGACY_LYRIA_SHIM_CTX.set(True)
        try:
            yield from super().__stream__()
        finally:
            LEGACY_LYRIA_SHIM_CTX.reset(token)


class LegacyLyriaInteractionAsyncStream(AsyncStream[_T]):
    """Async counterpart of `LegacyLyriaInteractionStream`."""

    @override
    async def __stream__(self) -> "AsyncIterator[_T]":
        token = LEGACY_LYRIA_SHIM_CTX.set(True)
        try:
            async for item in super().__stream__():
                yield item
        finally:
            LEGACY_LYRIA_SHIM_CTX.reset(token)


class LegacyLyriaInteractionDetectingStream(Stream[_T]):
    """Sync stream subclass that activates the shim lazily on first legacy event.

    Used by `get(stream=True)` where the model isn't known at request time, so
    we can't pre-detect. Replicates `Stream.__stream__` to peek at each raw
    event dict before parsing; the first event whose `event_type` matches a
    known legacy variant flips `LEGACY_LYRIA_SHIM_CTX` for the rest of the
    iteration. Reset in `finally`.

    For non-legacy interactions the dynamic detection never activates and the
    subclass is a no-op vs. plain `Stream`.
    """

    @override
    def __stream__(self) -> "Iterator[_T]":
        cast_to = cast(Any, self._cast_to)
        response = self.response
        process_data = self._client._process_response_data
        iterator = self._iter_events()
        token = None
        try:
            for sse in iterator:
                if sse.data.startswith("[DONE]"):
                    break
                data = sse.json()
                if token is None and _is_legacy_event_dict(data):
                    token = LEGACY_LYRIA_SHIM_CTX.set(True)
                yield process_data(data=data, cast_to=cast_to, response=response)
        finally:
            if token is not None:
                LEGACY_LYRIA_SHIM_CTX.reset(token)
            response.close()


class LegacyLyriaInteractionDetectingAsyncStream(AsyncStream[_T]):
    """Async counterpart of `LegacyLyriaInteractionDetectingStream`."""

    @override
    async def __stream__(self) -> "AsyncIterator[_T]":
        cast_to = cast(Any, self._cast_to)
        response = self.response
        process_data = self._client._process_response_data
        iterator = self._iter_events()
        token = None
        try:
            async for sse in iterator:
                if sse.data.startswith("[DONE]"):
                    break
                data = sse.json()
                if token is None and _is_legacy_event_dict(data):
                    token = LEGACY_LYRIA_SHIM_CTX.set(True)
                yield process_data(data=data, cast_to=cast_to, response=response)
        finally:
            if token is not None:
                LEGACY_LYRIA_SHIM_CTX.reset(token)
            await response.aclose()
