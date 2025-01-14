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


import pytest
from ... import types


def test_candidate_empty_text():
  response = types.GenerateContentResponse()
  assert response.text is None


def test_first_candidate_empty_content_text():
  response = types.GenerateContentResponse(candidates=[])

  # MUST assert None not implicit boolean False
  assert response.text is None


def test_first_candidate_empty_parts_text():
  response = types.GenerateContentResponse(candidates=[types.Candidate()])

  # MUST assert None not implicit boolean False
  assert response.text is None


def test_content_empty_parts_text():
  response = types.GenerateContentResponse(
      candidates=[types.Candidate(content=types.Content())]
  )

  # MUST assert None not implicit boolean False
  assert response.text is None


def test_two_candidates_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello1'),
                      types.Part(text='World1'),
                  ]
              )
          ),
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello2'),
                      types.Part(text='World2'),
                  ]
              )
          ),
      ]
  )

  assert response.text == 'Hello1World1'


def test_1_candidate_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello1'),
                      types.Part(text='World1'),
                  ]
              )
          )
      ]
  )

  assert response.text == 'Hello1World1'


def test_all_empty_text_in_parts():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text=''),
                      types.Part(text=''),
                  ]
              )
          ),
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello2'),
                      types.Part(text='World2'),
                  ]
              )
          ),
      ]
  )

  # MUST assert empty string, not implicit boolean False
  assert response.text == ''


def test_one_empty_text_in_parts():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text=''),
                      types.Part(text='World1'),
                  ]
              )
          ),
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello2'),
                      types.Part(text='World2'),
                  ]
              )
          ),
      ]
  )

  assert response.text == 'World1'


def test_all_none_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(),
                      types.Part(),
                  ]
              )
          ),
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello2'),
                      types.Part(text='World2'),
                  ]
              )
          ),
      ]
  )

  # MUST assert None not implicit boolean False
  assert response.text is None


def test_none_empty_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(),
                      types.Part(text=''),
                  ]
              )
          ),
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello2'),
                      types.Part(text='World2'),
                  ]
              )
          ),
      ]
  )

  # MUST assert empty string, not implicit boolean False
  assert response.text == ''


def test_non_text_part_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(function_call=types.FunctionCall()),
                  ]
              )
          ),
      ]
  )

  with pytest.raises(ValueError):
    response.text


def test_non_text_part_and_text_part_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(function_call=types.FunctionCall()),
                      types.Part(text='World1'),
                  ]
              )
          ),
      ]
  )

  with pytest.raises(ValueError):
    response.text


def test_candidates_none_function_calls():
  response = types.GenerateContentResponse()
  assert response.function_calls is None


def test_candidates_empty_function_calls():
  response = types.GenerateContentResponse(candidates=[])
  assert response.function_calls is None


def test_content_none_function_calls():
  response = types.GenerateContentResponse(candidates=[types.Candidate()])
  assert response.function_calls is None


def test_parts_none_function_calls():
  response = types.GenerateContentResponse(
      candidates=[types.Candidate(content=types.Content())]
  )
  assert response.function_calls is None


def test_parts_empty_function_calls():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(content=types.Content(parts=[])),
      ]
  )
  assert response.function_calls is None


def test_multiple_candidates_function_calls():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          function_call=types.FunctionCall.model_validate({
                              'args': {'key1': 'value1'},
                              'name': 'funcCall1',
                          })
                      )
                  ]
              )
          ),
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          function_call=types.FunctionCall.model_validate({
                              'args': {'key2': 'value2'},
                              'name': 'funcCall2',
                          })
                      )
                  ]
              )
          ),
      ]
  )
  assert response.function_calls == [
      types.FunctionCall(name='funcCall1', args={'key1': 'value1'})
  ]


def test_multiple_function_calls():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          function_call=types.FunctionCall.model_validate({
                              'args': {'key1': 'value1'},
                              'name': 'funcCall1',
                          })
                      ),
                      types.Part(
                          function_call=types.FunctionCall.model_validate({
                              'args': {'key2': 'value2'},
                              'name': 'funcCall2',
                          })
                      ),
                  ]
              )
          ),
      ]
  )
  assert response.function_calls == [
      types.FunctionCall(name='funcCall1', args={'key1': 'value1'}),
      types.FunctionCall(name='funcCall2', args={'key2': 'value2'}),
  ]


def test_no_function_calls():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(text='Hello1'),
                      types.Part(text='World1'),
                  ]
              )
          ),
      ]
  )
  assert response.function_calls is None
