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

"""Tests for batch response converters."""

from ... import batches
from ... import types


def test_mldev_batch_job_parses_input_config_src():
  response = {
      'name': 'batches/test-batch',
      'metadata': {
          'inputConfig': {
              'fileName': 'files/input-file',
          },
          'output': {
              'responsesFile': 'files/output-file',
          },
      },
  }

  parsed = types.BatchJob._from_response(
      response=batches._BatchJob_from_mldev(response),
      kwargs={},
  )

  assert parsed.src is not None
  assert parsed.src.file_name == 'files/input-file'
  assert parsed.dest is not None
  assert parsed.dest.file_name == 'files/output-file'
