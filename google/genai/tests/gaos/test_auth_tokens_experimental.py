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
"""Tests for the interactions.auth_tokens wrapper and experimental warning."""

from __future__ import annotations

import json
import warnings

import pytest

from ... import _live_interactions_experimental
from ..._api_client import GOOGLE_AI_API_DEFAULT_VERSION as _API_VERSION
# Import through `_gaos` so `run_tests.sh --private` rewrites these to
# `_gaos_private` and the classes match the client under test.
from ..._gaos.google_genai import (
    AsyncGeminiNextGenAuthTokens,
    GeminiNextGenAuthTokens,
)
from ..._gaos.lib import compat_errors
from . import conftest

_WARNING_TEXT = "Live Interactions usage"
_TOKEN_BODY = {
    "auth_token": "auth_tokens/tok_123",
    "expires_at": "2026-10-23T17:00:00Z",
}


@pytest.fixture(autouse=True)
def _reset_experimental_warning(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setattr(
      _live_interactions_experimental,
      "_live_interactions_experimental_warned",
      False,
  )


def _live_warnings(
    recorded: list[warnings.WarningMessage],
) -> list[warnings.WarningMessage]:
  return [w for w in recorded if _WARNING_TEXT in str(w.message)]


def test_auth_tokens_warns_once_at_caller(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.default_response = _TOKEN_BODY
  auth_tokens = mock_gaos_server.client.interactions.auth_tokens
  assert isinstance(auth_tokens, GeminiNextGenAuthTokens)

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter("always")
    created = auth_tokens.create("int_001")
    mock_gaos_server.default_response = {}
    auth_tokens.delete("int_001", "tok_123")
    auth_tokens.create("int_001")

  assert created.auth_token == "auth_tokens/tok_123"
  live = _live_warnings(recorded)
  assert len(live) == 1
  assert live[0].category is UserWarning
  assert live[0].filename == __file__
  assert mock_gaos_server.captured[:2] == [
      f"POST /{_API_VERSION}/interactions/int_001/auth_tokens",
      f"DELETE /{_API_VERSION}/interactions/int_001/auth_tokens/tok_123",
  ]


@pytest.mark.asyncio
async def test_async_auth_tokens_warns_once_at_caller(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.default_response = _TOKEN_BODY
  auth_tokens = mock_gaos_server.client.aio.interactions.auth_tokens
  assert isinstance(auth_tokens, AsyncGeminiNextGenAuthTokens)

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter("always")
    await auth_tokens.create("int_001")
    mock_gaos_server.default_response = {}
    await auth_tokens.delete("int_001", "tok_123")

  live = _live_warnings(recorded)
  assert len(live) == 1
  assert live[0].category is UserWarning
  assert live[0].filename == __file__


def test_auth_tokens_translates_errors(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:

  def reject(
      unused_req: conftest.CapturedRequest,
      unused_server: conftest.MockGaosServer,
  ) -> conftest.RawHttpResponse:
    return conftest.RawHttpResponse(
        body=json.dumps({
            "error": {
                "code": 400,
                "message": "bad interaction",
                "status": "INVALID_ARGUMENT",
            }
        }).encode("utf-8"),
        status=400,
    )

  mock_gaos_server.handler_fn = reject
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    with pytest.raises(compat_errors.BadRequestError):
      mock_gaos_server.client.interactions.auth_tokens.create("int_bad")


def test_auth_tokens_raw_and_streaming_warn_once_at_caller(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.default_response = _TOKEN_BODY
  auth_tokens = mock_gaos_server.client.interactions.auth_tokens

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter("always")
    raw = auth_tokens.with_raw_response.create("int_001")
    assert raw.parse().auth_token == "auth_tokens/tok_123"
    mock_gaos_server.default_response = {}
    with auth_tokens.with_streaming_response.delete(
        "int_001", "tok_123"
    ) as response:
      assert response.status_code == 200

  live = _live_warnings(recorded)
  assert len(live) == 1
  assert live[0].filename == __file__


def test_auth_tokens_streaming_warns_first(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.default_response = {}
  auth_tokens = mock_gaos_server.client.interactions.auth_tokens

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter("always")
    with auth_tokens.with_streaming_response.delete(
        "int_001", "tok_123"
    ) as response:
      assert response.status_code == 200

  live = _live_warnings(recorded)
  assert len(live) == 1
  assert live[0].filename == __file__


@pytest.mark.asyncio
async def test_async_auth_tokens_raw_and_streaming_warn_once_at_caller(
    mock_gaos_server: conftest.MockGaosServer,
) -> None:
  mock_gaos_server.default_response = _TOKEN_BODY
  auth_tokens = mock_gaos_server.client.aio.interactions.auth_tokens

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter("always")
    raw = await auth_tokens.with_raw_response.create("int_001")
    assert raw.status_code == 200
    mock_gaos_server.default_response = {}
    async with auth_tokens.with_streaming_response.delete(
        "int_001", "tok_123"
    ) as response:
      assert response.status_code == 200

  live = _live_warnings(recorded)
  assert len(live) == 1
  assert live[0].filename == __file__
