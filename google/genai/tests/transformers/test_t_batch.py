# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Tests for t_batch."""

import pytest
from ... import _transformers as t
from ... import client as google_genai_client_module
from ... import types


@pytest.fixture
def vertex_client():
  yield google_genai_client_module.Client(
      vertexai=True, project='test-project', location='test-location'
  )


@pytest.fixture
def mldev_client():
  yield google_genai_client_module.Client(
      vertexai=False, api_key='test-api-key'
  )


@pytest.mark.usefixtures('vertex_client', 'mldev_client')
class TestBatchJobSource:

  # Test cases for src as str
  @pytest.mark.parametrize(
      'src_str, expected_gcs_uri, expected_bigquery_uri, expected_file_name,'
      ' expected_format',
      [
          (
              'gs://bucket/path/to/data.jsonl',
              ['gs://bucket/path/to/data.jsonl'],
              None,
              None,
              'jsonl',
          ),
          (
              'bq://project.dataset.table',
              None,
              'bq://project.dataset.table',
              None,
              'bigquery',
          ),
          ('files/data.csv', None, None, 'files/data.csv', None),
      ],
  )
  def test_batch_job_source_str(
      self,
      mldev_client,
      src_str,
      expected_gcs_uri,
      expected_bigquery_uri,
      expected_file_name,
      expected_format,
  ):
    result = t.t_batch_job_source(mldev_client, src_str)
    expected = types.BatchJobSource(
        gcs_uri=expected_gcs_uri,
        bigquery_uri=expected_bigquery_uri,
        file_name=expected_file_name,
        format=expected_format,
    )
    assert result == expected

  def test_batch_job_source_str_unsupported(self, mldev_client):
    with pytest.raises(ValueError, match='Unsupported source'):
      t.t_batch_job_source(mldev_client, 'http://example.com/data')
    with pytest.raises(ValueError, match='Unsupported source'):
      t.t_batch_job_source(mldev_client, 'invalid-path')

  # Test cases for src as list
  def test_batch_job_source_list_empty(self, mldev_client):
    result = t.t_batch_job_source(mldev_client, [])
    expected = types.BatchJobSource(inlined_requests=[])
    assert result == expected

  def test_batch_job_source_list_with_items(self, mldev_client):
    inlined_data = [
        types.InlinedRequest(
            contents=[types.Content(parts=[types.Part(text='item1')])]
        ),
        types.InlinedRequest(
            contents=[types.Content(parts=[types.Part(text='item2')])]
        ),
    ]
    result = t.t_batch_job_source(mldev_client, inlined_data)
    expected = types.BatchJobSource(inlined_requests=inlined_data)
    assert result == expected

  # Test cases for src as dict
  def test_batch_job_source_dict(self, vertex_client, mldev_client):
    src_dict = {'gcs_uri': ['gs://test/file.jsonl'], 'format': 'jsonl'}
    result = t.t_batch_job_source(vertex_client, src_dict)
    expected = types.BatchJobSource(
        gcs_uri=['gs://test/file.jsonl'], format='jsonl'
    )
    assert result == expected

    src_dict_inlined = {
        'inlined_requests': [{
            'contents': [{
                'parts': [{
                    'text': 'Hello!',
                }],
                'role': 'user',
            }],
        }]
    }
    result_inlined = t.t_batch_job_source(mldev_client, src_dict_inlined)
    expected_inlined = types.BatchJobSource(inlined_requests=[{
            'contents': [{
                'parts': [{
                    'text': 'Hello!',
                }],
                'role': 'user',
            }],
        }])
    assert result_inlined == expected_inlined

  # Test cases for src as types.BatchJobSource (mocked MockBatchJobSource)

  def test_batch_job_source_mldev_valid_file_name(self, mldev_client):
    src_obj = types.BatchJobSource(file_name='files/my_data.csv')
    result = t.t_batch_job_source(mldev_client, src_obj)
    assert result is src_obj

  def test_batch_job_source_mldev_invalid_both_set(self, mldev_client):
    src_obj = types.BatchJobSource(
        inlined_requests=[types.InlinedRequest()],
        file_name='files/data.csv',
    )
    with pytest.raises(
        ValueError,
        match='`inlined_requests`, `file_name`,',
    ):
      t.t_batch_job_source(mldev_client, src_obj)

  def test_batch_job_source_mldev_invalid_neither_set(self, mldev_client):
    src_obj = types.BatchJobSource(
        gcs_uri=['gs://temp']
    )
    with pytest.raises(
        ValueError,
        match='`inlined_requests`, `file_name`,',
    ):
      t.t_batch_job_source(mldev_client, src_obj)

  # client.vertexai = True (Vertex AI)
  def test_batch_job_source_vertexai_valid_gcs(self, vertex_client):
    src_obj = types.BatchJobSource(gcs_uri=['gs://vertex-bucket/data.jsonl'])
    result = t.t_batch_job_source(vertex_client, src_obj)
    assert result is src_obj

  def test_batch_job_source_vertexai_valid_bigquery(self, vertex_client):
    src_obj = types.BatchJobSource(bigquery_uri='bq://project.dataset.table')
    result = t.t_batch_job_source(vertex_client, src_obj)
    assert result is src_obj

  def test_batch_job_source_vertexai_valid_both(self, vertex_client):
    src_obj = types.BatchJobSource(
        gcs_uri=['gs://vertex-bucket/data.jsonl'],
        bigquery_uri='bq://project.dataset.table',
    )
    with pytest.raises(ValueError, match='`gcs_uri` or `bigquery_uri`'):
      t.t_batch_job_source(vertex_client, src_obj)

  def test_batch_job_source_vertexai_invalid_neither_set(self, vertex_client):
    src_obj = types.BatchJobSource(
        file_name='files/data.csv'
    )
    with pytest.raises(ValueError, match='`gcs_uri` or `bigquery_uri`'):
      t.t_batch_job_source(vertex_client, src_obj)


