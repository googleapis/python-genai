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

"""Tests for t_part."""

import pytest
import pydantic

from ... import _transformers as t
from ... import types


def test_none():
  with pytest.raises(ValueError):
    t.t_part(None)


def test_empty_string():
  assert t.t_part('') == types.Part(text='')


def test_string():
  assert t.t_part('test') == types.Part(text='test')


def test_file():
  assert t.t_part(
      types.File(uri='gs://test', mime_type='image/png')
  ) == types.Part(
      file_data=types.FileData(file_uri='gs://test', mime_type='image/png')
  )


def test_file_dict():
  assert t.t_part(
      {'file_uri': 'gs://test', 'mime_type': 'image/png'}
  ) == types.Part(
      file_data=types.FileData(file_uri='gs://test', mime_type='image/png')
  )


def test_file_no_uri():
  with pytest.raises(ValueError):
    t.t_part(types.File(mime_type='image/png'))


def test_file_no_mime_type():
  with pytest.raises(ValueError):
    t.t_part(types.File(uri='gs://test'))


def test_empty_dict():
  assert t.t_part({}) == types.Part()


def test_dict():
  assert t.t_part({'text': 'test'}) == types.Part(text='test')


def test_invalid_dict():
  with pytest.raises(pydantic.ValidationError):
    t.t_part({'invalid_key': 'test'})


def test_part():
  assert t.t_part(types.Part(text='test')) == types.Part(text='test')


def test_int():
  try:
    t.t_part(1)
  except ValueError as e:
    assert 'Unsupported content part type: <class \'int\'>' in str(e)
