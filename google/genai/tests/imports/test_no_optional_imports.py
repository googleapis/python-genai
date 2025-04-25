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

import os
import pytest

IS_NOT_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS') != 'true'


@pytest.mark.skipif(IS_NOT_GITHUB_ACTIONS,
                    reason='This test is only run on GitHub Actions.')
def test_library_can_be_imported_without_optional_dependencies():
  """Tests that the library can be imported without optional dependencies.
  """
  from google import genai
  from google.genai import types
