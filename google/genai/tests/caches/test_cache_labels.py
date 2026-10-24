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

from ... import caches
from ... import types


def test_create_cached_content_config_to_vertex_includes_labels():
  parent_object = {}

  caches._CreateCachedContentConfig_to_vertex(
      types.CreateCachedContentConfig(
          display_name='test cache',
          labels={'team': 'genai', 'use_case': 'billing'},
      ),
      parent_object,
  )

  assert parent_object['labels'] == {
      'team': 'genai',
      'use_case': 'billing',
  }


def test_cached_content_accepts_labels():
  cached_content = types.CachedContent(
      name='cachedContents/123',
      labels={'team': 'genai'},
  )

  assert cached_content.labels == {'team': 'genai'}
