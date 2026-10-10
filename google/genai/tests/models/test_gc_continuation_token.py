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
      assert mock_raw_gc.call_args_list[0].kwargs['config'].max_output_tokens == 50000
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
    assert mock_raw_gc.call_args_list[0].kwargs['config'].max_output_tokens == 50000
    assert mock_raw_gc.call_args_list[1].kwargs['config'].max_output_tokens == 50000
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
          candidates_token_count=100,
          total_token_count=120,
          prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=20
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
          candidates_token_count=50,
          total_token_count=170,
          prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT, token_count=120
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
    assert response.usage_metadata.prompt_tokens_details == [
        types.ModalityTokenCount(
            modality=types.MediaModality.TEXT, token_count=140
        )
    ]


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
              candidates_token_count=32768,
              total_token_count=32792,
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
              candidates_token_count=32768,
              total_token_count=65560,
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
              candidates_token_count=32768,
              total_token_count=98328,
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
              candidates_token_count=11903,
              total_token_count=110231,
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
      assert chunks[-1].candidates[0].finish_reason == types.FinishReason.STOP
      assert chunks[-1].candidates[0].continuation_token is None

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
    assert mock_raw_gc.call_args_list[0].kwargs['config'].continuation_token is None
    assert (
        mock_raw_gc.call_args_list[1].kwargs['config'].continuation_token
        == b'afc_tok_1'
    )
    assert mock_raw_gc.call_args_list[2].kwargs['config'].continuation_token is None
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
              candidates_token_count=32768,
              total_token_count=32792,
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
              candidates_token_count=32768,
              total_token_count=65560,
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
              candidates_token_count=32768,
              total_token_count=98328,
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
              candidates_token_count=1024,
              total_token_count=99352,
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
      chunks = []
      async for chunk in await models_module.generate_content_stream(
          model='gemini-2.5-pro',
          contents='Hello async stream',
          config=stream_cfg,
      ):
        chunks.append(chunk.text)
      assert chunks == [
          'Async chunk 1. ',
          'Async chunk 2. ',
          'Async chunk 3. ',
          'Async chunk 4. ',
          'Async chunk 5.',
      ]
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
    assert mock_async_gc.call_args_list[0].kwargs['config'].max_output_tokens == 50000
    assert mock_async_gc.call_args_list[1].kwargs['config'].max_output_tokens == 50000


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

  # 4. Consecutive failure on resumed hop before any new checkpoint token -> raises without infinite looping
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          _failing_hop([chunk_ckpt_35k], server_503),
          _failing_hop([chunk_pre_32k], server_503),
      ],
  ) as mock_raw_stream:
    stream = models_module.generate_content_stream(
        model='gemini-2.5-pro',
        contents='Write a long book',
    )
    assert next(stream).text == 'Checkpoint 35k. '
    assert next(stream).text == 'Intro. '
    with pytest.raises(errors.ServerError):
      next(stream)
    assert mock_raw_stream.call_count == 2


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
