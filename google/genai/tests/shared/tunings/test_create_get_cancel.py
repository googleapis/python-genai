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


"""Tests tunings.tune(), tunings.get(), tunings.cancel()."""

from .... import types as genai_types
from ... import pytest_helper


def create_get_cancel(client, parameters):
  tuning_job = client.tunings.tune(
      base_model=parameters.base_model,
      training_dataset=parameters.training_dataset,
      config=parameters.config,
  )
  tuning_job = client.tunings.get(name=tuning_job.name)
  client.tunings.cancel(name=tuning_job.name)


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_create_get_cancel",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                epoch_count=1,
            ),
        ),
        exception_if_mldev="not supported in Gemini API.",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="create_get_cancel",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
