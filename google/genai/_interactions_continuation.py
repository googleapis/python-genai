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

"""Automatic continuation state and helpers for the Interactions API."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable, Generator, Mapping
import dataclasses
import time
from typing import Any, Optional
import warnings

from . import errors

# Maximum consecutive reconnects after a mid-hop disconnect that made no
# progress (no new checkpoint token since the hop's start token).
MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS = 3

_AUTO_CONTINUE_AND_BACKGROUND_ERROR = (
    'automatic_continuation=False cannot be used with background=True.'
)

_REQUEST_AND_BODY_ERROR = (
    'create() accepts either request=... or individual body keyword arguments, '
    'not both.'
)

_INCOMPLETE_CONTINUATION_WARNING = (
    "Interaction stopped before completion (status='requires_continuation') "
    'with a continuation_token because the per-request decode token limit was '
    'reached. To resume decoding automatically, pass '
    'automatic_continuation=True (note: each continuation hop re-prefills and '
    'bills input tokens), or use background=True (the most cost-efficient '
    'option for server-managed continuation), or resume manually by passing '
    'continuation_token to interactions.create() (with '
    "previous_interaction_id set to this interaction's id and no input, or "
    'with the original input when store=False).'
)

_RESUMABLE_STREAM_HOP_STATUSES = frozenset({
    None,
    'in_progress',
    'requires_continuation',
})

# Events that carry no model output. A stream that drops after one of these (and
# nothing else) since the last checkpoint can be resumed without duplicating
# output.
_NON_CONTENT_STREAM_EVENTS = frozenset({
    'interaction.created',
    'interaction.status_update',
})

# Usage list fields are merged per key (e.g. per modality), summing the value.
_USAGE_LIST_KEYS: dict[str, tuple[str, str]] = {
    'cached_tokens_by_modality': ('modality', 'tokens'),
    'input_tokens_by_modality': ('modality', 'tokens'),
    'output_tokens_by_modality': ('modality', 'tokens'),
    'tool_use_tokens_by_modality': ('modality', 'tokens'),
    'grounding_tool_count': ('type', 'count'),
}

_incomplete_continuation_warned = False


class ContinuationTimeoutError(TimeoutError):
  """The per-call `timeout` ran out before automatic continuation finished."""


class CallDeadline:
  """Wall-clock budget of one logical `interactions.create()` call.

  A numeric per-call `timeout` bounds the whole call rather than each
  continuation hop (HTTP request): the deadline is fixed when the call starts,
  every hop is sent with the time left, and no further hop starts once it has
  passed. An `httpx.Timeout` (or `None`) is a per-request setting and is passed
  to each hop unchanged, so the call is unbounded across hops.
  """

  def __init__(
      self,
      timeout: Any,
      *,
      enabled: bool = True,
      clock: Optional[Callable[[], float]] = None,
  ):
    self._timeout = timeout
    self._clock = clock or time.monotonic
    self._deadline: Optional[float] = None
    if (
        enabled
        and isinstance(timeout, (int, float))
        and not isinstance(timeout, bool)
    ):
      self._deadline = self._clock() + float(timeout)

  @property
  def timeout(self) -> Any:
    """The per-call `timeout` this deadline was created from."""
    return self._timeout

  def remaining(self) -> Optional[float]:
    """Seconds left before the deadline, or None if unbounded."""
    if self._deadline is None:
      return None
    return self._deadline - self._clock()

  def expired(self) -> bool:
    remaining = self.remaining()
    return remaining is not None and remaining <= 0

  def hop_timeout(self) -> Any:
    """The `timeout` to send with the next hop (the time left, if bounded)."""
    remaining = self.remaining()
    if remaining is None:
      return self._timeout
    return max(remaining, 0.0)

  def check(self) -> None:
    """Raises `ContinuationTimeoutError` once the deadline has passed."""
    if self.expired():
      raise ContinuationTimeoutError(
          f'interactions.create() timed out after {self._timeout} seconds'
          ' before automatic continuation finished. Increase `timeout` (it'
          ' bounds the whole call, across continuation hops) or resume from'
          ' the continuation_token.'
      )


def _get_value(value: Any, name: str) -> Any:
  if isinstance(value, Mapping):
    return value.get(name)
  return getattr(value, name, None)


def _set_or_copy(target: Any, updates: dict[str, Any]) -> Any:
  if hasattr(target, 'model_copy'):
    return target.model_copy(update=updates)
  if isinstance(target, dict):
    return {**target, **updates}
  for name, value in updates.items():
    setattr(target, name, value)
  return target


def _optional_bool(
    value: Any, default: Optional[bool] = None
) -> Optional[bool]:
  if isinstance(value, bool):
    return value
  return default


def _non_empty_str(value: Any) -> Optional[str]:
  return value if isinstance(value, str) and value else None


def _is_unset_or_none(
    value: Any, unset_cls: Optional[type[Any]] = None
) -> bool:
  if value is None:
    return True
  if unset_cls is not None and isinstance(value, unset_cls):
    return True
  return type(value).__name__ == 'Unset'


def _is_agent_body(body: Any, unset_cls: Optional[type[Any]] = None) -> bool:
  """Whether the create body targets an agent (server-managed loop)."""
  return not _is_unset_or_none(
      _get_value(body, 'agent'), unset_cls
  ) or not _is_unset_or_none(_get_value(body, 'agent_config'), unset_cls)


def _continuation_body(
    body: Any, token: str, token_owner_id: Optional[str]
) -> Any:
  """Returns the create body for a continuation hop resuming from `token`.

  With `store` enabled (the default) the server rebuilds the context from the
  stored interaction that issued `token`, so the hop sends that interaction as
  `previous_interaction_id` (the server checks the token belongs to it) and
  omits `input`. With `store=False` nothing is stored, so the original `input`
  is resent with the token instead.

  `token_owner_id` is None when the token did not come from an earlier hop
  (e.g. the caller's own `continuation_token`); the original request is then
  resent as-is with `token`.
  """
  updates: dict[str, Any] = {'continuation_token': token}
  stateful = bool(token_owner_id) and _get_value(body, 'store') is not False
  if stateful:
    updates['previous_interaction_id'] = token_owner_id
  if isinstance(body, Mapping):
    new_body = {**body, **updates}
    if stateful:
      new_body.pop('input', None)
    return new_body
  if hasattr(body, 'model_copy'):
    if stateful:
      updates['input'] = None
    return body.model_copy(update=updates)
  return body


def _with_request_continuation(
    request: Any, token: str, token_owner_id: Optional[str]
) -> Any:
  body = _get_value(request, 'body')
  new_body = _continuation_body(body, token, token_owner_id)
  if isinstance(request, Mapping):
    return {**request, 'body': new_body}
  if hasattr(request, 'model_copy'):
    return request.model_copy(update={'body': new_body})
  return request


@dataclasses.dataclass(frozen=True)
class ContinuationRequest:
  """Prepared `interactions.create()` request state and per-hop builder."""

  request: Any
  body: Mapping[str, Any]
  stream: bool
  caller_token: Optional[str]
  enable_continuation: bool
  warn_on_incomplete: bool = False
  stateful: bool = True

  @classmethod
  def from_create_args(
      cls,
      *,
      request: Any,
      body: dict[str, Any],
      automatic_continuation: Optional[bool],
      normalize_body: Callable[[dict[str, Any]], dict[str, Any]],
      unset_cls: Optional[type[Any]] = None,
  ) -> ContinuationRequest:
    """Validates and normalizes `create()` arguments for continuation."""
    if request is not None:
      if body:
        raise TypeError(_REQUEST_AND_BODY_ERROR)
      request_body = _get_value(request, 'body')
      is_background = bool(
          _optional_bool(_get_value(request_body, 'background'), default=False)
      )
      stream = bool(
          _optional_bool(_get_value(request_body, 'stream'), default=False)
      )
      caller_token = _non_empty_str(
          _get_value(request_body, 'continuation_token')
      )
      if automatic_continuation is None:
        req_auto = _get_value(request, 'automatic_continuation')
        if req_auto is None:
          req_auto = _get_value(request_body, 'automatic_continuation')
        automatic_continuation = req_auto
      normalized_body: Mapping[str, Any] = body
    else:
      is_background = bool(
          _optional_bool(body.get('background'), default=False)
      )
      stream = bool(_optional_bool(body.get('stream'), default=False))
      normalized_body = normalize_body(body)
      caller_token = _non_empty_str(normalized_body.get('continuation_token'))
      request_body = normalized_body

    if is_background and automatic_continuation is False:
      raise ValueError(_AUTO_CONTINUE_AND_BACKGROUND_ERROR)

    enable_continuation = (
        bool(_optional_bool(automatic_continuation, default=True))
        and not is_background
        and not _is_agent_body(request_body, unset_cls)
    )
    warn_on_incomplete = automatic_continuation is False and not caller_token
    stateful = _get_value(request_body, 'store') is not False

    return cls(
        request=request,
        body=normalized_body,
        stream=stream,
        caller_token=caller_token,
        enable_continuation=enable_continuation,
        warn_on_incomplete=warn_on_incomplete,
        stateful=stateful,
    )

  def hop_args(
      self,
      token: Optional[str] = None,
      token_owner_id: Optional[str] = None,
  ) -> tuple[Any, Mapping[str, Any]]:
    """Returns `(request, body)` for the initial hop or a continuation hop."""
    if self.request is not None:
      req = (
          self.request
          if token is None
          else _with_request_continuation(self.request, token, token_owner_id)
      )
      return req, self.body
    req_body = (
        self.body
        if token is None
        else _continuation_body(self.body, token, token_owner_id)
    )
    return None, req_body


def _extract_hop_continuation_state(
    event: Any,
    hop_status: Optional[str],
    hop_continuation_token: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
  """Extracts `(status, continuation_token)` updates from one SSE event."""
  if _get_value(event, 'event_type') == 'error':
    return 'error', None

  interaction = _get_value(event, 'interaction')
  if interaction is not None:
    status = _get_value(interaction, 'status')
    if isinstance(status, str) and status:
      hop_status = status
    token = _non_empty_str(_get_value(interaction, 'continuation_token'))
    if _get_value(event, 'event_type') == 'interaction.completed':
      # The terminal snapshot is authoritative: a missing token clears the hop's
      # seed token and any earlier mid-hop checkpoint token.
      hop_continuation_token = token
    elif token:
      hop_continuation_token = token

  direct_status = _get_value(event, 'status')
  if isinstance(direct_status, str) and direct_status:
    hop_status = direct_status
  direct_token = _get_value(event, 'continuation_token')
  if isinstance(direct_token, str) and direct_token:
    hop_continuation_token = direct_token

  return hop_status, hop_continuation_token


def _has_content_since_checkpoint(
    event: Any,
    content_since_checkpoint: bool,
) -> bool:
  """Tracks whether output was yielded since the latest resume point."""
  event_type = _get_value(event, 'event_type')
  if event_type == 'interaction.status_update':
    if _non_empty_str(_get_value(event, 'continuation_token')):
      return False
    return content_since_checkpoint
  if event_type == 'interaction.completed':
    # The terminal snapshot's token (if any) is a fresh resume point.
    return False
  if event_type in _NON_CONTENT_STREAM_EVENTS:
    return content_since_checkpoint
  return True


def _event_interaction_id(event: Any) -> Optional[str]:
  """The id of the interaction (hop) an SSE event belongs to, if present."""
  interaction_id = _non_empty_str(_get_value(event, 'interaction_id'))
  if interaction_id:
    return interaction_id
  return _non_empty_str(_get_value(_get_value(event, 'interaction'), 'id'))


def _can_resume_stream_hop(
    hop_status: Optional[str],
    hop_continuation_token: Optional[str],
) -> bool:
  return bool(
      hop_continuation_token and hop_status in _RESUMABLE_STREAM_HOP_STATUSES
  )


def _next_no_progress_reconnects(
    no_progress_reconnects: int,
    hop_status: Optional[str],
    hop_start_token: Optional[str],
    hop_continuation_token: Optional[str],
) -> int:
  """Updates the no-progress reconnect counter after a resumable hop ends."""
  if hop_status == 'requires_continuation':
    # Clean hop boundary (per-request decode limit reached).
    return 0
  if hop_continuation_token != hop_start_token:
    # Dropped mid-hop after a new checkpoint token was received.
    return 0
  # Dropped mid-hop before any new checkpoint: retry the hop's own token.
  return no_progress_reconnects + 1


@dataclasses.dataclass
class _StreamHop:
  """What was observed during one hop (HTTP request) of a continuation stream."""

  # The continuation_token and owner id this hop was requested with.
  start_token: Optional[str] = None
  start_token_owner_id: Optional[str] = None
  # Seeded with `start_token` so a disconnect before the hop's first checkpoint
  # retries from the hop start.
  token: Optional[str] = None
  # The interaction that issued `token`. With store=True the server only accepts
  # a token together with the interaction that issued it as
  # `previous_interaction_id`, so a retry of the seed token keeps the seed's
  # owner even after this hop's own interaction was created.
  token_owner_id: Optional[str] = None
  # This hop's own interaction id, once known.
  interaction_id: Optional[str] = None
  # Latest status observed during the hop, or None if none arrived yet.
  status: Optional[str] = None
  # Whether the HTTP stream was opened (response headers received).
  stream_opened: bool = False
  # Whether output events were yielded since the latest checkpoint token.
  content_since_checkpoint: bool = False


class StreamContinuation:
  """State of a streaming `interactions.create()` call with continuation.

  A stream is made of one or more hops (HTTP requests). Per-hop state lives in a
  `_StreamHop` record replaced wholesale by `start_hop()`, so per-hop fields
  cannot leak across hops. Loop state (the next resume token + owner id, the
  no-progress reconnect counter, and the pending transport error) persists on
  `StreamContinuation` across hops.
  """

  def __init__(
      self,
      initial_continuation_token: Optional[str] = None,
      *,
      connection_error_type: type[BaseException] = Exception,
      stateful: bool = True,
  ):
    self._next_token: Optional[str] = initial_continuation_token
    # The caller's own token: a failure that leaves nothing newer to resume
    # from is not "after progress" and is raised as-is.
    self._initial_token: Optional[str] = initial_continuation_token
    # The interaction that issued `_next_token`; None for the caller's own
    # token (the original request is resent as-is).
    self._next_token_owner_id: Optional[str] = None
    # The ids of every hop's interaction, in order (for error reporting).
    self._hop_ids: list[str] = []
    self._no_progress_reconnects = 0
    # The latest transport error not followed by progress; raised if the loop
    # gives up so the failure is not hidden by later clean closes.
    self._last_error: Optional[Exception] = None
    self._connection_error_type = connection_error_type
    self._stateful = stateful
    self._hop = _StreamHop(
        start_token=initial_continuation_token,
        token=initial_continuation_token,
    )

  def start_hop(
      self, *, stream_opened: bool = False
  ) -> tuple[Optional[str], Optional[str]]:
    """Starts a new hop and returns `(token, token_owner_id)` to request."""
    self._hop = _StreamHop(
        start_token=self._next_token,
        start_token_owner_id=self._next_token_owner_id,
        token=self._next_token,
        token_owner_id=self._next_token_owner_id,
        stream_opened=stream_opened,
    )
    return self._next_token, self._next_token_owner_id

  def mark_stream_opened(self) -> None:
    """Marks that the current hop's HTTP stream was opened."""
    self._hop.stream_opened = True

  def observe(self, event: Any) -> Any:
    """Records one streamed SSE event and returns it."""
    hop = self._hop
    hop.stream_opened = True
    event_interaction_id = _event_interaction_id(event)
    if event_interaction_id:
      hop.interaction_id = event_interaction_id
      if event_interaction_id not in self._hop_ids:
        self._hop_ids.append(event_interaction_id)
    previous_token = hop.token
    hop.status, hop.token = _extract_hop_continuation_state(
        event, hop.status, hop.token
    )
    if hop.token and hop.token != previous_token:
      hop.token_owner_id = hop.interaction_id
    hop.content_since_checkpoint = _has_content_since_checkpoint(
        event, hop.content_since_checkpoint
    )
    return event

  def _can_resume_hop(self) -> bool:
    # Resuming from the checkpoint would re-generate (and duplicate) any output
    # yielded since it.
    hop = self._hop
    return not hop.content_since_checkpoint and _can_resume_stream_hop(
        hop.status, hop.token
    )

  def _fail(self, error: Exception) -> Exception:
    """The error to raise when the stream gives up with `error`.

    If the server issued a resumable token during this call (a completed
    `requires_continuation` hop, or a mid-hop checkpoint), the work so far is
    resumable and `error` is wrapped in `errors.ContinuationInterruptedError`
    carrying that token. Otherwise `error` is returned as-is.
    """
    hop = self._hop
    token = (
        hop.token if _can_resume_stream_hop(hop.status, hop.token) else None
    )
    if not token or token == self._initial_token:
      return error
    interrupted = errors.ContinuationInterruptedError(
        f'Automatic continuation of the stream was interrupted: {error}.'
        ' The continuation_token can be used to resume (output yielded after'
        ' a mid-hop checkpoint is re-generated).',
        partial_interaction=None,
        continuation_token=token,
        interaction_id=hop.token_owner_id if self._stateful else None,
        continuation_ids=list(self._hop_ids),
    )
    interrupted.__cause__ = error
    return interrupted

  def end_hop(self, error: Optional[Exception] = None) -> bool:
    """Ends the current hop and returns True if another hop should start.

    Raises `error` (or the pending prior disconnect error) when the stream
    cannot safely resume or exceeds `MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS`,
    wrapped in `errors.ContinuationInterruptedError` if a server-issued token
    to resume from exists (see `_fail`).
    """
    hop = self._hop
    if isinstance(error, ContinuationTimeoutError):
      raise self._fail(error)
    if error is not None and not hop.stream_opened:
      # Pre-stream HTTP status or validation errors (already retried by
      # RetryConfig) must propagate immediately; only connection errors resume.
      if not isinstance(error, self._connection_error_type):
        raise self._fail(error)

    if not self._can_resume_hop():
      if error is not None:
        raise self._fail(error)
      return False

    if hop.status == 'requires_continuation' and hop.token == hop.start_token:
      # The hop finished but handed back the token it was started with:
      # resuming would loop forever without progress.
      if error is not None:
        raise self._fail(error)
      return False

    self._no_progress_reconnects = _next_no_progress_reconnects(
        self._no_progress_reconnects,
        hop.status,
        hop.start_token,
        hop.token,
    )
    if self._no_progress_reconnects == 0:
      self._last_error = None
    if error is not None:
      self._last_error = error
    if self._no_progress_reconnects > MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS:
      if self._last_error is not None:
        raise self._fail(self._last_error)
      return False

    self._next_token = hop.token
    self._next_token_owner_id = hop.token_owner_id
    return True


def wrap_stream_continuation(
    stream: Any,
    create_next_stream: Callable[[Optional[str], Optional[str]], Any],
    *,
    is_stream_fn: Callable[[Any], bool],
    wrap_errors_fn: Callable[[Any], Any],
    connection_error_type: type[BaseException],
    initial_continuation_token: Optional[str] = None,
    deadline: Optional[CallDeadline] = None,
    stateful: bool = True,
) -> Any:
  """Wraps a sync `Stream` to automatically continue across hops.

  `deadline` (if bounded) is checked before each event and before each new
  hop; once it has passed the stream stops with a `ContinuationTimeoutError`
  (wrapped in `errors.ContinuationInterruptedError` if resumable).
  """
  current_gen = stream.generator
  current_stream = stream
  deadline = deadline or CallDeadline(None)

  def _continuation_gen() -> Generator[Any, None, None]:
    nonlocal current_gen, current_stream
    state = StreamContinuation(
        initial_continuation_token=initial_continuation_token,
        connection_error_type=connection_error_type,
        stateful=stateful,
    )
    is_first_hop = True
    try:
      while True:
        token, token_owner_id = state.start_hop(stream_opened=is_first_hop)
        error: Optional[Exception] = None
        if is_first_hop:
          is_first_hop = False
        else:
          if hasattr(current_stream, 'response'):
            current_stream.response.close()
          try:
            deadline.check()
            next_stream = create_next_stream(token, token_owner_id)
          except Exception as e:  # pylint: disable=broad-exception-caught
            error = e
          else:
            if not is_stream_fn(next_stream):
              break
            state.mark_stream_opened()
            next_stream = wrap_errors_fn(next_stream)
            current_stream = next_stream
            current_gen = next_stream.generator
            if hasattr(stream, 'response') and hasattr(next_stream, 'response'):
              stream.response = next_stream.response

        if error is None:
          it = iter(current_gen)
          while True:
            try:
              deadline.check()
              event = next(it)
            except StopIteration:
              break
            except Exception as e:  # pylint: disable=broad-exception-caught
              error = e
              break
            yield state.observe(event)

        if not state.end_hop(error):
          break
    finally:
      if hasattr(current_gen, 'close'):
        current_gen.close()
      if current_stream is not stream:
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


def wrap_async_stream_continuation(
    stream: Any,
    create_next_stream: Callable[
        [Optional[str], Optional[str]], Awaitable[Any]
    ],
    *,
    is_stream_fn: Callable[[Any], bool],
    wrap_errors_fn: Callable[[Any], Any],
    connection_error_type: type[BaseException],
    initial_continuation_token: Optional[str] = None,
    deadline: Optional[CallDeadline] = None,
    stateful: bool = True,
) -> Any:
  """Wraps an `AsyncStream` to automatically continue across hops."""
  current_gen = stream.generator
  current_stream = stream
  deadline = deadline or CallDeadline(None)

  async def _continuation_agen() -> AsyncGenerator[Any, None]:
    nonlocal current_gen, current_stream
    state = StreamContinuation(
        initial_continuation_token=initial_continuation_token,
        connection_error_type=connection_error_type,
        stateful=stateful,
    )
    is_first_hop = True
    try:
      while True:
        token, token_owner_id = state.start_hop(stream_opened=is_first_hop)
        error: Optional[Exception] = None
        if is_first_hop:
          is_first_hop = False
        else:
          if hasattr(current_stream, 'response'):
            await current_stream.response.aclose()
          try:
            deadline.check()
            next_stream = await create_next_stream(token, token_owner_id)
          except Exception as e:  # pylint: disable=broad-exception-caught
            error = e
          else:
            if not is_stream_fn(next_stream):
              break
            state.mark_stream_opened()
            next_stream = wrap_errors_fn(next_stream)
            current_stream = next_stream
            current_gen = next_stream.generator
            if hasattr(stream, 'response') and hasattr(next_stream, 'response'):
              stream.response = next_stream.response

        if error is None:
          it = current_gen.__aiter__()
          while True:
            try:
              deadline.check()
              event = await it.__anext__()
            except StopAsyncIteration:
              break
            except Exception as e:  # pylint: disable=broad-exception-caught
              error = e
              break
            yield state.observe(event)

        if not state.end_hop(error):
          break
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


def _warn_incomplete_continuation(*, stacklevel: int = 3) -> None:
  global _incomplete_continuation_warned
  if not _incomplete_continuation_warned:
    _incomplete_continuation_warned = True
    warnings.warn(
        _INCOMPLETE_CONTINUATION_WARNING,
        category=UserWarning,
        stacklevel=stacklevel,
    )


def warn_if_incomplete_unary(interaction: Any) -> None:
  """Emits a one-time warning when unary `create()` stops uncontinued."""
  if _should_continue_unary(interaction):
    _warn_incomplete_continuation(stacklevel=4)


def wrap_stream_incomplete_warning(stream: Any) -> Any:
  """Wraps a sync `Stream` to emit a one-time warning when left uncontinued."""
  current_gen = stream.generator

  def _warning_gen() -> Generator[Any, None, None]:
    hop_status: Optional[str] = None
    hop_continuation_token: Optional[str] = None
    try:
      for event in current_gen:
        hop_status, hop_continuation_token = _extract_hop_continuation_state(
            event,
            hop_status,
            hop_continuation_token,
        )
        yield event
      if hop_status == 'requires_continuation' and hop_continuation_token:
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


def wrap_async_stream_incomplete_warning(stream: Any) -> Any:
  """Wraps an `AsyncStream` to emit a one-time warning when left uncontinued."""
  current_gen = stream.generator

  async def _warning_agen() -> AsyncGenerator[Any, None]:
    hop_status: Optional[str] = None
    hop_continuation_token: Optional[str] = None
    try:
      async for event in current_gen:
        hop_status, hop_continuation_token = _extract_hop_continuation_state(
            event,
            hop_status,
            hop_continuation_token,
        )
        yield event
      if hop_status == 'requires_continuation' and hop_continuation_token:
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


def _should_continue_unary(interaction: Any) -> Optional[str]:
  if _get_value(interaction, 'status') != 'requires_continuation':
    return None
  token = _get_value(interaction, 'continuation_token')
  if not isinstance(token, str) or not token:
    return None
  return token


def _next_unary_hop_token(hop: Any, sent_token: Optional[str]) -> Optional[str]:
  """The token to continue from after `hop`, or None to stop."""
  token = _should_continue_unary(hop)
  if token == sent_token:
    # The hop handed back the token it was started with: continuing would loop
    # forever without progress.
    return None
  return token


def _default_normalize_interaction(value: Any) -> Optional[Any]:
  return value if isinstance(_get_value(value, 'steps'), list) else None


def _identity(value: Any) -> Any:
  return value


def _interrupted_unary(
    error: Exception,
    hops: list[Any],
    token: str,
    *,
    normalize_interaction: Callable[[Any], Optional[Any]],
    finalize_interaction: Callable[[Any], Any],
    stateful: bool = True,
) -> errors.ContinuationInterruptedError:
  """Builds the error for a continuation hop that failed after `hops`."""
  partial = merge_unary_hops(
      hops,
      normalize_interaction=normalize_interaction,
      finalize_interaction=finalize_interaction,
  )
  interaction_id = (
      _non_empty_str(_get_value(hops[-1], 'id'))
      if stateful and _get_value(hops[0], 'store') is not False
      else None
  )
  return errors.ContinuationInterruptedError(
      f'Automatic continuation was interrupted after {len(hops)} completed'
      f' hop(s): {error}. The partial interaction (status'
      " 'requires_continuation') and its continuation_token can be used to"
      ' resume.',
      partial_interaction=partial,
      continuation_token=token,
      interaction_id=interaction_id,
      continuation_ids=_merge_continuation_ids(hops),
  )


def continue_unary_interaction(
    initial_response: Any,
    create_next: Callable[[Optional[str], Optional[str]], Any],
    *,
    initial_continuation_token: Optional[str] = None,
    normalize_interaction: Callable[
        [Any], Optional[Any]
    ] = _default_normalize_interaction,
    finalize_interaction: Callable[[Any], Any] = _identity,
    deadline: Optional[CallDeadline] = None,
    stateful: bool = True,
) -> Any:
  """Continues a unary interaction across `requires_continuation` hops.

  A hop that fails after an earlier hop completed raises
  `errors.ContinuationInterruptedError` (with the failure as `__cause__`)
  carrying the hops merged so far and the token to resume from, so the output
  already produced (and billed) is not lost. Running out of `deadline` before
  a hop starts is such a failure (`ContinuationTimeoutError`).
  """
  deadline = deadline or CallDeadline(None)
  hops = [initial_response]
  sent_token = initial_continuation_token
  while True:
    token = _next_unary_hop_token(hops[-1], sent_token)
    if not token:
      return merge_unary_hops(
          hops,
          normalize_interaction=normalize_interaction,
          finalize_interaction=finalize_interaction,
      )
    try:
      deadline.check()
      hop = create_next(token, _non_empty_str(_get_value(hops[-1], 'id')))
    except Exception as e:
      raise _interrupted_unary(
          e,
          hops,
          token,
          normalize_interaction=normalize_interaction,
          finalize_interaction=finalize_interaction,
          stateful=stateful,
      ) from e
    hops.append(hop)
    sent_token = token


async def continue_async_unary_interaction(
    initial_response: Any,
    create_next: Callable[[Optional[str], Optional[str]], Awaitable[Any]],
    *,
    initial_continuation_token: Optional[str] = None,
    normalize_interaction: Callable[
        [Any], Optional[Any]
    ] = _default_normalize_interaction,
    finalize_interaction: Callable[[Any], Any] = _identity,
    deadline: Optional[CallDeadline] = None,
    stateful: bool = True,
) -> Any:
  """Async `continue_unary_interaction`."""
  deadline = deadline or CallDeadline(None)
  hops = [initial_response]
  sent_token = initial_continuation_token
  while True:
    token = _next_unary_hop_token(hops[-1], sent_token)
    if not token:
      return merge_unary_hops(
          hops,
          normalize_interaction=normalize_interaction,
          finalize_interaction=finalize_interaction,
      )
    try:
      deadline.check()
      hop = await create_next(
          token, _non_empty_str(_get_value(hops[-1], 'id'))
      )
    except Exception as e:
      raise _interrupted_unary(
          e,
          hops,
          token,
          normalize_interaction=normalize_interaction,
          finalize_interaction=finalize_interaction,
          stateful=stateful,
      ) from e
    hops.append(hop)
    sent_token = token


def _strip_leading_user_input_steps(steps: list[Any]) -> list[Any]:
  start = 0
  while start < len(steps) and _get_value(steps[start], 'type') == 'user_input':
    start += 1
  return steps[start:]


def _merge_continuation_ids(hops: list[Any]) -> list[str]:
  ids: list[str] = []
  for hop in hops:
    hop_continuation_ids = _get_value(hop, 'continuation_ids')
    if isinstance(hop_continuation_ids, list):
      ids.extend(
          cid for cid in hop_continuation_ids if isinstance(cid, str) and cid
      )
    hop_id = _get_value(hop, 'id')
    if isinstance(hop_id, str) and hop_id:
      ids.append(hop_id)
  return list(dict.fromkeys(ids))


def merge_unary_hops(
    hops: list[Any],
    *,
    normalize_interaction: Callable[
        [Any], Optional[Any]
    ] = _default_normalize_interaction,
    finalize_interaction: Callable[[Any], Any] = _identity,
) -> Any:
  """Merges automatic continuation hops into a single interaction.

  Each hop is its own interaction on the server, and only contains the output
  generated during that hop. The merged result is the final hop (so `id`,
  `status`, etc. refer to it) with the steps of every hop concatenated, usage
  summed across hops, and `continuation_ids` listing every hop's id. Fields
  describing the turn's request (`previous_interaction_id`, `created`, `input`)
  come from the first hop: later hops point back at the hop before them, not at
  the caller's previous turn.
  """
  final = hops[-1]
  if normalize_interaction(final) is None:
    return final

  steps: list[Any] = []
  for hop_index, hop in enumerate(hops):
    hop_steps = _get_value(hop, 'steps')
    if isinstance(hop_steps, list):
      if hop_index > 0:
        # Later hops continue the same turn; a repeated user_input step would
        # duplicate the input and cut `output_text` (which stops at the latest
        # user_input step) short.
        hop_steps = _strip_leading_user_input_steps(hop_steps)
      steps.extend(hop_steps)

  updates: dict[str, Any] = {
      'steps': steps,
      'continuation_ids': _merge_continuation_ids(hops),
  }
  if len(hops) > 1:
    for name in ('previous_interaction_id', 'created', 'input'):
      updates[name] = _get_value(hops[0], name)
  usage = _merge_usages(
      [u for u in (_get_value(hop, 'usage') for hop in hops) if u is not None],
      first_hop_usage=_get_value(hops[0], 'usage'),
  )
  if usage is not None:
    updates['usage'] = usage

  return finalize_interaction(_set_or_copy(final, updates))


def _usage_field_names(usage: Any) -> list[str]:
  if isinstance(usage, Mapping):
    return list(usage.keys())
  names = list(
      getattr(type(usage), 'model_fields', None)
      or getattr(usage, '__dict__', {})
  )
  extra = getattr(usage, '__pydantic_extra__', None) or {}
  return names + [name for name in extra if name not in names]


def _is_int(value: Any) -> bool:
  return isinstance(value, int) and not isinstance(value, bool)


def _merge_usage_list(
    lists: list[list[Any]], key_name: str, value_name: str
) -> list[Any]:
  merged: dict[Any, Any] = {}
  for items in lists:
    for item in items:
      key = _get_value(item, key_name)
      value = _get_value(item, value_name)
      if key not in merged:
        merged[key] = item
        continue
      prev = _get_value(merged[key], value_name)
      if _is_int(prev) and _is_int(value):
        merged[key] = _set_or_copy(merged[key], {value_name: prev + value})
  return list(merged.values())


_UNSET = object()


def _merge_usages(
    usages: list[Any], *, first_hop_usage: Any = _UNSET
) -> Optional[Any]:
  """Sums token usage across hops, keeping the first hop's input tokens."""
  if not usages:
    return None
  first = usages[0] if first_hop_usage is _UNSET else first_hop_usage
  updates: dict[str, Any] = {}
  names: list[str] = []
  for usage in usages:
    names.extend(n for n in _usage_field_names(usage) if n not in names)

  for name in names:
    if name == 'initial_input_tokens':
      continue
    values = [_get_value(u, name) for u in usages]
    present = [v for v in values if v is not None]
    if not present:
      continue
    if all(_is_int(v) for v in present):
      updates[name] = sum(present)
    elif name in _USAGE_LIST_KEYS and all(isinstance(v, list) for v in present):
      updates[name] = _merge_usage_list(present, *_USAGE_LIST_KEYS[name])

  initial_input_tokens = (
      _get_value(first, 'initial_input_tokens') if first is not None else None
  )
  if initial_input_tokens is None and first is not None:
    initial_input_tokens = _get_value(first, 'total_input_tokens')
  if initial_input_tokens is not None or (
      _get_value(usages[-1], 'initial_input_tokens') is not None
  ):
    updates['initial_input_tokens'] = initial_input_tokens

  return _set_or_copy(usages[-1], updates)
