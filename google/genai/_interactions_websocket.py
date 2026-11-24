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

"""Async WebSocket connections for live Interactions API calls.

Experimental: Live Interactions SDK support is experimental and may change in
future versions.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable, Generator, Mapping, Sequence
import json
from typing import Any, Generic, Optional, Union, cast
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel as PydanticBaseModel
from typing_extensions import TypeVar
from websockets.asyncio.client import ClientConnection, connect as ws_connect
from websockets.exceptions import ConnectionClosed
from websockets.frames import CloseCode

from ._live_interactions_experimental import (
    _warn_live_interactions_experimental as _warn_live_interactions_experimental,
)
from ._interactions_errors import APIWebSocketError as APIWebSocketError

TClientEvent = TypeVar('TClientEvent', default=Any)
TServerEvent = TypeVar('TServerEvent', default=Any)


def _closed_websocket_error(close_code: Optional[int]) -> APIWebSocketError:
  """Returns an `APIWebSocketError` describing a closed connection."""
  detail = 'The live interaction connection closed.'
  if close_code is not None:
    detail = (
        f'The live interaction connection closed with code {close_code}.'
    )
  return APIWebSocketError(detail, close_code=close_code)


_LIVE_INTERACTIONS_PATH = 'interactions/live'
_TERMINAL_EVENTS = frozenset({
    'interaction.completed',
    'interaction.canceled',
    'interaction.cancelled',
    'reconnection_required',
})


def _decode_frame_text(raw: Any) -> Any:
  """Decodes raw bytes to UTF-8 text, raising `APIWebSocketError` on failure."""
  if not isinstance(raw, bytes):
    return raw
  try:
    return raw.decode('utf-8')
  except UnicodeDecodeError:
    raise APIWebSocketError(
        'Live interaction server frames must contain UTF-8 JSON text.'
    ) from None


def _require_server_event_dict(event: Any) -> dict[str, Any]:
  """Validates that a decoded event is a dict with a non-empty `event_type` string."""
  if (
      not isinstance(event, dict)
      or not isinstance(event.get('event_type'), str)
      or not event['event_type']
  ):
    raise APIWebSocketError(
        'Live interaction server events must have an event_type.'
    )
  return event


def _frame_events(raw: Any) -> list[dict[str, Any]]:
  """Decodes a server frame into its events in wire order."""
  text = _decode_frame_text(raw)
  try:
    payload = json.loads(text)
  except (TypeError, json.JSONDecodeError):
    raise APIWebSocketError(
        'Live interaction server frames must contain valid JSON.'
    ) from None
  candidates = (
      payload['events']
      if isinstance(payload, dict) and isinstance(payload.get('events'), list)
      else [payload]
  )
  return [_require_server_event_dict(event) for event in candidates]


def _to_json_value(value: Any) -> Any:
  """Recursively converts Pydantic models and mappings to plain JSON-serializable values."""
  if isinstance(value, PydanticBaseModel):
    return value.model_dump(
        mode='json',
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
    )
  if isinstance(value, Mapping):
    return {key: _to_json_value(item) for key, item in value.items()}
  if isinstance(value, (list, tuple)):
    return [_to_json_value(item) for item in value]
  return value


def _serialize_client_event(event: Any) -> dict[str, Any]:
  """Serializes a single client event (Pydantic model or mapping) to a JSON-ready dict."""
  if isinstance(event, PydanticBaseModel):
    return event.model_dump(
        mode='json',
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
    )
  if isinstance(event, Mapping):
    return {key: _to_json_value(value) for key, value in event.items()}
  raise ValueError('Live client events must be mappings or Pydantic models.')


def _serialize_client_payload(input: Any) -> dict[str, Any]:  # pylint: disable=redefined-builtin
  """Normalizes `send()` input (text, single event, or event list) into a wire payload dict."""
  if isinstance(input, str):
    return {
        'event_type': 'input',
        'content': [{'type': 'text', 'text': input}],
    }
  if isinstance(input, (list, tuple)):
    return {'events': [_serialize_client_event(item) for item in input]}
  return _serialize_client_event(input)


def _payload_has_cancel(payload: Mapping[str, Any]) -> bool:
  """Returns whether the serialized payload contains an `interaction.cancel` event."""
  if payload.get('event_type') == 'interaction.cancel':
    return True
  events = payload.get('events')
  if not isinstance(events, list):
    return False
  return any(
      isinstance(item, Mapping)
      and item.get('event_type') == 'interaction.cancel'
      for item in events
  )


def _safe_close_code(error: ConnectionClosed) -> int:
  """Returns a close code without exposing the peer's close reason."""
  close = error.rcvd if error.rcvd is not None else error.sent
  if close is None:
    return int(CloseCode.ABNORMAL_CLOSURE)
  return close.code


