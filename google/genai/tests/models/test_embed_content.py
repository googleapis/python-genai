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
#
# pylint: disable=protected-access


"""Tests for models.embedContent()."""

import json
import os
from unittest import mock

import pytest

from ... import _transformers as t
from ... import client as client_lib
from ... import types
from .. import pytest_helper


def _get_bytes_from_file(relative_path: str) -> bytes:
  abs_file_path = os.path.abspath(
      os.path.join(os.path.dirname(__file__), relative_path)
  )
  with open(abs_file_path, 'rb') as file:
    return file.read()

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name='test_multi_texts_with_config',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-001',
            contents=[
                t.t_content('What is your name?'),
                t.t_content('I am a model.'),
            ],
            config={
                'output_dimensionality': 10,
                'title': 'test_title',
                'task_type': 'RETRIEVAL_DOCUMENT',
                'http_options': {
                    'headers': {'test': 'headers'},
                },
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_single_text_with_mime_type_not_supported_in_mldev',
        parameters=types.EmbedContentParameters(
            model='text-embedding-005',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 10,
                'mime_type': 'text/plain',
            },
        ),
        exception_if_mldev=(
            'only supported in Gemini Enterprise Agent Platform mode'
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_single_text_with_auto_truncate_not_supported_in_mldev',
        parameters=types.EmbedContentParameters(
            model='text-embedding-005',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 10,
                'auto_truncate': True,
            },
        ),
        exception_if_mldev=(
            'only supported in Gemini Enterprise Agent Platform mode'
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_text_only_with_config',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 10,
                'title': 'test_title',
                'task_type': 'RETRIEVAL_DOCUMENT',
                'http_options': {
                    'headers': {'test': 'headers'},
                },
                'auto_truncate': True,
            },
        ),
        # auto_truncate not supported on MLDev.
        exception_if_mldev=(
            'only supported in Gemini Enterprise Agent Platform mode'
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_new_api_text_only',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 100,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_new_api_list_of_contents',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents=[
                types.Content(
                    parts=[types.Part.from_text(text='What is your name?')]
                ),
                types.Content(
                    parts=[types.Part.from_text(text='I am a model.')]
                ),
            ],
            config={
                'output_dimensionality': 10,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_new_api_maas',
        parameters=types.EmbedContentParameters(
            model=(
                'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
            ),
            contents=t.t_contents('What is your name?'),
            config={
                'output_dimensionality': 100,
            },
        ),
        # Model not exposed on MLDev.
        exception_if_mldev='404',
    ),
    pytest_helper.TestTableItem(
        name='test_new_api_gcs_image_and_config',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_text(
                            text='Similar things to the following image:'
                        ),
                        types.Part.from_uri(
                            file_uri='gs://cloud-samples-data/generative-ai/image/a-man-and-a-dog.png',
                            mime_type='image/png',
                        ),
                    ],
                )
            ],
            config={
                'output_dimensionality': 10,
                'title': 'test_title',
                'task_type': 'RETRIEVAL_DOCUMENT',
                'http_options': {
                    'headers': {'test': 'headers'},
                },
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_new_api_inline_pdf',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(
                            data=_get_bytes_from_file('../data/story.pdf'),
                            mime_type='application/pdf',
                        ),
                    ],
                )
            ],
            config={
                'output_dimensionality': 100,
            },
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_inline_pdf_document_ocr',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(
                            data=_get_bytes_from_file('../data/story.pdf'),
                            mime_type='application/pdf',
                        ),
                    ],
                )
            ],
            config={
                'output_dimensionality': 100,
                'document_ocr': True,
            },
        ),
        exception_if_mldev=(
            'only supported in Gemini Enterprise Agent Platform mode'
        ),
    ),
    pytest_helper.TestTableItem(
        name='test_vertex_inline_video_audio_track_extraction',
        parameters=types.EmbedContentParameters(
            model='gemini-embedding-2',
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(
                            data=_get_bytes_from_file('../data/animal.mp4'),
                            mime_type='video/mp4',
                        ),
                    ],
                )
            ],
            config={
                'output_dimensionality': 100,
                'audio_track_extraction': True,
            },
        ),
        exception_if_mldev=(
            'only supported in Gemini Enterprise Agent Platform mode'
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='models.embed_content',
    test_table=test_table,
)


