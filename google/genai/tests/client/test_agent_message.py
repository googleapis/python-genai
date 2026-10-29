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
from ... import errors
from ..._gaos._hooks.asyncregistration import init_async_hooks
from ..._gaos._hooks.asyncsdkhooks import AsyncSDKHooks
from ..._gaos._hooks.asynctypes import AfterSuccessContext as AsyncAfterSuccessContext
from ..._gaos._hooks.google_genai_auth import GoogleGenAIAgentMessageHook
from ..._gaos._hooks.sdkhooks import SDKHooks
from ..._gaos._hooks.types import AfterErrorContext, AfterSuccessContext


@pytest.fixture(autouse=True)
def clear_seen_agent_messages():
  _api_client.clear_seen_agent_messages()
  yield
  _api_client.clear_seen_agent_messages()


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


def test_http_response_emits_warning_and_deduplicates():
  header = (
      'field_ignored;field="temperature";'
      'msg=%"temperature is ignored by Gemini 3.6+ models."'
  )
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    _api_client.HttpResponse({'Agent-Message': header}, ['{}'])
    _api_client.HttpResponse({'agent-message': header}, ['{}'])
    _api_client.HttpResponse(
        {
            'AGENT-MESSAGE': (
                'field_ignored;field="top_k";'
                'msg=%"top_k is ignored by Gemini 3.6+ models."'
            )
        },
        ['{}'],
    )

  user_warnings = [
      _message(w) for w in recorded if issubclass(w.category, UserWarning)
  ]
  assert user_warnings == [
      'temperature is ignored by Gemini 3.6+ models.',
      'top_k is ignored by Gemini 3.6+ models.',
  ]


def test_httpx_headers_multiple_values():
  headers = httpx.Headers([
      ('Agent-Message', 'field_ignored;msg=%"first warning"'),
      ('agent-message', 'field_ignored;msg=%"second warning"'),
  ])
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    _api_client.HttpResponse(headers, ['{}'])

  user_warnings = [
      _message(w) for w in recorded if issubclass(w.category, UserWarning)
  ]
  assert user_warnings == ['first warning', 'second warning']


def test_warning_is_attributed_to_caller_outside_package():
  # Code compiled with a filename outside the google.genai package stands in for
  # user code; SDK-internal frames should be skipped when attributing the
  # warning.
  user_code = compile(
      "_api_client.HttpResponse({'Agent-Message': header}, ['{}'])",
      '/not/google/genai/user_code.py',
      'exec',
  )
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    exec(  # pylint: disable=exec-used
        user_code,
        {
            '_api_client': _api_client,
            'header': 'field_ignored;msg=%"attributed warning"',
        },
    )

  user_warnings = [w for w in recorded if issubclass(w.category, UserWarning)]
  assert [_message(w) for w in user_warnings] == ['attributed warning']
  assert user_warnings[0].filename == '/not/google/genai/user_code.py'


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


def test_gaos_shares_dedup_with_generate_content():
  hooks = SDKHooks()

  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    _api_client.HttpResponse(
        {'Agent-Message': 'field_ignored;msg=%"shared warning"'}, ['{}']
    )
    hooks.after_success(
        cast(AfterSuccessContext, None),
        _agent_message_response('shared warning'),
    )

  user_warnings = [
      _message(w) for w in recorded if issubclass(w.category, UserWarning)
  ]
  assert user_warnings == ['shared warning']


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


@pytest.mark.parametrize(
    'status, error_cls', [(400, errors.ClientError), (503, errors.ServerError)]
)
def test_generate_content_error_response_emits_warning(status, error_cls):
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    with pytest.raises(error_cls) as exc_info:
      errors.APIError.raise_for_response(
          _error_response(status, f'gc {status} warning')
      )

  assert exc_info.value.code == status
  assert _user_warnings(recorded) == [f'gc {status} warning']


@pytest.mark.asyncio
async def test_generate_content_async_error_response_emits_warning():
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    with pytest.raises(errors.ServerError):
      await errors.APIError.raise_for_async_response(
          _error_response(500, 'gc async 500 warning')
      )

  assert _user_warnings(recorded) == ['gc async 500 warning']


def test_generate_content_client_error_emits_warning():
  http_client = httpx.Client(
      transport=httpx.MockTransport(
          lambda request: _error_response(400, 'gc client 400 warning')
      )
  )
  client = client_lib.Client(
      api_key='fake-key', http_options={'httpx_client': http_client}
  )
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    with pytest.raises(errors.ClientError):
      client.models.generate_content(model='gemini-2.5-flash', contents='hi')

  assert _user_warnings(recorded) == ['gc client 400 warning']


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


def test_warnings_stop_after_max_seen_messages():
  # A server bug that puts per-request values in messages must not grow the
  # dedup set, or the output, without bound. 1000 is _MAX_SEEN_AGENT_MESSAGES
  # (not importable here: the private test variant can't see `_` names).
  limit = 1000
  with warnings.catch_warnings(record=True) as recorded:
    warnings.simplefilter('always')
    for i in range(limit + 5):
      _api_client.warn_from_agent_message_headers(
          {'Agent-Message': f'code;msg=%"message {i}"'}
      )

  assert len(_user_warnings(recorded)) == limit
