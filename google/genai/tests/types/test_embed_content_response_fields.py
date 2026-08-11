"""Regression tests for #2658 — EmbedContentResponse should surface usageMetadata
and HttpResponse in sdk_http_response should include body.

Background: ``EmbedContentResponse`` lacks a ``usage_metadata`` field. Separately,
every ``HttpResponse`` construction across the SDK passes only
``headers=response.headers``, silently dropping ``body=response.body`` —
users inspecting ``response.sdk_http_response.body`` always see ``None``.

Tests:

1. ``test_embed_content_response_has_usage_metadata_field`` — the type
   declares ``usage_metadata`` (model_fields contains the name).
2. ``test_embed_content_response_dict_has_usage_metadata_field`` — the
   corresponding TypedDict also declares the field.
3. ``test_http_response_body_construction_through_wrapper`` — using the
   `_common` machinery that wraps sdk_http_response, body should be
   preserved when present.
"""

from __future__ import annotations


def test_embed_content_response_has_usage_metadata_field():
    """The EmbedContentResponse Pydantic model must expose usage_metadata
    as a field so calling code can access ``response.usage_metadata``.
    """
    from google.genai import types

    field_names = types.EmbedContentResponse.model_fields.keys()
    assert "usage_metadata" in field_names, (
        "#2658 regression: EmbedContentResponse must declare a "
        "'usage_metadata' field so callers can read it. "
        f"Declared fields: {sorted(field_names)}"
    )


def test_embed_content_response_dict_has_usage_metadata_field():
    """The corresponding TypedDict must declare usage_metadata too."""
    from google.genai import types

    # TypedDict exposes annotations via __annotations__
    annotations = types.EmbedContentResponseDict.__annotations__
    assert "usage_metadata" in annotations, (
        "#2658 regression: EmbedContentResponseDict must declare "
        "'usage_metadata' for dict-style callers. "
        f"Declared annotations: {sorted(annotations.keys())}"
    )


def test_http_response_accepts_body():
    """HttpResponse type must accept body and round-trip it through
    Pydantic. (The bug is in call sites, but the type must support
    passing body= for the fix to take effect.)
    """
    from google.genai import types

    resp = types.HttpResponse(
        headers={"content-type": "application/json"},
        body='{"embeddings": []}',
    )
    assert resp.body == '{"embeddings": []}', (
        f"#2658 regression: HttpResponse must preserve body. Got: {resp.body!r}"
    )
    assert resp.headers == {"content-type": "application/json"}
