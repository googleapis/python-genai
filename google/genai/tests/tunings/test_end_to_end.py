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


"""Tests for tunings.tune()."""

import time
from ... import _replay_api_client
from ... import types as genai_types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = []

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="tunings.tune",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)


def test_tune_until_success(client):
  if client._api_client.vertexai:
    job = client.tunings.tune(
        base_model="gemini-2.5-flash-lite",
        training_dataset=genai_types.TuningDataset(
            gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
        ),
        config=genai_types.CreateTuningJobConfig(
            epoch_count=1,
        ),
    )
  else:
    # Remove GenAI SDK test since it is deprecated:
    # https://ai.google.dev/gemini-api/docs/model-tuning
    return

  while not job.has_ended:
    # Skipping the sleep for when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(300)
    job = client.tunings.get(name=job.name)

  assert job.has_ended
  assert job.has_succeeded


def test_continuous_tuning(client):
  if not client._api_client.vertexai:
    return

  job = client.tunings.tune(
      base_model="gemini-2.5-flash",
      training_dataset=genai_types.TuningDataset(
          gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
      ),
      config=genai_types.CreateTuningJobConfig(
          epoch_count=1,
      ),
  )

  while not job.has_ended:
    # Skipping the sleep for when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(300)
    job = client.tunings.get(name=job.name)

  assert job.has_ended
  assert job.has_succeeded

  continuous_job = client.tunings.tune(
      base_model=job.tuned_model.model,
      training_dataset=genai_types.TuningDataset(
          gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
      ),
      config=genai_types.CreateTuningJobConfig(
          tuned_model_display_name="continuous tuning job",
          epoch_count=1,
      )
  )

  while not continuous_job.has_ended:
    # Skipping the sleep for when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(300)
    continuous_job = client.tunings.get(name=continuous_job.name)

  assert continuous_job.has_ended
  assert continuous_job.has_succeeded


