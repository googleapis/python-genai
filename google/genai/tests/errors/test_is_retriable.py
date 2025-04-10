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

"""Unit tests for errors.is_retriable helper function."""

import httpx
from ... import errors


def test_is_exception_type_single_type():
  predicate = errors._if_exception_type(httpx.ConnectError)
  assert predicate(httpx.ConnectError('test'))
  assert not predicate(ValueError('test'))


def test_is_exception_type_multiple_types():
  predicate = errors._if_exception_type(
      httpx.ConnectError, httpx.TimeoutException
  )
  assert predicate(httpx.ConnectError('test'))
  assert predicate(httpx.TimeoutException('test'))
  assert not predicate(TypeError('test'))


def test_if_exception_type_no_type():
  predicate = errors._if_exception_type()
  assert not predicate(httpx.ConnectError('test'))
  assert not predicate(ValueError('test'))


def test_is_retriable_api_error():

  for code in [429, 500, 503]:
    assert errors.is_retriable(
        errors.APIError(code, httpx.Response(status_code=code))
    )
  assert not errors.is_retriable(
      errors.APIError(400, httpx.Response(status_code=400))
  )


def test_is_retriable_httpx_error():
  assert errors.is_retriable(httpx.ConnectError('test'))
  assert errors.is_retriable(httpx.TimeoutException('test'))


def test_is_retriable_other_non_retriable_error():
  assert not errors.is_retriable(Exception('test'))
  assert not errors.is_retriable(ValueError('test'))
  assert not errors.is_retriable(TypeError('test'))
