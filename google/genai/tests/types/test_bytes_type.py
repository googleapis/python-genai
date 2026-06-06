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
from datetime import datetime
from typing import Any, Optional

import pytest

from ... import _common

# 64 distinct chars in url safe base64.
_URL_SAFE_BASE64 = (
    '-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)
_RAW_BYTES = (
    b'\xfb\xf6\x9bq\xd7\x9f\x82\x18\xa3\x92Y\xa7\xa2\x9a\xab\xb2\xdb\xaf\xc3\x1c\xb3\x00\x10\x83\x10Q\x87'
    b' \x92\x8b0\xd3\x8fA\x14\x93QU\x97a\x9d5\xdb~9\xeb\xbf='
)
# 64 distinct chars in normal base64.
_BASE64 = '+/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
assert base64.b64decode(_BASE64) == _RAW_BYTES


class MyBytesModel(_common.BaseModel):
  image_data: Optional[bytes]


# This test shows that if user pass in url safe base64 string to a bytes field,
# then SDK will return raw bytes in pydantic, model_dump() and __str__()
# and base64 string in to_json_dict() and model_dump(mode='json').
def test_urlsafe_base64_input_success():
  my_data = MyBytesModel(image_data=_URL_SAFE_BASE64)

  # Check output is base64 string.
  assert my_data.to_json_dict() == {'image_data': _URL_SAFE_BASE64}
  assert my_data.model_dump(mode='json') == {'image_data': _URL_SAFE_BASE64}
  assert isinstance(my_data.to_json_dict()['image_data'], str)

  # Check output is bytes.
  assert my_data.model_dump() == {'image_data': _RAW_BYTES}
  assert my_data.image_data == _RAW_BYTES
  assert isinstance(my_data.image_data, bytes)

  # Check print(my_data) will output the bytes string, not the base64 string.
  assert str(my_data) == 'image_data=' + str(_RAW_BYTES)


# This test shows that if user pass in raw bytes to a bytes field,
# then SDK will return raw bytes in pydantic, model_dump() and __str__()
# and base64 string in to_json_dict() and model_dump(mode='json').
def test_raw_bytes_input_success():
  my_data = MyBytesModel(image_data=_RAW_BYTES)

  # Check output is base64 string.
  assert my_data.to_json_dict() == {'image_data': _URL_SAFE_BASE64}
  assert my_data.model_dump(mode='json') == {'image_data': _URL_SAFE_BASE64}
  assert isinstance(my_data.to_json_dict()['image_data'], str)

  # Check output is bytes.
  assert my_data.model_dump() == {'image_data': _RAW_BYTES}
  assert my_data.image_data == _RAW_BYTES
  assert isinstance(my_data.image_data, bytes)

  # Check print(my_data) will output the bytes string, not the base64 string.
  assert str(my_data) == 'image_data=' + str(_RAW_BYTES)


# This test shows that if user pass in invalid base64 string(normal base64 but
# not url safe) to a bytes field, then SDK will raise ValueError.
def test_invalid_base64_pydantic_input_failure():
  with pytest.raises(ValueError, match='Data should be valid base64'):
    MyBytesModel(image_data=_BASE64+'=')  # invalid base64


# This test shows that if user pass in invalid base64 string(normal base64 but
# not url safe) to a bytes field, then SDK will raise ValueError.
def test_invalid_base64_dict_input_failure():
  with pytest.raises(ValueError, match='Data should be valid base64'):
    MyBytesModel.model_validate({'image_data': _BASE64+'='})  # invalid base64


# This test shows that if user pass in normal base64 string(
# not url safe) to a bytes field, then Pydantic can correctly parse the normal
# base64 string to bytes.
def test_normal_base64_pydantic_input_success():
  data = MyBytesModel(image_data=_BASE64)
  assert data.image_data == _RAW_BYTES


# This test shows that if user pass in normal base64 string via(
# not url safe) via dict input with model_validate(), then Pydantic can
# correctly parse the normal base64 string to bytes.
def test_normal_base64_dict_input_success():
  data = MyBytesModel.model_validate({'image_data': _BASE64})
  assert data.image_data == _RAW_BYTES


class MyAnyModel(_common.BaseModel):
  data: Optional[Any]


# This test shows that if user pass in raw bytes to an Any type field,
# then SDK will return raw bytes in pydantic, model_dump() and __str__()
# and base64 string in to_json_dict() and model_dump(mode='json').
def test_any_type_urlsafe_base64_input():
  my_data = MyAnyModel(data=_RAW_BYTES)

  # Check output is base64 string.
  assert my_data.to_json_dict() == {'data': _URL_SAFE_BASE64}
  assert my_data.model_dump(mode='json') == {'data': _URL_SAFE_BASE64}
  assert isinstance(my_data.to_json_dict()['data'], str)

  # Check output is bytes.
  assert my_data.model_dump() == {'data': _RAW_BYTES}
  assert my_data.data == _RAW_BYTES
  assert isinstance(my_data.data, bytes)

  # Check print(my_data) will output the bytes string, not the base64 string.
  assert str(my_data) == 'data=' + str(_RAW_BYTES)


# This test shows if user pass in url safe base64 string to an Any type field,
# then SDK will always return the base64 string.
def test_any_type_urlsafe_base64_input():
  my_data = MyAnyModel(data=_URL_SAFE_BASE64)

  # Check output is base64 string.
  assert my_data.to_json_dict() == {'data': _URL_SAFE_BASE64}
  assert my_data.model_dump(mode='json') == {'data': _URL_SAFE_BASE64}
  assert isinstance(my_data.to_json_dict()['data'], str)

  # Check output is bytes.
  assert my_data.model_dump() == {'data': _URL_SAFE_BASE64}
  assert my_data.data == _URL_SAFE_BASE64
  assert isinstance(my_data.data, str)

  # Check print(my_data) will output the bytes string, not the base64 string.
  assert str(my_data) == "data='" + str(_URL_SAFE_BASE64) + "'"
