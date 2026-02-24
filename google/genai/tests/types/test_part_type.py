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


import pytest
from ... import types


@pytest.fixture
def generate_content_response():
  return types.GenerateContentResponse()


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


def test_two_candidates_text(caplog, generate_content_response):
  from ... import types as types_module
  types_module._response_text_warning_logged = False

  generate_content_response.candidates = [
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

  assert generate_content_response.text == 'Hello1World1'
  assert any(
      record.levelname == 'WARNING'
      and 'there are 2 candidates' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None


def test_thought_signature_no_warning(caplog, generate_content_response):
  generate_content_response.candidates = [
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(text='Hello'),
                  types.Part(thought_signature=b'thought'),
              ]
          )
      ),
  ]

  assert generate_content_response.text == 'Hello'
  assert not any(
      record.levelname == 'WARNING'
      and 'there are non-text parts in the response' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None


def test_thought_signature_no_warning_in_text(
    caplog, generate_content_response
):
  generate_content_response.candidates = [
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(text='Hello', thought_signature=b'thought'),
              ]
          )
      ),
  ]

  assert generate_content_response.text == 'Hello'
  assert not any(
      record.levelname == 'WARNING'
      and 'there are non-text parts in the response' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None


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


def test_non_text_part_text(caplog, generate_content_response):
  from ... import types as types_module
  types_module._response_text_non_text_warning_logged = False

  generate_content_response.candidates = [
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(function_call=types.FunctionCall()),
              ]
          )
      ),
  ]
  assert generate_content_response.text is None
  assert any(
      record.levelname == 'WARNING'
      and 'there are non-text parts in the response' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None


def test_non_text_part_and_text_part_text(caplog, generate_content_response):
  generate_content_response.candidates = [
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(function_call=types.FunctionCall()),
                  types.Part(text='World1'),
              ]
          )
      ),
  ]

  assert generate_content_response.text == 'World1'
  assert not any(
      record.levelname == 'WARNING'
      and 'there are no text parts in the response' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None


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


def test_multiple_candidates_function_calls(caplog, generate_content_response):
  generate_content_response.candidates = [
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
  assert generate_content_response.function_calls == [
      types.FunctionCall(name='funcCall1', args={'key1': 'value1'})
  ]
  assert any(
      record.levelname == 'WARNING'
      and 'there are multiple candidates in the response' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None


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


def test_executable_code_empty_candidates():
  response = types.GenerateContentResponse()

  assert response.executable_code is None


def test_executable_code_empty_content():
  response = types.GenerateContentResponse(candidates=[])

  assert response.executable_code is None


def test_executable_code_empty_parts():
  response = types.GenerateContentResponse(candidates=[types.Candidate(
      content=types.Content()
  )])

  assert response.executable_code is None


def test_executable_code_two_candidates(caplog, generate_content_response):
  generate_content_response.candidates = [
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(
                      executable_code=types.ExecutableCode(
                          code='print("hello")', language='PYTHON'
                      )
                  )
              ]
          )
      ),
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(
                      executable_code=types.ExecutableCode(
                          code='print("world")', language='PYTHON'
                      )
                  )
              ]
          )
      ),
  ]

  assert generate_content_response.executable_code == 'print("hello")'
  assert any(
      record.levelname == 'WARNING'
      and 'there are multiple candidates in the response' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None

def test_executable_code_one_candidate():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          executable_code=types.ExecutableCode(
                              code='print("hello")', language='PYTHON'
                          )
                      )
                  ]
              )
          )
      ]
  )

  assert response.executable_code == 'print("hello")'


def test_code_execution_result_empty_candidates():
  response = types.GenerateContentResponse()

  assert response.code_execution_result is None, response.code_execution_result


def test_code_execution_result_empty_content():
  response = types.GenerateContentResponse(candidates=[])

  assert response.code_execution_result is None


def test_code_execution_result_empty_parts():
  response = types.GenerateContentResponse(
      candidates=[types.Candidate(content=types.Content())]
  )

  assert response.code_execution_result is None


def test_code_execution_result_two_candidates(caplog, generate_content_response):
  generate_content_response.candidates = [
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(
                      code_execution_result=types.CodeExecutionResult(
                          outcome='OUTCOME_OK', output='"hello"'
                      )
                  )
              ]
          )
      ),
      types.Candidate(
          content=types.Content(
              parts=[
                  types.Part(
                      code_execution_result=types.CodeExecutionResult(
                          outcome='OUTCOME_ERROR', output='"world"'
                      )
                  )
              ]
          )
      ),
  ]

  assert generate_content_response.code_execution_result == '"hello"'
  assert any (
      record.levelname == 'WARNING'
      and 'there are multiple candidates in the response' in record.message
      for record in caplog.records
  )
  generate_content_response.candidates = None


def test_code_execution_result_one_candidate():
  response = types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          code_execution_result=types.CodeExecutionResult(
                              outcome='OUTCOME_OK', output='"hello"'
                          )
                      )
                  ]
              )
          )
      ]
  )

  assert response.code_execution_result == '"hello"'


def test_from_file_media_resolution_str():
  file_uri = types.Part.from_uri(
      file_uri='gs://test',
      mime_type='image/png',
      media_resolution='MEDIA_RESOLUTION_LOW',
  )
  assert file_uri.file_data.file_uri == 'gs://test'
  assert file_uri.file_data.mime_type == 'image/png'
  assert file_uri.media_resolution.level == types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW


def test_from_file_media_resolution_enum():
  file_uri = types.Part.from_uri(
      file_uri='gs://test',
      mime_type='image/png',
      media_resolution=types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW,
  )
  assert file_uri.file_data.file_uri == 'gs://test'
  assert file_uri.file_data.mime_type == 'image/png'
  assert file_uri.media_resolution.level == types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW


def test_from_file_media_resolution_object():
  file_uri = types.Part.from_uri(
      file_uri='gs://test',
      mime_type='image/png',
      media_resolution=types.PartMediaResolution(level='MEDIA_RESOLUTION_LOW'),
  )
  assert file_uri.file_data.file_uri == 'gs://test'
  assert file_uri.file_data.mime_type == 'image/png'
  assert file_uri.media_resolution.level == types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW


def test_from_bytes_media_resolution_str():
  file_uri = types.Part.from_bytes(
      data=b'1234',
      mime_type='image/png',
      media_resolution='MEDIA_RESOLUTION_LOW',
  )
  assert file_uri.inline_data.data == b'1234'
  assert file_uri.inline_data.mime_type == 'image/png'
  assert file_uri.media_resolution.level == types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW


def test_from_bytes_media_resolution_enum():
  file_uri = types.Part.from_bytes(
      data=b'1234',
      mime_type='image/png',
      media_resolution=types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW,
  )
  assert file_uri.inline_data.data == b'1234'
  assert file_uri.inline_data.mime_type == 'image/png'
  assert file_uri.media_resolution.level == types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW


def test_from_bytes_media_resolution_object():
  file_uri = types.Part.from_bytes(
      data=b'1234',
      mime_type='image/png',
      media_resolution=types.PartMediaResolution(level='MEDIA_RESOLUTION_LOW'),
  )
  assert file_uri.inline_data.data == b'1234'
  assert file_uri.inline_data.mime_type == 'image/png'
  assert file_uri.media_resolution.level == types.PartMediaResolutionLevel.MEDIA_RESOLUTION_LOW
