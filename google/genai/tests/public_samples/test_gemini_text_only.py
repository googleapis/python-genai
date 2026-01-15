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


"""Test for the code sample for Gemini text-only request."""

from .. import pytest_helper

pytestmark = pytest_helper.setup(file=__file__)


def test_sample(client):
  # [START generativeaionvertexai_gemini_text_only]
  response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=(
          "What's a good name for a flower shop that specializes in selling"
          " bouquets of dried flowers?"
      ),
  )
  print(response.text)
  # [END generativeaionvertexai_gemini_text_only]
