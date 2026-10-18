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

"""Unit tests for automatic continuation_token resumption in Models and AsyncModels."""

import base64
import json
from unittest import mock

import httpx
import pydantic
import pytest

from ... import _extra_utils
from ... import client
from ... import errors
from ... import models
from ... import types

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def mock_api_client():
  api_client = mock.MagicMock(spec=client.BaseApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}
  api_client.vertexai = False
  api_client._ws_connection = None
  setattr(api_client, '_async_ws_connection', None)
  api_client.tls_connection = None
  return api_client


def test_continuation_helpers_edge_cases():
  """Tests shared _extra_utils helper edge cases for config preparation and response merging."""
  # Default enabled for Models and Chat
  assert _extra_utils.should_enable_automatic_continuation(None)
  assert not _extra_utils.should_enable_automatic_continuation(
      None, default_enabled=False
  )
  assert _extra_utils.should_enable_automatic_continuation(
      None, default_enabled=True
  )
  assert _extra_utils.should_enable_automatic_continuation(
      {'automatic_continuation': True}, default_enabled=False
  )
  assert not _extra_utils.should_enable_automatic_continuation(
      {'automatic_continuation': False}, default_enabled=True
  )
  assert _extra_utils.should_enable_automatic_continuation(
      {'automatic_continuation': True, 'max_output_tokens': 1000},
      default_enabled=False,
  )

  assert _extra_utils.is_resumable_finish_reason(None)
  assert _extra_utils.is_resumable_finish_reason(
      types.FinishReason.CONTINUATION
  )
  assert not _extra_utils.is_resumable_finish_reason(
      types.FinishReason.MAX_TOKENS
  )
  assert not _extra_utils.is_resumable_finish_reason(types.FinishReason.STOP)

  assert _extra_utils.should_continue_generation(None) is None
  assert (
      _extra_utils.should_continue_generation(
          types.GenerateContentResponse(candidates=[])
      )
      is None
  )
  assert (
      _extra_utils.should_continue_generation(
          types.GenerateContentResponse(
              candidates=[
                  types.Candidate(
                      finish_reason=None,
                      continuation_token=b'tok',
                  )
              ]
          )
      )
      == b'tok'
  )
  assert (
      _extra_utils.should_continue_generation(
          types.GenerateContentResponse(
              candidates=[
                  types.Candidate(
                      finish_reason=types.FinishReason.MAX_TOKENS,
                      continuation_token=b'tok',
                  )
              ]
          )
      )
      is None
  )

  cfg_from_none = _extra_utils.prepare_continuation_config(None, b'tok')
  assert cfg_from_none is not None
  assert cfg_from_none.continuation_token == b'tok'

  cfg_from_dict = _extra_utils.prepare_continuation_config(
      {'temperature': 0.5, 'automatic_continuation': True},
      b'tok',
      clear_automatic_continuation=True,
  )
  assert cfg_from_dict is not None
  assert cfg_from_dict.continuation_token == b'tok'
  assert cfg_from_dict.temperature == 0.5
  assert cfg_from_dict.automatic_continuation is None

  assert (
      _extra_utils.merge_continuation_responses([])
      == types.GenerateContentResponse()
  )

  cand = types.Candidate(
      content=types.Content(role='model', parts=[types.Part(text='hi')])
  )
  assert _extra_utils.merge_candidates([], [cand]) == [cand]
  assert _extra_utils.merge_candidates([cand], []) == [cand]

  cand0_hop1 = types.Candidate(
      index=0,
      content=types.Content(role='model', parts=[types.Part(text='c0_1 ')]),
      finish_reason=types.FinishReason.CONTINUATION,
      continuation_token=b'tok0',
  )
  cand1_hop1 = types.Candidate(
      index=1,
      content=types.Content(role='model', parts=[types.Part(text='c1_1 ')]),
      finish_reason=types.FinishReason.CONTINUATION,
  )
  cand0_hop2 = types.Candidate(
      index=0,
      content=types.Content(role='model', parts=[types.Part(text='c0_2')]),
      finish_reason=types.FinishReason.STOP,
      continuation_token=None,
  )
  cand1_hop2 = types.Candidate(
      index=1,
      content=types.Content(role='model', parts=[types.Part(text='c1_2')]),
      finish_reason=types.FinishReason.STOP,
  )
  cand2_hop2 = types.Candidate(
      index=2,
      content=types.Content(role='model', parts=[types.Part(text='c2_2')]),
      finish_reason=types.FinishReason.STOP,
  )
  merged_cands = _extra_utils.merge_candidates(
      [cand0_hop1, cand1_hop1], [cand0_hop2, cand1_hop2, cand2_hop2]
  )
  assert len(merged_cands) == 3
  assert merged_cands[0].content.parts == [
      types.Part(text='c0_1 '),
      types.Part(text='c0_2'),
  ]
  assert merged_cands[0].finish_reason == types.FinishReason.STOP
  assert merged_cands[0].continuation_token is None
  assert merged_cands[1].content.parts == [
      types.Part(text='c1_1 '),
      types.Part(text='c1_2'),
  ]
  assert merged_cands[1].finish_reason == types.FinishReason.STOP
  assert merged_cands[2] == cand2_hop2

  # ModalityTokenCount when prev_val is empty list and curr_val is non-empty list
  r1 = types.GenerateContentResponse(
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_tokens_details=[]
      )
  )
  r2 = types.GenerateContentResponse(
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=10
              )
          ]
      )
  )
  merged = _extra_utils.merge_continuation_responses([r1, r2])
  assert merged.usage_metadata is not None
  assert merged.usage_metadata.prompt_tokens_details == [
      types.ModalityTokenCount(
          modality=types.MediaModality.TEXT, token_count=10
      )
  ]

  total_only_merged = _extra_utils.merge_pydantic_models(
      types.GenerateContentResponseUsageMetadata(
          prompt_token_count=15, total_token_count=100
      ),
      types.GenerateContentResponseUsageMetadata(
          prompt_token_count=80, total_token_count=50
      ),
  )
  assert total_only_merged.prompt_token_count == 95
  assert total_only_merged.initial_prompt_token_count == 15
  assert total_only_merged.total_token_count == 150
  assert types.GenerateContentResponse().initial_prompt_token_count is None
  single_hop_resp = types.GenerateContentResponse(
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=42
      )
  )
  assert single_hop_resp.initial_prompt_token_count == 42
  assert single_hop_resp.usage_metadata.initial_prompt_token_count == 42


def test_models_generate_content_auto_resumes_across_4_hops(mock_api_client):
  """Models.generate_content with automatic_continuation=True auto-resumes across 4 hops."""
  models_module = models.Models(mock_api_client)

  hop1_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 1 part. ')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'token_hop_1',
          )
      ],
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=10,
          candidates_token_count=32768,
          thoughts_token_count=500,
          total_token_count=33278,
      ),
  )
  hop2_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 2 part. ')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'token_hop_2',
          )
      ],
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=32778,
          candidates_token_count=32768,
          thoughts_token_count=300,
          total_token_count=65846,
      ),
  )
  hop3_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 3 part. ')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'token_hop_3',
          )
      ],
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=65546,
          candidates_token_count=32768,
          thoughts_token_count=200,
          total_token_count=98514,
      ),
  )
  hop4_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 4 final part.')],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ],
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=98314,
          candidates_token_count=1024,
          thoughts_token_count=100,
          total_token_count=99438,
      ),
  )

  for disable_afc in (False, True):
    user_config = types.GenerateContentConfig(
        automatic_continuation=True,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=disable_afc
        ),
    )
    with mock.patch.object(
        models.Models,
        '_generate_content',
        side_effect=[
            hop1_response.model_copy(deep=True),
            hop2_response.model_copy(deep=True),
            hop3_response.model_copy(deep=True),
            hop4_response.model_copy(deep=True),
        ],
    ) as mock_raw_gc:
      response = models_module.generate_content(
          model='gemini-2.5-pro',
          contents='Write a very long story',
          config=user_config,
      )

      assert mock_raw_gc.call_count == 4
      expected_tokens = [None, b'token_hop_1', b'token_hop_2', b'token_hop_3']
      first_contents = mock_raw_gc.call_args_list[0].kwargs['contents']
      for idx, expected_tok in enumerate(expected_tokens):
        call_kwargs = mock_raw_gc.call_args_list[idx].kwargs
        assert call_kwargs['config'].continuation_token == expected_tok
        assert call_kwargs['contents'] == first_contents

      assert (
          response.text
          == 'Hop 1 part. Hop 2 part. Hop 3 part. Hop 4 final part.'
      )
      assert response.candidates is not None
      cand = response.candidates[0]
      assert cand.finish_reason == types.FinishReason.STOP
      assert cand.continuation_token is None
      assert cand.content is not None
      assert cand.content.parts == [
          types.Part(text='Hop 1 part. '),
          types.Part(text='Hop 2 part. '),
          types.Part(text='Hop 3 part. '),
          types.Part(text='Hop 4 final part.'),
      ]
      assert response.usage_metadata is not None
      assert (
          response.usage_metadata.prompt_token_count
          == 10 + 32778 + 65546 + 98314
      )
      assert response.initial_prompt_token_count == 10
      assert response.usage_metadata.initial_prompt_token_count == 10
      assert response.usage_metadata.candidates_token_count == 32768 * 3 + 1024
      assert (
          response.usage_metadata.thoughts_token_count == 500 + 300 + 200 + 100
      )
      assert (
          response.usage_metadata.total_token_count
          == 33278 + 65846 + 98514 + 99438
      )
      # Caller's config is not mutated
      assert user_config.continuation_token is None


def test_models_automatic_continuation_config_rules(mock_api_client):
  """Verifies default-enabled, automatic_continuation, and finish_reason rules in Models."""
  models_module = models.Models(mock_api_client)

  hop1_max_tokens_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Stopped at hop 1.')],
              ),
              finish_reason=types.FinishReason.MAX_TOKENS,
              continuation_token=b'token_unused',
          )
      ]
  )
  hop1_cont_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 1 continuation. ')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_cont_1',
          )
      ]
  )
  hop2_stop_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 2 stop.')],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )

  # 1. Default (config=None or automatic_continuation=None) -> enabled in unary & stream
  for cfg in (
      None,
      types.GenerateContentConfig(),
      types.GenerateContentConfig(
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
              disable=True
          )
      ),
  ):
    with mock.patch.object(
        models.Models,
        '_generate_content',
        side_effect=[
            hop1_cont_response.model_copy(deep=True),
            hop2_stop_response.model_copy(deep=True),
        ],
    ) as mock_raw_gc:
      response = models_module.generate_content(
          model='gemini-2.5-pro',
          contents='Default config',
          config=cfg,
      )
      assert mock_raw_gc.call_count == 2
      assert response.text == 'Hop 1 continuation. Hop 2 stop.'
      assert response.candidates[0].finish_reason == types.FinishReason.STOP
      assert response.candidates[0].continuation_token is None

    with mock.patch.object(
        models.Models,
        '_generate_content_stream',
        side_effect=[
            iter([hop1_cont_response.model_copy(deep=True)]),
            iter([hop2_stop_response.model_copy(deep=True)]),
        ],
    ) as mock_raw_stream:
      chunks = list(
          models_module.generate_content_stream(
              model='gemini-2.5-pro',
              contents='Default stream config',
              config=cfg,
          )
      )
      assert mock_raw_stream.call_count == 2
      assert [c.text for c in chunks] == [
          'Hop 1 continuation. ',
          'Hop 2 stop.',
      ]
      assert chunks[0].candidates[0].finish_reason is None
      assert chunks[1].candidates[0].finish_reason == types.FinishReason.STOP

  # 2. Explicit automatic_continuation=False -> disabled in unary & stream
  for disable_afc in (False, True):
    cfg = types.GenerateContentConfig(
        automatic_continuation=False,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=disable_afc
        ),
    )
    with mock.patch.object(
        models.Models,
        '_generate_content',
        return_value=hop1_cont_response.model_copy(deep=True),
    ) as mock_raw_gc:
      response = models_module.generate_content(
          model='gemini-2.5-pro',
          contents='Explicit False',
          config=cfg,
      )
      assert mock_raw_gc.call_count == 1
      assert response.text == 'Hop 1 continuation. '
      assert (
          response.candidates[0].finish_reason
          == types.FinishReason.CONTINUATION
      )
      assert response.candidates[0].continuation_token == b'tok_cont_1'

    with mock.patch.object(
        models.Models,
        '_generate_content_stream',
        return_value=iter([hop1_cont_response.model_copy(deep=True)]),
    ) as mock_raw_stream:
      chunks = list(
          models_module.generate_content_stream(
              model='gemini-2.5-pro',
              contents='Explicit False stream',
              config=cfg,
          )
      )
      assert mock_raw_stream.call_count == 1
      assert [c.text for c in chunks] == ['Hop 1 continuation. ']
      assert (
          chunks[0].candidates[0].finish_reason
          == types.FinishReason.CONTINUATION
      )

  # 3. finish_reason != CONTINUATION (e.g. MAX_TOKENS) -> stops loop even when automatic_continuation=True
  for disable_afc in (False, True):
    cfg = types.GenerateContentConfig(
        max_output_tokens=50000,
        automatic_continuation=True,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=disable_afc
        ),
    )
    with mock.patch.object(
        models.Models,
        '_generate_content',
        return_value=hop1_max_tokens_response.model_copy(deep=True),
    ) as mock_raw_gc:
      response = models_module.generate_content(
          model='gemini-2.5-pro',
          contents='Stops on MAX_TOKENS',
          config=cfg,
      )
      assert mock_raw_gc.call_count == 1
      assert (
          mock_raw_gc.call_args_list[0].kwargs['config'].max_output_tokens
          == 50000
      )
      assert response.text == 'Stopped at hop 1.'
      assert (
          response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
      )
      assert response.candidates[0].continuation_token == b'token_unused'

    with mock.patch.object(
        models.Models,
        '_generate_content_stream',
        return_value=iter([hop1_max_tokens_response.model_copy(deep=True)]),
    ) as mock_raw_stream:
      chunks = list(
          models_module.generate_content_stream(
              model='gemini-2.5-pro',
              contents='Stops on MAX_TOKENS stream',
              config=cfg,
          )
      )
      assert mock_raw_stream.call_count == 1
      assert (
          mock_raw_stream.call_args_list[0].kwargs['config'].max_output_tokens
          == 50000
      )
      assert [c.text for c in chunks] == ['Stopped at hop 1.']
      assert (
          chunks[0].candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
      )
      # The token is surfaced so the caller can resume manually.
      assert chunks[0].candidates[0].continuation_token == b'token_unused'

  # 4. Explicit automatic_continuation=True -> continues on CONTINUATION and forwards max_output_tokens as-is
  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[
          hop1_cont_response.model_copy(deep=True),
          hop2_stop_response.model_copy(deep=True),
      ],
  ) as mock_raw_gc:
    response = models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Explicit True',
        config={'automatic_continuation': True, 'max_output_tokens': 50000},
    )
    assert mock_raw_gc.call_count == 2
    assert (
        mock_raw_gc.call_args_list[0].kwargs['config'].max_output_tokens
        == 50000
    )
    assert (
        mock_raw_gc.call_args_list[1].kwargs['config'].max_output_tokens
        == 50000
    )
    assert response.text == 'Hop 1 continuation. Hop 2 stop.'


