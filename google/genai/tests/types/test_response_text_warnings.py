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

"""Text accessor warnings must not be triggered by structured output parsing."""

from enum import Enum
from typing import Union

import httpx
from pydantic import BaseModel
import pytest

from ... import types
from ...client import Client


class Output(BaseModel):
  summary: str


class Status(Enum):
  OK = 'ok'


@pytest.fixture(autouse=True)
def reset_text_warnings(monkeypatch):
  monkeypatch.setattr(types, '_response_text_warning_logged', False)
  monkeypatch.setattr(types, '_response_text_non_text_warning_logged', False)


@pytest.mark.parametrize(
    'config,text,expected',
    [
        pytest.param(
            {'response_schema': Output},
            '{"summary":"ok"}',
            Output(summary='ok'),
            id='pydantic',
        ),
        pytest.param({'response_schema': Status}, '"ok"', Status.OK, id='enum'),
        pytest.param(
            {'response_schema': list[str]}, '["ok"]', ['ok'], id='generic-alias'
        ),
        pytest.param({'response_schema': str}, '"ok"', 'ok', id='primitive'),
        pytest.param(
            {'response_schema': {'type': 'STRING'}}, '"ok"', 'ok', id='dict'
        ),
        pytest.param(
            {'response_schema': types.Schema(type=types.Type.STRING)},
            '"ok"',
            'ok',
            id='schema',
        ),
        pytest.param(
            {'response_schema': Union[int, Output]},
            '{"summary":"ok"}',
            Output(summary='ok'),
            id='model-union',
        ),
        pytest.param(
            {'response_schema': Union[str, int]},
            '"ok"',
            'ok',
            id='primitive-union',
        ),
        pytest.param(
            {'response_json_schema': {'type': 'string'}},
            '"ok"',
            'ok',
            id='json-schema',
        ),
    ],
)
@pytest.mark.parametrize('include_text', [False, True])
def test_structured_output_does_not_warn(
    config, text, expected, include_text, caplog
):
  parts = [
      {'function_call': {'name': 'lookup_data', 'args': {'query': 'test'}}}
  ]
  if include_text:
    parts.append({'text': text})
  response = types.GenerateContentResponse._from_response(
      response={'candidates': [{'content': {'parts': parts}}]},
      kwargs={'config': config},
  )

  assert response.parsed == (expected if include_text else None)
  assert response.function_calls[0].name == 'lookup_data'
  assert not caplog.records
  assert not types._response_text_non_text_warning_logged

  # Internal parsing must not consume the one-time warning for explicit access.
  assert response.text == (text if include_text else None)
  assert len(caplog.records) == 1
  assert 'non-text parts' in caplog.records[0].message
  assert response.text == (text if include_text else None)
  assert len(caplog.records) == 1


def test_multiple_candidates_only_warn_on_explicit_text_access(caplog):
  response = types.GenerateContentResponse._from_response(
      response={
          'candidates': [
              {'content': {'parts': [{'text': '{"summary":"first"}'}]}},
              {'content': {'parts': [{'text': '{"summary":"second"}'}]}},
          ]
      },
      kwargs={'config': {'response_schema': Output}},
  )

  assert response.parsed == Output(summary='first')
  assert not caplog.records
  assert not types._response_text_warning_logged
  assert response.text == '{"summary":"first"}'
  assert len(caplog.records) == 1
  assert 'there are 2 candidates' in caplog.records[0].message
  assert response.text == '{"summary":"first"}'
  assert len(caplog.records) == 1


@pytest.mark.parametrize(
    'parts,expected',
    [
        ([{'text': '{"summary":"ok"}'}], Output(summary='ok')),
        ([{'text': '{"summary":'}], None),
        ([{'text': ''}], None),
        ([{'text': '{"summary":"thought"}', 'thought': True}], None),
        ([], None),
    ],
)
def test_structured_text_parsing_is_unchanged(parts, expected, caplog):
  response = types.GenerateContentResponse._from_response(
      response={'candidates': [{'content': {'parts': parts}}]},
      kwargs={'config': {'response_schema': Output}},
  )

  assert response.parsed == expected
  assert not caplog.records


@pytest.mark.asyncio
@pytest.mark.parametrize('use_async', [False, True])
async def test_generate_content_tool_call_with_schema(use_async, caplog):
  requests = []

  def respond(request):
    requests.append(request)
    return httpx.Response(
        200,
        json={
            'candidates': [
                {
                    'content': {
                        'role': 'model',
                        'parts': [
                            {
                                'functionCall': {
                                    'name': 'lookup_data',
                                    'args': {'query': 'test'},
                                },
                            }
                        ],
                    },
                    'finishReason': 'STOP',
                }
            ],
        },
    )

  transport = httpx.MockTransport(respond)
  client = Client(
      api_key='test-key',
      http_options=types.HttpOptions(
          client_args={'transport': transport},
          async_client_args={'transport': transport},
      ),
  )
  config = types.GenerateContentConfig(
      response_mime_type='application/json',
      response_schema=Output,
      tools=[
          types.Tool(
              function_declarations=[
                  types.FunctionDeclaration(name='lookup_data'),
              ]
          )
      ],
      automatic_function_calling=types.AutomaticFunctionCallingConfig(
          disable=True
      ),
  )
  try:
    if use_async:
      response = await client.aio.models.generate_content(
          model='gemini-flash-latest', contents='Look up test.', config=config
      )
    else:
      response = client.models.generate_content(
          model='gemini-flash-latest', contents='Look up test.', config=config
      )
  finally:
    await client.aio.aclose()
    client.close()

  assert len(requests) == 1
  assert response.parsed is None
  assert response.function_calls[0].name == 'lookup_data'
  assert not caplog.records
