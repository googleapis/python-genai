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

from ... import errors
from .. import pytest_helper

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_has_thought_with_include_thoughts_v1alpha(client):
  # Thinking config currently only works in v1alpha for Gemini AI API.
  with pytest_helper.exception_if_vertex(client, errors.ClientError):
    chat = client.chats.create(
        model='gemini-2.0-flash-thinking-exp',
        config={
            'thinking_config': {'include_thoughts': True},
            'http_options': {'api_version': 'v1alpha'},
        },
    )
    response = chat.send_message(
        'What is the sum of natural numbers from 1 to 100?'
    )
    has_thought = False
    thought = ''
    if response.candidates:
      for candidate in response.candidates:
        for part in candidate.content.parts:
          if part.thought:
            has_thought = True
            thought = part.text
            break
    assert has_thought
    assert thought not in response.text


def test_has_thought_with_include_thoughts(client):
  with pytest_helper.exception_if_mldev(client, errors.ClientError):
    chat = client.chats.create(
        model='gemini-2.0-flash-thinking-exp-1219',
        config={
            'thinking_config': {'include_thoughts': True},
        },
    )
    response = chat.send_message(
        'What is the sum of natural numbers from 1 to 100?'
    )
    has_thought = False
    thought = ''
    if response.candidates:
      for candidate in response.candidates:
        for part in candidate.content.parts:
          if part.thought:
            has_thought = True
            thought = part.text
            break
    assert has_thought
    assert thought not in response.text


def test_no_thought_with_default_config(client):
  chat = client.chats.create(
      model='gemini-2.0-flash-thinking-exp-1219'
  )
  response = chat.send_message(
      'What is the sum of natural numbers from 1 to 100?'
  )
  has_thought = False
  for candidate in response.candidates:
    for part in candidate.content.parts:
      if part.thought:
        has_thought = True
        break
  assert not has_thought
