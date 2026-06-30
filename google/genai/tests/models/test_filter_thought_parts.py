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

"""Unit tests for _filter_thought_parts.

Verifies client-side filtering of thought parts when include_thoughts=False
is set in ThinkingConfig. Regression test for:
https://github.com/googleapis/python-genai/issues/2239
"""

import pytest

from ... import _transformers as t
from ... import types
from ...models import _filter_thought_parts


def _make_response_with_thoughts() -> types.GenerateContentResponse:
  """Build a synthetic response resembling Vertex AI image gen with thoughts."""
  parts = [
      types.Part(text='thinking step 1', thought=True),
      types.Part(text='thinking step 2', thought=True),
      types.Part(inline_data=types.Blob(mime_type='image/png', data=b'draft'), thought=True),
      types.Part(text='self-critique', thought=True),
      types.Part(inline_data=types.Blob(mime_type='image/png', data=b'final')),
  ]
  content = types.Content(role='model', parts=parts)
  candidate = types.Candidate(content=content)
  return types.GenerateContentResponse(candidates=[candidate])


def _make_parameter_model(include_thoughts) -> types._GenerateContentParameters:
  return types._GenerateContentParameters(
      model='gemini-3.1-flash-image-preview',
      contents=t.t_contents('Draw a red car'),
      config=types.GenerateContentConfig(
          thinking_config=types.ThinkingConfig(include_thoughts=include_thoughts)
      ),
  )


class TestFilterThoughtParts:

  def test_include_thoughts_false_removes_thought_parts(self):
    """When include_thoughts=False, all parts with thought=True are removed."""
    response = _make_response_with_thoughts()
    parameter_model = _make_parameter_model(include_thoughts=False)

    result = _filter_thought_parts(response, parameter_model)

    parts = result.candidates[0].content.parts
    assert all(not part.thought for part in parts), (
        'Expected no thought parts but found some'
    )
    assert len(parts) == 1, f'Expected 1 non-thought part, got {len(parts)}'
    assert parts[0].inline_data is not None
    assert parts[0].inline_data.data == b'final'

  def test_include_thoughts_true_preserves_all_parts(self):
    """When include_thoughts=True, no parts are filtered."""
    response = _make_response_with_thoughts()
    parameter_model = _make_parameter_model(include_thoughts=True)

    result = _filter_thought_parts(response, parameter_model)

    parts = result.candidates[0].content.parts
    assert len(parts) == 5, f'Expected 5 parts, got {len(parts)}'

  def test_include_thoughts_none_preserves_all_parts(self):
    """When include_thoughts is unset, no parts are filtered."""
    response = _make_response_with_thoughts()
    parameter_model = _make_parameter_model(include_thoughts=None)

    result = _filter_thought_parts(response, parameter_model)

    parts = result.candidates[0].content.parts
    assert len(parts) == 5

  def test_no_thinking_config_preserves_all_parts(self):
    """When ThinkingConfig is absent entirely, no parts are filtered."""
    response = _make_response_with_thoughts()
    parameter_model = types._GenerateContentParameters(
        model='gemini-3.1-flash-image-preview',
        contents=t.t_contents('Draw a red car'),
        config=types.GenerateContentConfig(),
    )

    result = _filter_thought_parts(response, parameter_model)

    parts = result.candidates[0].content.parts
    assert len(parts) == 5

  def test_no_config_preserves_all_parts(self):
    """When config is None entirely, no parts are filtered."""
    response = _make_response_with_thoughts()
    parameter_model = types._GenerateContentParameters(
        model='gemini-3.1-flash-image-preview',
        contents=t.t_contents('Draw a red car'),
    )

    result = _filter_thought_parts(response, parameter_model)

    parts = result.candidates[0].content.parts
    assert len(parts) == 5

  def test_empty_candidates_is_safe(self):
    """Response with no candidates does not raise."""
    response = types.GenerateContentResponse(candidates=[])
    parameter_model = _make_parameter_model(include_thoughts=False)

    result = _filter_thought_parts(response, parameter_model)

    assert result.candidates == []

  def test_no_thought_parts_in_response(self):
    """If API returns no thought parts, filtering is a no-op."""
    parts = [
        types.Part(inline_data=types.Blob(mime_type='image/png', data=b'final')),
    ]
    content = types.Content(role='model', parts=parts)
    candidate = types.Candidate(content=content)
    response = types.GenerateContentResponse(candidates=[candidate])
    parameter_model = _make_parameter_model(include_thoughts=False)

    result = _filter_thought_parts(response, parameter_model)

    assert len(result.candidates[0].content.parts) == 1
