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


"""Tests for generate_videos."""

import os
import time
import pytest

from ... import _replay_api_client
from ... import types
from .. import pytest_helper

VEO_MODEL_LATEST = "veo-2.0-generate-001"

OUTPUT_GCS_URI = "gs://genai-sdk-tests/temp/videos/"

GCS_IMAGE = types.Image(
    gcs_uri="gs://cloud-samples-data/vertex-ai/llm/prompts/landmark1.png",
    # Required
    mime_type="image/png",
)

GCS_IMAGE2 = types.Image(
    gcs_uri="gs://cloud-samples-data/vertex-ai/llm/prompts/landmark2.png",
    # Required
    mime_type="image/png",
)

IMAGE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/bridge1.png")
)
LOCAL_IMAGE = types.Image.from_file(location=IMAGE_FILE_PATH)

LOCAL_IMAGE_MAN = types.Image.from_file(
    location=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/man.jpg")
    )
)

LOCAL_IMAGE_DOG = types.Image.from_file(
    location=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/dog.jpg")
    )
)

GCS_OUTPAINT_MASK = types.Image(
    gcs_uri="gs://genai-sdk-tests/inputs/videos/video_outpaint_mask.png",
    mime_type="image/png",
)

GCS_REMOVE_MASK = types.Image(
    gcs_uri="gs://genai-sdk-tests/inputs/videos/video_remove_mask.png",
    mime_type="image/png",
)

