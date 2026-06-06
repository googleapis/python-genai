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


from unittest.mock import patch


@patch.dict('sys.modules', {'PIL': None, 'PIL.Image': None})
def test_without_pil_installed_mocked():
  from ... import types

  type_names_in_union = [
      arg.__name__ if hasattr(arg, '__name__') else str(arg)
      for arg in types.PartUnion.__args__]
  assert 'Image' not in type_names_in_union

def test_without_pil_installed_mocked():
  from ... import types

  type_names_in_union = [
      arg.__name__ if hasattr(arg, '__name__') else str(arg)
      for arg in types.PartUnion.__args__]

  assert 'Image' in type_names_in_union