def test_models_generate_content_and_stream_incompatible_tools_with_continuation(
    mock_api_client,
):
  """Incompatible AFC tools path in Models also supports continuation token resumption."""
  models_module = models.Models(mock_api_client)

  hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Part 1. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_incompat',
          )
      ]
  )
  hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Part 2.')]
              ),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )

  tool_decl = types.Tool(
      function_declarations=[
          types.FunctionDeclaration(name='manual_fn', description='manual')
      ]
  )
  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[hop1.model_copy(deep=True), hop2.model_copy(deep=True)],
  ) as mock_raw_gc:
    resp = models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Test incompatible tools unary',
        config=types.GenerateContentConfig(
            automatic_continuation=True, tools=[tool_decl]
        ),
    )
    assert mock_raw_gc.call_count == 2
    assert resp.text == 'Part 1. Part 2.'

  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          iter([hop1.model_copy(deep=True)]),
          iter([hop2.model_copy(deep=True)]),
      ],
  ) as mock_raw_stream:
    chunks = list(
        models_module.generate_content_stream(
            model='gemini-2.5-pro',
            contents='Test incompatible tools stream',
            config=types.GenerateContentConfig(
                automatic_continuation=True, tools=[tool_decl]
            ),
        )
    )
    assert mock_raw_stream.call_count == 2
    assert [c.text for c in chunks] == ['Part 1. ', 'Part 2.']


def test_models_generate_content_preserves_empty_text_thought_part(
    mock_api_client,
):
  """Empty placeholder Part(text='') from a thought-only hop is never dropped in Models.generate_content."""
  models_module = models.Models(mock_api_client)

  hop1_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[
                      types.Part(text='', thought_signature=b'sig_hop_1'),
                  ],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_after_thought',
          )
      ]
  )
  hop2_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Final answer after deep thinking.')],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )

  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[hop1_response, hop2_response],
  ) as mock_raw_gc:
    response = models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Solve hard math problem',
        config=types.GenerateContentConfig(automatic_continuation=True),
    )
    assert mock_raw_gc.call_count == 2
    assert response.text == 'Final answer after deep thinking.'
    parts = response.candidates[0].content.parts
    assert len(parts) == 2
    assert parts[0].text == ''  # pylint: disable=g-explicit-bool-comparison
    assert parts[0].thought_signature == b'sig_hop_1'
    assert parts[1].text == 'Final answer after deep thinking.'


def test_models_generate_content_recursive_metadata_and_parsed_schema_merging(
    mock_api_client,
):
  """Verifies recursive Pydantic merging for all metadata fields and response_schema in Models.generate_content."""

  class StorySummary(pydantic.BaseModel):
    title: str
    pages: int

  models_module = models.Models(mock_api_client)

  hop1_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='{"title": "Long ')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_meta_1',
              safety_ratings=[
                  types.SafetyRating(
                      category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                      probability=types.HarmProbability.NEGLIGIBLE,
                  )
              ],
              citation_metadata=types.CitationMetadata(
                  citations=[types.Citation(title='Source 1', start_index=0)]
              ),
              grounding_metadata=types.GroundingMetadata(
                  web_search_queries=['query 1'],
              ),
              logprobs_result=types.LogprobsResult(
                  log_probability_sum=-1.5,
                  chosen_candidates=[
                      types.LogprobsResultCandidate(
                          token='{"title":', log_probability=-1.5
                      )
                  ],
              ),
          )
      ],
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=20,
          cached_content_token_count=8,
          candidates_token_count=100,
          thoughts_token_count=30,
          tool_use_prompt_token_count=5,
          total_token_count=155,
          prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=20
              )
          ],
          cache_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=8
              )
          ],
          candidates_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=100
              )
          ],
          tool_use_prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=5
              )
          ],
      ),
  )

  hop2_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Odyssey", "pages": 42}')],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
              safety_ratings=[
                  types.SafetyRating(
                      category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                      probability=types.HarmProbability.LOW,
                  ),
                  types.SafetyRating(
                      category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                      probability=types.HarmProbability.NEGLIGIBLE,
                  ),
              ],
              citation_metadata=types.CitationMetadata(
                  citations=[types.Citation(title='Source 2', start_index=10)]
              ),
              grounding_metadata=types.GroundingMetadata(
                  web_search_queries=['query 2'],
              ),
              logprobs_result=types.LogprobsResult(
                  log_probability_sum=-2.0,
                  chosen_candidates=[
                      types.LogprobsResultCandidate(
                          token='Odyssey"}', log_probability=-2.0
                      )
                  ],
              ),
          )
      ],
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=120,
          cached_content_token_count=8,
          candidates_token_count=50,
          thoughts_token_count=15,
          tool_use_prompt_token_count=10,
          total_token_count=195,
          prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=120
              )
          ],
          cache_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=8
              )
          ],
          candidates_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=50
              )
          ],
          tool_use_prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=10
              )
          ],
      ),
  )

  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[hop1_response, hop2_response],
  ):
    response = models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Give me JSON',
        config=types.GenerateContentConfig(
            automatic_continuation=True,
            response_schema=StorySummary,
        ),
    )

    assert response.text == '{"title": "Long Odyssey", "pages": 42}'
    assert response.parsed == StorySummary(title='Long Odyssey', pages=42)
    cand = response.candidates[0]
    assert len(cand.safety_ratings) == 2
    assert cand.safety_ratings[0].probability == types.HarmProbability.LOW
    assert len(cand.citation_metadata.citations) == 2
    assert cand.grounding_metadata.web_search_queries == ['query 1', 'query 2']
    assert cand.logprobs_result.log_probability_sum == -3.5
    assert len(cand.logprobs_result.chosen_candidates) == 2
    assert response.initial_prompt_token_count == 20
    assert response.usage_metadata.initial_prompt_token_count == 20
    assert response.usage_metadata.prompt_token_count == 140
    assert response.usage_metadata.cached_content_token_count == 16
    assert response.usage_metadata.candidates_token_count == 150
    assert response.usage_metadata.thoughts_token_count == 45
    assert response.usage_metadata.tool_use_prompt_token_count == 15
    assert response.usage_metadata.total_token_count == 350
    assert response.usage_metadata.prompt_tokens_details == [
        types.ModalityTokenCount(
            modality=types.MediaModality.TEXT, token_count=140
        )
    ]
    assert response.usage_metadata.cache_tokens_details == [
        types.ModalityTokenCount(
            modality=types.MediaModality.TEXT, token_count=16
        )
    ]
    assert response.usage_metadata.candidates_tokens_details == [
        types.ModalityTokenCount(
            modality=types.MediaModality.TEXT, token_count=150
        )
    ]
    assert response.usage_metadata.tool_use_prompt_tokens_details == [
        types.ModalityTokenCount(
            modality=types.MediaModality.TEXT, token_count=15
        )
    ]


def test_merge_continuation_responses_shifts_grounding_support_chunk_and_part_indices():
  """Merging responses across hops shifts GroundingSupport chunk and part indices."""
  hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[
                      types.Part(text='Thinking...', thought=True),
                      types.Part(text='part 1 '),
                  ],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_1',
              grounding_metadata=types.GroundingMetadata(
                  grounding_chunks=[
                      types.GroundingChunk(
                          image=types.GroundingChunkImage(
                              image_uri='https://img1.example/a.png',
                              source_uri='https://source1.example/img',
                              title='Image 1',
                              domain='source1.example',
                          )
                      ),
                      types.GroundingChunk(
                          web=types.GroundingChunkWeb(
                              uri='https://source1.example',
                              title='Source 1',
                          )
                      ),
                  ],
                  grounding_supports=[
                      types.GroundingSupport(
                          grounding_chunk_indices=[0, 1],
                          confidence_scores=[0.9, 0.8],
                          segment=types.Segment(
                              part_index=1,
                              start_index=0,
                              end_index=7,
                              text='part 1 ',
                          ),
                      )
                  ],
              ),
          )
      ]
  )
  hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='part 2 ')],
              ),
              finish_reason=types.FinishReason.STOP,
              grounding_metadata=types.GroundingMetadata(
                  grounding_chunks=[
                      types.GroundingChunk(
                          web=types.GroundingChunkWeb(
                              uri='https://source2.example',
                              title='Source 2',
                          )
                      )
                  ],
                  grounding_supports=[
                      types.GroundingSupport(
                          grounding_chunk_indices=[0],
                          confidence_scores=[0.95],
                          segment=types.Segment(
                              part_index=0,
                              start_index=0,
                              end_index=7,
                              text='part 2 ',
                          ),
                      ),
                      types.GroundingSupport(
                          grounding_chunk_indices=[0],
                          segment=types.Segment(
                              start_index=0,
                              end_index=7,
                              text='part 2 ',
                          ),
                      ),
                  ],
              ),
          )
      ]
  )

  merged = _extra_utils.merge_continuation_responses([hop1, hop2])
  cand = merged.candidates[0]
  gm = cand.grounding_metadata

  assert len(gm.grounding_chunks) == 3
  assert len(gm.grounding_supports) == 3

  # First hop's support remains unchanged.
  assert gm.grounding_supports[0].grounding_chunk_indices == [0, 1]
  assert gm.grounding_supports[0].segment.part_index == 1

  # Second hop's supports have chunk indices shifted by +2 and part_index by +2.
  s1 = gm.grounding_supports[1]
  assert s1.grounding_chunk_indices == [2]
  assert s1.segment.part_index == 2
  assert (
      gm.grounding_chunks[s1.grounding_chunk_indices[0]].web.uri
      == 'https://source2.example'
  )
  assert cand.content.parts[s1.segment.part_index].text == 'part 2 '

  # Support with omitted part_index (None -> 0) also shifts by +2.
  s2 = gm.grounding_supports[2]
  assert s2.grounding_chunk_indices == [2]
  assert s2.segment.part_index == 2

  # Original hop2 input must not be mutated.
  assert hop2.candidates[0].grounding_metadata.grounding_supports[
      0
  ].grounding_chunk_indices == [0]
  assert (
      hop2.candidates[0]
      .grounding_metadata.grounding_supports[0]
      .segment.part_index
      == 0
  )
  assert (
      hop2.candidates[0]
      .grounding_metadata.grounding_supports[1]
      .segment.part_index
      is None
  )


