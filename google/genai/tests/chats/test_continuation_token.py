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

"""Unit tests for continuation_token and CONTINUATION finish_reason."""

from unittest import mock

import pydantic
import pytest

from ... import _extra_utils
from ... import chats
from ... import client
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
  """Tests helper edge cases for config preparation and response merging."""
  assert _extra_utils.should_continue_generation(None) is None
  assert (
      _extra_utils.should_continue_generation(
          types.GenerateContentResponse(candidates=[])
      )
      is None
  )

  cfg_from_none = _extra_utils.prepare_continuation_config(None, b'tok')
  assert cfg_from_none is not None
  assert cfg_from_none.continuation_token == b'tok'

  cfg_from_dict = _extra_utils.prepare_continuation_config(
      {'temperature': 0.5}, b'tok'  # type: ignore[arg-type]
  )
  assert cfg_from_dict is not None
  assert cfg_from_dict.continuation_token == b'tok'
  assert cfg_from_dict.temperature == 0.5

  assert (
      _extra_utils.merge_continuation_responses([])
      == types.GenerateContentResponse()
  )

  cand = types.Candidate(
      content=types.Content(role='model', parts=[types.Part(text='hi')])
  )
  assert _extra_utils.merge_candidates([], [cand]) == [cand]
  assert _extra_utils.merge_candidates([cand], []) == [cand]

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


