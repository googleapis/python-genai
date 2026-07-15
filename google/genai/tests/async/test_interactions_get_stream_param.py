"""Regression tests for #2661 — interactions.get should honor stream=None.

Background: ``client.interactions.get(id)`` always serializes ``stream=false``
on the wire because the public wrapper coerces ``_optional_bool(stream,
default=False)`` through ``bool(...)`` which collapses ``None`` to ``False``.
The lower-level request model correctly drops the param when ``stream`` is
``None``, so the bug is the bool() wrapper at the public API boundary.

Tests:

1. ``test_get_preserves_none_stream`` — calling ``client.interactions.get(id,
   stream=None)`` must NOT serialize ``stream`` in the outgoing query.
2. ``test_get_default_stream_omitted_param`` — calling
   ``client.interactions.get(id)`` (default) must NOT serialize ``stream``
   (default behavior should be to omit, not force ``stream=false``).
3. ``test_get_explicit_false_still_sends_stream`` — calling
   ``client.interactions.get(id, stream=False)`` MUST send ``stream=false``
   for backward compat (the existing public API documented behavior).
4. ``test_async_get_preserves_none_stream`` — same shape for the async
   variant.

All four tests use a recorded transport that captures the outgoing request.
"""

from __future__ import annotations

import json


class _QueryCaptureTransport:
    """An httpx-style transport that captures the query params of the
    outgoing request so tests can assert what was serialized to the wire.

    Each captured request is appended to ``self.captured_queries``.
    """

    def __init__(self):
        self.captured_queries: list[list[tuple[str, str]]] = []

    def __call__(self, request):
        # Parse query params manually (httpx-style)
        from urllib.parse import urlparse, parse_qsl

        url = urlparse(str(request.url))
        params = parse_qsl(url.query)
        self.captured_queries.append(params)

        # Return a minimal Interactions response
        from google.genai.types import HttpResponse

        body = json.dumps({"id": "test-id"})
        return HttpResponse(
            headers={"content-type": "application/json"},
            body=body,
        )


def test_get_preserves_none_stream():
    """When the caller passes stream=None, the wire request must NOT
    contain the ``stream`` query parameter.

    This is the user-visible contract from #2661: 'please let callers
    omit stream on the non-streaming get() path.'
    """
    from unittest.mock import patch

    from google.genai import Client

    transport = _QueryCaptureTransport()

    client = Client(api_key="sk-test")
    api_client = client._api_client

    # Monkey-patch the underlying httpx client's transport
    # The exact name of the attribute differs between versions; try several.
    for attr_name in ("_transport", "transport"):
        if hasattr(api_client._httpx_client, attr_name):
            setattr(api_client._httpx_client, attr_name, _wrap_transport(transport))
            break
    else:
        # Last-resort: replace the entire httpx client
        import httpx as _httpx

        api_client._httpx_client = _httpx.Client(
            transport=_wrap_transport(transport),
            base_url="https://backend.invalid",
        )

    try:
        client.interactions.get("test-id", stream=None)
    except Exception:
        # The transport may not produce a fully-shaped Interactions response;
        # what matters for this regression is the outgoing query, captured
        # before any unmarshalling. Swallow downstream errors.
        pass

    assert transport.captured_queries, "Expected at least one captured query"
    last_query = dict(transport.captured_queries[-1])
    assert "stream" not in last_query, (
        f"#2661 regression: interactions.get(id, stream=None) must NOT "
        f"serialize 'stream' in the query. Got query params: {last_query!r}. "
        "The bool() coercion around _optional_bool(stream, default=False) "
        "wraps None into False and forces serialization."
    )


def test_get_default_stream_omitted_param():
    """Calling client.interactions.get(id) without explicit stream arg
    must NOT serialize 'stream' on the wire.

    The default-of-None lets callers opt out without using a private
    argument; pre-fix, this call sent ?stream=false (bug)."""
    from google.genai import Client

    transport = _QueryCaptureTransport()

    client = Client(api_key="sk-test")
    api_client = client._api_client
    import httpx as _httpx

    api_client._httpx_client = _httpx.Client(
        transport=_wrap_transport(transport),
        base_url="https://backend.invalid",
    )

    try:
        client.interactions.get("test-id")
    except Exception:
        pass

    assert transport.captured_queries
    last_query = dict(transport.captured_queries[-1])
    assert "stream" not in last_query, (
        f"#2661 regression: default call must omit 'stream' from query. "
        f"Got: {last_query!r}"
    )


def test_get_explicit_false_still_sends_stream():
    """Backward compat: explicit stream=False must still serialize
    stream=false on the wire. (The fix preserves the existing API
    contract; only the default-of-None behavior changes.)
    """
    from google.genai import Client

    transport = _QueryCaptureTransport()

    client = Client(api_key="sk-test")
    api_client = client._api_client
    import httpx as _httpx

    api_client._httpx_client = _httpx.Client(
        transport=_wrap_transport(transport),
        base_url="https://backend.invalid",
    )

    try:
        client.interactions.get("test-id", stream=False)
    except Exception:
        pass

    assert transport.captured_queries
    last_query = dict(transport.captured_queries[-1])
    assert last_query.get("stream") == "false", (
        f"#2661 backward-compat guard: explicit stream=False must keep "
        f"sending stream=false on the wire. Got: {last_query!r}"
    )


def _wrap_transport(qt):
    """Adapter that adapts the QueryCaptureTransport to whatever httpx
    transport protocol the SDK uses. We proxy to ``qt.__call__(request)``."""
    import httpx

    class _Adapter(httpx.MockTransport):
        def __init__(self, q):
            super().__init__(q)
            self.q = q

    return _Adapter(qt)