def test_merge_continuation_responses_grounding_supports_corner_cases():
  """Covers 3-hop cumulative shifting, None grounding_metadata/segment, empty chunk indices, and multi-candidate independence."""
  hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              index=0,
              content=types.Content(
                  role='model',
                  parts=[
                      types.Part(text='c0-h1-p0 '),
                      types.Part(text='c0-h1-p1 '),
                  ],
              ),
              grounding_metadata=None,
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b't1',
          ),
          types.Candidate(
              index=1,
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='c1-h1-p0 ')],
              ),
              grounding_metadata=types.GroundingMetadata(
                  grounding_chunks=[
                      types.GroundingChunk(
                          web=types.GroundingChunkWeb(
                              uri='https://c1-s0.example'
                          )
                      )
                  ],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b't1-c1',
          ),
      ]
  )
  hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              index=0,
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='c0-h2-p0 ')],
              ),
              grounding_metadata=types.GroundingMetadata(
                  grounding_chunks=[
                      types.GroundingChunk(
                          web=types.GroundingChunkWeb(
                              uri='https://c0-s0.example'
                          )
                      ),
                      types.GroundingChunk(
                          web=types.GroundingChunkWeb(
                              uri='https://c0-s1.example'
                          )
                      ),
                  ],
                  grounding_supports=None,
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b't2',
          ),
          types.Candidate(
              index=1,
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='c1-h2-p0 ')],
              ),
              grounding_metadata=types.GroundingMetadata(
                  grounding_chunks=[
                      types.GroundingChunk(
                          web=types.GroundingChunkWeb(
                              uri='https://c1-s1.example'
                          )
                      )
                  ],
                  grounding_supports=[
                      types.GroundingSupport(
                          grounding_chunk_indices=[0],
                          segment=types.Segment(part_index=0, text='c1-h2-p0 '),
                      )
                  ],
              ),
              finish_reason=types.FinishReason.STOP,
          ),
      ]
  )
  hop3 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              index=0,
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='c0-h3-p0.')],
              ),
              grounding_metadata=types.GroundingMetadata(
                  grounding_chunks=[
                      types.GroundingChunk(
                          web=types.GroundingChunkWeb(
                              uri='https://c0-s2.example'
                          )
                      )
                  ],
                  grounding_supports=[
                      types.GroundingSupport(
                          grounding_chunk_indices=[0],
                          segment=None,
                      ),
                      types.GroundingSupport(
                          grounding_chunk_indices=[],
                          segment=types.Segment(part_index=0, text='c0-h3-p0.'),
                      ),
                      types.GroundingSupport(
                          grounding_chunk_indices=[0],
                          segment=types.Segment(part_index=0, text='c0-h3-p0.'),
                      ),
                  ],
              ),
              finish_reason=types.FinishReason.STOP,
          ),
      ]
  )

  merged = _extra_utils.merge_continuation_responses([hop1, hop2, hop3])

  cand0 = merged.candidates[0]
  gm0 = cand0.grounding_metadata
  assert len(cand0.content.parts) == 4
  assert len(gm0.grounding_chunks) == 3
  assert len(gm0.grounding_supports) == 3
  assert gm0.grounding_supports[0].segment is None
  assert gm0.grounding_supports[0].grounding_chunk_indices == [2]
  assert gm0.grounding_supports[1].grounding_chunk_indices == []
  assert gm0.grounding_supports[1].segment.part_index == 3
  s2 = gm0.grounding_supports[2]
  assert (
      gm0.grounding_chunks[s2.grounding_chunk_indices[0]].web.uri
      == 'https://c0-s2.example'
  )
  assert cand0.content.parts[s2.segment.part_index].text == 'c0-h3-p0.'

  cand1 = merged.candidates[1]
  gm1 = cand1.grounding_metadata
  assert gm1.grounding_supports[0].grounding_chunk_indices == [1]
  assert gm1.grounding_supports[0].segment.part_index == 1
  assert (
      gm1.grounding_chunks[
          gm1.grounding_supports[0].grounding_chunk_indices[0]
      ].web.uri
      == 'https://c1-s1.example'
  )
  assert (
      cand1.content.parts[gm1.grounding_supports[0].segment.part_index].text
      == 'c1-h2-p0 '
  )


def test_models_generate_content_stream_grounding_metadata_across_hops(
    mock_api_client,
):
  """Verifies generate_content_stream preserves per-chunk grounding_metadata and merges cleanly across hops."""
  models_module = models.Models(mock_api_client)

  hop1_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='hop 1 intro, ')],
                  ),
              )
          ]
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='hop 1 grounded. ')],
                  ),
                  grounding_metadata=types.GroundingMetadata(
                      grounding_chunks=[
                          types.GroundingChunk(
                              web=types.GroundingChunkWeb(
                                  uri='https://source1.example'
                              )
                          )
                      ],
                      grounding_supports=[
                          types.GroundingSupport(
                              grounding_chunk_indices=[0],
                              segment=types.Segment(
                                  part_index=0, text='hop 1 grounded. '
                              ),
                          )
                      ],
                  ),
                  finish_reason=types.FinishReason.CONTINUATION,
                  continuation_token=b'tok-stream-1',
              )
          ]
      ),
  ]
  hop2_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='hop 2 intro, ')],
                  ),
              )
          ]
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='hop 2 grounded.')],
                  ),
                  grounding_metadata=types.GroundingMetadata(
                      grounding_chunks=[
                          types.GroundingChunk(
                              web=types.GroundingChunkWeb(
                                  uri='https://source2.example'
                              )
                          )
                      ],
                      grounding_supports=[
                          types.GroundingSupport(
                              grounding_chunk_indices=[0],
                              segment=types.Segment(
                                  part_index=0, text='hop 2 grounded.'
                              ),
                          )
                      ],
                  ),
                  finish_reason=types.FinishReason.STOP,
              )
          ]
      ),
  ]

  with mock.patch.object(
      models_module,
      '_generate_content_stream',
      side_effect=[iter(hop1_chunks), iter(hop2_chunks)],
  ) as mock_stream:
    chunks = list(
        models_module.generate_content_stream(
            model='gemini-2.5-flash',
            contents='Grounded stream query',
        )
    )

  assert mock_stream.call_count == 2
  assert len(chunks) == 4
  # Each yielded terminal hop chunk resolves its support to its own grounding_chunks[0] and parts[0].
  s_hop1 = chunks[1].candidates[0].grounding_metadata.grounding_supports[0]
  assert (
      chunks[1]
      .candidates[0]
      .grounding_metadata.grounding_chunks[s_hop1.grounding_chunk_indices[0]]
      .web.uri
      == 'https://source1.example'
  )
  assert (
      chunks[1].candidates[0].content.parts[s_hop1.segment.part_index].text
      == 'hop 1 grounded. '
  )
  assert chunks[1].candidates[0].finish_reason is None

  s_hop2 = chunks[3].candidates[0].grounding_metadata.grounding_supports[0]
  assert (
      chunks[3]
      .candidates[0]
      .grounding_metadata.grounding_chunks[s_hop2.grounding_chunk_indices[0]]
      .web.uri
      == 'https://source2.example'
  )
  assert (
      chunks[3].candidates[0].content.parts[s_hop2.segment.part_index].text
      == 'hop 2 grounded.'
  )
  assert chunks[3].candidates[0].finish_reason == types.FinishReason.STOP

  # Merging all streamed chunks shifts GroundingSupports indices across the 4 chunks.
  merged = _extra_utils.merge_continuation_responses(chunks)
  cand = merged.candidates[0]
  gm = cand.grounding_metadata
  assert len(gm.grounding_supports) == 2
  assert (
      gm.grounding_chunks[
          gm.grounding_supports[0].grounding_chunk_indices[0]
      ].web.uri
      == 'https://source1.example'
  )
  assert (
      cand.content.parts[gm.grounding_supports[0].segment.part_index].text
      == 'hop 1 grounded. '
  )
  assert (
      gm.grounding_chunks[
          gm.grounding_supports[1].grounding_chunk_indices[0]
      ].web.uri
      == 'https://source2.example'
  )
  assert (
      cand.content.parts[gm.grounding_supports[1].segment.part_index].text
      == 'hop 2 grounded.'
  )


def test_models_generate_content_stream_auto_resumes_across_hops(
    mock_api_client,
):
  """Streaming Models.generate_content_stream yields chunks seamlessly across 4 continuation hops."""
  models_module = models.Models(mock_api_client)

  hop1_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(
                              text=(
                                  '# ENGINEERING A MODERN PRODUCTION COMPILER\n'
                              )
                          )
                      ],
                  )
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_1',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              traffic_type=types.TrafficType.ON_DEMAND
          ),
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(text='## CHAPTER 1: Lexical Analysis\n')
                      ],
                  ),
                  continuation_token=(
                      b'AY89a181L6ffhy7s5hBG6S1Zea0DmuUzVC4ByCWe'
                  ),
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_1',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              traffic_type=types.TrafficType.ON_DEMAND
          ),
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(
                              text='',
                              thought_signature=b'sig_hop_1',
                          )
                      ],
                  ),
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_1',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=24,
              cached_content_token_count=10,
              candidates_token_count=32768,
              thoughts_token_count=400,
              total_token_count=33192,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]
  hop2_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(
                              text='## CHAPTER 2: SSA Optimization Pipeline\n'
                          )
                      ],
                  ),
                  continuation_token=b'stream_tok_hop_2',
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_2',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              traffic_type=types.TrafficType.ON_DEMAND
          ),
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(
                              text='',
                              thought_signature=b'sig_hop_2',
                          )
                      ],
                  ),
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_2',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=32792,
              cached_content_token_count=10,
              candidates_token_count=32768,
              thoughts_token_count=300,
              total_token_count=65860,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]
  hop3_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(text='## CHAPTER 3: Register Allocation\n')
                      ],
                  ),
                  continuation_token=b'stream_tok_hop_3',
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_3',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              traffic_type=types.TrafficType.ON_DEMAND
          ),
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(
                              text='',
                              thought_signature=b'sig_hop_3',
                          )
                      ],
                  ),
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_3',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=65560,
              cached_content_token_count=10,
              candidates_token_count=32768,
              thoughts_token_count=200,
              total_token_count=98528,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]
  hop4_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(text='## CHAPTER 4: Code Generation\n')
                      ],
                  )
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_4',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              traffic_type=types.TrafficType.ON_DEMAND
          ),
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(
                              text='End of compiler textbook.',
                              thought_signature=b'sig_hop_4',
                          )
                      ],
                  ),
                  finish_reason=types.FinishReason.STOP,
              )
          ],
          model_version='gemini-2.5-pro',
          response_id='resp_hop_4',
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=98328,
              cached_content_token_count=10,
              candidates_token_count=11903,
              thoughts_token_count=100,
              total_token_count=110331,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]

  for disable_afc in (True, False):
    with mock.patch.object(
        models.Models,
        '_generate_content_stream',
        side_effect=[
            iter(hop1_chunks),
            iter(hop2_chunks),
            iter(hop3_chunks),
            iter(hop4_chunks),
        ],
    ) as mock_raw_stream:
      chunks = list(
          models_module.generate_content_stream(
              model='gemini-2.5-pro',
              contents=(
                  'Write an exhaustive, multi-chapter textbook on compiler'
                  ' design that is around 100,000 tokens long.'
              ),
              config=types.GenerateContentConfig(
                  automatic_continuation=True,
                  automatic_function_calling=types.AutomaticFunctionCallingConfig(
                      disable=disable_afc
                  ),
              ),
          )
      )
      assert mock_raw_stream.call_count == 4
      assert [c.text for c in chunks] == [
          '# ENGINEERING A MODERN PRODUCTION COMPILER\n',
          '## CHAPTER 1: Lexical Analysis\n',
          '',
          '## CHAPTER 2: SSA Optimization Pipeline\n',
          '',
          '## CHAPTER 3: Register Allocation\n',
          '',
          '## CHAPTER 4: Code Generation\n',
          'End of compiler textbook.',
      ]
      assert chunks[2].initial_prompt_token_count == 24
      assert chunks[2].usage_metadata.prompt_token_count == 24
      assert [c.candidates[0].finish_reason for c in chunks[:-1]] == [None] * (
          len(chunks) - 1
      )
      assert (
          hop1_chunks[2].candidates[0].finish_reason
          == types.FinishReason.CONTINUATION
      )
      assert chunks[-1].candidates[0].finish_reason == types.FinishReason.STOP
      assert chunks[-1].candidates[0].continuation_token is None
      assert chunks[-1].usage_metadata is not None
      assert chunks[-1].initial_prompt_token_count == 24
      assert chunks[-1].usage_metadata.initial_prompt_token_count == 24
      assert (
          chunks[-1].usage_metadata.prompt_token_count
          == 24 + 32792 + 65560 + 98328
      )
      assert chunks[-1].usage_metadata.cached_content_token_count == 40
      assert (
          chunks[-1].usage_metadata.candidates_token_count == 32768 * 3 + 11903
      )
      assert (
          chunks[-1].usage_metadata.thoughts_token_count
          == 400 + 300 + 200 + 100
      )
      assert (
          chunks[-1].usage_metadata.total_token_count
          == 33192 + 65860 + 98528 + 110331
      )
      assert (
          chunks[-1].usage_metadata.traffic_type == types.TrafficType.ON_DEMAND
      )

      first_call_kwargs = mock_raw_stream.call_args_list[0].kwargs
      second_call_kwargs = mock_raw_stream.call_args_list[1].kwargs
      third_call_kwargs = mock_raw_stream.call_args_list[2].kwargs
      fourth_call_kwargs = mock_raw_stream.call_args_list[3].kwargs
      assert first_call_kwargs['config'].continuation_token is None
      assert (
          second_call_kwargs['config'].continuation_token
          == b'AY89a181L6ffhy7s5hBG6S1Zea0DmuUzVC4ByCWe'
      )
      assert (
          third_call_kwargs['config'].continuation_token == b'stream_tok_hop_2'
      )
      assert (
          fourth_call_kwargs['config'].continuation_token == b'stream_tok_hop_3'
      )
      for call_kwargs in (
          second_call_kwargs,
          third_call_kwargs,
          fourth_call_kwargs,
      ):
        assert call_kwargs['contents'] == first_call_kwargs['contents']


