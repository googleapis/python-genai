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


"""Tests for the Gemini Developer API BatchJob response converter."""

from typing import Any

from ... import batches
from ... import types


def _batch_job_from_mldev(response: dict[str, Any]) -> types.BatchJob:
  return types.BatchJob._from_response(
      response=batches._BatchJob_from_mldev(response), kwargs={}
  )


def test_batch_job_from_mldev_sets_src_file_name():
  """The input file name in the response metadata populates src.file_name."""
  job = _batch_job_from_mldev({
      'name': 'batches/123',
      'metadata': {
          'state': 'BATCH_STATE_PENDING',
          'inputConfig': {'fileName': 'files/abc'},
      },
  })

  assert job.src is not None
  assert job.src.file_name == 'files/abc'
  assert job.src.inlined_requests is None


def test_batch_job_from_mldev_inlined_requests_leaves_src_unset():
  """Inline requests in the response are not mapped to src."""
  job = _batch_job_from_mldev({
      'name': 'batches/123',
      'metadata': {
          'state': 'BATCH_STATE_PENDING',
          'inputConfig': {
              'requests': {
                  'requests': [{
                      'request': {'contents': [{'parts': [{'text': 'Hello'}]}]},
                  }],
              },
          },
      },
  })

  assert job.name == 'batches/123'
  assert job.src is None


def test_batch_job_from_mldev_without_input_config():
  """A response without inputConfig leaves src unset."""
  job = _batch_job_from_mldev({
      'name': 'batches/123',
      'metadata': {'state': 'BATCH_STATE_SUCCEEDED'},
  })

  assert job.state == types.JobState.JOB_STATE_SUCCEEDED
  assert job.src is None