def test_gemini_embedding_2_content_combination(client):
  response = client.models.embed_content(
      model='gemini-embedding-2',
      contents=[
          'The jetpack is cool',
          types.Part.from_bytes(
              data=_get_bytes_from_file('../data/checkerboard.png'),
              mime_type='image/png',
          ),
          types.Part.from_uri(
              file_uri='gs://generativeai-downloads/images/scones.jpg',
              mime_type='image/jpeg',
          ),
      ],
      config={'output_dimensionality': 100},
  )
  # assert has one total embedding
  assert response.embeddings is not None
  assert len(response.embeddings) == 1
  assert len(response.embeddings[0].values) == 100
  if client._api_client.vertexai:
    statistics = response.embeddings[0].statistics
    assert statistics is not None
    assert statistics.token_count is not None
    assert statistics.tokens_details is not None
    assert len(statistics.tokens_details) > 0
    assert response.usage_metadata is not None
    assert response.usage_metadata.traffic_type is not None


@pytest.mark.asyncio
async def test_async(client):
  response = await client.aio.models.embed_content(
      model='gemini-embedding-001',
      contents='What is your name?',
      config={'output_dimensionality': 10},
  )
  assert response


@pytest.mark.asyncio
async def test_async_new_api(client):
  response = await client.aio.models.embed_content(
      model='gemini-embedding-2',
      contents=t.t_contents('What is your name?'),
      config={'output_dimensionality': 10},
  )
  assert response


