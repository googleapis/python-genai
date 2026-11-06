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

"""Tests for operation transformers."""

from unittest import mock

import pytest

from ... import _transformers as t


class _PendingOperationClient:

  def __init__(self) -> None:
    self.request_count = 0

  def request(self, **kwargs):
    self.request_count += 1
    if self.request_count > 5:
      raise AssertionError('operation polling did not time out')
    return {
        'name': 'projects/test/locations/us-central1/operations/123',
        'done': False,
    }


def test_resolve_operation_times_out_for_pending_operation(monkeypatch):
  client = _PendingOperationClient()

  monkeypatch.setattr(t, 'LRO_POLLING_INITIAL_DELAY_SECONDS', 0.5)
  monkeypatch.setattr(t, 'LRO_POLLING_MAXIMUM_DELAY_SECONDS', 0.5)
  monkeypatch.setattr(t, 'LRO_POLLING_TIMEOUT_SECONDS', 1.0)

  with mock.patch.object(t.time, 'sleep') as sleep_mock:
    with pytest.raises(RuntimeError, match='timed out'):
      t.t_resolve_operation(
          client,
          {
              'name': 'projects/test/locations/us-central1/operations/123',
              'done': False,
          },
      )

  assert client.request_count == 3
  sleep_mock.assert_has_calls([mock.call(0.5), mock.call(0.5), mock.call(0.5)])