def test_chat_send_message_default_auto_resumes_on_max_tokens(mock_api_client):
  """Default Chat config auto-resumes across 4 hops on CONTINUATION + continuation_token."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-pro')

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

  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[hop1_response, hop2_response, hop3_response, hop4_response],
  ) as mock_gc:
    response = chat.send_message('Write a very long story')

    assert mock_gc.call_count == 4
    expected_tokens = [None, b'token_hop_1', b'token_hop_2', b'token_hop_3']
    first_contents = mock_gc.call_args_list[0].kwargs['contents']
    assert len(first_contents) == 1
    for idx, expected_tok in enumerate(expected_tokens):
      call_kwargs = mock_gc.call_args_list[idx].kwargs
      assert call_kwargs['config'].continuation_token == expected_tok
      assert call_kwargs['contents'] == first_contents

    assert (
        response.text == 'Hop 1 part. Hop 2 part. Hop 3 part. Hop 4 final part.'
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
        response.usage_metadata.prompt_token_count == 10 + 32778 + 65546 + 98314
    )
    assert response.usage_metadata.candidates_token_count == 32768 * 3 + 1024
    assert response.usage_metadata.thoughts_token_count == 500 + 300 + 200 + 100
    assert (
        response.usage_metadata.total_token_count
        == 33278 + 65846 + 98514 + 99438
    )

    assert chat._config.continuation_token is None
    history = chat.get_history(curated=True)
    assert len(history) == 2
    assert history[0].role == 'user'
    assert history[1].role == 'model'
    assert history[1].parts == [
        types.Part(text='Hop 1 part. '),
        types.Part(text='Hop 2 part. '),
        types.Part(text='Hop 3 part. '),
        types.Part(text='Hop 4 final part.'),
    ]


def test_chat_send_message_explicit_max_output_tokens_stops_on_max_tokens(
    mock_api_client,
):
  """When user explicitly sets max_output_tokens, sync unary and stream do not auto-resume on MAX_TOKENS."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(
      model='gemini-2.5-pro',
      config=types.GenerateContentConfig(max_output_tokens=1000),
  )

  hop1_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Stopped at 1000 tokens.')],
              ),
              finish_reason=types.FinishReason.MAX_TOKENS,
              continuation_token=b'token_unused',
          )
      ]
  )

  # 1. Sync unary (AFC enabled by default, max_output_tokens on chat config)
  with mock.patch.object(
      models.Models, '_generate_content', return_value=hop1_response
  ) as mock_gc:
    response = chat.send_message('Short response please')
    assert mock_gc.call_count == 1
    assert response.text == 'Stopped at 1000 tokens.'
    assert response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
    assert response.candidates[0].continuation_token == b'token_unused'

  # 2. Sync unary (AFC disabled, max_output_tokens on method config)
  chat_no_cfg = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.Models, '_generate_content', return_value=hop1_response
  ) as mock_gc:
    response = chat_no_cfg.send_message(
        'Short response please',
        config=types.GenerateContentConfig(
            max_output_tokens=1000,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )
    assert mock_gc.call_count == 1
    assert response.text == 'Stopped at 1000 tokens.'
    assert response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
    assert response.candidates[0].continuation_token == b'token_unused'

  # 3. Sync stream (AFC enabled by default, max_output_tokens on chat config)
  stream_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='Stream chunk 1. ')],
                  ),
                  continuation_token=b'stream_token_unused',
              )
          ]
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='Stopped stream at 1000 tokens.')],
                  ),
                  finish_reason=types.FinishReason.MAX_TOKENS,
              )
          ]
      ),
  ]
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      return_value=iter(stream_chunks),
  ) as mock_stream:
    chunks = list(chat.send_message_stream('Short stream please'))
    assert mock_stream.call_count == 1
    assert [c.text for c in chunks] == [
        'Stream chunk 1. ',
        'Stopped stream at 1000 tokens.',
    ]
    assert (
        chunks[-1].candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
    )

  # 4. Sync stream (AFC disabled, max_output_tokens on method config)
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      return_value=iter(stream_chunks),
  ) as mock_stream:
    chunks = list(
        chat_no_cfg.send_message_stream(
            'Short stream please',
            config=types.GenerateContentConfig(
                max_output_tokens=1000,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )
    )
    assert mock_stream.call_count == 1
    assert [c.text for c in chunks] == [
        'Stream chunk 1. ',
        'Stopped stream at 1000 tokens.',
    ]
    assert (
        chunks[-1].candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
    )


def test_chat_automatic_continuation_config_rules(
    mock_api_client,
):
  """Verifies rules for automatic_continuation and max_output_tokens pass-through in Chat."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)

  hop1_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 1. ')],
              ),
              finish_reason=types.FinishReason.CONTINUATION,
              continuation_token=b'tok_1',
          )
      ]
  )
  hop2_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Hop 2.')],
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )

  # Rule 1: automatic_continuation unset, max_output_tokens unset -> enabled
  chat = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[
          hop1_response.model_copy(deep=True),
          hop2_response.model_copy(deep=True),
      ],
  ) as mock_gc:
    response = chat.send_message('Rule 1')
    assert mock_gc.call_count == 2
    assert response.text == 'Hop 1. Hop 2.'

  # Rule 2: max_output_tokens is set -> forwarded as-is; enabled when automatic_continuation is None or True
  for auto_cont in (None, True):
    chat = chats_module.create(model='gemini-2.5-pro')
    with mock.patch.object(
        models.Models,
        '_generate_content',
        side_effect=[
            hop1_response.model_copy(deep=True),
            hop2_response.model_copy(deep=True),
        ],
    ) as mock_gc:
      response = chat.send_message(
          'Rule 2 enabled',
          config={
              'max_output_tokens': 50000,
              'automatic_continuation': auto_cont,
              'automatic_function_calling': {'disable': True},
          },
      )
      assert mock_gc.call_count == 2
      assert response.text == 'Hop 1. Hop 2.'
      assert mock_gc.call_args_list[0].kwargs['config'].max_output_tokens == 50000
      assert mock_gc.call_args_list[1].kwargs['config'].max_output_tokens == 50000

  chat = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.Models,
      '_generate_content',
      return_value=hop1_response.model_copy(deep=True),
  ) as mock_gc:
    response = chat.send_message(
        'Rule 2 disabled',
        config={
            'max_output_tokens': 50000,
            'automatic_continuation': False,
            'automatic_function_calling': {'disable': True},
        },
    )
    assert mock_gc.call_count == 1
    assert response.text == 'Hop 1. '
    assert (
        response.candidates[0].finish_reason
        == types.FinishReason.CONTINUATION
    )
    assert response.candidates[0].continuation_token == b'tok_1'

  # Rule 3: automatic_continuation=True, max_output_tokens unset -> enabled
  chat = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[
          hop1_response.model_copy(deep=True),
          hop2_response.model_copy(deep=True),
      ],
  ) as mock_gc:
    response = chat.send_message(
        'Rule 3',
        config=types.GenerateContentConfig(automatic_continuation=True),
    )
    assert mock_gc.call_count == 2
    assert response.text == 'Hop 1. Hop 2.'
    assert (
        mock_gc.call_args_list[0].kwargs['config'].automatic_continuation
        is True
    )

  # Rule 4: automatic_continuation=False, max_output_tokens unset -> disabled
  chat = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.Models,
      '_generate_content',
      return_value=hop1_response.model_copy(deep=True),
  ) as mock_gc:
    response = chat.send_message(
        'Rule 4',
        config=types.GenerateContentConfig(automatic_continuation=False),
    )
    assert mock_gc.call_count == 1
    assert response.text == 'Hop 1. '
    assert response.candidates[0].continuation_token == b'tok_1'

  # Rule 4 in streaming: automatic_continuation=False, max_output_tokens unset -> disabled
  stream_chunks = [hop1_response.model_copy(deep=True)]
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      return_value=iter(stream_chunks),
  ) as mock_stream:
    chunks = list(
        chat.send_message_stream(
            'Rule 4 stream',
            config=types.GenerateContentConfig(automatic_continuation=False),
        )
    )
    assert mock_stream.call_count == 1
    assert [c.text for c in chunks] == ['Hop 1. ']


def test_chat_send_message_incompatible_tools_with_continuation(
    mock_api_client,
):
  """Incompatible AFC tools path also supports continuation token resumption."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-pro')

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
      models.Models, '_generate_content', side_effect=[hop1, hop2]
  ) as mock_gc:
    resp = chat.send_message(
        'Test incompatible tools',
        config=types.GenerateContentConfig(tools=[tool_decl]),
    )
    assert mock_gc.call_count == 2
    assert resp.text == 'Part 1. Part 2.'


