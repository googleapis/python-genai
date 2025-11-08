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

VEO_MODEL_LATEST = "veo-3.1-generate-preview"
VEO_MODEL_2 = "veo-2.0-generate-001"
VEO_MODEL_2_EXP = "veo-2.0-generate-exp"

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
                    mime_type="video/mp4",
                ),
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                output_gcs_uri=OUTPUT_GCS_URI,
            ),
        ),
        exception_if_mldev=(
            "output_gcs_uri parameter is not supported in Gemini API"
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
                    mime_type="video/mp4",
                ),
            ),
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                output_gcs_uri=OUTPUT_GCS_URI,
            ),
        ),
        exception_if_mldev=(
            "output_gcs_uri parameter is not supported in Gemini API"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_video_edit_outpaint",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_2_EXP,
            source=types.GenerateVideosSource(
                prompt="A mountain landscape",
                video=types.Video(
                    uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
                    mime_type="video/mp4",
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
            model=VEO_MODEL_2,
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
            model=VEO_MODEL_LATEST,
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
            model=VEO_MODEL_LATEST,
            prompt="Rain",
            config=types.GenerateVideosConfig(
                output_gcs_uri=OUTPUT_GCS_URI,
                reference_images=[
                    types.VideoGenerationReferenceImage(
                        image=GCS_IMAGE,
                        reference_type=types.VideoGenerationReferenceType.ASSET,
                    )
                ],
            ),
        ),
        exception_if_mldev=(
            "output_gcs_uri parameter is not supported in Gemini API"
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
  # GCS URI video input is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model=VEO_MODEL_2,
      video=types.Video(
          uri="gs://genai-sdk-tests/inputs/videos/cat_driving.mp4",
          mime_type="video/mp4",
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
  # GCS URI video input is only supported in Vertex AI.
  if not client.vertexai:
    return

  operation = client.models.generate_videos(
      model=VEO_MODEL_2,
      prompt="Rain",
      video=types.Video(
          uri="gs://genai-sdk-tests/inputs/videos/cat_driving.mp4",
          mime_type="video/mp4",
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


def test_generated_video_extension_poll(client):
  # Gemini API only supports video extension on generated videos.
  if client.vertexai:
    return

  operation1 = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="Rain",
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation1.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation1 = client.operations.get(operation=operation1)

  video1 = operation1.result.generated_videos[0].video
  assert video1.uri
  client.files.download(file=video1)
  assert video1.video_bytes

  operation2 = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="Sun",
      video=video1,
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation2.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation2 = client.operations.get(operation=operation2)

  video2 = operation2.result.generated_videos[0].video
  assert video2.uri
  client.files.download(file=video2)
  assert video2.video_bytes


def test_generated_video_extension_from_source_poll(client):
  # Gemini API only supports video extension on generated videos.
  if client.vertexai:
    return

  operation1 = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="Rain",
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation1.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation1 = client.operations.get(operation=operation1)

  video1 = operation1.result.generated_videos[0].video
  assert video1.uri
  client.files.download(file=video1)
  assert video1.video_bytes

  operation2 = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      source=types.GenerateVideosSource(
          prompt="Sun",
          video=video1
      ),
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation2.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation2 = client.operations.get(operation=operation2)

  video2 = operation2.result.generated_videos[0].video
  assert video2.uri
  client.files.download(file=video2)
  assert video2.video_bytes


def test_generated_video_extension_from_source_dict_poll(client):
  # Gemini API only supports video extension on generated videos.
  if client.vertexai:
    return

  operation1 = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="Rain",
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation1.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation1 = client.operations.get(operation=operation1)

  video1 = operation1.result.generated_videos[0].video
  assert video1.uri
  client.files.download(file=video1)
  assert video1.video_bytes

  operation2 = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
      source={
          "prompt": "Sun",
          "video": video1,
      },
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation2.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation2 = client.operations.get(operation=operation2)

  video2 = operation2.result.generated_videos[0].video
  assert video2.uri
  client.files.download(file=video2)
  assert video2.video_bytes


def test_image_to_video_frame_interpolation_poll(client):
  operation = client.models.generate_videos(
      model=VEO_MODEL_LATEST,
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
      model=VEO_MODEL_LATEST,
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
      model=VEO_MODEL_2_EXP,
      source=types.GenerateVideosSource(
          prompt="A mountain landscape",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
              mime_type="video/mp4",
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
      model=VEO_MODEL_2_EXP,
      source=types.GenerateVideosSource(
          prompt="A red dune buggy",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
              mime_type="video/mp4",
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
      model=VEO_MODEL_2_EXP,
      source=types.GenerateVideosSource(
          prompt="A red dune buggy",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
              mime_type="video/mp4",
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
      model=VEO_MODEL_2_EXP,
      source=types.GenerateVideosSource(
          prompt="Bike",
          video=types.Video(
              uri="gs://genai-sdk-tests/inputs/videos/editing_demo.mp4",
              mime_type="video/mp4",
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
    operation_name = "projects/<project>/locations/<location>/publishers/google/models/veo-3.1-generate-preview/operations/9d2fc0b5-5bdf-4b5f-9a41-82970515e20b"
  else:
    operation_name = "models/veo-3.1-generate-preview/operations/vz341u0pmdlc"

  operation = types.GenerateVideosOperation(
      name=operation_name,
  )
  operation = client.operations.get(operation=operation)
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


@pytest.mark.asyncio
async def test_generated_video_extension_from_source_poll_async(client):
  # Gemini API only supports video extension on generated videos.
  if client.vertexai:
    return

  operation1 = await client.aio.models.generate_videos(
      model=VEO_MODEL_LATEST,
      prompt="Rain",
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation1.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation1 = await client.aio.operations.get(operation=operation1)

  video1 = operation1.result.generated_videos[0].video
  assert video1.uri
  assert await client.aio.files.download(file=video1)

  operation2 = await client.aio.models.generate_videos(
      model=VEO_MODEL_LATEST,
      source=types.GenerateVideosSource(
          prompt="Sun",
          video=video1
      ),
      config=types.GenerateVideosConfig(
          number_of_videos=1,
      ),
  )
  while not operation2.done:
    # Skip the sleep when in replay mode.
    if client._api_client._mode not in ("replay", "auto"):
      time.sleep(20)
    operation2 = await client.aio.operations.get(operation=operation2)

  video2 = operation2.result.generated_videos[0].video
  assert video2.uri
  assert await client.aio.files.download(file=video2)

