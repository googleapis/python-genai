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


"""Tests batches.create(), batches.get(), batches.cancel()."""

from .... import types as genai_types
from ... import pytest_helper


def create_get_cancel(client, parameters):
  batch_job = client.batches.create(
      model=parameters.model,
      src=parameters.src,
      config=parameters.config,
  )
  batch_job = client.batches.get(name=batch_job.name)
  client.batches.cancel(name=batch_job.name)


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_create_get_cancel_mldev",
        parameters=genai_types._CreateBatchJobParameters(
            model="gemini-2.5-flash",
            src=[{
                "contents": [{
                    "parts": [{"text": "Why is the sky blue?"}],
                    "role": "user",
                }]
            }],
        ),
        exception_if_vertex="not supported in Vertex AI.",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="create_get_cancel",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
