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
# %%


"""Tests for create_sft_job."""

from ... import types as genai_types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_dataset_gcs_uri",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-1.5-pro-002",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
        ),
        exception_if_mldev="gcs_uri parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_gcs_uri_all_parameters",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-1.5-pro-002",
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
                # Not supported in Vertex AI
                # batch_size=4,
                # learning_rate=0.01,
            ),
        ),
        exception_if_mldev="gcs_uri parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_gcs_uri_parameters_unsupported_by_vertex",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-1.5-pro-002",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                # Not supported in Vertex AI
                batch_size=4,
                learning_rate=0.01,
            ),
        ),
        exception_if_vertex="batch_size parameter is not supported in Vertex AI.",
        exception_if_mldev="gcs_uri parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_examples_parameters_unsupported_by_mldev",
        parameters=genai_types._CreateTuningJobParameters(
            # Error: "models/gemini-1.5-pro-002 is not found for
            # CREATE TUNED MODEL at API version v1beta."
            # base_model="gemini-1.5-pro-002",
            base_model="models/gemini-1.0-pro-001",
            training_dataset=genai_types.TuningDataset(
                examples=[
                    genai_types.TuningExample(
                        text_input=f"Input text {i}",
                        output=f"Output text {i}",
                    )
                    for i in range(5)
                ],
            ),
            # Required for MLDev:
            # "Either tuned_model_id or display_name must be set."
            config=genai_types.CreateTuningJobConfig(
                tuned_model_display_name="Model display name",
                # Not supported in MLDev
                adapter_size="ADAPTER_SIZE_ONE",
                # Generator issue: "validationDatasetUri": {}. See b/375079287
                # validation_dataset=genai_types.TuningDataset(
                #     gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_validation_data.jsonl",
                # ),
            ),
        ),
        exception_if_mldev="adapter_size parameter is not supported in Gemini API.",
        exception_if_vertex="examples parameter is not supported in Vertex AI.",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_vertex_dataset_resource",
        parameters=genai_types._CreateTuningJobParameters(
            base_model="gemini-1.5-pro-002",
            training_dataset=genai_types.TuningDataset(
                vertex_dataset_resource="projects/613165508263/locations/us-central1/datasets/8254568702121345024",
            ),
        ),
        exception_if_mldev="vertex_dataset_resource parameter is not supported in Gemini API.",
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
                # Not supported in Vertex AI
                # batch_size=4,
                # learning_rate=0.01,
            ),
        ),
        exception_if_mldev="vertex_dataset_resource parameter is not supported in Gemini API.",
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="tunings.tune",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)