def test_models_afc_decoupled_from_continuation_token(mock_api_client):
  """AFC in Models.generate_content and generate_content_stream resumes continuation during thinking, then clears continuation_token on function_response."""
  models_module = models.Models(mock_api_client)

  def get_weather(city: str) -> str:
    """Gets weather for a city."""
    return f'Sunny in {city}'

  turn1_hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='', thought_signature=b'thought_sig')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'afc_tok_1',
          )
      ]
  )
  turn1_hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[
                      types.Part(
                          function_call=types.FunctionCall(
                              name='get_weather', args={'city': 'Mountain View'}
                          )
                      )
                  ],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )
  turn2_final = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='It is Sunny in Mountain View!')],
              ),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )

  # 1. Unary Models.generate_content with AFC + continuation
  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[
          turn1_hop1.model_copy(deep=True),
          turn1_hop2.model_copy(deep=True),
          turn2_final.model_copy(deep=True),
      ],
  ) as mock_raw_gc:
    response = models_module.generate_content(
        model='gemini-2.5-pro',
        contents='What is the weather in Mountain View?',
        config=types.GenerateContentConfig(
            automatic_continuation=True,
            tools=[get_weather],
        ),
    )
    assert mock_raw_gc.call_count == 3
    assert (
        mock_raw_gc.call_args_list[0].kwargs['config'].continuation_token
        is None
    )
    assert (
        mock_raw_gc.call_args_list[1].kwargs['config'].continuation_token
        == b'afc_tok_1'
    )
    assert (
        mock_raw_gc.call_args_list[2].kwargs['config'].continuation_token
        is None
    )
    assert response.text == 'It is Sunny in Mountain View!'

  # 2. Streaming Models.generate_content_stream with AFC + continuation
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          iter([turn1_hop1.model_copy(deep=True)]),
          iter([turn1_hop2.model_copy(deep=True)]),
          iter([turn2_final.model_copy(deep=True)]),
      ],
  ) as mock_raw_stream:
    chunks = list(
        models_module.generate_content_stream(
            model='gemini-2.5-pro',
            contents='What is the weather in Mountain View?',
            config=types.GenerateContentConfig(
                automatic_continuation=True,
                tools=[get_weather],
            ),
        )
    )
    assert mock_raw_stream.call_count == 3
    assert (
        mock_raw_stream.call_args_list[0].kwargs['config'].continuation_token
        is None
    )
    assert (
        mock_raw_stream.call_args_list[1].kwargs['config'].continuation_token
        == b'afc_tok_1'
    )
    assert (
        mock_raw_stream.call_args_list[2].kwargs['config'].continuation_token
        is None
    )
    assert chunks[-1].text == 'It is Sunny in Mountain View!'


@pytest.mark.asyncio
async def test_async_models_generate_content_and_stream_auto_resume(
    mock_api_client,
):
  """AsyncModels auto-resumes on continuation_token across 4 hops in unary, AFC, incompatible-tools, and streaming modes when automatic_continuation=True."""
  models_module = models.AsyncModels(mock_api_client)

  hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async 1. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'async_tok_1',
          )
      ]
  )
  hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async 2. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'async_tok_2',
          )
      ]
  )
  hop3 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async 3. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'async_tok_3',
          )
      ]
  )
  hop4 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async 4.')]
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )

  def _assert_async_unary_4_hops(mock_async_gc):
    assert mock_async_gc.call_count == 4
    c1 = mock_async_gc.call_args_list[0].kwargs
    c2 = mock_async_gc.call_args_list[1].kwargs
    c3 = mock_async_gc.call_args_list[2].kwargs
    c4 = mock_async_gc.call_args_list[3].kwargs
    assert c1['config'].continuation_token is None
    assert c2['config'].continuation_token == b'async_tok_1'
    assert c3['config'].continuation_token == b'async_tok_2'
    assert c4['config'].continuation_token == b'async_tok_3'
    for call_kwargs in (c2, c3, c4):
      assert call_kwargs['contents'] == c1['contents']

  # 1. Test AFC disabled path in AsyncModels.generate_content
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[
          hop1.model_copy(deep=True),
          hop2.model_copy(deep=True),
          hop3.model_copy(deep=True),
          hop4.model_copy(deep=True),
      ],
  ) as mock_async_gc:
    resp = await models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Hello async no afc',
        config=types.GenerateContentConfig(
            automatic_continuation=True,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )
    assert resp.text == 'Async 1. Async 2. Async 3. Async 4.'
    assert resp.candidates[0].finish_reason == types.FinishReason.STOP
    _assert_async_unary_4_hops(mock_async_gc)

  # 2. Test incompatible tools path in AsyncModels.generate_content
  tool_decl = types.Tool(
      function_declarations=[
          types.FunctionDeclaration(name='manual_fn', description='manual')
      ]
  )
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[
          hop1.model_copy(deep=True),
          hop2.model_copy(deep=True),
          hop3.model_copy(deep=True),
          hop4.model_copy(deep=True),
      ],
  ) as mock_async_gc:
    resp = await models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Hello async incompat',
        config=types.GenerateContentConfig(
            automatic_continuation=True, tools=[tool_decl]
        ),
    )
    assert resp.text == 'Async 1. Async 2. Async 3. Async 4.'
    assert resp.candidates[0].finish_reason == types.FinishReason.STOP
    _assert_async_unary_4_hops(mock_async_gc)

  # 3. Test default AFC path in AsyncModels.generate_content
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[
          hop1.model_copy(deep=True),
          hop2.model_copy(deep=True),
          hop3.model_copy(deep=True),
          hop4.model_copy(deep=True),
      ],
  ) as mock_async_gc:
    resp = await models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Hello async default',
        config=types.GenerateContentConfig(automatic_continuation=True),
    )
    assert resp.text == 'Async 1. Async 2. Async 3. Async 4.'
    assert resp.candidates[0].finish_reason == types.FinishReason.STOP
    _assert_async_unary_4_hops(mock_async_gc)

  stream_hop1_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='Async chunk 1. ')]
                  ),
                  continuation_token=b'async_stream_tok_1',
              )
          ],
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              traffic_type=types.TrafficType.ON_DEMAND
          ),
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[
                          types.Part(
                              text='Async chunk 2. ',
                              thought_signature=b'async_sig_1',
                          )
                      ],
                  ),
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ],
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=24,
              cached_content_token_count=12,
              candidates_token_count=32768,
              thoughts_token_count=400,
              total_token_count=33192,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]
  stream_hop2_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='Async chunk 3. ')]
                  ),
                  continuation_token=b'async_stream_tok_2',
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ],
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=32792,
              cached_content_token_count=12,
              candidates_token_count=32768,
              thoughts_token_count=300,
              total_token_count=65860,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]
  stream_hop3_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='Async chunk 4. ')]
                  ),
                  continuation_token=b'async_stream_tok_3',
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ],
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=65560,
              cached_content_token_count=12,
              candidates_token_count=32768,
              thoughts_token_count=200,
              total_token_count=98528,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]
  stream_hop4_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='Async chunk 5.')]
                  ),
                  finish_reason=types.FinishReason.STOP,
              )
          ],
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=98328,
              cached_content_token_count=12,
              candidates_token_count=1024,
              thoughts_token_count=100,
              total_token_count=99452,
              traffic_type=types.TrafficType.ON_DEMAND,
          ),
      ),
  ]

  async def _make_async_stream(chunk_list):
    for c in chunk_list:
      yield c

  def _assert_async_stream_4_hops(mock_async_stream):
    assert mock_async_stream.call_count == 4
    c1 = mock_async_stream.call_args_list[0].kwargs
    c2 = mock_async_stream.call_args_list[1].kwargs
    c3 = mock_async_stream.call_args_list[2].kwargs
    c4 = mock_async_stream.call_args_list[3].kwargs
    assert c1['config'].continuation_token is None
    assert c2['config'].continuation_token == b'async_stream_tok_1'
    assert c3['config'].continuation_token == b'async_stream_tok_2'
    assert c4['config'].continuation_token == b'async_stream_tok_3'
    for call_kwargs in (c2, c3, c4):
      assert call_kwargs['contents'] == c1['contents']

  # 4. Test AFC disabled, incompatible tools, and default AFC paths in AsyncModels.generate_content_stream
  for stream_cfg in (
      types.GenerateContentConfig(
          automatic_continuation=True,
          automatic_function_calling=types.AutomaticFunctionCallingConfig(
              disable=True
          ),
      ),
      types.GenerateContentConfig(
          automatic_continuation=True, tools=[tool_decl]
      ),
      types.GenerateContentConfig(automatic_continuation=True),
  ):
    with mock.patch.object(
        models.AsyncModels,
        '_generate_content_stream',
        new_callable=mock.AsyncMock,
        side_effect=[
            _make_async_stream(stream_hop1_chunks),
            _make_async_stream(stream_hop2_chunks),
            _make_async_stream(stream_hop3_chunks),
            _make_async_stream(stream_hop4_chunks),
        ],
    ) as mock_async_stream:
      chunk_objs = []
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Hello async stream',
          config=stream_cfg,
      ):
        chunk_objs.append(chunk)
      assert [c.text for c in chunk_objs] == [
          'Async chunk 1. ',
          'Async chunk 2. ',
          'Async chunk 3. ',
          'Async chunk 4. ',
          'Async chunk 5.',
      ]
      assert chunk_objs[1].initial_prompt_token_count == 24
      assert [c.candidates[0].finish_reason for c in chunk_objs[:-1]] == [
          None
      ] * (len(chunk_objs) - 1)
      assert (
          chunk_objs[-1].candidates[0].finish_reason == types.FinishReason.STOP
      )
      assert (
          stream_hop1_chunks[1].candidates[0].finish_reason
          == types.FinishReason.CONTINUATION
      )
      assert (
          stream_hop2_chunks[0].candidates[0].finish_reason
          == types.FinishReason.CONTINUATION
      )
      assert chunk_objs[-1].usage_metadata is not None
      assert chunk_objs[-1].initial_prompt_token_count == 24
      assert chunk_objs[-1].usage_metadata.initial_prompt_token_count == 24
      assert (
          chunk_objs[-1].usage_metadata.prompt_token_count
          == 24 + 32792 + 65560 + 98328
      )
      assert chunk_objs[-1].usage_metadata.cached_content_token_count == 48
      assert (
          chunk_objs[-1].usage_metadata.candidates_token_count
          == 32768 * 3 + 1024
      )
      assert (
          chunk_objs[-1].usage_metadata.thoughts_token_count
          == 400 + 300 + 200 + 100
      )
      assert (
          chunk_objs[-1].usage_metadata.total_token_count
          == 33192 + 65860 + 98528 + 99452
      )
      _assert_async_stream_4_hops(mock_async_stream)


