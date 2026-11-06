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

import copy
import pickle

import httpx
import pytest

try:
  import httpx2
except ImportError:
  httpx2 = None

from ... import _interactions  # pylint: disable=g-import-not-at-top
from ... import client as client_lib  # pylint: disable=g-import-not-at-top
from ... import errors  # pylint: disable=g-import-not-at-top
from ... import interactions  # pylint: disable=g-import-not-at-top
from ..._gaos.basesdk import AsyncBaseSDK, BaseSDK  # pylint: disable=g-import-not-at-top,g-multiple-import
from ..._gaos.errors.genaierror import GenAiError  # pylint: disable=g-import-not-at-top
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
def test_injected_httpx2_client_passed_to_gaos():
  http_client = httpx2.Client()
  try:
    client = client_lib.Client(
        api_key="fake-key",
        http_options={"httpx_client": http_client},
    )

    assert client._api_client._httpx_client is http_client
    interactions_client = client.interactions
    assert interactions_client.sdk_configuration.client is http_client
    assert isinstance(interactions_client.sdk_configuration.client, httpx2.Client)
  finally:
    http_client.close()


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_env_var_httpx2_passed_to_gaos(monkeypatch):
  monkeypatch.setenv("GOOGLE_GENAI_HTTP_CLIENT", "httpx2")
  client = client_lib.Client(api_key="fake-key")
  assert isinstance(client._api_client._httpx_client, httpx2.Client)
  interactions_client = client.interactions
  assert interactions_client.sdk_configuration.client is client._api_client._httpx_client
  assert isinstance(interactions_client.sdk_configuration.client, httpx2.Client)


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
@pytest.mark.asyncio
async def test_injected_httpx2_async_client_passed_to_gaos():
  http_async_client = httpx2.AsyncClient()
  try:
    client = client_lib.Client(
        api_key="fake-key",
        http_options={"httpx_async_client": http_async_client},
    )

    assert client._api_client._async_httpx_client is http_async_client
    interactions_client = client.aio.interactions
    assert interactions_client.sdk_configuration.async_client is http_async_client
    assert isinstance(interactions_client.sdk_configuration.async_client, httpx2.AsyncClient)
  finally:
    await http_async_client.aclose()


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_env_var_httpx2_async_passed_to_gaos(monkeypatch):
  monkeypatch.setenv("GOOGLE_GENAI_HTTP_CLIENT", "httpx2")
  client = client_lib.Client(api_key="fake-key")
  assert isinstance(client._api_client._async_httpx_client, httpx2.AsyncClient)
  interactions_client = client.aio.interactions
  assert interactions_client.sdk_configuration.async_client is client._api_client._async_httpx_client
  assert isinstance(interactions_client.sdk_configuration.async_client, httpx2.AsyncClient)


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


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_interactions_create_with_httpx2_mock_transport():
  recorded_requests = []

  def handler(request: httpx2.Request) -> httpx2.Response:
    recorded_requests.append(request)
    return httpx2.Response(
        200,
        headers={"content-type": "application/json"},
        content=b'{"id": "test-interaction-id", "status": "completed"}',
    )

  http_client = httpx2.Client(transport=httpx2.MockTransport(handler))
  try:
    client = client_lib.Client(
        api_key="fake-key",
        http_options={"httpx_client": http_client},
    )
    result = client.interactions.create(
        model="gemini-1.5-flash",
        input="Hello from httpx2",
    )
    assert len(recorded_requests) == 1
    assert recorded_requests[0].method == "POST"
    assert "/interactions" in str(recorded_requests[0].url)
    assert result.status == "completed"
  finally:
    http_client.close()


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
@pytest.mark.asyncio
async def test_async_interactions_create_with_httpx2_mock_transport():
  recorded_requests = []

  def handler(request: httpx2.Request) -> httpx2.Response:
    recorded_requests.append(request)
    return httpx2.Response(
        200,
        headers={"content-type": "application/json"},
        content=b'{"id": "test-interaction-async-id", "status": "completed"}',
    )

  http_async_client = httpx2.AsyncClient(
      transport=httpx2.MockTransport(handler)
  )
  try:
    client = client_lib.Client(
        api_key="fake-key",
        http_options={"httpx_async_client": http_async_client},
    )
    result = await client.aio.interactions.create(
        model="gemini-1.5-flash",
        input="Hello from async httpx2",
    )
    assert len(recorded_requests) == 1
    assert recorded_requests[0].method == "POST"
    assert "/interactions" in str(recorded_requests[0].url)
    assert result.status == "completed"
  finally:
    await http_async_client.aclose()


@pytest.mark.skipif(
    httpx2 is None, reason="httpx2 not installed in this environment"
)
def test_interactions_create_env_var_httpx2_mock_transport(monkeypatch):
  monkeypatch.setenv("GOOGLE_GENAI_HTTP_CLIENT", "httpx2")
  recorded_requests = []

  def handler(request: httpx2.Request) -> httpx2.Response:
    recorded_requests.append(request)
    return httpx2.Response(
        200,
        headers={"content-type": "application/json"},
        content=b'{"id": "test-interaction-env-id", "status": "completed"}',
    )

  client = client_lib.Client(
      api_key="fake-key",
      http_options={"client_args": {"transport": httpx2.MockTransport(handler)}},
  )
  result = client.interactions.create(
      model="gemini-1.5-flash",
      input="Hello from env var httpx2",
  )
  assert len(recorded_requests) == 1
  assert isinstance(recorded_requests[0], httpx2.Request)
  assert result.status == "completed"


