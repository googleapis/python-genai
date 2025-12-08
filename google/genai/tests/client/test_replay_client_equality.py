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


"""Tests replay client correctly compares requests ignoring key casing."""

from ... import _replay_api_client
from ... import types


def test_equal_objects_with_same_casing_returns_true():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'topK': 2.0, 'maxOutputTokens': 3},
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'topK': 2.0, 'maxOutputTokens': 3},
  }]

  assert _replay_api_client._equals_ignore_key_case(obj1, obj2)


def test_equal_objects_with_different_casing_returns_true():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'topK': 2.0, 'maxOutputTokens': 3},
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generation_config': {'topK': 2.0, 'max_output_tokens': 3},
  }]

  assert _replay_api_client._equals_ignore_key_case(obj1, obj2)


def test_equal_objects_with_different_nested_casing_returns_true():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'topK': 2.0, 'maxOutputTokens': 3},
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'top_k': 2.0, 'maxOutputTokens': 3},
  }]

  assert _replay_api_client._equals_ignore_key_case(obj1, obj2)

def test_equal_int_float_values_returns_true():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'topK': 2.0, 'maxOutputTokens': 3},
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generation_config': {'topK': 2, 'max_output_tokens': 3},
  }]

  assert _replay_api_client._equals_ignore_key_case(obj1, obj2)


def test_equal_enum_string_values_returns_true():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {
          'topK': 2.0,
          'maxOutputTokens': 3,
          'type': types.Type.STRING,
      },
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generation_config': {
          'topK': 2,
          'max_output_tokens': 3,
          'type': 'STRING',
      },
  }]

  assert _replay_api_client._equals_ignore_key_case(obj1, obj2)


def test_equal_enum_values_returns_true():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {
          'topK': 2.0,
          'maxOutputTokens': 3,
          'type': types.Type.STRING,
      },
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generation_config': {
          'topK': 2,
          'max_output_tokens': 3,
          'type': types.Type.STRING,
      },
  }]

  assert _replay_api_client._equals_ignore_key_case(obj1, obj2)


def test_different_number_value_returns_false():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'topK': 3, 'maxOutputTokens': 3},
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generation_config': {'topK': 2.0, 'max_output_tokens': 3},
  }]

  assert not _replay_api_client._equals_ignore_key_case(
      obj1, obj2
  )


def test_different_string_value_returns_false():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {'topK': 3, 'maxOutputTokens': 3},
  }]
  obj2 = [{
      'contents': [
          {'parts': [{'text': 'What is your name?'}], 'role': 'model'}
      ],
      'generation_config': {'topK': 3, 'max_output_tokens': 3},
  }]

  assert not _replay_api_client._equals_ignore_key_case(
      obj1, obj2
  )


def test_different_enum_values_returns_false():
  obj1 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generationConfig': {
          'topK': 2.0,
          'maxOutputTokens': 3,
          'type': types.Type.STRING,
      },
  }]
  obj2 = [{
      'contents': [{'parts': [{'text': 'What is your name?'}], 'role': 'user'}],
      'generation_config': {
          'topK': 2,
          'max_output_tokens': 3,
          'type': types.Type.OBJECT,
      },
  }]

  assert not _replay_api_client._equals_ignore_key_case(
      obj1, obj2
  )