@pytest.mark.asyncio
async def test_async_models_automatic_continuation_config_rules(
    mock_api_client,
):
  """Verifies default-enabled, automatic_continuation=False, and max_output_tokens pass-through in AsyncModels."""
  models_module = models.AsyncModels(mock_api_client)

  hop1_max_tokens = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Stopped at async hop 1.')],
              ),
              finish_reason=types.FinishReason.MAX_TOKENS,
              continuation_token=b'token_unused_async',
          )
      ]
  )
  hop1_continuation = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Async Hop 1. ')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'token_async_1',
          )
      ]
  )
  hop2_stop = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Async Hop 2.')],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )

  async def _make_async_stream(chunk_list):
    for c in chunk_list:
      yield c

  # 1. automatic_continuation=False, or finish_reason == MAX_TOKENS -> stops after 1 hop
  for cfg, hop1_resp in (
      (
          types.GenerateContentConfig(automatic_continuation=False),
          hop1_continuation,
      ),
      (
          types.GenerateContentConfig(
              automatic_continuation=True, max_output_tokens=1000
          ),
          hop1_max_tokens,
      ),
      (
          types.GenerateContentConfig(
              automatic_continuation=True,
              max_output_tokens=50000,
              automatic_function_calling=types.AutomaticFunctionCallingConfig(
                  disable=True
              ),
          ),
          hop1_max_tokens,
      ),
  ):
    with mock.patch.object(
        models.AsyncModels,
        '_generate_content',
        new_callable=mock.AsyncMock,
        return_value=hop1_resp.model_copy(deep=True),
    ) as mock_async_gc:
      response = await models_module.generate_content(
          model='gemini-2.5-pro',
          contents='Write a long essay',
          config=cfg,
      )
      assert mock_async_gc.call_count == 1
      assert response.text == hop1_resp.text
      assert (
          response.candidates[0].finish_reason
          == hop1_resp.candidates[0].finish_reason
      )
      assert (
          response.candidates[0].continuation_token
          == hop1_resp.candidates[0].continuation_token
      )

    with mock.patch.object(
        models.AsyncModels,
        '_generate_content_stream',
        new_callable=mock.AsyncMock,
        side_effect=[_make_async_stream([hop1_resp.model_copy(deep=True)])],
    ) as mock_async_stream:
      chunks = []
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long essay stream',
          config=cfg,
      ):
        chunks.append(chunk)
      assert mock_async_stream.call_count == 1
      assert [c.text for c in chunks] == [hop1_resp.text]
      assert (
          chunks[0].candidates[0].finish_reason
          == hop1_resp.candidates[0].finish_reason
      )

  # 2. Default (config=None or automatic_continuation=None) -> continues across hops in unary & stream
  for cfg in (None, types.GenerateContentConfig()):
    with mock.patch.object(
        models.AsyncModels,
        '_generate_content',
        new_callable=mock.AsyncMock,
        side_effect=[
            hop1_continuation.model_copy(deep=True),
            hop2_stop.model_copy(deep=True),
        ],
    ) as mock_async_gc:
      response = await models_module.generate_content(
          model='gemini-2.5-pro',
          contents='Write a long essay default',
          config=cfg,
      )
      assert mock_async_gc.call_count == 2
      assert response.text == 'Async Hop 1. Async Hop 2.'
      assert response.candidates[0].finish_reason == types.FinishReason.STOP
      assert response.candidates[0].continuation_token is None

    with mock.patch.object(
        models.AsyncModels,
        '_generate_content_stream',
        new_callable=mock.AsyncMock,
        side_effect=[
            _make_async_stream([hop1_continuation.model_copy(deep=True)]),
            _make_async_stream([hop2_stop.model_copy(deep=True)]),
        ],
    ) as mock_async_stream:
      chunks = []
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long essay stream default',
          config=cfg,
      ):
        chunks.append(chunk)
      assert mock_async_stream.call_count == 2
      assert [c.text for c in chunks] == ['Async Hop 1. ', 'Async Hop 2.']
      assert chunks[0].candidates[0].finish_reason is None
      assert chunks[1].candidates[0].finish_reason == types.FinishReason.STOP

  # 3. automatic_continuation=True with max_output_tokens set and finish_reason == CONTINUATION -> continues and forwards max_output_tokens as-is
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[
          hop1_continuation.model_copy(deep=True),
          hop2_stop.model_copy(deep=True),
      ],
  ) as mock_async_gc:
    response = await models_module.generate_content(
        model='gemini-2.5-pro',
        contents='Write a long essay',
        config=types.GenerateContentConfig(
            automatic_continuation=True, max_output_tokens=50000
        ),
    )
    assert mock_async_gc.call_count == 2
    assert response.text == 'Async Hop 1. Async Hop 2.'
    assert (
        mock_async_gc.call_args_list[0].kwargs['config'].max_output_tokens
        == 50000
    )
    assert (
        mock_async_gc.call_args_list[1].kwargs['config'].max_output_tokens
        == 50000
    )


@pytest.mark.asyncio
async def test_async_models_afc_decoupled_from_continuation_token(
    mock_api_client,
):
  """AFC in AsyncModels.generate_content and generate_content_stream resumes continuation during thinking, then clears continuation_token on function_response."""
  models_module = models.AsyncModels(mock_api_client)

  def get_weather(city: str) -> str:
    """Gets weather for a city."""
    return f'Sunny in {city}'

  turn1_hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='', thought_signature=b'thought_sig')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'async_afc_tok_1',
          )
      ]
  )
  turn1_hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[
                      types.Part(
                          function_call=types.FunctionCall(
                              name='get_weather', args={'city': 'Mountain View'}
                          )
                      )
                  ],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )
  turn2_final = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='It is Sunny in Mountain View!')],
              ),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )

  # 1. AsyncModels.generate_content with AFC + continuation
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[
          turn1_hop1.model_copy(deep=True),
          turn1_hop2.model_copy(deep=True),
          turn2_final.model_copy(deep=True),
      ],
  ) as mock_async_gc:
    response = await models_module.generate_content(
        model='gemini-2.5-pro',
        contents='What is the weather in Mountain View?',
        config=types.GenerateContentConfig(
            automatic_continuation=True,
            tools=[get_weather],
        ),
    )
    assert mock_async_gc.call_count == 3
    assert (
        mock_async_gc.call_args_list[0].kwargs['config'].continuation_token
        is None
    )
    assert (
        mock_async_gc.call_args_list[1].kwargs['config'].continuation_token
        == b'async_afc_tok_1'
    )
    assert (
        mock_async_gc.call_args_list[2].kwargs['config'].continuation_token
        is None
    )
    assert response.text == 'It is Sunny in Mountain View!'

  async def _make_async_stream(chunk_list):
    for c in chunk_list:
      yield c

  # 2. AsyncModels.generate_content_stream with AFC + continuation
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream([turn1_hop1.model_copy(deep=True)]),
          _make_async_stream([turn1_hop2.model_copy(deep=True)]),
          _make_async_stream([turn2_final.model_copy(deep=True)]),
      ],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='What is the weather in Mountain View?',
        config=types.GenerateContentConfig(
            automatic_continuation=True,
            tools=[get_weather],
        ),
    ):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 3
    assert (
        mock_async_stream.call_args_list[0].kwargs['config'].continuation_token
        is None
    )
    assert (
        mock_async_stream.call_args_list[1].kwargs['config'].continuation_token
        == b'async_afc_tok_1'
    )
    assert (
        mock_async_stream.call_args_list[2].kwargs['config'].continuation_token
        is None
    )
    assert chunks[-1].text == 'It is Sunny in Mountain View!'


def test_models_generate_content_stream_recovers_from_midstream_checkpoint_error(
    mock_api_client,
):
  """Streaming Models.generate_content_stream resumes when a hop ends or errors with finish_reason=None after receiving a continuation_token."""
  models_module = models.Models(mock_api_client)

  chunk_pre_32k = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Intro. ')]
              ),
          )
      ]
  )
  chunk_ckpt_35k = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Checkpoint 35k. ')]
              ),
              continuation_token=b'v2_ckpt_35k',
          )
      ]
  )
  chunk_ckpt_40k = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Checkpoint 40k. ')]
              ),
              continuation_token=b'v2_ckpt_40k',
          )
      ]
  )
  chunk_hop2_final = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Resumed and completed.')],
              ),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )

  def _failing_hop(chunks_before_error, exc=None):
    for c in chunks_before_error:
      yield c.model_copy(deep=True)
    if exc is not None:
      raise exc

  server_503 = errors.ServerError(
      503,
      {
          'error': {
              'code': 503,
              'message': 'Service unavailable',
              'status': 'UNAVAILABLE',
          }
      },
  )

  # 1. Recovers from mid-stream exception or premature EOF (finish_reason=None) using latest v2 checkpoint token
  for hop1_exc in (server_503, httpx.ReadTimeout('read timed out'), None):
    with mock.patch.object(
        models.Models,
        '_generate_content_stream',
        side_effect=[
            _failing_hop(
                [chunk_pre_32k, chunk_ckpt_35k, chunk_ckpt_40k],
                hop1_exc,
            ),
            iter([chunk_hop2_final.model_copy(deep=True)]),
        ],
    ) as mock_raw_stream:
      chunks = list(
          models_module.generate_content_stream(
              model='gemini-2.5-pro',
              contents='Write a long book',
          )
      )
      assert mock_raw_stream.call_count == 2
      assert (
          mock_raw_stream.call_args_list[0].kwargs['config'] is None
          or mock_raw_stream.call_args_list[0]
          .kwargs['config']
          .continuation_token
          is None
      )
      assert (
          mock_raw_stream.call_args_list[1].kwargs['config'].continuation_token
          == b'v2_ckpt_40k'
      )
      assert [c.text for c in chunks] == [
          'Intro. ',
          'Checkpoint 35k. ',
          'Checkpoint 40k. ',
          'Resumed and completed.',
      ]
      assert chunks[-1].candidates[0].finish_reason == types.FinishReason.STOP

  # 2. Error before any checkpoint token in the hop -> raises without retrying
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[_failing_hop([chunk_pre_32k], server_503)],
  ) as mock_raw_stream:
    stream = models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
    )
    assert next(stream).text == 'Intro. '
    with pytest.raises(errors.ServerError):
      next(stream)
    assert mock_raw_stream.call_count == 1

  # 3. Error when automatic_continuation=False -> raises even if checkpoint token was emitted
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[_failing_hop([chunk_ckpt_35k], server_503)],
  ) as mock_raw_stream:
    stream = models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
        config=types.GenerateContentConfig(automatic_continuation=False),
    )
    assert next(stream).text == 'Checkpoint 35k. '
    with pytest.raises(errors.ServerError):
      next(stream)
    assert mock_raw_stream.call_count == 1

  # 4. Consecutive connection drops on resumed hops before any new checkpoint
  # chunk is emitted -> retries from the hop's start token a bounded number of
  # times, then raises without infinite looping.
  max_retries = _extra_utils.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  dropped = httpx.RemoteProtocolError('peer closed connection')
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[_failing_hop([chunk_ckpt_35k], server_503)]
      + [_failing_hop([], dropped) for _ in range(max_retries + 1)],
  ) as mock_raw_stream:
    stream = models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
    )
    assert next(stream).text == 'Checkpoint 35k. '
    with pytest.raises(httpx.RemoteProtocolError):
      next(stream)
    assert mock_raw_stream.call_count == max_retries + 2
    for call in mock_raw_stream.call_args_list[1:]:
      assert call.kwargs['config'].continuation_token == b'v2_ckpt_35k'

  # 4b. A resumed hop's request is rejected before streaming anything (HTTP
  # error status) -> raised without retrying; retrying rejected requests is the
  # job of HttpOptions.retry_options.
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          _failing_hop([chunk_ckpt_35k], server_503),
          _failing_hop([], server_503),
      ],
  ) as mock_raw_stream:
    stream = models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
    )
    assert next(stream).text == 'Checkpoint 35k. '
    with pytest.raises(errors.ServerError):
      next(stream)
    assert mock_raw_stream.call_count == 2

  # 4c. A connection drop followed by retries that end cleanly without progress
  # -> the drop is re-raised when the stream gives up, not hidden.
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          _failing_hop([chunk_ckpt_35k], server_503),
          _failing_hop([], dropped),
      ]
      + [_failing_hop([]) for _ in range(max_retries)],
  ) as mock_raw_stream:
    stream = models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
    )
    assert next(stream).text == 'Checkpoint 35k. '
    with pytest.raises(httpx.RemoteProtocolError):
      next(stream)
    assert mock_raw_stream.call_count == max_retries + 2

  # 5. Error after STOP finish_reason in same hop -> stale checkpoint token was cleared, so does not resume
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          _failing_hop([chunk_ckpt_35k, chunk_hop2_final], server_503),
      ],
  ) as mock_raw_stream:
    stream = models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
    )
    assert next(stream).text == 'Checkpoint 35k. '
    assert next(stream).text == 'Resumed and completed.'
    with pytest.raises(errors.ServerError):
      next(stream)
    assert mock_raw_stream.call_count == 1

  # 6. Resumed hop drops (or closes cleanly) before emitting any content or
  # checkpoint (e.g. during server prefill) -> retries from the token the hop
  # was started with. (A rejected request is not retried; see 4b.)
  chunk_hop1_boundary = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Hop 1 end. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'v2_hop1_end',
          )
      ]
  )
  for hop2_exc in (httpx.RemoteProtocolError('peer closed'), None):
    with mock.patch.object(
        models.Models,
        '_generate_content_stream',
        side_effect=[
            iter([chunk_hop1_boundary.model_copy(deep=True)]),
            _failing_hop([], hop2_exc),
            iter([chunk_hop2_final.model_copy(deep=True)]),
        ],
    ) as mock_raw_stream:
      chunks = list(
          models_module.generate_content_stream(
              model='gemini-2.5-pro',
              contents='Write a long book',
          )
      )
      assert mock_raw_stream.call_count == 3
      assert [
          call.kwargs['config'].continuation_token
          for call in mock_raw_stream.call_args_list[1:]
      ] == [b'v2_hop1_end', b'v2_hop1_end']
      assert [c.text for c in chunks] == [
          'Hop 1 end. ',
          'Resumed and completed.',
      ]
      assert chunks[0].candidates[0].finish_reason is None
      assert chunks[-1].candidates[0].finish_reason == types.FinishReason.STOP

  # 6b. Resumed hop drops AFTER yielding candidate content but before its first
  # checkpoint -> does NOT retry from hop_start_token (which would duplicate
  # already-yielded text) and surfaces the error immediately.
  chunk_hop2_pre_ckpt = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Hop 2 intro. ')]
              ),
          )
      ]
  )
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          iter([chunk_hop1_boundary.model_copy(deep=True)]),
          _failing_hop(
              [chunk_hop2_pre_ckpt], httpx.RemoteProtocolError('peer closed')
          ),
      ],
  ) as mock_raw_stream:
    received = []
    with pytest.raises(httpx.RemoteProtocolError):
      for chunk in models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book',
      ):
        received.append(chunk.text)
    assert mock_raw_stream.call_count == 2
    assert received == ['Hop 1 end. ', 'Hop 2 intro. ']

  # 7. Resumed hop ends with finish_reason=CONTINUATION but no new token ->
  # stops instead of replaying the hop's start token.
  chunk_continuation_no_token = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='No token. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
          )
      ]
  )
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          iter([chunk_hop1_boundary.model_copy(deep=True)]),
          iter([chunk_continuation_no_token.model_copy(deep=True)]),
      ],
  ) as mock_raw_stream:
    chunks = list(
        models_module.generate_content_stream(
            model='gemini-2.5-pro',
            contents='Write a long book',
        )
    )
    assert mock_raw_stream.call_count == 2
    assert chunks[-1].candidates[0].finish_reason == (
        types.FinishReason.CONTINUATION
    )