def _interaction_id(value: Any) -> str:
  """Validates and returns a non-empty interaction ID string."""
  if not isinstance(value, str) or not value.strip():
    raise ValueError('A non-empty interaction ID is required to connect.')
  return value


def _websocket_url(
    api_client: Any,
    api_version: Optional[str],
) -> str:
  """Builds the WebSocket URL from the parent client's HTTP options."""
  if getattr(api_client, 'vertexai', False):
    raise ValueError('Live Interactions is currently Gemini API only.')
  http_options = getattr(api_client, '_http_options')
  parts = urlsplit(str(http_options.base_url).rstrip('/'))
  scheme = 'ws' if parts.scheme in {'http', 'ws'} else 'wss'
  version = api_version or http_options.api_version or ''
  path = '/'.join(
      part.strip('/')
      for part in (parts.path, version, _LIVE_INTERACTIONS_PATH)
      if part.strip('/')
  )
  return urlunsplit((scheme, parts.netloc, f'/{path}', parts.query, ''))


def _websocket_transport_kwargs(api_client: Any) -> dict[str, Any]:
  """Returns additional keyword arguments for the `websockets` transport layer."""
  transport_kwargs = getattr(api_client, '_websocket_ssl_ctx', None)
  if isinstance(transport_kwargs, Mapping):
    return dict(transport_kwargs)
  return {}


def _set_header(headers: dict[str, str], name: str, value: str) -> None:
  """Sets `name` on `headers`, replacing any case-insensitive match."""
  for candidate in [k for k in headers if k.lower() == name.lower()]:
    del headers[candidate]
  headers[name] = value


async def _websocket_headers(
    api_client: Any,
    extra_headers: Optional[Mapping[str, str]],
    api_revision: Optional[str] = None,
) -> dict[str, str]:
  """Builds the WebSocket handshake headers, including auth and API revision."""
  headers: dict[str, str] = (
      {'api-revision': api_revision} if api_revision is not None else {}
  )
  credentials = getattr(api_client, '_credentials', None)
  user_project = getattr(credentials, 'quota_project_id', None)
  if user_project:
    headers['x-goog-user-project'] = user_project
  api_key = getattr(api_client, 'api_key', None)
  if api_key:
    headers['x-goog-api-key'] = api_key
  for source in (getattr(api_client, '_http_options').headers, extra_headers):
    for name, value in (source or {}).items():
      _set_header(headers, name, value)
  if isinstance(api_key, str) and api_key.startswith('auth_tokens/'):
    for name in [k for k in headers if k.lower() == 'authorization']:
      del headers[name]
    _set_header(headers, 'x-goog-api-key', api_key)
  return headers


