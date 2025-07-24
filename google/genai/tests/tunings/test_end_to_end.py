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
        base_model="gemini-2.0-flash-001",
        training_dataset=genai_types.TuningDataset(
            gcs_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
        ),
    )
  else:
    # Remove GenAI SDK test since it is deprecated:
    # https://ai.google.dev/gemini-api/docs/model-tuning
    return

  while not job.has_ended:
    # Skipping the sleep for when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(60)
    job = client.tunings.get(name=job.name)

  assert job.has_ended
  assert job.has_succeeded
