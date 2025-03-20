# Copyright 2024 Google LLC
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


"""Tests for generate_videos."""

import os
import time
import pytest

from ... import _replay_api_client
from ... import types
from .. import pytest_helper

VEO_MODEL_LATEST = "veo-2.0-generate-001"

GCS_IMAGE = types.Image(
    gcs_uri="gs://cloud-samples-data/vertex-ai/llm/prompts/landmark1.png",
    # Required
    mime_type="image/png",
)

IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/bridge1.png")
)
LOCAL_IMAGE = types.Image.from_file(location=IMAGE_FILE_PATH)


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_simple_prompt",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            prompt="Man with a dog",
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_all_parameters_vertex",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            prompt="A neon hologram of a cat driving at top speed",
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                output_gcs_uri=(
                    "gs://unified-genai-tests/tmp/genai/video/outputs"
                ),
                fps=30,
                duration_seconds=6,
                seed=1,
                aspect_ratio="16:9",
                resolution="720p",
                person_generation="allow_adult",
                # pubsub_topic="projects/<my-project>/topics/video-generation-test",
                negative_prompt="ugly, low quality",
                enhance_prompt=True,
            ),
        ),
        exception_if_mldev=(
            "output_gcs_uri parameter is not supported in Gemini API"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_all_parameters_mldev",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            prompt="A neon hologram of a cat driving at top speed",
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=6,
                aspect_ratio="16:9",
                person_generation="allow_adult",
                negative_prompt="ugly, low quality",
            ),
        ),
    ),
]

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="models.generate_videos",
    test_table=test_table,
)


def test_text_to_video_poll(client):
  operation = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="A neon hologram of a cat driving at top speed",
      config=types.GenerateVideosConfig(
          output_gcs_uri="gs://unified-genai-tests/tmp/genai/video/outputs"
          if client.vertexai
          else None,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if not isinstance(client.api_client, _replay_api_client.ReplayApiClient):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_image_to_video_poll(client):
  output_gcs_uri = "gs://unified-genai-tests/tmp/genai/video/outputs" if client.vertexai else None
  operation = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      image=GCS_IMAGE if client.vertexai else LOCAL_IMAGE,
      config=types.GenerateVideosConfig(
          output_gcs_uri=output_gcs_uri,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if not isinstance(client.api_client, _replay_api_client.ReplayApiClient):
      time.sleep(60)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_text_and_image_to_video_poll(client):
  output_gcs_uri = "gs://unified-genai-tests/tmp/genai/video/outputs" if client.vertexai else None
  operation = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="Lightning storm",
      image=GCS_IMAGE if client.vertexai else LOCAL_IMAGE,
      config=types.GenerateVideosConfig(
          output_gcs_uri=output_gcs_uri,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if not isinstance(client.api_client, _replay_api_client.ReplayApiClient):
      time.sleep(60)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_create_operation_to_poll(client):
  if client.vertexai:
    # Fill in project and location for record mode
    operation_name = "projects/<project>/locations/<location>/publishers/google/models/veo-2.0-generate-001/operations/ce4324d0-1a9f-4fd0-98de-0c54e2ca5798"
  else:
    operation_name = "models/veo-2.0-generate-001/operations/s421ckxsogje"

  operation = types.GenerateVideosOperation(
      name=operation_name,
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if not isinstance(client.api_client, _replay_api_client.ReplayApiClient):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


@pytest.mark.asyncio
async def test_text_to_video_poll_async(client):
  operation = await client.aio.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="A neon hologram of a cat driving at top speed",
      config=types.GenerateVideosConfig(
          output_gcs_uri="gs://unified-genai-tests/tmp/genai/video/outputs"
          if client.vertexai
          else None,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if not isinstance(client.api_client, _replay_api_client.ReplayApiClient):
      time.sleep(20)
    operation = await client.aio.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri
