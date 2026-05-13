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

import base64
import json
from ..._interactions._utils._json import openapi_dumps


def test_openapi_dumps_bytes():
  data = {"image": b"123", "text": "hello"}
  expected_image_b64 = base64.b64encode(b"123").decode("ascii")

  result_bytes = openapi_dumps(data)
  result_dict = json.loads(result_bytes.decode("utf-8"))

  assert result_dict["image"] == expected_image_b64
  assert result_dict["text"] == "hello"


def test_openapi_dumps_nested_bytes():
  data = {"outer": {"inner": b"binary_data"}}
  expected_b64 = base64.b64encode(b"binary_data").decode("ascii")

  result_bytes = openapi_dumps(data)
  result_dict = json.loads(result_bytes.decode("utf-8"))

  assert result_dict["outer"]["inner"] == expected_b64
