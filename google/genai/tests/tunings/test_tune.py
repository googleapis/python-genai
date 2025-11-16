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

from ... import types as genai_types
from .. import pytest_helper
import pytest

evaluation_config=genai_types.EvaluationConfig(
    metrics=[
        genai_types.Metric(name="bleu", prompt_template="test prompt template")
    ],
    output_config=genai_types.OutputConfig(
        gcs_destination=genai_types.GcsDestination(
            output_uri_prefix="gs://sararob_test/"
        )
    ),
)

test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_dataset_gcs_uri",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
        ),
        exception_if_mldev="gcs_uri parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_tune_pretuned_model",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="projects/801452371447/locations/us-central1/models/9030969596621881344",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
            ),
        ),
        exception_if_mldev="is not supported in Gemini API",
    ),
    pytest_helper.TestTableItem(
        name="test_tune_pretuned_model_with_checkpoint_id",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="projects/801452371447/locations/us-central1/models/9030969596621881344",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                pre_tuned_model_checkpoint_id="3",
            ),
        ),
        exception_if_mldev="is not supported in Gemini API",
    ),
    pytest_helper.TestTableItem(
        name="test_tune_simple_dpo",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                tuned_model_display_name="Model display name",
                epoch_count=1,
                method="PREFERENCE_TUNING",
            ),
        ),
        exception_if_mldev="parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_tune_dpo_with_beta",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                tuned_model_display_name="Model display name",
                epoch_count=1,
                method=genai_types.TuningMethod.PREFERENCE_TUNING,
                beta=0.5,
            ),
        ),
        exception_if_mldev="parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_non_pretuned_model_with_checkpoint_id",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                pre_tuned_model_checkpoint_id="3",
            ),
        ),
        exception_if_mldev="is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_gcs_uri_all_parameters",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
            ),
            config=genai_types.CreateTuningJobConfig(
                tuned_model_display_name="Model display name",
                epoch_count=1,
                learning_rate_multiplier=1.0,
                adapter_size="ADAPTER_SIZE_ONE",
                validation_dataset=genai_types.TuningValidationDataset(
                    gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_validation_data.jsonl",
                ),
            ),
        ),
        exception_if_mldev="gcs_uri parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_vertex_dataset_resource",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                vertex_dataset_resource="projects/801452371447/locations/us-central1/datasets/5779918772206829568",
            ),
        ),
        exception_if_mldev="vertex_dataset_resource parameter is not supported in Gemini API.",
    ),
    pytest_helper.TestTableItem(
        name="test_dataset_dataset_resource_all_parameters",
        parameters=genai_types.CreateTuningJobParameters(
            base_model="gemini-2.5-flash",
            training_dataset=genai_types.TuningDataset(
                vertex_dataset_resource="projects/801452371447/locations/us-central1/datasets/5779918772206829568",
            ),
            config=genai_types.CreateTuningJobConfig(
                tuned_model_display_name="Model display name",
                epoch_count=1,
                learning_rate_multiplier=1.0,
                adapter_size="ADAPTER_SIZE_ONE",
                validation_dataset=genai_types.TuningValidationDataset(
                    vertex_dataset_resource="projects/801452371447/locations/us-central1/datasets/1168232753779441664",
                ),
                labels={"testlabelkey": "testlabelvalue"},
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


@pytest.mark.skipif(
    "config.getoption('--private')",
    reason="Skipping in pre-public tests"
)
def test_eval_config(client):
  """Tests tuning with eval config."""

  if client._api_client.vertexai:
    tuning_job = client.tunings.tune(
      base_model="gemini-2.5-flash",
      training_dataset=genai_types.TuningDataset(gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl"),
      config=genai_types.CreateTuningJobConfig(
          tuned_model_display_name="tuning job with eval config",
          epoch_count=1,
          learning_rate_multiplier=1.0,
          adapter_size="ADAPTER_SIZE_ONE",
          validation_dataset=genai_types.TuningValidationDataset(
              gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_validation_data.jsonl"
          ),
          evaluation_config=evaluation_config,
      ),
    )

    assert tuning_job.state == genai_types.JobState.JOB_STATE_PENDING
    assert tuning_job.evaluation_config == evaluation_config


@pytest.mark.skipif(
    "config.getoption('--private')",
    reason="Skipping in pre-public tests"
)
def test_eval_config_with_metrics(client):
  """Tests tuning with eval config metrics."""
  if client._api_client.vertexai:
    evaluation_config=genai_types.EvaluationConfig(
        metrics=[
            genai_types.Metric(
                name="prompt-relevance",
                prompt_template="How well does the response address the prompt?: PROMPT: {request}\n RESPONSE: {response}\n",
                return_raw_output=True,
                judge_model_system_instruction="You are a cat. Make all evaluations from this perspective.",
            ),
            genai_types.Metric(name='bleu'),
            genai_types.Metric(name='rouge_1'),
        ],
        output_config=genai_types.OutputConfig(
            gcs_destination=genai_types.GcsDestination(
                output_uri_prefix="gs://sararob_test/"
            )
        ),
        autorater_config=genai_types.AutoraterConfig(
            sampling_count=1,
            autorater_model="test-model",
        ),
    )
    tuning_job = client.tunings.tune(
      base_model="gemini-2.5-flash",
      training_dataset=genai_types.TuningDataset(gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl"),
      config=genai_types.CreateTuningJobConfig(
          tuned_model_display_name="tuning job with eval config",
          epoch_count=1,
          learning_rate_multiplier=1.0,
          adapter_size="ADAPTER_SIZE_ONE",
          validation_dataset=genai_types.TuningValidationDataset(
              gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_validation_data.jsonl"
          ),
          evaluation_config=evaluation_config,
      ),
    )
    assert tuning_job.state == genai_types.JobState.JOB_STATE_PENDING


@pytest.mark.skipif(
    "config.getoption('--private')",
    reason="Skipping in pre-public tests"
)
@pytest.mark.asyncio
async def test_eval_config_async(client):
  """Tests tuning with eval config."""
  if client._api_client.vertexai:
    tuning_job = await client.aio.tunings.tune(
      base_model="gemini-2.5-flash",
      training_dataset=genai_types.TuningDataset(gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl"),
      config=genai_types.CreateTuningJobConfig(
          tuned_model_display_name="tuning job with eval config",
          epoch_count=1,
          learning_rate_multiplier=1.0,
          adapter_size="ADAPTER_SIZE_ONE",
          validation_dataset=genai_types.TuningValidationDataset(
              gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_validation_data.jsonl"
          ),
          evaluation_config=evaluation_config,
      ),
    )

    assert tuning_job.state == genai_types.JobState.JOB_STATE_PENDING
