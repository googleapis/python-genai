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

from ... import _transformers as t
from ... import types


def test_none():
  with pytest.raises(ValueError) as e:
    t.t_contents(None, None)
  assert 'contents are required' in str(e)


def test_empty_list():
  with pytest.raises(ValueError) as e:
    t.t_contents(None, [])
  assert 'contents are required' in str(e)


def test_string():
  assert t.t_contents(None, 'hello world') == [
      types.UserContent(parts=[types.Part(text='hello world')])
  ]


def test_list_of_strings():
  assert t.t_contents(None, ['hello', 'world']) == [
      types.UserContent(
          parts=[
              types.Part(text='hello'),
              types.Part(text='world'),
          ],
      ),
  ]


def test_part():
  assert t.t_contents(None, types.Part(text='hello world')) == [
      types.UserContent(parts=[types.Part(text='hello world')])
  ]


def test_list_of_parts():
  assert t.t_contents(None, [
      types.Part(text='hello'),
      types.Part(text='world'),
  ]) == [
      types.UserContent(parts=[
          types.Part(text='hello'),
          types.Part(text='world'),
      ]),
  ]


def test_content():
  assert t.t_contents(None, types.Content(role='user', parts=[
      types.Part(text='hello'),
      types.Part(text='world'),
  ])) == [
      types.Content(role='user', parts=[
          types.Part(text='hello'),
          types.Part(text='world'),
      ]),
  ]


def test_list_of_contents():
  assert t.t_contents(None, [
      types.Content(role='user', parts=[
          types.Part(text='hello'),
      ]),
      types.Content(role='user', parts=[
          types.Part(text='world'),
      ]),
  ]) == [
      types.Content(role='user', parts=[
          types.Part(text='hello'),
      ]),
      types.Content(role='user', parts=[
          types.Part(text='world'),
      ]),
  ]


def test_part_dict():
  assert t.t_contents(None, {'text': 'hello world'}) == [
      types.UserContent(parts=[types.Part(text='hello world')])
  ]


def test_list_of_part_dicts():
  assert t.t_contents(
      None,
      [
          {'text': 'hello'},
          {'text': 'world'},
      ],
  ) == [
      types.UserContent(
          parts=[
              types.Part(text='hello'),
              types.Part(text='world'),
          ]
      ),
  ]


def test_content_dict():
  assert t.t_contents(
      None,
      {
          'role': 'user',
          'parts': [
              {'text': 'hello'},
              {'text': 'world'},
          ],
      },
  ) == [
      types.Content(
          role='user',
          parts=[
              types.Part(text='hello'),
              types.Part(text='world'),
          ],
      ),
  ]


def test_list_of_content_dicts():
  assert t.t_contents(
      None,
      [
          {
              'role': 'user',
              'parts': [
                  {'text': 'hello'},
              ],
          },
          {
              'role': 'user',
              'parts': [
                  {'text': 'world'},
              ],
          },
      ],
  ) == [
      types.Content(
          role='user',
          parts=[
              types.Part(text='hello'),
          ],
      ),
      types.Content(
          role='user',
          parts=[
              types.Part(text='world'),
          ],
      ),
  ]


def test_list_of_part_content_dicts():
  assert t.t_contents(
      None,
      [
          {'text': 'hello'},
          {
              'role': 'user',
              'parts': [
                  {'text': 'world'},
              ],
          },
      ],
  ) == [
      types.UserContent(
          parts=[
              types.Part(text='hello'),
          ]
      ),
      types.Content(
          role='user',
          parts=[
              types.Part(text='world'),
          ],
      ),
  ]