def test_chat_send_message_preserves_empty_text_thought_part(mock_api_client):
  """Empty placeholder Part(text='') from a thought-only hop is never dropped."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-pro')

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
  ) as mock_gc:
    response = chat.send_message('Solve hard math problem')
    assert mock_gc.call_count == 2
    assert response.text == 'Final answer after deep thinking.'
    parts = response.candidates[0].content.parts
    assert len(parts) == 2
    assert parts[0].text == ''  # pylint: disable=g-explicit-bool-comparison
    assert parts[0].thought_signature == b'sig_hop_1'
    assert parts[1].text == 'Final answer after deep thinking.'
    assert len(chat.get_history(curated=True)) == 2


def test_chat_send_message_recursive_metadata_and_parsed_schema_merging(
    mock_api_client,
):
  """Verifies recursive Pydantic merging for all metadata fields and response_schema."""

  class StorySummary(pydantic.BaseModel):
    title: str
    pages: int

  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-pro')

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
    response = chat.send_message(
        'Give me JSON',
        config=types.GenerateContentConfig(response_schema=StorySummary),
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


def test_chat_send_message_stream_auto_resumes_across_hops(mock_api_client):
  """Streaming send_message_stream yields chunks seamlessly across 4 continuation hops."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-pro')

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

  # Test without AFC (disable=True)
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          iter(hop1_chunks),
          iter(hop2_chunks),
          iter(hop3_chunks),
          iter(hop4_chunks),
      ],
  ) as mock_stream:
    chunks = list(
        chat.send_message_stream(
            'Write an exhaustive, multi-chapter textbook on compiler design '
            'that is around 100,000 tokens long.',
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
        )
    )
    assert mock_stream.call_count == 4
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

    first_call_kwargs = mock_stream.call_args_list[0].kwargs
    second_call_kwargs = mock_stream.call_args_list[1].kwargs
    third_call_kwargs = mock_stream.call_args_list[2].kwargs
    fourth_call_kwargs = mock_stream.call_args_list[3].kwargs
    assert first_call_kwargs['config'].continuation_token is None
    assert (
        second_call_kwargs['config'].continuation_token
        == b'AY89a181L6ffhy7s5hBG6S1Zea0DmuUzVC4ByCWe'
    )
    assert third_call_kwargs['config'].continuation_token == b'stream_tok_hop_2'
    assert (
        fourth_call_kwargs['config'].continuation_token == b'stream_tok_hop_3'
    )
    for call_kwargs in (
        second_call_kwargs,
        third_call_kwargs,
        fourth_call_kwargs,
    ):
      assert len(call_kwargs['contents']) == 1
      assert call_kwargs['contents'] == first_call_kwargs['contents']

    curated = chat.get_history(curated=True)
    assert len(curated) == 10  # 1 user + 9 model chunks

  # Test default AFC-enabled path in Chat.send_message_stream
  chat_default = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[
          iter(hop1_chunks),
          iter(hop2_chunks),
          iter(hop3_chunks),
          iter(hop4_chunks),
      ],
  ) as mock_stream:
    chunks = list(
        chat_default.send_message_stream(
            'Write an exhaustive, multi-chapter textbook on compiler design '
            'that is around 100,000 tokens long.'
        )
    )
    assert mock_stream.call_count == 4
    assert chunks[-1].candidates[0].finish_reason == types.FinishReason.STOP
    first_call_kwargs = mock_stream.call_args_list[0].kwargs
    second_call_kwargs = mock_stream.call_args_list[1].kwargs
    third_call_kwargs = mock_stream.call_args_list[2].kwargs
    fourth_call_kwargs = mock_stream.call_args_list[3].kwargs
    assert first_call_kwargs['config'].continuation_token is None
    assert (
        second_call_kwargs['config'].continuation_token
        == b'AY89a181L6ffhy7s5hBG6S1Zea0DmuUzVC4ByCWe'
    )
    assert third_call_kwargs['config'].continuation_token == b'stream_tok_hop_2'
    assert (
        fourth_call_kwargs['config'].continuation_token == b'stream_tok_hop_3'
    )
    for call_kwargs in (
        second_call_kwargs,
        third_call_kwargs,
        fourth_call_kwargs,
    ):
      assert len(call_kwargs['contents']) == 1
      assert call_kwargs['contents'] == first_call_kwargs['contents']