# --- Error hierarchy unification tests (b/577987345) ---


@pytest.mark.parametrize(
    "compat_cls, expected_native",
    [
        (compat_errors.APIStatusError, errors.APIError),
        (compat_errors.BadRequestError, errors.ClientError),
        (compat_errors.AuthenticationError, errors.ClientError),
        (compat_errors.PermissionDeniedError, errors.ClientError),
        (compat_errors.NotFoundError, errors.ClientError),
        (compat_errors.ConflictError, errors.ClientError),
        (compat_errors.UnprocessableEntityError, errors.ClientError),
        (compat_errors.RateLimitError, errors.ClientError),
        (compat_errors.InternalServerError, errors.ServerError),
    ],
)
def test_compat_status_errors_subclass_native_errors(
    compat_cls, expected_native
):
  """Tests that status-bearing compat errors subclass native errors."""
  assert issubclass(compat_cls, expected_native)
  assert issubclass(compat_cls, errors.APIError)
  assert issubclass(compat_cls, compat_errors.APIError)
  assert issubclass(compat_cls, compat_errors.GeminiNextGenAPIClientError)
  if expected_native is errors.ClientError:
    assert not issubclass(compat_cls, errors.ServerError)
  elif expected_native is errors.ServerError:
    assert not issubclass(compat_cls, errors.ClientError)


@pytest.mark.parametrize(
    "compat_cls",
    [
        compat_errors.GeminiNextGenAPIClientError,
        compat_errors.APIError,
        compat_errors.APIConnectionError,
        compat_errors.APITimeoutError,
        compat_errors.APIResponseValidationError,
    ],
)
def test_non_status_compat_errors_do_not_subclass_native_api_error(compat_cls):
  """Tests that non-status compat errors do not subclass native APIError."""
  assert not issubclass(compat_cls, errors.APIError)


def test_compat_errors_exported_on_interactions_and_errors_entrypoints():
  """Tests that compat errors are exported on interactions and errors."""
  for name in (
      "APIConnectionError",
      "APIResponseValidationError",
      "APIStatusError",
      "APITimeoutError",
      "AuthenticationError",
      "BadRequestError",
      "ConflictError",
      "GeminiNextGenAPIClientError",
      "InternalServerError",
      "NotFoundError",
      "PermissionDeniedError",
      "RateLimitError",
      "UnprocessableEntityError",
  ):
    assert getattr(interactions, name) is getattr(compat_errors, name)
    assert getattr(_interactions, name) is getattr(compat_errors, name)
    assert getattr(errors, name) is getattr(compat_errors, name)
  assert interactions.APIError is compat_errors.APIError
  assert _interactions.APIError is compat_errors.APIError
  assert errors.InteractionsAPIError is compat_errors.APIError


def test_wrap_sdk_error_populates_native_api_error_fields_and_roundtrips():
  """Tests native field population and copy/pickle roundtripping."""
  req = httpx.Request("POST", "https://example.com/v1beta/interactions")
  raw_body = (
      '{"error": {"code": 400, "message": "bad model",'
      ' "status": "INVALID_ARGUMENT"}}'
  )
  resp = httpx.Response(
      400,
      request=req,
      headers={"content-type": "application/json"},
      text=raw_body,
  )
  sdk_err = GenAiError("API error occurred", resp, raw_body)

  with pytest.raises(errors.ClientError) as exc_info:
    raise compat_errors.wrap_sdk_error(sdk_err)

  err = exc_info.value
  assert isinstance(err, compat_errors.BadRequestError)
  assert isinstance(err, errors.APIError)
  assert err.status_code == 400
  assert err.code == 400
  assert err.status == "INVALID_ARGUMENT"
  assert err.details == {
      "error": {
          "code": 400,
          "message": "bad model",
          "status": "INVALID_ARGUMENT",
      }
  }
  assert err.body == err.details
  assert err.response is resp
  assert err.message.startswith("Error code: 400 - ")
  assert str(err) == err.message

  unpickled = pickle.loads(pickle.dumps(err))  # pylint: disable=g-unsafe-pickle-load
  for clone in (copy.copy(err), copy.deepcopy(err), unpickled):
    assert clone.__class__ is compat_errors.BadRequestError
    assert clone.status_code == 400
    assert clone.code == 400
    assert clone.status == "INVALID_ARGUMENT"
    assert clone.details == err.details
    assert clone.message == err.message
    assert str(clone) == str(err)


def test_unmapped_4xx_status_caught_by_native_client_error():
  """Tests that unmapped 4xx status codes are caught by native ClientError."""
  req = httpx.Request("POST", "https://example.com/v1beta/interactions")
  resp = httpx.Response(413, request=req, text="Payload too large")
  sdk_err = GenAiError("API error occurred", resp, "Payload too large")

  with pytest.raises(errors.ClientError) as exc_info:
    raise compat_errors.wrap_sdk_error(sdk_err)

  err = exc_info.value
  assert isinstance(err, compat_errors.APIStatusError)
  assert not isinstance(err, errors.ServerError)
  assert err.status_code == 413
  assert err.code == 413
  assert err.details == {
      "message": "Payload too large",
      "status": "Request Entity Too Large",
  }
  unpickled = pickle.loads(pickle.dumps(err))  # pylint: disable=g-unsafe-pickle-load
  assert isinstance(unpickled, errors.ClientError)
  assert isinstance(unpickled, compat_errors.APIStatusError)
  assert unpickled.code == 413
