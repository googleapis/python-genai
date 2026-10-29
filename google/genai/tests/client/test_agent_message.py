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

"""Tests for Agent-Message response header parsing and warning emission."""

from typing import cast
import warnings

import httpx
import pytest

from ... import _api_client
from ... import client as client_lib
from ..._gaos._hooks.asyncregistration import init_async_hooks
from ..._gaos._hooks.asyncsdkhooks import AsyncSDKHooks
from ..._gaos._hooks.asynctypes import AfterSuccessContext as AsyncAfterSuccessContext
from ..._gaos._hooks.google_genai_auth import GoogleGenAIAgentMessageHook
from ..._gaos._hooks.sdkhooks import SDKHooks
from ..._gaos._hooks.types import AfterErrorContext, AfterSuccessContext


@pytest.fixture(autouse=True)
def clear_seen_agent_messages():
  _api_client._SEEN_AGENT_MESSAGES.clear()
  yield
  _api_client._SEEN_AGENT_MESSAGES.clear()


def _message(w: warnings.WarningMessage) -> str:
  """Returns a recorded warning's text after checking and removing the prefix."""
  text = str(w.message)
  assert text.startswith('[Gemini API] '), text
  return text[len('[Gemini API] '):]


def test_parse_single_structured_item():
  header = (
      'field_ignored;field="temperature";'
      'msg=%"temperature is ignored by Gemini 3.6+ models and will be removed'
      ' in a future release."'
  )
  assert _api_client.parse_agent_message_header(header) == [
      'temperature is ignored by Gemini 3.6+ models and will be removed in a'
      ' future release.'
  ]


def test_parse_multiple_comma_separated_items():
  header = (
      'field_ignored;field="temperature";'
      'msg=%"temperature is ignored, using default.", '
      'field_ignored;field="top_k";'
      'msg=%"top_k is ignored; see docs."'
  )
  assert _api_client.parse_agent_message_header(header) == [
      'temperature is ignored, using default.',
      'top_k is ignored; see docs.',
  ]


def test_parse_item_without_field_and_unknown_params():
  header = (
      'legacy_usage;severity="warn";experimental;'
      'msg=%"generateContent is a legacy endpoint. Use the Interactions API'
      ' for new development."'
  )
  assert _api_client.parse_agent_message_header(header) == [
      'generateContent is a legacy endpoint. Use the Interactions API for new'
      ' development.'
  ]


def test_parse_percent_encoded_utf8_and_quoted_string():
  header = (
      'field_ignored;msg=%"use %22max_output_tokens%22 %E2%80%94 100%25", '
      'other_code;msg="plain \\"quoted\\" \\\\ string"'
  )
  assert _api_client.parse_agent_message_header(header) == [
      'use "max_output_tokens" \u2014 100%',
      'plain "quoted" \\ string',
  ]


def test_parse_malformed_headers_gracefully_ignored():
  assert _api_client.parse_agent_message_header('') == []
  assert _api_client.parse_agent_message_header('   ') == []
  assert _api_client.parse_agent_message_header(';;;') == []
  assert _api_client.parse_agent_message_header('field_ignored') == []
  assert (
      _api_client.parse_agent_message_header('field_ignored;field="temperature"')
      == []
  )
  assert (
      _api_client.parse_agent_message_header('field_ignored;msg=unquoted') == []
  )
  assert (
      _api_client.parse_agent_message_header('field_ignored;msg=%"unterminated')
      == []
  )
  assert (
      _api_client.parse_agent_message_header('bad code;msg=%"not a token"')
      == []
  )


def test_parse_skips_malformed_sibling_item():
  header = (
      'field_ignored;field="temperature", '
      'field_ignored;field="top_k";msg=%"top_k is ignored."'
  )
  assert _api_client.parse_agent_message_header(header) == ['top_k is ignored.']


def test_parse_plain_string_fallback():
  header = 'generation_config.temperature is ignored, using default value.'
  assert _api_client.parse_agent_message_header(header) == [
      'generation_config.temperature is ignored, using default value.'
  ]


def _agent_message_response(msg: str) -> httpx.Response:
  return httpx.Response(
      200, headers={'Agent-Message': f'field_ignored;msg=%"{msg}"'}
  )


def test_gaos_sdk_hooks_emit_warnings():
  hooks = SDKHooks()

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    hooks.after_success(
        cast(AfterSuccessContext, None),
        _agent_message_response('gaos sync warning'),
    )

  user_warnings = [
      _message(w) for w in recorded if issubclass(w.category, UserWarning)
  ]
  assert user_warnings == ['gaos sync warning']


@pytest.mark.asyncio
async def test_gaos_async_sdk_hooks_emit_warnings():
  hooks = AsyncSDKHooks()
  init_async_hooks(hooks)

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    await hooks.after_success(
        cast(AsyncAfterSuccessContext, None),
        _agent_message_response('gaos async warning'),
    )

  user_warnings = [
      _message(w) for w in recorded if issubclass(w.category, UserWarning)
  ]
  assert user_warnings == ['gaos async warning']


def _user_warnings(recorded) -> list[str]:
  return [
      _message(w) for w in recorded if issubclass(w.category, UserWarning)
  ]


def _error_response(status: int, msg: str) -> httpx.Response:
  return httpx.Response(
      status,
      headers={'Agent-Message': f'field_ignored;msg=%"{msg}"'},
      json={'error': {'code': status, 'message': 'boom', 'status': 'X'}},
  )


def test_interactions_client_error_emits_warning():
  http_client = httpx.Client(
      transport=httpx.MockTransport(
          lambda request: _error_response(400, 'interactions 400 warning')
      )
  )
  client = client_lib.Client(
      api_key='fake-key', http_options={'httpx_client': http_client}
  )
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    with pytest.raises(Exception) as exc_info:
      client.interactions.create(model='gemini-2.5-flash', input='hi')

  assert getattr(exc_info.value, 'status_code', None) == 400
  assert _user_warnings(recorded) == ['interactions 400 warning']


@pytest.mark.asyncio
async def test_interactions_async_client_error_emits_warning():
  http_client = httpx.AsyncClient(
      transport=httpx.MockTransport(
          lambda request: _error_response(400, 'interactions async 400 warning')
      )
  )
  client = client_lib.Client(
      api_key='fake-key', http_options={'httpx_async_client': http_client}
  )
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    with pytest.raises(Exception) as exc_info:
      await client.aio.interactions.create(model='gemini-2.5-flash', input='hi')

  assert getattr(exc_info.value, 'status_code', None) == 400
  assert _user_warnings(recorded) == ['interactions async 400 warning']


def test_gaos_after_error_hook_passes_through_5xx():
  hooks = SDKHooks()
  response = _error_response(500, 'gaos 500 warning')

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    result = hooks.after_error(cast(AfterErrorContext, None), response, None)

  assert result == (response, None)
  assert _user_warnings(recorded) == ['gaos 500 warning']


def test_gaos_after_error_hook_ignores_missing_response():
  hook = GoogleGenAIAgentMessageHook()
  error = httpx.ConnectError('no connection')

  result = hook.after_error(cast(AfterErrorContext, None), None, error)

  assert result == (None, error)
