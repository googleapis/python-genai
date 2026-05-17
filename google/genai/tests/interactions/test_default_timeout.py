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

"""Tests for default timeout behavior of the interactions client.

When no timeout is configured in http_options, the wrapper must pass
NOT_GIVEN to the Stainless client so it falls back to DEFAULT_TIMEOUT
(60s).  Previously it passed None, which httpx interprets as "no timeout"
causing requests to hang indefinitely.
"""

from unittest import mock

import pytest

from ... import client as client_lib
from ..._interactions._types import NotGiven

pytest_plugins = ("pytest_asyncio",)


class TestSyncDefaultTimeout:
  """Sync client default timeout tests."""

  def test_default_timeout_is_not_given(self):
    """When no timeout is set, NOT_GIVEN (not None) should be passed."""
    with mock.patch.object(
        client_lib, "GeminiNextGenAPIClient", spec_set=True
    ) as mock_nextgen_client:
      client = client_lib.Client(
          api_key="placeholder",
          http_options={"api_version": "v1alpha"},
      )
      _ = client.interactions

      timeout_arg = mock_nextgen_client.call_args.kwargs["timeout"]
      assert isinstance(timeout_arg, NotGiven), (
          f"Expected timeout to be NOT_GIVEN but got {timeout_arg!r}. "
          f"None would disable httpx timeouts entirely."
      )

  def test_explicit_timeout_passes_through(self):
    """When timeout is set, it should pass through as seconds (ms / 1000)."""
    with mock.patch.object(
        client_lib, "GeminiNextGenAPIClient", spec_set=True
    ) as mock_nextgen_client:
      client = client_lib.Client(
          api_key="placeholder",
          http_options={"api_version": "v1alpha", "timeout": 30000},
      )
      _ = client.interactions

      mock_nextgen_client.assert_called_once_with(
          base_url=mock.ANY,
          api_key="placeholder",
          api_version="v1alpha",
          default_headers=mock.ANY,
          http_client=mock.ANY,
          timeout=30.0,
          max_retries=mock.ANY,
          client_adapter=mock.ANY,
      )

  def test_no_http_options_uses_not_given(self):
    """When no http_options at all, timeout should still be NOT_GIVEN."""
    with mock.patch.object(
        client_lib, "GeminiNextGenAPIClient", spec_set=True
    ) as mock_nextgen_client:
      client = client_lib.Client(api_key="placeholder")
      _ = client.interactions

      timeout_arg = mock_nextgen_client.call_args.kwargs["timeout"]
      assert isinstance(timeout_arg, NotGiven), (
          f"Expected timeout to be NOT_GIVEN but got {timeout_arg!r}."
      )


class TestAsyncDefaultTimeout:
  """Async client default timeout tests."""

  @pytest.mark.asyncio
  async def test_default_timeout_is_not_given(self):
    """When no timeout is set, NOT_GIVEN (not None) should be passed."""
    with mock.patch.object(
        client_lib, "AsyncGeminiNextGenAPIClient", spec_set=True
    ) as mock_nextgen_client:
      client = client_lib.Client(
          api_key="placeholder",
          http_options={"api_version": "v1alpha"},
      )
      _ = client.aio.interactions

      timeout_arg = mock_nextgen_client.call_args.kwargs["timeout"]
      assert isinstance(timeout_arg, NotGiven), (
          f"Expected timeout to be NOT_GIVEN but got {timeout_arg!r}. "
          f"None would disable httpx timeouts entirely."
      )

  @pytest.mark.asyncio
  async def test_explicit_timeout_passes_through(self):
    """When timeout is set, it should pass through as seconds (ms / 1000)."""
    with mock.patch.object(
        client_lib, "AsyncGeminiNextGenAPIClient", spec_set=True
    ) as mock_nextgen_client:
      client = client_lib.Client(
          api_key="placeholder",
          http_options={"api_version": "v1alpha", "timeout": 30000},
      )
      _ = client.aio.interactions

      mock_nextgen_client.assert_called_once_with(
          base_url=mock.ANY,
          api_key="placeholder",
          api_version="v1alpha",
          default_headers=mock.ANY,
          http_client=mock.ANY,
          timeout=30.0,
          max_retries=mock.ANY,
          client_adapter=mock.ANY,
      )