def test_list_of_list_of_part_content_dicts():
  assert t.t_contents(
      None,
      [
          'why is the sky blue?',
          [
              {'text': 'hello'},
              {'text': 'world'},
          ],
          'what is the weather in New York?',
          [
              {'text': 'foo'},
              {'text': 'bar'},
          ],
          'what is the weather in Boston?',
      ],
  ) == [
      types.UserContent(parts=[types.Part(text='why is the sky blue?')]),
      types.UserContent(
          parts=[
              types.Part(text='hello'),
              types.Part(text='world'),
          ]
      ),
      types.UserContent(
          parts=[types.Part(text='what is the weather in New York?')]
      ),
      types.UserContent(
          parts=[
              types.Part(text='foo'),
              types.Part(text='bar'),
          ]
      ),
      types.UserContent(
          parts=[types.Part(text='what is the weather in Boston?')]
      ),
  ]


def test_mix_types():
  assert t.t_contents(
      None,
      [
          'hello',
          'Gemini',
          {'role': 'model', 'parts': [{'text': 'hello human'}]},
          [{'text': 'how do I call you?'}, 'My name is Jack.'],
          {
              'role': 'model',
              'parts': [{'text': 'Hi Jack! You can call me Gemini.'}],
          },
          'Hi Gemini, nice to meet you.',
      ],
  ) == [
      types.UserContent(
          parts=[
              types.Part(text='hello'),
              types.Part(text='Gemini'),
          ],
      ),
      types.Content(
          role='model',
          parts=[
              types.Part(text='hello human'),
          ],
      ),
      types.UserContent(
          parts=[
              types.Part(text='how do I call you?'),
              types.Part(text='My name is Jack.'),
          ],
      ),
      types.Content(
          role='model',
          parts=[
              types.Part(text='Hi Jack! You can call me Gemini.'),
          ],
      ),
      types.UserContent(
          parts=[
              types.Part(text='Hi Gemini, nice to meet you.'),
          ],
      ),
  ]


def test_function_call_part():
  assert t.t_contents(
      None,
      [
          'what is the weather in Boston?',
          types.Part.from_function_call(
              name='get_weather', args={'location': 'Boston'}
          ),
          types.Part.from_function_response(
              name='get_weather',
              response={'weather': 'sunny'},
          ),
      ],
  ) == [
      types.UserContent(
          parts=[
              types.Part(text='what is the weather in Boston?'),
          ]
      ),
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      args={'location': 'Boston'}, name='get_weather'
                  )
              )
          ]
      ),
      types.UserContent(
          parts=[
              types.Part(
                  function_response=types.FunctionResponse(
                      name='get_weather',
                      response={'weather': 'sunny'},
                  )
              ),
          ]
      ),
  ]


def test_function_call_part_dict():
  assert t.t_contents(
      None,
      [
          'what is the weather in Boston?',
          {
              'function_call': {
                  'name': 'get_weather',
                  'args': {'location': 'Boston'},
              }
          },
          {
              'function_response': {
                  'name': 'get_weather',
                  'response': {'weather': 'sunny'},
              }
          },
      ],
  ) == [
      types.UserContent(parts=[types.Part(text='what is the weather in Boston?')]),
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      args={'location': 'Boston'}, name='get_weather'
                  )
              )
          ]
      ),
      types.UserContent(
          parts=[
              types.Part(
                  function_response=types.FunctionResponse(
                      name='get_weather',
                      response={'weather': 'sunny'},
                  )
              ),
          ]
      ),
  ]


def test_user_content():
  assert t.t_contents(
      None,
      types.UserContent(
          parts=[
              types.Part(text='what is the weather in Boston?'),
          ]
      ),
  ) == [
      types.UserContent(
          parts=[
              types.Part(text='what is the weather in Boston?'),
          ]
      ),
  ]


def test_model_content():
  assert t.t_contents(
      None,
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      args={'location': 'Boston'}, name='get_weather'
                  )
              )
          ]
      ),
  ) == [
      types.ModelContent(
          parts=[
              types.Part(
                  function_call=types.FunctionCall(
                      args={'location': 'Boston'}, name='get_weather'
                  )
              )
          ]
      )
  ]
