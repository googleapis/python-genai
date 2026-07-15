"""Regression tests for #2527 — AsyncLiveSession.receive() should drain
trailing sessionResumptionUpdate messages after turnComplete,
not break out of the loop and drop them.

Background: ``AsyncSession.receive()`` in google/genai/live.py:444 has a
``while result := await self._receive()`` loop that yields and breaks
the moment a server message has ``server_content.turn_complete = True``.
If the server then sends a final ``sessionResumptionUpdate`` (a common
race during server-side routing), the SDK swallows it.

User workaround: call receive() again. That's fragile. The SDK should
drain trailing non-content updates before terminating.
"""

from __future__ import annotations

import json

import pytest


def _build_session_with_ws(ws, *, vertexai=False):
    """Build an AsyncSession with a controlled websocket mock.

    Avoids touching real auth/network.
    """
    from unittest.mock import MagicMock

    from google.genai import _api_client
    from google.genai import live as live_module

    api_client_inst = _api_client.BaseApiClient(
        vertexai=vertexai, api_key="sk-test"
    )
    api_client_inst.api_key = "sk-test"
    api_client_inst.vertexai = vertexai

    session = live_module.AsyncSession.__new__(live_module.AsyncSession)
    session._api_client = api_client_inst
    session._ws = ws
    return session


def _build_ws_with_messages(messages_json):
    """WebSocket mock whose recv() yields each JSON message in order then
    yields "" (close sentinel) on the next call."""
    from unittest.mock import AsyncMock

    from websockets.exceptions import ConnectionClosed

    ws = AsyncMock()
    ws.send = AsyncMock()

    iter_messages = iter(list(messages_json) + [None])  # None = close

    async def _recv(*args, **kwargs):
        try:
            item = next(iter_messages)
        except StopIteration:
            # Return empty string to match the receive() code path's
            # `if raw_response:` falsy branch.
            raise ConnectionClosed(rcvd=None)  # Forces exit

        if item is None:
            # Treat as connection-close
            raise ConnectionClosed(rcvd=None)
        return item

    ws.recv = _recv
    ws.close = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_receive_drains_trailing_session_resumption_update():
    """Regression for #2527: receive() yields BOTH turnComplete
    AND the trailing sessionResumptionUpdate.
    """
    turn_complete_msg = json.dumps({
        "serverContent": {"turnComplete": True},
    })
    session_resume_msg = json.dumps({
        "sessionResumptionUpdate": {
            "resumable": True,
            "newHandle": "test-handle-abc123",
        },
    })
    ws = _build_ws_with_messages([turn_complete_msg, session_resume_msg])
    session = _build_session_with_ws(ws)

    messages = []
    async for msg in session.receive():
        messages.append(msg)
        # Safety net
        if len(messages) >= 5:
            break

    # turn_complete is always yielded
    turn_complete_msgs = [
        m for m in messages if m.server_content and m.server_content.turn_complete
    ]
    assert turn_complete_msgs, (
        f"Expected turn_complete message; got {[type(m).__name__ for m in messages]}"
    )

    # The trailing handle update must also be present
    handle_msgs = [m for m in messages if m.session_resumption_update]
    assert handle_msgs, (
        f"#2527 regression: trailing sessionResumptionUpdate was dropped "
        f"by receive(). Got {[type(m).__name__ for m in messages]}"
    )
    assert messages.index(handle_msgs[0]) > messages.index(turn_complete_msgs[0]), (
        f"Trailing handle should come after turn_complete. "
        f"Got order: {[type(m).__name__ for m in messages]}"
    )
    assert handle_msgs[0].session_resumption_update.new_handle == "test-handle-abc123"


@pytest.mark.asyncio
async def test_receive_no_trailing_update_yields_only_turn_complete():
    """Sanity guard: when there's no trailing update, receive() yields
    only turn_complete and exits cleanly.
    """
    turn_complete_msg = json.dumps({
        "serverContent": {"turnComplete": True},
    })
    ws = _build_ws_with_messages([turn_complete_msg])
    session = _build_session_with_ws(ws)

    messages = []
    async for msg in session.receive():
        messages.append(msg)
        if len(messages) >= 5:
            break

    assert len(messages) == 1
    assert messages[0].server_content and messages[0].server_content.turn_complete
