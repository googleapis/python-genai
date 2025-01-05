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


import json
from ..._api_client import RequestJsonEncoder


def test_json_encoder():
  assert json.dumps({'key': 'value'}, cls=RequestJsonEncoder) == '{"key": "value"}'
  assert json.dumps({'key': b'value'}, cls=RequestJsonEncoder) == '{"key": "value"}'
  assert (
      json.dumps({'nested': {'key': 'value'}}, cls=RequestJsonEncoder)
      == '{"nested": {"key": "value"}}'
  )
  assert (
      json.dumps({'nested': {'key': b'value'}}, cls=RequestJsonEncoder)
      == '{"nested": {"key": "value"}}'
  )
  assert (
      json.dumps({'list': ['value', 'value']}, cls=RequestJsonEncoder)
      == '{"list": ["value", "value"]}'
  )
  assert (
      json.dumps({'list': [b'value', b'value']}, cls=RequestJsonEncoder)
      == '{"list": ["value", "value"]}'
  )
