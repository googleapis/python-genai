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
from .... import types
from ... import pytest_helper

VEO_MODEL_LATEST_VERTEX = "veo-2.0-generate-001"
VEO_MODEL_LATEST_GEMINI = "veo-3.1-generate-preview"


test_table: list[pytest_helper.TestTableItem] = [
    pytest_helper.TestTableItem(
        name="test_simple_prompt_vertex",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST_VERTEX,
            prompt="Man with a dog",
        ),
        exception_if_mldev=(
            "models/veo-2.0-generate-001 is not found for API version v1beta"
        ),
    ),
    pytest_helper.TestTableItem(
        name="test_simple_prompt_gemini",
        parameters=types._GenerateVideosParameters(
            model=VEO_MODEL_LATEST_GEMINI,
            prompt="Man with a dog",
        ),
        exception_if_vertex=(
            "404 NOT_FOUND"
        ),
    ),
]
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="models.generate_videos",
    test_table=test_table,
)
