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


"""Tests for tunings.get()."""

from ... import types as genai_types
from .. import pytest_helper

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_vertexai",
        parameters=genai_types._GetTuningJobParameters(
            name="projects/801452371447/locations/us-central1/tuningJobs/4303478340632707072"
        ),
        exception_if_mldev="Not Found",
    ),
    pytest_helper.TestTableItem(
        name="test_vertexai_with_pretuned_model",
        parameters=genai_types._GetTuningJobParameters(
            name="projects/801452371447/locations/us-central1/tuningJobs/8520221517529743360",
        ),
        exception_if_mldev="Not Found",
    ),
    pytest_helper.TestTableItem(
        name="test_mldev",
        parameters=genai_types._GetTuningJobParameters(
            name="tunedModels/generate-num-1896"
        ),
        exception_if_vertex="Not Found",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="tunings.get",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)


def test_helper_properties(client):
  if client._api_client.vertexai:
    job = client.tunings.get(
        name="projects/801452371447/locations/us-central1/tuningJobs/4303478340632707072",
    )
  else:
    job = client.tunings.get(
        name="tunedModels/testdatasetexamples-model-j0fpgpaksvri"
    )

  assert job.has_ended
  assert job.has_succeeded