@pytest.mark.asyncio
async def test_async_models_generate_content_stream_recovers_from_midstream_checkpoint_error(
    mock_api_client,
):
  """AsyncModels.generate_content_stream resumes when a hop ends or errors with finish_reason=None after receiving a continuation_token."""
  models_module = models.AsyncModels(mock_api_client)

  chunk_pre_32k = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async Intro. ')]
              ),
          )
      ]
  )
  chunk_ckpt_35k = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async Ckpt 35k. ')]
              ),
              continuation_token=b'async_v2_ckpt_35k',
          )
      ]
  )
  chunk_ckpt_40k = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async Ckpt 40k. ')]
              ),
              continuation_token=b'async_v2_ckpt_40k',
          )
      ]
  )
  chunk_hop2_final = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Async resumed and completed.')],
              ),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )

  async def _make_async_stream(chunk_list, exc=None):
    for c in chunk_list:
      yield c.model_copy(deep=True)
    if exc is not None:
      raise exc

  server_504 = errors.ServerError(
      504,
      {
          'error': {
              'code': 504,
              'message': 'Deadline exceeded',
              'status': 'DEADLINE_EXCEEDED',
          }
      },
  )

  # 1. Recovers from mid-stream exception or premature EOF (finish_reason=None) using latest v2 checkpoint token
  for hop1_exc in (server_504, httpx.ReadTimeout('async read timed out'), None):
    with mock.patch.object(
        models.AsyncModels,
        '_generate_content_stream',
        new_callable=mock.AsyncMock,
        side_effect=[
            _make_async_stream(
                [chunk_pre_32k, chunk_ckpt_35k, chunk_ckpt_40k],
                hop1_exc,
            ),
            _make_async_stream([chunk_hop2_final]),
        ],
    ) as mock_async_stream:
      chunks = []
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
      ):
        chunks.append(chunk)
      assert mock_async_stream.call_count == 2
      assert (
          mock_async_stream.call_args_list[1]
          .kwargs['config']
          .continuation_token
          == b'async_v2_ckpt_40k'
      )
      assert [c.text for c in chunks] == [
          'Async Intro. ',
          'Async Ckpt 35k. ',
          'Async Ckpt 40k. ',
          'Async resumed and completed.',
      ]
      assert chunks[-1].candidates[0].finish_reason == types.FinishReason.STOP

  # 2. Error before any checkpoint token in the hop -> raises without retrying
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_make_async_stream([chunk_pre_32k], server_504)],
  ) as mock_async_stream:
    received = []
    with pytest.raises(errors.ServerError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
      ):
        received.append(chunk.text)
    assert received == ['Async Intro. ']
    assert mock_async_stream.call_count == 1

  # 3. Error when automatic_continuation=False -> raises even if checkpoint token was emitted
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_make_async_stream([chunk_ckpt_35k], server_504)],
  ) as mock_async_stream:
    received = []
    with pytest.raises(errors.ServerError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
          config=types.GenerateContentConfig(automatic_continuation=False),
      ):
        received.append(chunk.text)
    assert received == ['Async Ckpt 35k. ']
    assert mock_async_stream.call_count == 1

  # 4. Consecutive connection drops on resumed hops before any new checkpoint
  # chunk is emitted -> retries from the hop's start token a bounded number of
  # times, then raises without infinite looping.
  max_retries = _extra_utils.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  dropped = httpx.RemoteProtocolError('peer closed connection')
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_make_async_stream([chunk_ckpt_35k], server_504)]
      + [_make_async_stream([], dropped) for _ in range(max_retries + 1)],
  ) as mock_async_stream:
    received = []
    with pytest.raises(httpx.RemoteProtocolError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
      ):
        received.append(chunk.text)
    assert received == ['Async Ckpt 35k. ']
    assert mock_async_stream.call_count == max_retries + 2
    for call in mock_async_stream.call_args_list[1:]:
      assert call.kwargs['config'].continuation_token == b'async_v2_ckpt_35k'

  # 4b. A resumed hop's request is rejected before streaming anything -> raised
  # without retrying (left to HttpOptions.retry_options).
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream([chunk_ckpt_35k], server_504),
          _make_async_stream([], server_504),
      ],
  ) as mock_async_stream:
    received = []
    with pytest.raises(errors.ServerError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
      ):
        received.append(chunk.text)
    assert received == ['Async Ckpt 35k. ']
    assert mock_async_stream.call_count == 2

  # 4c. A connection drop followed by retries that end cleanly without progress
  # -> the drop is re-raised when the stream gives up, not hidden.
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream([chunk_ckpt_35k], server_504),
          _make_async_stream([], dropped),
      ]
      + [_make_async_stream([]) for _ in range(max_retries)],
  ) as mock_async_stream:
    received = []
    with pytest.raises(httpx.RemoteProtocolError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
      ):
        received.append(chunk.text)
    assert received == ['Async Ckpt 35k. ']
    assert mock_async_stream.call_count == max_retries + 2

  # 5. Error after STOP finish_reason in same hop -> stale checkpoint token was cleared, so does not resume
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream([chunk_ckpt_35k, chunk_hop2_final], server_504),
      ],
  ) as mock_async_stream:
    received = []
    with pytest.raises(errors.ServerError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
      ):
        received.append(chunk.text)
    assert received == ['Async Ckpt 35k. ', 'Async resumed and completed.']
    assert mock_async_stream.call_count == 1

  # 6. Resumed hop drops before emitting any content or checkpoint -> retries
  # from the token the hop was started with.
  chunk_hop1_boundary = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async hop 1 end. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'async_v2_hop1_end',
          )
      ]
  )
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream([chunk_hop1_boundary]),
          _make_async_stream([], httpx.RemoteProtocolError('peer closed')),
          _make_async_stream([chunk_hop2_final]),
      ],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book async',
    ):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 3
    assert [
        call.kwargs['config'].continuation_token
        for call in mock_async_stream.call_args_list[1:]
    ] == [b'async_v2_hop1_end', b'async_v2_hop1_end']
    assert [c.text for c in chunks] == [
        'Async hop 1 end. ',
        'Async resumed and completed.',
    ]

  # 6b. Resumed hop drops AFTER yielding candidate content but before its first
  # checkpoint -> does NOT retry from hop_start_token and raises immediately.
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream([chunk_hop1_boundary]),
          _make_async_stream(
              [chunk_pre_32k], httpx.RemoteProtocolError('peer closed')
          ),
      ],
  ) as mock_async_stream:
    received = []
    with pytest.raises(httpx.RemoteProtocolError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Write a long book async',
      ):
        received.append(chunk.text)
    assert mock_async_stream.call_count == 2
    assert received == ['Async hop 1 end. ', 'Async Intro. ']



def test_next_stream_continuation_token():
  """StreamContinuation picks the token for the next streaming hop."""
  max_retries = _extra_utils.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS

  def nxt(
      *,
      hop_start_token,
      hop_token,
      finish_reason,
      reconnects_without_progress,
      has_prompt_feedback=False,
      hop_has_yielded_content=False,
  ):
    state = _extra_utils.StreamContinuation(config=None)
    state._reconnects_without_progress = reconnects_without_progress
    # `type(state._hop)` rather than `_extra_utils._StreamHop`: the private
    # `_extra_utils` module re-exports with a wildcard import, which skips
    # underscore-prefixed names.
    state._hop = type(state._hop)(
        start_token=hop_start_token,
        token=hop_token,
        finish_reason=finish_reason,
        has_prompt_feedback=has_prompt_feedback,
        has_yielded_content=hop_has_yielded_content,
    )
    return state._next_resume_token()

  # New checkpoint token received -> resume from it and reset the retry count.
  assert nxt(
      hop_start_token=b'a',
      hop_token=b'b',
      finish_reason=None,
      reconnects_without_progress=2,
      hop_has_yielded_content=True,
  ) == (b'b', 0)
  assert nxt(
      hop_start_token=None,
      hop_token=b'b',
      finish_reason=types.FinishReason.CONTINUATION,
      reconnects_without_progress=0,
      hop_has_yielded_content=True,
  ) == (b'b', 0)

  # Dropped before a new checkpoint and before yielding content -> retry from
  # the hop's start token.
  for hop_token in (None, b'a'):
    assert nxt(
        hop_start_token=b'a',
        hop_token=hop_token,
        finish_reason=None,
        reconnects_without_progress=0,
    ) == (b'a', 1)

  # Dropped before a new checkpoint AFTER yielding content -> do not replay
  # hop_start_token (would duplicate yielded content).
  for hop_token in (None, b'a'):
    assert nxt(
        hop_start_token=b'a',
        hop_token=hop_token,
        finish_reason=None,
        reconnects_without_progress=0,
        hop_has_yielded_content=True,
    ) == (None, 0)

  # Initial request dropped before any checkpoint -> nothing to resume from.
  assert nxt(
      hop_start_token=None,
      hop_token=None,
      finish_reason=None,
      reconnects_without_progress=0,
  ) == (None, 1)

  # Retry budget exhausted -> stop.
  assert nxt(
      hop_start_token=b'a',
      hop_token=None,
      finish_reason=None,
      reconnects_without_progress=max_retries,
  ) == (None, max_retries)

  # Terminal finish_reason without a new token -> stop, never replay the hop.
  for finish_reason in (
      types.FinishReason.STOP,
      types.FinishReason.CONTINUATION,
  ):
    for hop_token in (None, b'a'):
      assert nxt(
          hop_start_token=b'a',
          hop_token=hop_token,
          finish_reason=finish_reason,
          reconnects_without_progress=0,
      ) == (None, 0)

  # Prompt feedback received -> stop immediately, never replay the hop.
  for hop_token in (None, b'a', b'b'):
    assert nxt(
        hop_start_token=b'a',
        hop_token=hop_token,
        finish_reason=None,
        reconnects_without_progress=0,
        has_prompt_feedback=True,
    ) == (None, 0)
  assert not _extra_utils.can_resume_stream(
      True, b'a', None, has_prompt_feedback=True
  )


def test_stream_continuation_hop2_prompt_feedback_does_not_retry(
    mock_api_client,
):
  """Sync generate_content_stream stops cleanly without retrying when a resumed hop yields prompt_feedback."""
  models_module = models.Models(mock_api_client)
  chunk_hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Hop 1. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_1',
          )
      ]
  )
  chunk_hop2_pf = types.GenerateContentResponse(
      candidates=None,
      prompt_feedback=types.GenerateContentResponsePromptFeedback(
          block_reason=types.BlockedReason.SAFETY
      ),
  )
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          iter([chunk_hop1.model_copy(deep=True)]),
          iter([chunk_hop2_pf.model_copy(deep=True)]),
      ],
  ) as mock_raw_stream:
    chunks = list(
        models_module.generate_content_stream(
            model='gemini-2.5-pro',
            contents='Write a long book',
        )
    )
    assert mock_raw_stream.call_count == 2
    assert len(chunks) == 2
    assert chunks[0].text == 'Hop 1. '
    assert chunks[1].prompt_feedback is not None
    assert chunks[1].prompt_feedback.block_reason == types.BlockedReason.SAFETY


@pytest.mark.asyncio
async def test_async_stream_continuation_hop2_prompt_feedback_does_not_retry(
    mock_api_client,
):
  """Async generate_content_stream stops cleanly without retrying when a resumed hop yields prompt_feedback."""
  models_module = models.AsyncModels(mock_api_client)
  chunk_hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async Hop 1. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'async_tok_1',
          )
      ]
  )
  chunk_hop2_pf = types.GenerateContentResponse(
      candidates=None,
      prompt_feedback=types.GenerateContentResponsePromptFeedback(
          block_reason=types.BlockedReason.SAFETY
      ),
  )

  async def _make_async_stream(chunk_list):
    for c in chunk_list:
      yield c.model_copy(deep=True)

  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream([chunk_hop1]),
          _make_async_stream([chunk_hop2_pf]),
      ],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book async',
    ):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 2
    assert len(chunks) == 2
    assert chunks[0].text == 'Async Hop 1. '
    assert chunks[1].prompt_feedback is not None
    assert chunks[1].prompt_feedback.block_reason == types.BlockedReason.SAFETY


def test_stream_continuation_eof_without_finish_reason_ends_normally_after_retries(
    mock_api_client,
):
  """Sync generate_content_stream ends normally (no SDK-invented error) if a resumed continuation stream closes cleanly without finish_reason after exhausting retries."""
  models_module = models.Models(mock_api_client)
  chunk_hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Hop 1. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_1',
          )
      ]
  )
  max_retries = _extra_utils.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[iter([chunk_hop1.model_copy(deep=True)])]
      + [iter([]) for _ in range(max_retries + 1)],
  ) as mock_raw_stream:
    received = []
    # No exception: the API returned no error, so the stream ends normally.
    for chunk in models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
    ):
      received.append(chunk.text)
    assert received == ['Hop 1. ']
    assert mock_raw_stream.call_count == 1 + 1 + max_retries