def test_chat_afc_decoupled_from_continuation_token(mock_api_client):
  """AFC resumes continuation during thinking, then clears continuation_token on function_response."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)

  def get_weather(city: str) -> str:
    """Gets weather for a city."""
    return f'Sunny in {city}'

  chat = chats_module.create(
      model='gemini-2.5-pro',
      config=types.GenerateContentConfig(tools=[get_weather]),
  )

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

  with mock.patch.object(
      models.Models,
      '_generate_content',
      side_effect=[turn1_hop1, turn1_hop2, turn2_final],
  ) as mock_gc:
    response = chat.send_message('What is the weather in Mountain View?')
    assert mock_gc.call_count == 3

    assert mock_gc.call_args_list[0].kwargs['config'].continuation_token is None
    assert (
        mock_gc.call_args_list[1].kwargs['config'].continuation_token
        == b'afc_tok_1'
    )
    assert mock_gc.call_args_list[2].kwargs['config'].continuation_token is None
    assert response.text == 'It is Sunny in Mountain View!'


@pytest.mark.asyncio
async def test_async_chat_send_message_and_stream_auto_resume(mock_api_client):
  """AsyncChat auto-resumes on continuation_token across 4 hops in unary, AFC, and streaming modes."""
  models_module = models.AsyncModels(mock_api_client)
  chats_module = chats.AsyncChats(modules=models_module)

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

  # Test AFC disabled path in AsyncChat.send_message
  chat_no_afc = chats_module.create(model='gemini-2.5-pro')
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
    resp = await chat_no_afc.send_message(
        'Hello async no afc',
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        ),
    )
    assert resp.text == 'Async 1. Async 2. Async 3. Async 4.'
    assert resp.candidates[0].finish_reason == types.FinishReason.STOP
    _assert_async_unary_4_hops(mock_async_gc)

  # Test incompatible tools path in AsyncChat.send_message
  tool_decl = types.Tool(
      function_declarations=[
          types.FunctionDeclaration(name='manual_fn', description='manual')
      ]
  )
  chat_incompat = chats_module.create(model='gemini-2.5-pro')
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
    resp = await chat_incompat.send_message(
        'Hello async incompat',
        config=types.GenerateContentConfig(tools=[tool_decl]),
    )
    assert resp.text == 'Async 1. Async 2. Async 3. Async 4.'
    assert resp.candidates[0].finish_reason == types.FinishReason.STOP
    _assert_async_unary_4_hops(mock_async_gc)

  # Test default AFC path in AsyncChat.send_message
  chat_default_unary = chats_module.create(model='gemini-2.5-pro')
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
    resp = await chat_default_unary.send_message('Hello async default')
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
      assert len(call_kwargs['contents']) == 1
      assert call_kwargs['contents'] == c1['contents']

  # Test AFC disabled path in AsyncChat.send_message_stream
  async_chat_no_afc = chats_module.create(model='gemini-2.5-pro')
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
    async for chunk in await async_chat_no_afc.send_message_stream(
        'Hello async stream no afc',
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        ),
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

  # Test default AFC path in AsyncChat.send_message_stream
  async_chat_default = chats_module.create(model='gemini-2.5-pro')
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
    async for chunk in await async_chat_default.send_message_stream(
        'Hello async stream'
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
async def test_async_chat_explicit_max_output_tokens_stops_on_max_tokens(
    mock_api_client,
):
  """When max_output_tokens is explicitly set, AsyncChat (unary and stream) does NOT auto-resume on MAX_TOKENS."""
  models_module = models.AsyncModels(mock_api_client)
  chats_module = chats.AsyncChats(modules=models_module)
  chat = chats_module.create(
      model='gemini-2.5-pro',
      config=types.GenerateContentConfig(max_output_tokens=1000),
  )

  hop1_response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model',
                  parts=[types.Part(text='Stopped at async budget.')],
              ),
              finish_reason=types.FinishReason.MAX_TOKENS,
              continuation_token=b'token_unused_async',
          )
      ]
  )

  # Async unary with chat-level max_output_tokens (default AFC)
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      return_value=hop1_response,
  ) as mock_async_gc:
    response = await chat.send_message('Write a long essay')
    assert mock_async_gc.call_count == 1
    assert response.text == 'Stopped at async budget.'
    assert response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
    assert response.candidates[0].continuation_token == b'token_unused_async'

  # Async unary with method-level max_output_tokens (AFC disabled)
  chat_no_default = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      return_value=hop1_response,
  ) as mock_async_gc:
    response = await chat_no_default.send_message(
        'Write a long essay',
        config=types.GenerateContentConfig(
            max_output_tokens=500,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )
    assert mock_async_gc.call_count == 1
    assert response.text == 'Stopped at async budget.'

  stream_hop1_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='Async stream stopped ')],
                  ),
                  continuation_token=b'async_stream_token_unused',
              )
          ]
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='at budget.')],
                  ),
                  finish_reason=types.FinishReason.MAX_TOKENS,
              )
          ]
      ),
  ]

  async def _make_async_stream(chunk_list):
    for c in chunk_list:
      yield c

  # Async stream with chat-level max_output_tokens (default AFC)
  chat_stream_budget = chats_module.create(
      model='gemini-2.5-pro',
      config=types.GenerateContentConfig(max_output_tokens=1000),
  )
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_make_async_stream(stream_hop1_chunks)],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await chat_stream_budget.send_message_stream(
        'Write a long essay'
    ):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 1
    assert [c.text for c in chunks] == ['Async stream stopped ', 'at budget.']
    assert (
        chunks[-1].candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
    )

  # Async stream with method-level max_output_tokens (AFC disabled)
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[_make_async_stream(stream_hop1_chunks)],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await chat_no_default.send_message_stream(
        'Write a long essay',
        config=types.GenerateContentConfig(
            max_output_tokens=500,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    ):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 1
    assert [c.text for c in chunks] == ['Async stream stopped ', 'at budget.']
    assert (
        chunks[-1].candidates[0].finish_reason == types.FinishReason.MAX_TOKENS
    )


@pytest.mark.asyncio
async def test_async_chat_automatic_continuation_config_rules(mock_api_client):
  """Verifies Rules 1-4 for automatic_continuation and max_output_tokens pass-through in AsyncChat."""
  models_module = models.AsyncModels(mock_api_client)
  chats_module = chats.AsyncChats(modules=models_module)

  hop1 = types.GenerateContentResponse(
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
  hop2 = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='Async Hop 2.')]
              ),
              finish_reason=types.FinishReason.STOP,
              continuation_token=None,
          )
      ]
  )

  # Rule 2: automatic_continuation=True + max_output_tokens set -> enabled and max_output_tokens forwarded as-is
  chat = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[hop1.model_copy(deep=True), hop2.model_copy(deep=True)],
  ) as mock_gc:
    resp = await chat.send_message(
        'Rule 2 async',
        config=types.GenerateContentConfig(
            automatic_continuation=True, max_output_tokens=1000
        ),
    )
    assert mock_gc.call_count == 2
    assert resp.text == 'Async Hop 1. Async Hop 2.'
    assert mock_gc.call_args_list[0].kwargs['config'].max_output_tokens == 1000
    assert mock_gc.call_args_list[1].kwargs['config'].max_output_tokens == 1000

  # Rule 3: automatic_continuation=True + max_output_tokens unset -> enabled
  chat = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      side_effect=[hop1.model_copy(deep=True), hop2.model_copy(deep=True)],
  ) as mock_gc:
    resp = await chat.send_message(
        'Rule 3 async',
        config=types.GenerateContentConfig(automatic_continuation=True),
    )
    assert mock_gc.call_count == 2
    assert resp.text == 'Async Hop 1. Async Hop 2.'

  # Rule 4: automatic_continuation=False + max_output_tokens unset -> disabled
  chat = chats_module.create(model='gemini-2.5-pro')
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content',
      new_callable=mock.AsyncMock,
      return_value=hop1.model_copy(deep=True),
  ) as mock_gc:
    resp = await chat.send_message(
        'Rule 4 async',
        config=types.GenerateContentConfig(automatic_continuation=False),
    )
    assert mock_gc.call_count == 1
    assert resp.text == 'Async Hop 1. '


def test_chat_send_message_stream_incomplete_continuation_not_recorded(
    mock_api_client,
):
  """When a continuation hop is cut off without finish_reason, the turn is excluded from curated history."""
  models_module = models.Models(mock_api_client)
  chats_module = chats.Chats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-pro')

  hop1_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='Hop 1 part. ')]
                  ),
                  continuation_token=b'tok_hop_1',
              )
          ]
      ),
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='End of hop 1. ')]
                  ),
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ]
      ),
  ]
  hop2_cutoff_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='Hop 2 cut off mid-stream')],
                  ),
                  finish_reason=None,
              )
          ]
      )
  ]

  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      side_effect=[iter(hop1_chunks), iter(hop2_cutoff_chunks)],
  ) as mock_stream:
    chunks = list(chat.send_message_stream('Write a long story'))
    assert mock_stream.call_count == 2
    assert [c.text for c in chunks] == [
        'Hop 1 part. ',
        'End of hop 1. ',
        'Hop 2 cut off mid-stream',
    ]
    assert chat.get_history(curated=True) == []


@pytest.mark.asyncio
async def test_async_chat_send_message_stream_incomplete_continuation_not_recorded(
    mock_api_client,
):
  """When an async continuation hop is cut off without finish_reason, the turn is excluded from curated history."""
  models_module = models.AsyncModels(mock_api_client)
  chats_module = chats.AsyncChats(modules=models_module)
  chat = chats_module.create(model='gemini-2.5-pro')

  hop1_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model', parts=[types.Part(text='Async Hop 1. ')]
                  ),
                  continuation_token=b'async_tok_hop_1',
                  finish_reason=types.FinishReason.CONTINUATION,
              )
          ]
      )
  ]
  hop2_cutoff_chunks = [
      types.GenerateContentResponse(
          candidates=[
              types.Candidate(
                  content=types.Content(
                      role='model',
                      parts=[types.Part(text='Async Hop 2 cut off')],
                  ),
                  finish_reason=None,
              )
          ]
      )
  ]

  async def _make_async_stream(chunk_list):
    for c in chunk_list:
      yield c

  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
      side_effect=[
          _make_async_stream(hop1_chunks),
          _make_async_stream(hop2_cutoff_chunks),
      ],
  ) as mock_async_stream:
    chunks = []
    async for chunk in await chat.send_message_stream('Write a long story'):
      chunks.append(chunk)
    assert mock_async_stream.call_count == 2
    assert [c.text for c in chunks] == ['Async Hop 1. ', 'Async Hop 2 cut off']
    assert chat.get_history(curated=True) == []