class InteractionWebSocketConnection(Generic[TClientEvent, TServerEvent]):
  """An active asynchronous live interaction WebSocket connection.

  Experimental: Live Interactions SDK support is experimental and may change
  in future versions.
  """

  def __init__(
      self,
      websocket: ClientConnection,
      interaction_id: Optional[str] = None,
      *,
      event_parser: Optional[Callable[[dict[str, Any]], TServerEvent]] = None,
  ) -> None:
    """Initializes the connection wrapper around an open WebSocket."""
    self._websocket = websocket
    self.id = interaction_id
    self._event_parser = event_parser
    self._terminal = False
    self._detached = False
    self._receiving = False
    self._connection_error = False
    self._socket_closed = False
    self._recv_task: Optional[asyncio.Future[Any]] = None
    self._recv_cancelled_by_session = False
    self._pending_events: deque[dict[str, Any]] = deque()

  async def _close_socket_only(self) -> None:
    """Closes the underlying WebSocket without marking the session detached or clearing buffered events."""
    if self._socket_closed:
      return
    self._socket_closed = True
    try:
      await self._websocket.close()
    except Exception:  # pylint: disable=broad-exception-caught
      pass

  def _end_receive_wait(self) -> None:
    """Cancels an in-flight WebSocket recv task when the session terminates or detaches."""
    if self._recv_task is not None and not self._recv_task.done():
      self._recv_cancelled_by_session = True
      self._recv_task.cancel()

  async def _send_payload(self, payload: dict[str, Any]) -> None:
    """Sends a JSON-serialized payload dict over the WebSocket."""
    try:
      await self._websocket.send(json.dumps(payload, separators=(',', ':')))
    except ConnectionClosed as error:
      await self._close_socket_only()
      raise self._redacted_connection_error(error) from None

  def _redacted_connection_error(
      self, error: ConnectionClosed
  ) -> APIWebSocketError:
    """Wraps a `ConnectionClosed` exception into an `APIWebSocketError` without leaking the close reason."""
    self._connection_error = True
    return _closed_websocket_error(_safe_close_code(error))

  def _ensure_active(self) -> None:
    """Raises `RuntimeError` if the interaction is terminal or detached."""
    if self._terminal:
      raise RuntimeError('This live interaction is already terminal.')
    if self._detached:
      raise RuntimeError('This live interaction is detached.')

  async def send(
      self,
      input: Union[  # pylint: disable=redefined-builtin
          str,
          TClientEvent,
          Mapping[str, Any],
          Sequence[Union[TClientEvent, Mapping[str, Any]]],
      ],
  ) -> None:
    """Sends text, one ClientEvent, or a list of ClientEvents."""
    self._ensure_active()
    payload = _serialize_client_payload(input)
    if payload.get('events') == []:
      raise ValueError('Empty client event batch.')
    await self._send_payload(payload)
    if _payload_has_cancel(payload):
      self._terminal = True
      self._end_receive_wait()
      await self._close_socket_only()

  async def _fill_pending_events(self) -> bool:
    """Reads WebSocket frames into `_pending_events` until at least one event is queued."""
    while not self._pending_events:
      if self._terminal or self._detached:
        return False
      recv_task = asyncio.ensure_future(self._websocket.recv())
      self._recv_task = recv_task
      self._recv_cancelled_by_session = False
      try:
        raw = await recv_task
      except asyncio.CancelledError:
        current_task = asyncio.current_task()
        if (
            self._recv_cancelled_by_session
            and (self._terminal or self._detached)
            and getattr(current_task, 'cancelling', lambda: 0)() == 0
        ):
          return False
        raise
      except ConnectionClosed as error:
        self._connection_error = True
        await self._close_socket_only()
        if self._terminal or self._detached:
          return False
        raise self._redacted_connection_error(error) from None
      finally:
        self._recv_task = None
      if self._terminal or self._detached:
        return False
      self._pending_events.extend(_frame_events(raw))
    return True

  async def receive(self) -> AsyncIterator[TServerEvent]:
    """Yields generated server events until the interaction completes or detaches."""
    try:
      while not self._detached:
        if self._receiving:
          raise RuntimeError(
              'Only one receive iterator may be active at a time.'
          )
        # Scope to _fill_pending_events(): Python async-for break/anext() does
        # not synchronously close generators.
        self._receiving = True
        try:
          has_events = await self._fill_pending_events()
        finally:
          self._receiving = False
        if not has_events:
          return
        event = self._pending_events.popleft()
        terminal = event['event_type'] in _TERMINAL_EVENTS
        if terminal:
          self._terminal = True
          self._pending_events.clear()
          await self._close_socket_only()
        yield (
            self._event_parser(event)
            if self._event_parser is not None
            else cast(TServerEvent, event)
        )
        if terminal or self._detached:
          return
    except APIWebSocketError as error:
      if error.close_code is None:
        self._pending_events.clear()
        await self._close_transport()
      raise

  async def complete(self) -> None:
    """Requests completion while leaving the socket open for acknowledgement."""
    if self._terminal:
      return
    if self._detached:
      raise RuntimeError('This live interaction is detached.')
    await self._send_payload({'event_type': 'interaction.complete'})

  async def cancel(self) -> None:
    """Cancels inference on the server."""
    if self._terminal:
      return
    if self._detached:
      raise RuntimeError('This live interaction is detached.')
    await self._send_payload({'event_type': 'interaction.cancel'})
    self._terminal = True
    self._end_receive_wait()
    await self._close_socket_only()

  async def _close_transport(self) -> None:
    """Marks the connection as detached, clears buffered events, and closes the WebSocket."""
    self._detached = True
    self._pending_events.clear()
    self._end_receive_wait()
    await self._close_socket_only()

  async def detach(self) -> None:
    """Gracefully detaches from the interaction without completing it."""
    if self._detached:
      return
    send_disconnect = not self._terminal and not self._connection_error
    self._detached = True
    self._pending_events.clear()
    self._end_receive_wait()
    if send_disconnect:
      try:
        await self._send_payload({'event_type': 'interaction.disconnect'})
      except Exception:  # pylint: disable=broad-exception-caught
        pass
    await self._close_socket_only()


