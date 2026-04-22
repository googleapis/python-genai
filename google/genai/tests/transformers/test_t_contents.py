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

"""Tests for t_contents."""

import pytest
import pydantic

from ... import _transformers as t
from ... import types


def test_none():
  with pytest.raises(ValueError):
    t.t_contents(None)


def test_empty_list():
  with pytest.raises(ValueError):
    t.t_contents([])


def test_content():
  assert t.t_contents(
      [types.Content(parts=[types.Part(text='test')])]
  ) == [types.Content(parts=[types.Part(text='test')])]


def test_content_dict():
  assert t.t_contents(
      [{'role': 'user', 'parts': [{'text': 'test'}]}]
  ) == [types.Content(parts=[types.Part(text='test')], role='user')]


def test_empty_dict():
  assert t.t_contents({}) == [types.Content()]


def test_invalid_dict():
  with pytest.raises(pydantic.ValidationError):
    t.t_contents({'invalid_key': 'test'})


def test_text_part():
  assert t.t_contents([types.Part(text='test')]) == [
      types.UserContent(parts=[types.Part(text='test')])
  ]


def test_function_call_part():
  function_call = types.FunctionCall(name='test_func', args={'arg1': 'value1'})
  assert t.t_contents(
      [types.Part(function_call=function_call)]
  ) == [
      types.ModelContent(
          parts=[
              types.Part(function_call=function_call)
          ]
      )
  ]


def test_text_part_dict():
  assert t.t_contents([{'text': 'test'}]) == [
      types.UserContent(parts=[types.Part(text='test')])
  ]


def test_function_call_part_dict():
  assert t.t_contents(
      [{'function_call': {'name': 'test_func', 'args': {'arg1': 'value1'}}}]
  ) == [
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      name='test_func', args={'arg1': 'value1'}
                  )
              )
          ]
      )
  ]


def test_empty_string():
  assert t.t_contents('') == [
      types.UserContent(parts=[types.Part(text='')])
  ]


def test_string():
  assert t.t_contents('test') == [
      types.UserContent(parts=[types.Part(text='test')])
  ]


def test_file():
  assert t.t_contents(
      types.File(uri='gs://test', mime_type='image/png')
  ) == [
      types.UserContent(
          parts=[
              types.Part(
                  file_data=types.FileData(
                      file_uri='gs://test', mime_type='image/png'
                  )
              )
          ]
      )
  ]


def test_file_dict():
  assert t.t_contents({'file_uri': 'gs://test', 'mime_type': 'image/png'}) == [
      types.UserContent(
          parts=[
              types.Part(
                  file_data=types.FileData(
                      file_uri='gs://test', mime_type='image/png'
                  )
              )
          ]
      )
  ]

def test_file_dict_list():
  assert t.t_contents([{'file_uri': 'gs://test', 'mime_type': 'image/png'}]) == [
      types.UserContent(
          parts=[
              types.Part(
                  file_data=types.FileData(
                      file_uri='gs://test', mime_type='image/png'
                  )
              )
          ]
      )
  ]

def test_file_no_uri():
  with pytest.raises(ValueError):
    t.t_contents(types.File(mime_type='image/png'))


def test_file_no_mime_type():
  with pytest.raises(ValueError):
    t.t_contents(types.File(uri='gs://test'))


def test_string_list():
  assert t.t_contents(['test1', 'test2']) == [
      types.UserContent(parts=[
          types.Part(text='test1'),
          types.Part(text='test2'),
      ])
  ]


def test_file_list():
  assert t.t_contents(
      [
          types.File(uri='gs://test1', mime_type='image/png'),
          types.File(uri='gs://test2', mime_type='image/png'),
      ],
  ) == [
      types.UserContent(
          parts=[
              types.Part(
                  file_data=types.FileData(
                      file_uri='gs://test1', mime_type='image/png'
                  )
              ),
              types.Part(
                  file_data=types.FileData(
                      file_uri='gs://test2', mime_type='image/png'
                  )
              ),
          ]
      )
  ]


def test_string_file_list():
  assert t.t_contents(
      ['test1', types.File(uri='gs://test2', mime_type='image/png')],
  ) == [
      types.UserContent(
          parts=[
              types.Part(text='test1'),
              types.Part(
                  file_data=types.FileData(
                      file_uri='gs://test2', mime_type='image/png'
                  )
              ),
          ]
      )
  ]


