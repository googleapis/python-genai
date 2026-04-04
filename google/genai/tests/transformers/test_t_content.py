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

"""Tests for t_content."""

import pytest
import pydantic

from ... import _transformers as t
from ... import types


def test_none():
  with pytest.raises(ValueError):
    t.t_content( None)


def test_content():
  assert t.t_content(
      types.Content(parts=[types.Part(text='test')])
  ) == types.Content(parts=[types.Part(text='test')])


def test_content_dict():
  assert t.t_content(
      {'role': 'user', 'parts': [{'text': 'test'}]}
  ) == types.Content(parts=[types.Part(text='test')], role='user')


def test_content_dict_invalid():
  with pytest.raises(pydantic.ValidationError):
    t.t_content({'invalid_key': 'test'})


def test_text_part_dict():
  assert t.t_content({'text': 'test'}) == types.UserContent(
      parts=[types.Part(text='test')]
  )


def test_function_call_part_dict():
  assert t.t_content(
      {'function_call': {'name': 'test_func', 'args': {'arg1': 'value1'}}}
  ) == (
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      name='test_func', args={'arg1': 'value1'}
                  )
              )
          ]
      )
  )


def test_text_part():
  assert t.t_content(types.Part(text='test')) == types.UserContent(
      parts=[types.Part(text='test')]
  )


def test_function_call_part():
  assert t.t_content(
      types.Part(
          function_call=types.FunctionCall(
              name='test_func', args={'arg1': 'value1'}
          )
      ),
  ) == (
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      name='test_func', args={'arg1': 'value1'}
                  )
              )
          ]
      )
  )


def test_string():
  assert t.t_content('test') == types.UserContent(
      parts=[types.Part(text='test')]
  )


def test_file():
  assert t.t_content(
      types.File(uri='gs://test', mime_type='image/png')
  ) == types.UserContent(
      parts=[
          types.Part(
              file_data=types.FileData(
                  file_uri='gs://test', mime_type='image/png'
              )
          )
      ]
  )


def test_file_no_uri():
  with pytest.raises(ValueError):
    t.t_content(types.File(mime_type='image/png'))


def test_file_no_mime_type():
  with pytest.raises(ValueError):
    t.t_content(types.File(uri='gs://test'))


def test_file_dict():
  assert t.t_content({'file_uri': 'gs://test', 'mime_type': 'image/png'}) == types.UserContent(
          parts=[
              types.Part(
                  file_data=types.FileData(
                      file_uri='gs://test', mime_type='image/png'
                  )
              )
          ]
      )

def test_int():
  try:
    t.t_content(1)
  except ValueError as e:
    assert 'Unsupported content part type: <class \'int\'>' in str(e)


@pytest.mark.parametrize(
    'contents',
    [
        types.Content(parts=[types.Part(inline_data=types.Blob(data=b'test'))]),
        {'parts': [{'inline_data': {'data': b'test'}}]},
        [
            types.Content(
                parts=[types.Part(inline_data=types.Blob(data=b'test'))]
            )
        ],
        [{'parts': [{'inline_data': {'data': b'test'}}]}],
    ],
)
def test_t_contents_strict_content(contents):
  result = t.t_contents_strict(contents)
  assert result == [
      types.Content(parts=[types.Part(inline_data=types.Blob(data=b'test'))])
  ]
