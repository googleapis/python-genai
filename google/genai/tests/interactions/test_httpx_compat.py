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

"""Tests for httpx and httpx2 compatibility across the GAOS client."""

import httpx
import pytest

try:
  import httpx2
except ImportError:
  httpx2 = None

from ... import client as client_lib
from ..._gaos.basesdk import AsyncBaseSDK, BaseSDK
from ..._gaos.httpclient import AsyncHttpClient, HttpClient
from ..._gaos.lib import compat_errors
from ..._gaos.utils import eventstreaming, retries


# --- Standard httpx tests ---


def test_error_wrapping_httpx_errors():
  req = httpx.Request("GET", "https://example.com")
  err = httpx.ConnectError("failed to connect", request=req)
  wrapped = compat_errors.wrap_sdk_error(err)
  assert isinstance(wrapped, compat_errors.APIConnectionError)
  assert wrapped.__cause__ is err

  timeout_err = httpx.TimeoutException("timed out", request=req)
  wrapped_timeout = compat_errors.wrap_sdk_error(timeout_err)
  assert isinstance(wrapped_timeout, compat_errors.APITimeoutError)
  assert wrapped_timeout.__cause__ is timeout_err


def test_base_sdk_timeout_coercion():
  sdk = BaseSDK.__new__(BaseSDK)

  assert sdk._coerce_timeout_ms(None) is None
  assert sdk._coerce_timeout_ms(5) == 5000
  assert sdk._coerce_timeout_ms(2.5) == 2500
  assert (
      sdk._coerce_timeout_ms(
          httpx.Timeout(connect=1.0, read=4.0, write=2.0, pool=None)
      )
      == 4000
  )

  with pytest.raises(
      TypeError, match="timeout must be a float, int, httpx.Timeout, or None"
  ):
    sdk._coerce_timeout_ms("invalid_timeout")


def test_injected_client_passed_to_gaos():
  http_client = httpx.Client()
  try:
    client = client_lib.Client(
        api_key="fake-key",
        http_options={"httpx_client": http_client},
    )

    assert client._api_client._httpx_client is http_client
    interactions_client = client.interactions
    assert interactions_client.sdk_configuration.client is http_client
  finally:
    http_client.close()


def test_stream_error_wrapping_httpx_errors():
  def failing_gen():
    yield "chunk1"
    raise httpx.ConnectError("stream network broken")

  stream = eventstreaming.Stream.__new__(eventstreaming.Stream)
  stream.generator = failing_gen()
  wrapped_stream = compat_errors.wrap_stream_errors(stream)

  gen = wrapped_stream.generator
  assert next(gen) == "chunk1"
  with pytest.raises(compat_errors.APIConnectionError) as exc_info:
    next(gen)
  assert "stream network broken" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_stream_error_wrapping_httpx_errors():
  async def failing_agen():
    yield "async_chunk1"
    raise httpx.ConnectError("async stream network broken")

  stream = eventstreaming.AsyncStream.__new__(eventstreaming.AsyncStream)
  stream.generator = failing_agen()
  wrapped_stream = compat_errors.wrap_async_stream_errors(stream)

  agen = wrapped_stream.generator
  chunk = await agen.__anext__()
  assert chunk == "async_chunk1"
  with pytest.raises(compat_errors.APIConnectionError) as exc_info:
    await agen.__anext__()
  assert "async stream network broken" in str(exc_info.value)


# --- httpx2 tests (run in CI when httpx2 is installed) ---


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_httpx2_error_wrapping():
  req = httpx2.Request("GET", "https://example.com")
  err = httpx2.ConnectError("failed to connect", request=req)
  wrapped = compat_errors.wrap_sdk_error(err)
  assert isinstance(wrapped, compat_errors.APIConnectionError)
  assert wrapped.__cause__ is err

  timeout_err = httpx2.TimeoutException("timed out", request=req)
  wrapped_timeout = compat_errors.wrap_sdk_error(timeout_err)
  assert isinstance(wrapped_timeout, compat_errors.APITimeoutError)
  assert wrapped_timeout.__cause__ is timeout_err


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_httpx2_timeout_coercion():
  sdk = BaseSDK.__new__(BaseSDK)
  timeout = httpx2.Timeout(connect=1.0, read=4.0, write=2.0, pool=None)
  assert sdk._coerce_timeout_ms(timeout) == 4000

  async_sdk = AsyncBaseSDK.__new__(AsyncBaseSDK)
  assert async_sdk._coerce_timeout_ms(timeout) == 4000


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_httpx2_client_protocols():
  assert issubclass(httpx2.Client, HttpClient)
  assert issubclass(httpx2.AsyncClient, AsyncHttpClient)


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_httpx2_retries():
  attempts = 0

  def flaky_operation(_attempt):
    nonlocal attempts
    attempts += 1
    if attempts < 3:
      raise httpx2.NetworkError("temporary network error")
    return httpx2.Response(200, json={"status": "ok"})

  config = retries.RetryConfig(
      strategy="attempt-count-backoff",
      retry_connection_errors=True,
      backoff=retries.BackoffStrategy(
          initial_interval=1,
          max_interval=5,
          exponent=1.1,
          max_elapsed_time=100,
      ),
      max_retries=3,
  )
  res = retries.retry(flaky_operation, retries.Retries(config, ["5XX"]))
  assert res.status_code == 200
  assert attempts == 3


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
@pytest.mark.asyncio
async def test_httpx2_async_retries():
  attempts = 0

  async def flaky_async_operation(_attempt):
    nonlocal attempts
    attempts += 1
    if attempts < 3:
      raise httpx2.NetworkError("temporary async network error")
    return httpx2.Response(200, json={"status": "ok"})

  config = retries.RetryConfig(
      strategy="attempt-count-backoff",
      retry_connection_errors=True,
      backoff=retries.BackoffStrategy(
          initial_interval=1,
          max_interval=5,
          exponent=1.1,
          max_elapsed_time=100,
      ),
      max_retries=3,
  )
  res = await retries.retry_async(
      flaky_async_operation, retries.Retries(config, ["5XX"])
  )
  assert res.status_code == 200
  assert attempts == 3


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_httpx2_stream_error_wrapping():
  def failing_gen():
    yield "chunk1"
    raise httpx2.ConnectError("stream network broken")

  stream = eventstreaming.Stream.__new__(eventstreaming.Stream)
  stream.generator = failing_gen()
  wrapped_stream = compat_errors.wrap_stream_errors(stream)

  gen = wrapped_stream.generator
  assert next(gen) == "chunk1"
  with pytest.raises(compat_errors.APIConnectionError) as exc_info:
    next(gen)
  assert "stream network broken" in str(exc_info.value)


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
@pytest.mark.asyncio
async def test_httpx2_async_stream_error_wrapping():
  async def failing_agen():
    yield "async_chunk1"
    raise httpx2.ConnectError("async stream network broken")

  stream = eventstreaming.AsyncStream.__new__(eventstreaming.AsyncStream)
  stream.generator = failing_agen()
  wrapped_stream = compat_errors.wrap_async_stream_errors(stream)

  agen = wrapped_stream.generator
  chunk = await agen.__anext__()
  assert chunk == "async_chunk1"
  with pytest.raises(compat_errors.APIConnectionError) as exc_info:
    await agen.__anext__()
  assert "async stream network broken" in str(exc_info.value)
