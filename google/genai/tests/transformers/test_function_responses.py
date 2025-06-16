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


"""Tests for live.py."""
from ... import types
from ... import _transformers as t

def test_function_response_dict():
  input = {
      'name': 'get_current_weather',
      'response': {'temperature': 14.5, 'unit': 'C'},
      'id': 'some-id',
  }

  function_responses = t.t_function_responses(input)

  assert len(function_responses) == 1
  assert function_responses[0].name == 'get_current_weather'
  assert function_responses[0].response['temperature'] == 14.5
  assert function_responses[0].response['unit'] == 'C'


def test_send_function_response():
  input = types.FunctionResponse(
      name='get_current_weather',
      response={'temperature': 14.5, 'unit': 'C'},
      id='some-id',
  )
  
  function_responses = t.t_function_responses(input)

  assert len(function_responses) == 1
  assert function_responses[0].name == 'get_current_weather'
  assert function_responses[0].response['temperature'] == 14.5
  assert function_responses[0].response['unit'] == 'C'


def test_send_function_response_list():

  input1 = {
      'name': 'get_current_weather',
      'response': {'temperature': 14.5, 'unit': 'C'},
      'id': '1',
  }
  input2 = {
      'name': 'get_current_weather',
      'response': {'temperature': 99.9, 'unit': 'C'},
      'id': '2',
  }

  function_responses = t.t_function_responses([input1, input2])

  assert len(function_responses) == 2
  assert function_responses[0].name == 'get_current_weather'
  assert function_responses[0].response['temperature'] == 14.5
  assert function_responses[0].response['unit'] == 'C'
  assert function_responses[1].name == 'get_current_weather'
  assert function_responses[1].response['temperature'] == 99.9
  assert function_responses[1].response['unit'] == 'C'
