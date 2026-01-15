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


from ... import types
from ...chats import _validate_response


def test_validate_response_default_response():
  response = types.GenerateContentResponse()

  assert not _validate_response(response)


def test_validate_response_empty_content():
  response = types.GenerateContentResponse(candidates=[])

  assert not _validate_response(response)


def test_validate_response_empty_parts():
  response = types.GenerateContentResponse(
      candidates=[types.Candidate(content=types.Content(parts=[]))]
  )

  assert not _validate_response(response)


def test_validate_response_empty_part():
  response = types.GenerateContentResponse(
      candidates=[types.Candidate(content=types.Content(parts=[types.Part()]))]
  )

  assert not _validate_response(response)


def test_validate_response_part_with_empty_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(content=types.Content(parts=[types.Part(text='')]))
      ]
  )

  assert _validate_response(response)


def test_validate_response_part_with_text():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[types.Part(text='response from model')]
              )
          )
      ]
  )

  assert _validate_response(response)


def test_validate_response_part_with_function_call():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          function_call=types.FunctionCall(
                              name='foo', args={'bar': 'baz'}
                          )
                      )
                  ]
              )
          )
      ]
  )

  assert _validate_response(response)