class TestBatchJobDestination:

  @pytest.mark.parametrize(
      'dest_str, expected_gcs_uri, expected_bigquery_uri, expected_format',
      [
          (
              'gs://bucket/path/to/output',
              'gs://bucket/path/to/output',
              None,
              'jsonl',
          ),
          (
              'bq://project.dataset.output_table',
              None,
              'bq://project.dataset.output_table',
              'bigquery',
          ),
      ],
  )
  def test_valid_destinations(
      self, dest_str, expected_gcs_uri, expected_bigquery_uri, expected_format
  ):
    result = t.t_batch_job_destination(dest_str)
    expected = types.BatchJobDestination(
        gcs_uri=expected_gcs_uri,
        bigquery_uri=expected_bigquery_uri,
        format=expected_format,
    )
    assert result == expected

  def test_unsupported_destination(self):
    with pytest.raises(ValueError, match='Unsupported destination'):
      t.t_batch_job_destination('local/path/output.jsonl')
    with pytest.raises(ValueError, match='Unsupported destination'):
      t.t_batch_job_destination('http://some.url')


class TestBatchJobName:

  def test_mldev_valid_name(self, mldev_client):
    name = 'batches/my-job-123'
    assert t.t_batch_job_name(mldev_client, name) == 'my-job-123'

  @pytest.mark.parametrize(
      'invalid_name',
      [
          'my-job-123',
          'batches/my-job/suffix',
          'batches/',
          'batches/my-job-123/',
      ],
  )
  def test_mldev_invalid_name(self, mldev_client, invalid_name):
    with pytest.raises(ValueError, match='Invalid batch job name'):
      t.t_batch_job_name(mldev_client, invalid_name)

  def test_vertexai_valid_full_path(self, vertex_client):
    name = 'projects/123/locations/us-central1/batchPredictionJobs/my-vertex-job-456'
    assert t.t_batch_job_name(vertex_client, name) == 'my-vertex-job-456'

  def test_vertexai_valid_digit_name(self, vertex_client):
    name = '9876543210'
    assert t.t_batch_job_name(vertex_client, name) == '9876543210'

  @pytest.mark.parametrize(
      'invalid_name',
      [
          'my-vertex-job-456',
          'projects/123/locations/us-central1/job/my-vertex-job-456',
          'projects/123/locations/us-central1/batchPredictionJobs/',
          'not-a-number-or-path',
          'batchPredictionJobs/my-job',
      ],
  )
  def test_vertexai_invalid_name(self, vertex_client, invalid_name):
    with pytest.raises(ValueError, match='Invalid batch job name'):
      t.t_batch_job_name(vertex_client, invalid_name)


class TestJobState:

  @pytest.mark.parametrize(
      'input_state, expected_output_state',
      [
          ('BATCH_STATE_UNSPECIFIED', 'JOB_STATE_UNSPECIFIED'),
          ('BATCH_STATE_PENDING', 'JOB_STATE_PENDING'),
          ('BATCH_STATE_SUCCEEDED', 'JOB_STATE_SUCCEEDED'),
          ('BATCH_STATE_FAILED', 'JOB_STATE_FAILED'),
          ('BATCH_STATE_CANCELLED', 'JOB_STATE_CANCELLED'),
          ('BATCH_STATE_EXPIRED', 'JOB_STATE_EXPIRED'),
          ('BATCH_STATE_RUNNING', 'JOB_STATE_RUNNING'),
          ('BATCH_STATE_FOOBAR', 'BATCH_STATE_FOOBAR'),
      ],
  )
  def test_job_state_mapping(self, input_state, expected_output_state):
    assert t.t_job_state(input_state) == expected_output_state