class InteractionWebSocketConnectionContext(
    Awaitable[InteractionWebSocketConnection[TClientEvent, TServerEvent]],
    Generic[TClientEvent, TServerEvent],
):
  """Async context manager that connects to an existing live interaction.

  Experimental: Live Interactions SDK support is experimental and may change
  in future versions.

  Exiting `async with` detaches the local WebSocket without ending the
  server-side interaction. Call `complete()` (and drain `receive()` for
  `interaction.completed`) or `cancel()` to finish or abort the
  interaction on the server.
  """

  def __init__(
      self,
      api_client: Any,
      id: str,  # pylint: disable=redefined-builtin
      *,
      api_version: Optional[str] = None,
      extra_headers: Optional[Mapping[str, str]] = None,
      timeout: float = 30.0,
      api_revision: Optional[str] = None,
      event_parser: Optional[Callable[[dict[str, Any]], TServerEvent]] = None,
  ) -> None:
    """Configures the context manager with connection parameters and validates inputs."""
    _warn_live_interactions_experimental(stacklevel=2)
    if getattr(api_client, 'vertexai', False) is True:
      raise ValueError('Live Interactions is currently Gemini API only.')
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 0 < timeout < float('inf')
    ):
      raise ValueError('timeout must be positive and finite.')
    interaction_id = _interaction_id(id)
    self._timeout = timeout
    self._api_client = api_client
    self._initial_event: dict[str, Any] = {
        'event_type': 'interaction.connect',
        'id': interaction_id,
    }
    self._interaction_id = interaction_id
    self._api_version = api_version
    self._extra_headers = extra_headers
    self._api_revision = api_revision
    self._event_parser = event_parser
    if 'additional_headers' in _websocket_transport_kwargs(api_client):
      raise ValueError(
          "WebSocket client arguments cannot supply 'additional_headers'; "
          'use extra_headers to add request headers.'
      )
    self._connection: Any = None
    self._session: Optional[
        InteractionWebSocketConnection[TClientEvent, TServerEvent]
    ] = None

  async def _connect(self) -> ClientConnection:
    """Opens the underlying `websockets` connection and returns the `ClientConnection`."""
    url = _websocket_url(self._api_client, self._api_version)
    kwargs = _websocket_transport_kwargs(self._api_client)
    if not url.startswith('wss://'):
      kwargs.pop('ssl', None)
    kwargs.setdefault('open_timeout', self._timeout)
    kwargs['additional_headers'] = await _websocket_headers(
        self._api_client,
        self._extra_headers,
        self._api_revision,
    )
    self._connection = ws_connect(url, **kwargs)
    conn: ClientConnection = await self._connection.__aenter__()
    return conn

  async def _open(
      self,
  ) -> InteractionWebSocketConnection[TClientEvent, TServerEvent]:
    """Establishes the WebSocket connection, sends the initial event, and returns the session."""
    if self._session is not None:
      return self._session
    session: Optional[
        InteractionWebSocketConnection[TClientEvent, TServerEvent]
    ] = None
    failure: Optional[APIWebSocketError] = None

    async def establish() -> None:
      nonlocal session
      websocket = await self._connect()
      session = InteractionWebSocketConnection(
          websocket,
          self._interaction_id,
          event_parser=self._event_parser,
      )
      await session._send_payload(self._initial_event)  # pylint: disable=protected-access

    try:
      await asyncio.wait_for(establish(), timeout=self._timeout)
      assert session is not None
      self._session = session
      return session
    except (asyncio.CancelledError, ValueError):
      raise
    except APIWebSocketError as error:
      failure = (
          APIWebSocketError(
              'The connection closed during live setup.',
              close_code=error.close_code,
          )
          if error.close_code is not None
          else error
      )
    except ConnectionClosed as error:
      failure = APIWebSocketError(
          'The connection closed during live setup.',
          close_code=_safe_close_code(error),
      )
    except asyncio.TimeoutError:
      failure = APIWebSocketError(
          'Timed out establishing live interaction connection.'
      )
    except Exception as error:  # pylint: disable=broad-exception-caught
      response = getattr(error, 'response', None)
      status = getattr(response, 'status_code', None)
      failure = APIWebSocketError(
          'The live interaction setup failed.',
          http_status=status if isinstance(status, int) else None,
      )
    finally:
      if self._session is None:
        if session is not None:
          await session._close_transport()  # pylint: disable=protected-access
        if self._connection is not None:
          try:
            await self._connection.__aexit__(None, None, None)
          except Exception:  # pylint: disable=broad-exception-caught
            pass
          self._connection = None
    assert failure is not None
    raise failure from None

  def __await__(
      self,
  ) -> Generator[
      Any, None, InteractionWebSocketConnection[TClientEvent, TServerEvent]
  ]:
    """Allows `await context` as a shorthand for `await context._open()`."""
    return self._open().__await__()

  async def __aenter__(
      self,
  ) -> InteractionWebSocketConnection[TClientEvent, TServerEvent]:
    """Enters the async context manager by opening the connection."""
    return await self._open()

  async def __aexit__(
      self, exc_type: Any, exc: Any, traceback: Any
  ) -> Optional[bool]:
    """Exits the async context manager by detaching from the interaction."""
    if self._session is not None:
      await self._session.detach()

    if self._connection is not None:
      result: Optional[bool] = await self._connection.__aexit__(
          exc_type, exc, traceback
      )
      return result
    return False