def test_function_call_list():
  function_call1 = types.FunctionCall(
      name='test_func1', args={'arg1': 'value1'}
  )
  function_call2 = types.FunctionCall(
      name='test_func2', args={'arg2': 'value2'}
  )

  assert t.t_contents(
      [
          types.Part(function_call=function_call1),
          types.Part(function_call=function_call2),
      ],
  ) == [
      types.ModelContent(
          parts=[
              types.Part(function_call=function_call1),
              types.Part(function_call=function_call2),
          ]
      )
  ]


def test_function_call_function_response_list():
  question1 = 'question1'
  question2 = 'question2'
  function_call1 = types.FunctionCall(
      name='test_func1', args={'arg1': 'value1'}
  )
  function_call2 = types.FunctionCall(
      name='test_func2', args={'arg2': 'value2'}
  )
  function_response1 = types.FunctionResponse(
      name='test_func1',
      response={
          'answer': 'answer1',
      },
  )
  function_response2 = types.FunctionResponse(
      name='test_func2',
      response={
          'answer': 'answer2',
      },
  )

  assert t.t_contents(
      [
          question1,
          question2,
          types.Part(function_call=function_call1),
          {'function_call': function_call2},
          {'function_response': function_response1},
          types.Part(function_response=function_response2),
      ],
  ) == [
      types.UserContent(
          parts=[
              types.Part(text=question1),
              types.Part(text=question2),
          ]
      ),
      types.ModelContent(
          parts=[
              types.Part(function_call=function_call1),
              types.Part(function_call=function_call2),
          ]
      ),
      types.UserContent(
          parts=[
              types.Part(function_response=function_response1),
              types.Part(function_response=function_response2),
          ]
      ),
  ]


def test_content_list():
  assert t.t_contents(
      [
          types.Content(parts=[types.Part(text='test1')]),
          types.Content(parts=[types.Part(text='test2')]),
      ],
  ) == [
      types.Content(parts=[types.Part(text='test1')]),
      types.Content(parts=[types.Part(text='test2')]),
  ]


def test_content_text_part_list():
  assert t.t_contents(
      [
          types.Part(text='test1'),
          types.Part(text='test2'),
          types.Content(parts=[types.Part(text='test3')]),
          types.Part(text='test4'),
      ],
  ) == [
      types.UserContent(
          parts=[
              types.Part(text='test1'),
              types.Part(text='test2'),
          ]
      ),
      types.Content(parts=[types.Part(text='test3')]),
      types.UserContent(parts=[types.Part(text='test4')]),
  ]


def test_list_of_text_part_list():
  contents = [
      'question1',
      {'function_call': {'name': 'test_func1', 'args': {'arg1': 'value1'}}},
      types.Part(
          function_response=types.FunctionResponse(
              name='test_func1',
              response={
                  'answer': 'answer1',
              },
          )
      ),
      ['context2_1', 'context2_2', types.Part(text='context2_3')],
      'question2',
      types.Part(
          function_call={'name': 'test_func2', 'args': {'arg2': 'value2'}}
      ),
      {
          'function_response': types.FunctionResponse(
              name='test_func2',
              response={
                  'answer': 'answer2',
              },
          )
      },
  ]

  assert t.t_contents(contents) == [
      types.UserContent(parts='question1'),
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      name='test_func1', args={'arg1': 'value1'}
                  )
              )
          ]
      ),
      types.UserContent(
          parts=[
              types.Part(
                  function_response=types.FunctionResponse(
                      name='test_func1',
                      response={
                          'answer': 'answer1',
                      },
                  )
              )
          ]
      ),
      types.UserContent(
          parts=[
              types.Part(text='context2_1'),
              types.Part(text='context2_2'),
              types.Part(text='context2_3'),
          ]
      ),
      types.UserContent(parts=[types.Part(text='question2')]),
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      name='test_func2', args={'arg2': 'value2'}
                  )
              )
          ]
      ),
      types.UserContent(
          parts=[
              types.Part(
                  function_response=types.FunctionResponse(
                      name='test_func2',
                      response={
                          'answer': 'answer2',
                      },
                  )
              )
          ]
      ),
  ]
