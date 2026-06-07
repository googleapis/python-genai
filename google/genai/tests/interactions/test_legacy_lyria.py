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

from ..._interactions._legacy_lyria import (
    is_legacy_lyria_request,
    is_legacy_lyria_response_body,
)
from ..._interactions.types.interaction import Interaction


_LYRIA_MODEL_PATH = (
    "projects/123/locations/global/publishers/google/models/lyria-3-clip-preview"
)


def test_legacy_lyria_vertex_model_path_rewrites_outputs_to_steps():
    interaction = Interaction.model_validate(
        {
            "id": "interaction-1",
            "created": "2026-01-01T00:00:00Z",
            "updated": "2026-01-01T00:00:01Z",
            "status": "completed",
            "model": _LYRIA_MODEL_PATH,
            "outputs": [
                {
                    "type": "audio",
                    "data": "abc",
                    "mime_type": "audio/wav",
                }
            ],
        }
    )

    assert len(interaction.steps) == 1
    assert interaction.output_audio is not None
    assert interaction.output_audio.data == "abc"
    assert interaction.model_extra is None or "outputs" not in interaction.model_extra


def test_legacy_lyria_model_path_detection():
    assert is_legacy_lyria_request(is_vertex=True, model=_LYRIA_MODEL_PATH)
    assert is_legacy_lyria_response_body({"model": _LYRIA_MODEL_PATH})


def test_output_accessors_tolerate_missing_steps():
    interaction = Interaction.construct(
        id="interaction-1",
        created="2026-01-01T00:00:00Z",
        updated="2026-01-01T00:00:01Z",
        status="completed",
        steps=None,
    )

    assert interaction.output_image is None
    assert interaction.output_audio is None
    assert interaction.output_video is None