@pytest.mark.asyncio
async def test_async_stream_continuation_eof_without_finish_reason_ends_normally_after_retries(
    mock_api_client,
):
  """Async generate_content_stream ends normally (no SDK-invented error) if a resumed continuation stream closes cleanly without finish_reason after exhausting retries."""
  models_module = models.AsyncModels(mock_api_client)
  chunk_hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async Hop 1. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'async_tok_1',
          )
      ]
  )

  async def _make_async_stream(chunk_list):
    for c in chunk_list:
      yield c.model_copy(deep=True)

  max_retries = _extra_utils.MAX_STREAM_RECONNECTS_WITHOUT_PROGRESS
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_make_async_stream([chunk_hop1])]
      + [_make_async_stream([]) for _ in range(max_retries + 1)],
  ) as mock_async_stream:
    received = []
    # No exception: the API returned no error, so the stream ends normally.
    async for chunk in await models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book async',
    ):
      received.append(chunk.text)
    assert received == ['Async Hop 1. ']
    assert mock_async_stream.call_count == 1 + 1 + max_retries


TOK_UNARY_HOP1_B64 = base64.b64encode(b'tok_unary_hop1').decode('ascii')
TOK_STREAM_CP1_B64 = base64.b64encode(b'tok_stream_cp1').decode('ascii')
TOK_STREAM_FINAL_B64 = base64.b64encode(b'tok_stream_final').decode('ascii')
TOK_STREAM_HOP1_B64 = base64.b64encode(b'tok_stream_hop1').decode('ascii')
TOK_STREAM_HOP2_B64 = base64.b64encode(b'tok_stream_hop2').decode('ascii')

UNARY_HOP1_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [
                {'text': 'Thinking step 1...', 'thought': True},
                {'text': 'Hello '},
            ],
        },
        'finishReason': 'CONTINUATION',
        'continuationToken': TOK_UNARY_HOP1_B64,
        'groundingMetadata': {
            'webSearchQueries': ['query1'],
            'searchEntryPoint': {'renderedContent': '<div>hop1</div>'},
            'groundingChunks': [
                {'web': {'uri': 'https://source1.example', 'title': 'Source 1'}}
            ],
            'groundingSupports': [{
                'groundingChunkIndices': [0],
                'segment': {'partIndex': 1, 'text': 'Hello '},
            }],
        },
        'citationMetadata': {
            'citationSources': [{
                'startIndex': 0,
                'endIndex': 5,
                'uri': 'https://a.example',
            }]
        },
    }],
    'usageMetadata': {
        'promptTokenCount': 120,
        'candidatesTokenCount': 50,
        'thoughtsTokenCount': 30,
        'totalTokenCount': 200,
        'cachedContentTokenCount': 40,
        'toolUsePromptTokenCount': 10,
        'trafficType': 'ON_DEMAND',
    },
}

UNARY_HOP2_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [
                {'text': 'world!'},
            ],
        },
        'finishReason': 'STOP',
        'groundingMetadata': {
            'webSearchQueries': ['query2'],
            'searchEntryPoint': {'renderedContent': '<div>hop2</div>'},
            'groundingChunks': [
                {'web': {'uri': 'https://source2.example', 'title': 'Source 2'}}
            ],
            'groundingSupports': [{
                'groundingChunkIndices': [0],
                'segment': {'partIndex': 0, 'text': 'world!'},
            }],
        },
        'citationMetadata': {
            'citationSources': [{
                'startIndex': 6,
                'endIndex': 12,
                'uri': 'https://b.example',
            }]
        },
    }],
    'usageMetadata': {
        'promptTokenCount': 200,
        'candidatesTokenCount': 25,
        'thoughtsTokenCount': 15,
        'totalTokenCount': 240,
        'cachedContentTokenCount': 180,
        'toolUsePromptTokenCount': 5,
        'trafficType': 'ON_DEMAND',
    },
}

STREAM_HOP1_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Stream 1 '}],
        },
        'finishReason': 'CONTINUATION',
        'continuationToken': TOK_STREAM_HOP1_B64,
    }],
    'usageMetadata': {
        'promptTokenCount': 150,
        'candidatesTokenCount': 64000,
        'totalTokenCount': 64150,
    },
}

STREAM_HOP2_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Stream 2!'}],
        },
        'finishReason': 'STOP',
        'continuationToken': TOK_STREAM_HOP2_B64,
    }],
    'usageMetadata': {
        'promptTokenCount': 64150,
        'candidatesTokenCount': 1200,
        'totalTokenCount': 65350,
    },
}

STREAM_DROP_PART_A_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Part A '}],
        },
    }],
    'usageMetadata': {
        'promptTokenCount': 100,
        'candidatesTokenCount': 10,
        'totalTokenCount': 110,
    },
}

STREAM_DROP_PART_B_CKPT_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Part B '}],
        },
        'continuationToken': TOK_STREAM_CP1_B64,
    }],
    'usageMetadata': {
        'promptTokenCount': 100,
        'candidatesTokenCount': 35000,
        'totalTokenCount': 35100,
    },
}

STREAM_DROP_PART_C_STOP_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Part C!'}],
        },
        'finishReason': 'STOP',
        'continuationToken': TOK_STREAM_FINAL_B64,
    }],
    'usageMetadata': {
        'promptTokenCount': 35100,
        'candidatesTokenCount': 500,
        'totalTokenCount': 35600,
    },
}

STREAM_UNCHECKPOINTED_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Uncheckpointed '}],
        },
    }],
    'usageMetadata': {
        'promptTokenCount': 100,
        'candidatesTokenCount': 10,
        'totalTokenCount': 110,
    },
}

STREAM_STALE_CHUNK1_CKPT_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Chunk 1 checkpoint '}],
        },
        'continuationToken': TOK_STREAM_CP1_B64,
    }],
    'usageMetadata': {
        'promptTokenCount': 50,
        'candidatesTokenCount': 200,
        'totalTokenCount': 250,
    },
}

STREAM_STALE_CHUNK2_STOP_PAYLOAD = {
    'candidates': [{
        'index': 0,
        'content': {
            'role': 'model',
            'parts': [{'text': 'Chunk 2 stop'}],
        },
        'finishReason': 'STOP',
    }],
    'usageMetadata': {
        'promptTokenCount': 50,
        'candidatesTokenCount': 205,
        'totalTokenCount': 255,
    },
}


def _json_http_response(payload: dict[str, object]) -> types.HttpResponse:
  return types.HttpResponse(headers={}, body=json.dumps(payload))


def _stream_http_responses(
    payloads: list[dict[str, object]], exc: Exception | None = None
):
  for payload in payloads:
    yield _json_http_response(payload)
  if exc is not None:
    raise exc


async def _async_stream_http_responses(
    payloads: list[dict[str, object]], exc: Exception | None = None
):
  for payload in payloads:
    yield _json_http_response(payload)
  if exc is not None:
    raise exc


def test_e2e_unary_multihop_aggregation_and_usage():
  """Verifies unary multi-hop request/response serialization, aggregation, and usage."""
  test_client = client.Client(api_key='test-key')
  with mock.patch.object(
      client.BaseApiClient,
      'request',
      side_effect=[
          _json_http_response(UNARY_HOP1_PAYLOAD),
          _json_http_response(UNARY_HOP2_PAYLOAD),
      ],
  ) as mock_request:
    resp = test_client.models.generate_content(
        model='gemini-2.5-pro',
        contents='Hello',
    )
  cand = resp.candidates[0]
  u = resp.usage_metadata

  assert mock_request.call_count == 2
  assert 'continuationToken' not in mock_request.call_args_list[0].args[2]
  assert 'automaticContinuation' not in mock_request.call_args_list[0].args[2]
  assert (
      mock_request.call_args_list[1].args[2].get('continuationToken')
      == TOK_UNARY_HOP1_B64
  )
  assert 'automaticContinuation' not in mock_request.call_args_list[1].args[2]
  assert resp.text == 'Hello world!'
  assert cand.finish_reason == types.FinishReason.STOP
  assert u.initial_prompt_token_count == 120
  assert u.prompt_token_count == 320
  assert u.candidates_token_count == 75
  assert u.thoughts_token_count == 45
  assert u.cached_content_token_count == 220
  assert u.tool_use_prompt_token_count == 15
  assert u.total_token_count == 440
  assert cand.grounding_metadata.web_search_queries == ['query1', 'query2']
  assert (
      cand.grounding_metadata.search_entry_point.rendered_content
      == '<div>hop2</div>'
  )
  gm = cand.grounding_metadata
  assert len(gm.grounding_chunks) == 2
  assert len(gm.grounding_supports) == 2
  last_support = gm.grounding_supports[-1]
  assert last_support.grounding_chunk_indices == [1]
  assert (
      gm.grounding_chunks[last_support.grounding_chunk_indices[0]].web.uri
      == 'https://source2.example'
  )
  assert last_support.segment.part_index == 2
  assert cand.content.parts[last_support.segment.part_index].text == 'world!'
  assert len(cand.citation_metadata.citations) == 2


def test_e2e_unary_automatic_continuation_false():
  """Verifies automatic_continuation=False stops after one hop and decodes token."""
  test_client = client.Client(api_key='test-key')
  with mock.patch.object(
      client.BaseApiClient,
      'request',
      return_value=_json_http_response(UNARY_HOP1_PAYLOAD),
  ) as mock_request:
    resp_no_cont = test_client.models.generate_content(
        model='gemini-2.5-pro',
        contents='Hello',
        config=types.GenerateContentConfig(automatic_continuation=False),
    )

  assert mock_request.call_count == 1
  assert 'automaticContinuation' not in mock_request.call_args_list[0].args[2]
  assert (
      resp_no_cont.candidates[0].finish_reason
      == types.FinishReason.CONTINUATION
  )
  assert resp_no_cont.candidates[0].continuation_token == b'tok_unary_hop1'
  assert resp_no_cont.usage_metadata.initial_prompt_token_count == 120
  assert resp_no_cont.usage_metadata.prompt_token_count == 120


def test_e2e_streaming_continuation_boundary():
  """Verifies streaming continuation clears intermediate finish_reason across hops."""
  test_client = client.Client(api_key='test-key')
  with mock.patch.object(
      client.BaseApiClient,
      'request_streamed',
      side_effect=[
          _stream_http_responses([STREAM_HOP1_PAYLOAD]),
          _stream_http_responses([STREAM_HOP2_PAYLOAD]),
      ],
  ) as mock_stream:
    chunks = list(
        test_client.models.generate_content_stream(
            model='gemini-2.5-pro',
            contents='Stream test',
        )
    )

  assert mock_stream.call_count == 2
  assert (
      mock_stream.call_args_list[1].args[2].get('continuationToken')
      == TOK_STREAM_HOP1_B64
  )
  assert len(chunks) == 2
  assert chunks[0].candidates[0].finish_reason is None
  assert chunks[1].candidates[0].finish_reason == types.FinishReason.STOP
  assert ''.join(c.text for c in chunks) == 'Stream 1 Stream 2!'
  assert chunks[0].usage_metadata.initial_prompt_token_count == 150
  assert chunks[1].usage_metadata.initial_prompt_token_count == 150


def test_e2e_streaming_drop_recovery_after_checkpoint():
  """Verifies streaming recovery when request_streamed drops after a checkpoint."""
  test_client = client.Client(api_key='test-key')
  with mock.patch.object(
      client.BaseApiClient,
      'request_streamed',
      side_effect=[
          _stream_http_responses(
              [STREAM_DROP_PART_A_PAYLOAD, STREAM_DROP_PART_B_CKPT_PAYLOAD],
              exc=httpx.RemoteProtocolError('peer closed connection'),
          ),
          _stream_http_responses([STREAM_DROP_PART_C_STOP_PAYLOAD]),
      ],
  ) as mock_stream:
    drop_chunks = list(
        test_client.models.generate_content_stream(
            model='gemini-2.5-pro',
            contents='Drop test',
        )
    )

  assert mock_stream.call_count == 2
  assert (
      mock_stream.call_args_list[1].args[2].get('continuationToken')
      == TOK_STREAM_CP1_B64
  )
  assert len(drop_chunks) == 3
  assert ''.join(c.text for c in drop_chunks) == 'Part A Part B Part C!'
  assert drop_chunks[-1].candidates[0].finish_reason == types.FinishReason.STOP
  assert all(
      c.usage_metadata.initial_prompt_token_count == 100 for c in drop_chunks
  )


def test_e2e_streaming_drop_before_checkpoint_raises():
  """Verifies streaming error before any checkpoint token propagates without retry."""
  test_client = client.Client(api_key='test-key')
  yielded_before_err = []
  with mock.patch.object(
      client.BaseApiClient,
      'request_streamed',
      side_effect=[
          _stream_http_responses(
              [STREAM_UNCHECKPOINTED_PAYLOAD],
              exc=httpx.RemoteProtocolError('peer closed connection'),
          )
      ],
  ) as mock_stream:
    with pytest.raises(httpx.RemoteProtocolError):
      for ch in test_client.models.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Drop before checkpoint test',
      ):
        yielded_before_err.append(ch.text)

  assert mock_stream.call_count == 1
  assert yielded_before_err == ['Uncheckpointed ']


