import datetime
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
  date_value = datetime.datetime.fromtimestamp(
      1736397612, tz=datetime.timezone.utc
  )
  assert (
      json.dumps({'key': date_value}, cls=RequestJsonEncoder)
      == '{"key": "2025-01-09T04:40:12Z"}'
  )
  assert (
      json.dumps({'nested': {'key': date_value}}, cls=RequestJsonEncoder)
      == '{"nested": {"key": "2025-01-09T04:40:12Z"}}'
  )
  assert (
      json.dumps({'nested': {'key': date_value}}, cls=RequestJsonEncoder)
      == '{"nested": {"key": "2025-01-09T04:40:12Z"}}'
  )
  assert (
      json.dumps({'list': [date_value, date_value]}, cls=RequestJsonEncoder)
      == '{"list": ["2025-01-09T04:40:12Z", "2025-01-09T04:40:12Z"]}'
  )
  assert (
      json.dumps({'list': [date_value, date_value]}, cls=RequestJsonEncoder)
      == '{"list": ["2025-01-09T04:40:12Z", "2025-01-09T04:40:12Z"]}'
  )
