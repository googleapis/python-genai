"""Tests for create_sft_job."""

from ... import types as genai_types
from .. import pytest_helper
from ... import _replay_api_client


test_table: list[pytest_helper.TestTableItem] = []

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="tunings.tune",
    test_table=test_table,
)

pytest_plugins = ("pytest_asyncio",)


def test_tune_until_success(client):
  import time

  if client._api_client.vertexai:
    job = client.tunings.tune(
        base_model="gemini-1.5-pro-002",
        training_dataset=genai_types.TuningDataset(
            gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl",
        ),
    )
  else:
    job = client.tunings.tune(
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
            tuned_model_display_name="test_dataset_examples model",
        ),
    )

  while not job.has_ended:
    # Skipping the sleep for when in replay mode.
    if not isinstance(client._api_client, _replay_api_client.ReplayApiClient):
      time.sleep(60)
    job = client.tunings.get(name=job.name)

  assert job.has_ended
  assert job.has_succeeded