GCS_REMOVE_STATIC_MASK = types.Image(
    gcs_uri="gs://genai-sdk-tests/inputs/videos/video_remove_static_mask.png",
    mime_type="image/png",
)


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
                output_gcs_uri=OUTPUT_GCS_URI,
                fps=30,
                duration_seconds=6,
                seed=1,
                aspect_ratio="16:9",
                resolution="720p",
                person_generation="allow_adult",
                # pubsub_topic="projects/<my-project>/topics/video-generation-test",
                negative_prompt="ugly, low quality",
                enhance_prompt=True,
                compression_quality=types.VideoCompressionQuality.LOSSLESS,
            ),
        ),
        exception_if_mldev=(
            "not supported in Gemini API"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_from_text_source",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            source=types.GenerateVideosSource(prompt="Man with a dog"),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_from_image_source",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            source=types.GenerateVideosSource(
                image=LOCAL_IMAGE,
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_from_text_and_image_source",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            source=types.GenerateVideosSource(
                prompt="Lightning storm",
                image=LOCAL_IMAGE,
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_from_video_source",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            source=types.GenerateVideosSource(
                video=types.Video(
                    uri="gs://genai-sdk-tests/inputs/videos/cat_driving.mp4",
                ),
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                output_gcs_uri=OUTPUT_GCS_URI,
            ),
        ),
        exception_if_mldev=(
            "not supported in Gemini API"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_from_text_and_video_source",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST,
            source=types.GenerateVideosSource(
                prompt="Rain",
                video=types.Video(
                    uri="gs://genai-sdk-tests/inputs/videos/cat_driving.mp4",
                ),
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                output_gcs_uri=OUTPUT_GCS_URI,
            ),
        ),
        exception_if_mldev=(
            "not supported in Gemini API"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_video_edit_outpaint",
        parameters=types._GenerateVideosParameters(
            model="veo-2.0-generate-exp",
            source=types.GenerateVideosSource(
                prompt="A mountain landscape",
                video=types.Video(
                    uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
                ),
            ),
            config=types.GenerateVideosConfig(
                output_gcs_uri=OUTPUT_GCS_URI,
                aspect_ratio="16:9",
                mask=types.VideoGenerationMask(
                    image=GCS_OUTPAINT_MASK,
                    mask_mode=types.VideoGenerationMaskMode.OUTPAINT,
                ),
            ),
        ),
        exception_if_mldev=(
            "not supported in Gemini API"
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
                enhance_prompt=True,
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_all_parameters_veo3_mldev",
        parameters=types._GenerateVideosParameters(
            model="veo-3.0-generate-preview",
            prompt="A neon hologram of a cat driving at top speed",
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                aspect_ratio="16:9",
                resolution="1080p",
                negative_prompt="ugly, low quality",
            ),
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_reference_to_video",
        parameters=types._GenerateVideosParameters(
            model="veo-2.0-generate-exp",
            prompt="Rain",
            config=types.GenerateVideosConfig(
                output_gcs_uri=OUTPUT_GCS_URI,
                reference_images=[
                    types.VideoGenerationReferenceImage(
                        image=GCS_IMAGE,
                        reference_type=types.VideoGenerationReferenceType.STYLE,
                    )
                ],
            ),
        ),
        exception_if_mldev=(
            "not supported in Gemini API"
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
          output_gcs_uri=OUTPUT_GCS_URI if client.vertexai else None,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_image_to_video_poll(client):
  operation = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      image=GCS_IMAGE if client.vertexai else LOCAL_IMAGE,
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI if client.vertexai else None,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_text_and_image_to_video_poll(client):
  operation = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="Lightning storm",
      image=GCS_IMAGE if client.vertexai else LOCAL_IMAGE,
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI if client.vertexai else None,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_video_to_video_poll(client):
  # Video extension is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp",
      video=types.Video(
          uri="gs://genai-sdk-tests/inputs/videos/cat_driving.mp4",
      ),
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_text_and_video_to_video_poll(client):
  # Video extension is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp",
      prompt="Rain",
      video=types.Video(
          uri="gs://genai-sdk-tests/inputs/videos/cat_driving.mp4",
      ),
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_image_to_video_frame_interpolation_poll(client):
  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp" if client.vertexai else "veo-3-exp",
      prompt="Rain",
      image=GCS_IMAGE if client.vertexai else LOCAL_IMAGE_MAN,
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI if client.vertexai else None,
          last_frame=GCS_IMAGE2 if client.vertexai else LOCAL_IMAGE_DOG,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_reference_images_to_video_poll(client):
  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp" if client.vertexai else "veo-3-exp",
      prompt="Chirping birds in a colorful forest",
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI if client.vertexai else None,
          reference_images=[
              types.VideoGenerationReferenceImage(
                  image=GCS_IMAGE if client.vertexai else LOCAL_IMAGE_MAN,
                  reference_type=types.VideoGenerationReferenceType.ASSET,
              ),
          ],
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_video_edit_outpaint_poll(client):
  # Editing videos is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp",
      source=types.GenerateVideosSource(
          prompt="A mountain landscape",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
          ),
      ),
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI,
          aspect_ratio="16:9",
          mask=types.VideoGenerationMask(
              image=GCS_OUTPAINT_MASK,
              mask_mode=types.VideoGenerationMaskMode.OUTPAINT,
          ),
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_video_edit_remove_poll(client):
  # Editing videos is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp",
      source=types.GenerateVideosSource(
          prompt="A red dune buggy",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
          ),
      ),
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI,
          aspect_ratio="16:9",
          mask=types.VideoGenerationMask(
              image=GCS_REMOVE_MASK,
              mask_mode=types.VideoGenerationMaskMode.REMOVE,
          ),
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_video_edit_remove_static_poll(client):
  # Editing videos is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp",
      source=types.GenerateVideosSource(
          prompt="A red dune buggy",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
          ),
      ),
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI,
          aspect_ratio="16:9",
          mask=types.VideoGenerationMask(
              image=GCS_REMOVE_STATIC_MASK,
              mask_mode=types.VideoGenerationMaskMode.REMOVE_STATIC,
          ),
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_video_edit_insert_poll(client):
  # Editing videos is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model="veo-2.0-generate-exp",
      source=types.GenerateVideosSource(
          prompt="Bike",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
          ),
      ),
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI,
          aspect_ratio="16:9",
          mask=types.VideoGenerationMask(
              # Insert and remove masks are the same for this input.
              image=GCS_REMOVE_MASK,
              mask_mode=types.VideoGenerationMaskMode.INSERT,
          ),
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_create_operation_to_poll(client):
  if client.vertexai:
    # Fill in project and location for record mode
    operation_name = "projects/<project>/locations/<location>/publishers/google/models/veo-2.0-generate-001/operations/ddb46542-07ed-4000-958d-655fbffb05a4"
  else:
    operation_name = "models/veo-2.0-generate-001/operations/ren0ubieaocs"

  operation = types.GenerateVideosOperation(
      name=operation_name,
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = client.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri


def test_source_and_prompt_raises(client):
  with pytest.raises(ValueError):
    client.models.generate_videos(
        model=VEO_MODEL_LATEST,
        prompt="Prompt 1",
        source=types.GenerateVideosSource(prompt="Prompt 2"),
    )


@pytest.mark.asyncio
async def test_text_to_video_poll_async(client):
  operation = await client.aio.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="A neon hologram of a cat driving at top speed",
      config=types.GenerateVideosConfig(
          output_gcs_uri=OUTPUT_GCS_URI if client.vertexai else None,
      ),
  )
  while not operation.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation = await client.aio.operations.get(operation=operation)

  assert operation.result.generated_videos[0].video.uri