def test_e2e_streaming_stale_token_discard_on_stop():
  """Verifies an earlier checkpoint token in the same hop is discarded on STOP."""
  test_client = client.Client(api_key='test-key')
  with mock.patch.object(
      client.BaseApiClient,
      'request_streamed',
      side_effect=[
          _stream_http_responses([
              STREAM_STALE_CHUNK1_CKPT_PAYLOAD,
              STREAM_STALE_CHUNK2_STOP_PAYLOAD,
          ])
      ],
  ) as mock_stream:
    chunks = list(
        test_client.models.generate_content_stream(
            model='gemini-2.5-pro',
            contents='Stale token test',
        )
    )

  assert mock_stream.call_count == 1
  assert len(chunks) == 2
  assert chunks[0].text == 'Chunk 1 checkpoint '
  assert chunks[1].text == 'Chunk 2 stop'
  assert chunks[1].candidates[0].finish_reason == types.FinishReason.STOP
  assert chunks[1].candidates[0].continuation_token is None


def test_e2e_chat_unary_vs_stream_history():
  """Verifies Chat history accumulation across multi-hop unary and stream calls."""
  test_client = client.Client(api_key='test-key')
  with (
      mock.patch.object(
          client.BaseApiClient,
          'request',
          side_effect=[
              _json_http_response(UNARY_HOP1_PAYLOAD),
              _json_http_response(UNARY_HOP2_PAYLOAD),
          ],
      ) as mock_request,
      mock.patch.object(
          client.BaseApiClient,
          'request_streamed',
          side_effect=[
              _stream_http_responses([STREAM_HOP1_PAYLOAD]),
              _stream_http_responses([STREAM_HOP2_PAYLOAD]),
          ],
      ) as mock_stream,
  ):
    chat_unary = test_client.chats.create(model='gemini-2.5-pro')
    _ = chat_unary.send_message('Hello unary chat')
    unary_history = chat_unary.get_history()

    chat_stream = test_client.chats.create(model='gemini-2.5-pro')
    _ = list(chat_stream.send_message_stream('Hello stream chat'))
    stream_history = chat_stream.get_history()

  assert mock_request.call_count == 2
  assert mock_stream.call_count == 2
  assert len(unary_history) == 2
  assert unary_history[0].role == 'user'
  assert unary_history[1].role == 'model'
  assert (
      ''.join(p.text for p in unary_history[1].parts if not p.thought)
      == 'Hello world!'
  )

  assert len(stream_history) == 3
  assert stream_history[0].role == 'user'
  assert all(h.role == 'model' for h in stream_history[1:])
  assert [h.parts[0].text for h in stream_history[1:]] == [
      'Stream 1 ',
      'Stream 2!',
  ]


@pytest.mark.asyncio
async def test_e2e_async_client_continuation():
  """Verifies AsyncClient unary multi-hop and streaming checkpoint recovery."""
  async with client.Client(api_key='test-key').aio as aclient:
    with (
        mock.patch.object(
            client.BaseApiClient,
            'async_request',
            new_callable=mock.AsyncMock,
            side_effect=[
                _json_http_response(UNARY_HOP1_PAYLOAD),
                _json_http_response(UNARY_HOP2_PAYLOAD),
            ],
        ) as mock_async_request,
        mock.patch.object(
            client.BaseApiClient,
            'async_request_streamed',
            new_callable=mock.AsyncMock,
            side_effect=[
                _async_stream_http_responses(
                    [
                        STREAM_DROP_PART_A_PAYLOAD,
                        STREAM_DROP_PART_B_CKPT_PAYLOAD,
                    ],
                    exc=httpx.RemoteProtocolError('peer closed connection'),
                ),
                _async_stream_http_responses([STREAM_DROP_PART_C_STOP_PAYLOAD]),
            ],
        ) as mock_async_stream,
    ):
      aresp = await aclient.models.generate_content(
          model='gemini-2.5-pro',
          contents='Async hello',
      )
      astream_chunks = []
      async for ch in await aclient.models.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Async drop',
      ):
        astream_chunks.append(ch)

    assert mock_async_request.call_count == 2
    assert (
        mock_async_request.call_args_list[1].args[2].get('continuationToken')
        == TOK_UNARY_HOP1_B64
    )
    assert mock_async_stream.call_count == 2
    assert (
        mock_async_stream.call_args_list[1].args[2].get('continuationToken')
        == TOK_STREAM_CP1_B64
    )
    assert aresp.text == 'Hello world!'
    assert aresp.usage_metadata.initial_prompt_token_count == 120
    assert ''.join(c.text for c in astream_chunks) == 'Part A Part B Part C!'


def test_merge_continuation_responses_empty_candidates_clears_finish_reason_and_preserves_prompt_feedback(
    mock_api_client,
):
  """When a continuation hop returns no candidates (e.g. prompt_feedback block), finish_reason is cleared to None and prompt_feedback is preserved."""
  models_module = models.Models(mock_api_client)

  hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Partial output before block.')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_hop_1',
              finish_message='Continuing',
          )
      ],
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          prompt_token_count=10,
          candidates_token_count=100,
          total_token_count=110,
      ),
  )

  for empty_candidates in (None, []):
    hop2 = types.GenerateContentResponse(
        candidates=empty_candidates,
        prompt_feedback=types.GenerateContentResponsePromptFeedback(
            block_reason=types.BlockedReason.OTHER,
            block_reason_message='Blocked on continuation hop',
        ),
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=110,
            total_token_count=110,
        ),
    )

    with mock.patch.object(
        models.Models,
        '_generate_content',
        side_effect=[
            hop1.model_copy(deep=True),
            hop2.model_copy(deep=True),
        ],
    ) as mock_raw_gc:
      response = models_module.generate_content(
          model='gemini-2.5-pro',
          contents='Test prompt',
      )
      assert mock_raw_gc.call_count == 2
      assert response.text == 'Partial output before block.'
      assert response.candidates is not None
      assert len(response.candidates) == 1
      assert response.candidates[0].finish_reason is None
      assert response.candidates[0].continuation_token is None
      assert response.candidates[0].finish_message is None
      assert response.prompt_feedback is not None
      assert response.prompt_feedback.block_reason == types.BlockedReason.OTHER
      assert (
          response.prompt_feedback.block_reason_message
          == 'Blocked on continuation hop'
      )
      assert response.usage_metadata is not None
      assert response.usage_metadata.prompt_token_count == 120
      assert response.usage_metadata.initial_prompt_token_count == 10


def _blocked_after_checkpoint_chunks():
  text_chunk = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(role='model', parts=[types.Part(text='Hi ')])
          )
      ]
  )
  checkpoint_chunk = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='there. ')]
              ),
              continuation_token=b'ckpt_before_block',
          )
      ]
  )
  blocked_chunk = types.GenerateContentResponse(
      prompt_feedback=types.GenerateContentResponsePromptFeedback(
          block_reason=types.BlockedReason.SAFETY
      )
  )
  return [text_chunk, checkpoint_chunk, blocked_chunk]


def test_models_generate_content_stream_does_not_resume_after_block(
    mock_api_client,
):
  """A no-candidate blocked chunk after a checkpoint ends the stream without resuming."""
  models_module = models.Models(mock_api_client)
  server_503 = errors.ServerError(
      503, {'error': {'code': 503, 'message': 'x', 'status': 'UNAVAILABLE'}}
  )

  def _hop(exc=None):
    for c in _blocked_after_checkpoint_chunks():
      yield c
    if exc is not None:
      raise exc

  # 1. Stream ends after the block -> no resume.
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[_hop(), _hop()],
  ) as mock_raw_stream:
    chunks = list(
        models_module.generate_content_stream(
            model='gemini-2.5-pro', contents='Write something'
        )
    )
    assert mock_raw_stream.call_count == 1
    assert len(chunks) == 3
    assert chunks[0].text == 'Hi '
    assert chunks[1].text == 'there. '
    assert not chunks[2].candidates
    assert chunks[2].prompt_feedback.block_reason == types.BlockedReason.SAFETY

  # 2. Error after the block -> raises instead of resuming from checkpoint.
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[_hop(server_503), _hop()],
  ) as mock_raw_stream:
    received = []
    with pytest.raises(errors.ServerError):
      for chunk in models_module.generate_content_stream(
          model='gemini-2.5-pro', contents='Write something'
      ):
        received.append(chunk)
    assert len(received) == 3
    assert mock_raw_stream.call_count == 1


@pytest.mark.asyncio
async def test_async_models_generate_content_stream_does_not_resume_after_block(
    mock_api_client,
):
  """Async: a no-candidate blocked chunk after a checkpoint ends the stream without resuming."""
  models_module = models.AsyncModels(mock_api_client)
  server_503 = errors.ServerError(
      503, {'error': {'code': 503, 'message': 'x', 'status': 'UNAVAILABLE'}}
  )

  async def _hop(exc=None):
    for c in _blocked_after_checkpoint_chunks():
      yield c
    if exc is not None:
      raise exc

  # 1. Stream ends after the block -> no resume.
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_hop(), _hop()],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await models_module.generate_content_stream(
        model='gemini-2.5-pro', contents='Write something'
    ):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 1
    assert len(chunks) == 3
    assert chunks[0].text == 'Hi '
    assert chunks[1].text == 'there. '
    assert not chunks[2].candidates
    assert chunks[2].prompt_feedback.block_reason == types.BlockedReason.SAFETY

  # 2. Error after the block -> raises instead of resuming from checkpoint.
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_hop(server_503), _hop()],
  ) as mock_async_stream:
    received = []
    with pytest.raises(errors.ServerError):
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro', contents='Write something'
      ):
        received.append(chunk)
    assert len(received) == 3
    assert mock_async_stream.call_count == 1


def _max_tokens_on_resumed_hop_responses():
  hop1 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Hop 1. ')]
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_hop1',
          )
      ]
  )
  hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Hop 2.')]
              ),
              finish_reason=types.FinishReason.MAX_TOKENS,
              continuation_token=b'tok_hop2_max_tokens',
          )
      ]
  )
  return hop1, hop2


def test_models_max_tokens_on_resumed_hop_stops_and_returns_token(
    mock_api_client,
):
  """MAX_TOKENS on a later hop stops the loop and surfaces its token."""
  models_module = models.Models(mock_api_client)

  hop1, hop2 = _max_tokens_on_resumed_hop_responses()
  with mock.patch.object(
      models.Models, '_generate_content', side_effect=[hop1, hop2]
  ) as mock_raw_gc:
    response = models_module.generate_content(
        model='gemini-2.5-pro', contents='Write something'
    )
    assert mock_raw_gc.call_count == 2
    assert response.text == 'Hop 1. Hop 2.'
    candidate = response.candidates[0]
    assert candidate.finish_reason == types.FinishReason.MAX_TOKENS
    assert candidate.continuation_token == b'tok_hop2_max_tokens'

  hop1, hop2 = _max_tokens_on_resumed_hop_responses()
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[iter([hop1]), iter([hop2]), iter([])],
  ) as mock_raw_stream:
    # No APIError: MAX_TOKENS is a terminal finish_reason.
    chunks = list(
        models_module.generate_content_stream(
            model='gemini-2.5-pro', contents='Write something'
        )
    )
    assert mock_raw_stream.call_count == 2
    assert [c.text for c in chunks] == ['Hop 1. ', 'Hop 2.']
    assert chunks[0].candidates[0].finish_reason is None
    last = chunks[-1].candidates[0]
    assert last.finish_reason == types.FinishReason.MAX_TOKENS
    assert last.continuation_token == b'tok_hop2_max_tokens'


@pytest.mark.asyncio
async def test_async_models_max_tokens_on_resumed_hop_stops_and_returns_token(
    mock_api_client,
):
  """Async: MAX_TOKENS on a later hop stops the loop and surfaces its token."""
  models_module = models.AsyncModels(mock_api_client)

  hop1, hop2 = _max_tokens_on_resumed_hop_responses()
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[hop1, hop2],
  ) as mock_raw_gc:
    response = await models_module.generate_content(
        model='gemini-2.5-pro', contents='Write something'
    )
    assert mock_raw_gc.call_count == 2
    assert response.text == 'Hop 1. Hop 2.'
    candidate = response.candidates[0]
    assert candidate.finish_reason == types.FinishReason.MAX_TOKENS
    assert candidate.continuation_token == b'tok_hop2_max_tokens'

  async def _hop(resp):
    yield resp

  hop1, hop2 = _max_tokens_on_resumed_hop_responses()
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_hop(hop1), _hop(hop2)],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await models_module.generate_content_stream(
        model='gemini-2.5-pro', contents='Write something'
    ):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 2
    assert [c.text for c in chunks] == ['Hop 1. ', 'Hop 2.']
    last = chunks[-1].candidates[0]
    assert last.finish_reason == types.FinishReason.MAX_TOKENS
    assert last.continuation_token == b'tok_hop2_max_tokens'
