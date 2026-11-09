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


"""Tests for operations._get."""

from .. import pytest_helper
from ... import types


def test_project_operation_get(client):
  test_operation_id = '3787416390563004416'
  if client._api_client.vertexai:
    operation = client.operations._get(
        operation_id=test_operation_id
    )
    assert operation.name.endswith(test_operation_id)
    assert operation.done
    assert isinstance(operation, types.ProjectOperation)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='operations._get',
)
