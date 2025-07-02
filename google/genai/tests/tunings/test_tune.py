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


"""Tests for create_sft_job."""

from ... import types as genai_types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_dataset_gcs_uri",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
        ),
        exception_if_mldev="todo err msg",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_gcs_uri_all_parameters",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                tuned_model_display_name="Model display name",
                epoch_count=1,
                learning_rate_multiplier=1.0,
                adapter_size="ADAPTER_SIZE_ONE",
                validation_dataset=genai_types.TuningDataset(
                    gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_validation_data.jsonl",
                ),
            ),
        ),
        exception_if_mldev="todo err msg",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_vertex_dataset_resource",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-1.5-pro-002",
            training_dataset=genai_types.TuningDataset(
                vertex_dataset_resource="projects/613165508263/locations/us-central1/datasets/8254568702121345024",
            ),
        ),
        exception_if_mldev="todo err msg",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_dataset_resource_all_parameters",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-1.5-pro-002",
            training_dataset=genai_types.TuningDataset(
                vertex_dataset_resource="projects/613165508263/locations/us-central1/datasets/8254568702121345024",
            ),
            config=genai_types.CreateTuningJobConfig(
                tuned_model_display_name="Model display name",
                epoch_count=1,
                learning_rate_multiplier=1.0,
                adapter_size="ADAPTER_SIZE_ONE",
                validation_dataset=genai_types.TuningDataset(
                    vertex_dataset_resource="projects/613165508263/locations/us-central1/datasets/5556912525326417920",
                ),
            ),
        ),
        exception_if_mldev="todo err msg",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="tunings.tune",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