def test_endpoint_routing(use_vertex, replays_prefix, http_options):
  """Tests endpoint routing across Gemini Enterprise API and Gemini Developer API."""
  del replays_prefix, http_options
  assert t.t_is_vertex_embed_content_model('gemini-embedding-001')
  assert t.t_is_vertex_embed_content_model('gemini-embedding-2')
  assert t.t_is_vertex_embed_content_model(
      'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
  )
  assert not t.t_is_vertex_embed_content_model('text-embedding-005')
  assert not t.t_is_vertex_embed_content_model(
      'projects/my-gemini-app/locations/us-central1/publishers/google/models/text-embedding-005'
  )
  assert not t.t_is_vertex_embed_content_model(
      'projects/my-gemini-app/locations/us-central1/endpoints/12345'
  )
  assert t.t_is_vertex_maas_model(
      'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
  )
  assert not t.t_is_vertex_maas_model('gemini-embedding-001')
  assert not t.t_is_vertex_maas_model(
      'projects/my-maas-app/locations/us-central1/'
      'publishers/google/models/gemini-embedding-001'
  )
  assert t.t_is_multimodal_embedding_model('gemini-embedding-2')
  assert t.t_is_multimodal_embedding_model('models/gemini-embedding-2-preview')
  assert t.t_is_multimodal_embedding_model(
      'publishers/google/models/gemini-embedding-2'
  )
  assert t.t_is_multimodal_embedding_model('gemini-embedding-3')
  assert not t.t_is_multimodal_embedding_model('gemini-embedding-001')
  assert not t.t_is_multimodal_embedding_model('models/gemini-embedding-001')
  assert not t.t_is_multimodal_embedding_model(
      'publishers/google/models/gemini-embedding-001'
  )
  assert not t.t_is_multimodal_embedding_model('gemini-embedding-exp-03-07')
  assert not t.t_is_multimodal_embedding_model('text-embedding-005')
  assert not t.t_is_multimodal_embedding_model(
      'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
  )

  mock_client = client_lib.Client(vertexai=use_vertex, api_key='fake-key')
  captured: list[tuple[str, dict[str, object]]] = []

  def fake_request(http_method, path, request_dict, http_opts=None):
    del http_method, http_opts
    captured.append((path, request_dict))
    if path.endswith(':embedContent'):
      payload = {
          'embedding': {'values': [0.1, 0.2]},
          'usageMetadata': {
              'promptTokenCount': 4,
              'trafficType': 'PROVISIONED_THROUGHPUT',
          },
          'truncated': False,
      }
    elif path.endswith(':batchEmbedContents'):
      payload = {
          'embeddings': [
              {'values': [0.1, 0.2]} for _ in request_dict.get('requests', [])
          ],
          'usageMetadata': {
              'promptTokenCount': 8,
              'trafficType': 'ON_DEMAND',
          },
      }
    else:
      payload = {
          'predictions': [{
              'embeddings': {
                  'values': [0.5, 0.6],
                  'statistics': {'token_count': 3, 'truncated': False},
              }
          }]
      }
    return types.HttpResponse(headers={}, body=json.dumps(payload))

  with mock.patch.object(
      mock_client._api_client, 'request', side_effect=fake_request
  ):
    single_resp = mock_client.models.embed_content(
        model='gemini-embedding-001',
        contents='hello',
        config={'output_dimensionality': 2, 'task_type': 'RETRIEVAL_DOCUMENT'},
    )
    ge1_str_list_resp = mock_client.models.embed_content(
        model='gemini-embedding-001',
        contents=['first', 'second'],
        config={'output_dimensionality': 2, 'title': 'doc'},
    )
    ge1_part_list_resp = mock_client.models.embed_content(
        model='gemini-embedding-001',
        contents=[
            types.Part.from_text(text='first'),
            types.Part.from_text(text='second'),
        ],
    )
    ge1_content_list_resp = mock_client.models.embed_content(
        model='gemini-embedding-001',
        contents=[
            types.Content(parts=[types.Part.from_text(text='first')]),
            types.Content(parts=[types.Part.from_text(text='second')]),
        ],
    )
    ge2_str_list_resp = mock_client.models.embed_content(
        model='gemini-embedding-2',
        contents=['first', 'second'],
        config={'output_dimensionality': 2, 'title': 'doc'},
    )
    ge2_part_list_resp = mock_client.models.embed_content(
        model='gemini-embedding-2',
        contents=[
            types.Part.from_text(text='first'),
            types.Part.from_text(text='second'),
        ],
    )
    ge2_content_list_resp = mock_client.models.embed_content(
        model='gemini-embedding-2',
        contents=[
            types.Content(parts=[types.Part.from_text(text='first')]),
            types.Content(parts=[types.Part.from_text(text='second')]),
        ],
        config={'output_dimensionality': 2, 'title': 'doc'},
    )
    multimodal_resp = mock_client.models.embed_content(
        model='gemini-embedding-2',
        contents=[
            'caption',
            types.Part.from_uri(
                file_uri='gs://b/img.png', mime_type='image/png'
            ),
        ],
    )
    if use_vertex:
      predict_resp = mock_client.models.embed_content(
          model=(
              'projects/my-gemini-app/locations/us-central1/'
              'publishers/google/models/text-embedding-005'
          ),
          contents=['a', 'b'],
          config={'output_dimensionality': 2},
      )
      maas_single_resp = mock_client.models.embed_content(
          model=(
              'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
          ),
          contents='hello',
      )
      maas_str_list_resp = mock_client.models.embed_content(
          model=(
              'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
          ),
          contents=['a', 'b'],
      )
      with pytest.raises(
          ValueError,
          match=(
              'The embedContent API for this model only supports one content'
              ' at a time.'
          ),
      ):
        mock_client.models.embed_content(
            model=(
                'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
            ),
            contents=[
                types.Content(parts=[types.Part.from_text(text='a')]),
                types.Content(parts=[types.Part.from_text(text='b')]),
            ],
        )
    ge1_multi_part_content_resp = mock_client.models.embed_content(
        model='gemini-embedding-001',
        contents=types.Content(
            parts=[
                types.Part.from_text(text='first'),
                types.Part.from_text(text='second'),
            ]
        ),
    )

  if use_vertex:
    assert captured[0][0].endswith('gemini-embedding-001:embedContent')
    assert 'content' in captured[0][1]
    assert 'instances' not in captured[0][1]
    assert 'requests' not in captured[0][1]
    assert len(single_resp.embeddings) == 1
    assert (
        single_resp.usage_metadata.traffic_type
        == types.TrafficType.PROVISIONED_THROUGHPUT
    )

    assert captured[1][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[1][1]['requests']) == 2
    assert captured[1][1]['requests'][0]['embedContentConfig'] == {
        'outputDimensionality': 2,
        'title': 'doc',
    }
    assert len(ge1_str_list_resp.embeddings) == 2

    assert captured[2][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[2][1]['requests']) == 2
    assert len(ge1_part_list_resp.embeddings) == 2

    assert captured[3][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[3][1]['requests']) == 2
    assert len(ge1_content_list_resp.embeddings) == 2

    assert captured[4][0].endswith('gemini-embedding-2:embedContent')
    assert len(captured[4][1]['content']['parts']) == 2
    assert len(ge2_str_list_resp.embeddings) == 1

    assert captured[5][0].endswith('gemini-embedding-2:embedContent')
    assert len(captured[5][1]['content']['parts']) == 2
    assert len(ge2_part_list_resp.embeddings) == 1

    assert captured[6][0].endswith('gemini-embedding-2:batchEmbedContents')
    assert len(captured[6][1]['requests']) == 2
    assert len(ge2_content_list_resp.embeddings) == 2

    assert captured[7][0].endswith('gemini-embedding-2:embedContent')
    assert len(multimodal_resp.embeddings) == 1

    assert captured[8][0].endswith('text-embedding-005:predict')
    assert 'instances' in captured[8][1]
    assert len(predict_resp.embeddings) == 1

    assert len(captured) == 12
    assert captured[9][0].endswith(
        'multilingual-e5-large-instruct-maas:embedContent'
    )
    assert len(maas_single_resp.embeddings) == 1
    assert captured[10][0].endswith(
        'multilingual-e5-large-instruct-maas:embedContent'
    )
    assert len(captured[10][1]['content']['parts']) == 2
    assert len(maas_str_list_resp.embeddings) == 1
    assert captured[11][0].endswith('gemini-embedding-001:embedContent')
    assert len(captured[11][1]['content']['parts']) == 2
    assert len(ge1_multi_part_content_resp.embeddings) == 1
  else:
    assert captured[0][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[0][1]['requests']) == 1
    assert captured[1][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[1][1]['requests']) == 2
    assert len(ge1_str_list_resp.embeddings) == 2
    assert captured[2][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[2][1]['requests']) == 2
    assert len(ge1_part_list_resp.embeddings) == 2
    assert captured[3][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[3][1]['requests']) == 2
    assert len(ge1_content_list_resp.embeddings) == 2
    assert captured[4][0].endswith('gemini-embedding-2:batchEmbedContents')
    assert len(captured[4][1]['requests']) == 1
    assert len(captured[4][1]['requests'][0]['content']['parts']) == 2
    assert len(ge2_str_list_resp.embeddings) == 1
    assert captured[5][0].endswith('gemini-embedding-2:batchEmbedContents')
    assert len(captured[5][1]['requests']) == 1
    assert len(captured[5][1]['requests'][0]['content']['parts']) == 2
    assert len(ge2_part_list_resp.embeddings) == 1
    assert captured[6][0].endswith('gemini-embedding-2:batchEmbedContents')
    assert len(captured[6][1]['requests']) == 2
    assert len(ge2_content_list_resp.embeddings) == 2
    assert captured[7][0].endswith('gemini-embedding-2:batchEmbedContents')
    assert len(captured[7][1]['requests']) == 1
    assert captured[8][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert len(captured[8][1]['requests']) == 1
    assert len(captured[8][1]['requests'][0]['content']['parts']) == 2
    assert len(ge1_multi_part_content_resp.embeddings) == 1


@pytest.mark.asyncio
async def test_async_endpoint_routing(use_vertex, replays_prefix, http_options):
  """Tests async endpoint routing across Gemini Enterprise API and Gemini Developer API."""
  del replays_prefix, http_options
  mock_client = client_lib.Client(vertexai=use_vertex, api_key='fake-key')
  captured: list[tuple[str, dict[str, object]]] = []

  async def fake_async_request(http_method, path, request_dict, http_opts=None):
    del http_method, http_opts
    captured.append((path, request_dict))
    if path.endswith(':embedContent'):
      payload = {'embedding': {'values': [0.1, 0.2]}}
    else:
      payload = {
          'embeddings': [
              {'values': [0.1, 0.2]} for _ in request_dict.get('requests', [])
          ]
      }
    return types.HttpResponse(headers={}, body=json.dumps(payload))

  with mock.patch.object(
      mock_client._api_client, 'async_request', side_effect=fake_async_request
  ):
    single_resp = await mock_client.aio.models.embed_content(
        model='gemini-embedding-001',
        contents='hello',
    )
    ge1_batch_resp = await mock_client.aio.models.embed_content(
        model='gemini-embedding-001',
        contents=['one', 'two'],
    )
    ge2_str_list_resp = await mock_client.aio.models.embed_content(
        model='gemini-embedding-2',
        contents=['one', 'two'],
    )
    ge2_batch_resp = await mock_client.aio.models.embed_content(
        model='gemini-embedding-2',
        contents=[
            types.Content(parts=[types.Part.from_text(text='one')]),
            types.Content(parts=[types.Part.from_text(text='two')]),
        ],
    )
    if use_vertex:
      with pytest.raises(
          ValueError,
          match=(
              'The embedContent API for this model only supports one content'
              ' at a time.'
          ),
      ):
        await mock_client.aio.models.embed_content(
            model=(
                'publishers/intfloat/models/multilingual-e5-large-instruct-maas'
            ),
            contents=[
                types.Content(parts=[types.Part.from_text(text='one')]),
                types.Content(parts=[types.Part.from_text(text='two')]),
            ],
        )

  assert len(captured) == 4

  if use_vertex:
    assert captured[0][0].endswith('gemini-embedding-001:embedContent')
    assert captured[1][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert captured[2][0].endswith('gemini-embedding-2:embedContent')
    assert captured[3][0].endswith('gemini-embedding-2:batchEmbedContents')
  else:
    assert captured[0][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert captured[1][0].endswith('gemini-embedding-001:batchEmbedContents')
    assert captured[2][0].endswith('gemini-embedding-2:batchEmbedContents')
    assert len(captured[2][1]['requests']) == 1
    assert captured[3][0].endswith('gemini-embedding-2:batchEmbedContents')
    assert len(captured[3][1]['requests']) == 2
  assert len(single_resp.embeddings) == 1
  assert len(ge1_batch_resp.embeddings) == 2
  assert len(ge2_str_list_resp.embeddings) == 1
  assert len(ge2_batch_resp.embeddings) == 2
