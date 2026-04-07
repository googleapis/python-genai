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
"""Unit tests for client-side thought part filtering.

When ThinkingConfig(include_thoughts=False) is set, the SDK must strip thought
parts from the response regardless of what the API returns. On Vertex AI,
gemini-3.1-flash-image-preview returns thought parts even when
include_thoughts=False is requested.

See: https://github.com/googleapis/python-genai/issues/2239
"""

import pytest

from ... import types


# Raw API response containing both thought parts and a final non-thought part.
_RAW_RESPONSE_WITH_THOUGHTS = {
    'candidates': [
        {
            'content': {
                'parts': [
                    {'text': 'thinking step 1', 'thought': True},
                    {'text': 'thinking step 2', 'thought': True},
                    {'thought': True, 'inline_data': {'mime_type': 'image/png', 'data': 'ZHJhZnQ='}},
                    {'inline_data': {'mime_type': 'image/png', 'data': 'ZmluYWw='}},
                ],
                'role': 'model',
            },
            'finish_reason': 'STOP',
        }
    ]
}


def test_include_thoughts_false_strips_thought_parts():
    """Thought parts are removed when include_thoughts=False."""
    response = types.GenerateContentResponse._from_response(
        response=_RAW_RESPONSE_WITH_THOUGHTS,
        kwargs={'config': {'thinking_config': {'include_thoughts': False}}},
    )
    parts = response.candidates[0].content.parts
    assert all(
        not (isinstance(p.thought, bool) and p.thought) for p in parts
    ), 'No thought parts should remain when include_thoughts=False'
    assert len(parts) == 1, 'Only the final non-thought part should remain'


def test_include_thoughts_true_preserves_thought_parts():
    """Thought parts are preserved when include_thoughts=True."""
    response = types.GenerateContentResponse._from_response(
        response=_RAW_RESPONSE_WITH_THOUGHTS,
        kwargs={'config': {'thinking_config': {'include_thoughts': True}}},
    )
    parts = response.candidates[0].content.parts
    assert len(parts) == 4, 'All parts must be present when include_thoughts=True'
    thought_parts = [p for p in parts if isinstance(p.thought, bool) and p.thought]
    assert len(thought_parts) == 3


def test_no_thinking_config_preserves_all_parts():
    """Parts are untouched when no thinking_config is provided."""
    response = types.GenerateContentResponse._from_response(
        response=_RAW_RESPONSE_WITH_THOUGHTS,
        kwargs={},
    )
    parts = response.candidates[0].content.parts
    assert len(parts) == 4, 'Parts must not be filtered when thinking_config is absent'


def test_include_thoughts_false_empty_candidates():
    """No error when candidates list is empty."""
    response = types.GenerateContentResponse._from_response(
        response={'candidates': []},
        kwargs={'config': {'thinking_config': {'include_thoughts': False}}},
    )
    assert response.candidates == [] or response.candidates is None


def test_include_thoughts_false_no_thought_parts_unchanged():
    """Response with no thought parts is returned as-is."""
    raw = {
        'candidates': [
            {
                'content': {
                    'parts': [
                        {'inline_data': {'mime_type': 'image/png', 'data': 'ZmluYWw='}},
                    ],
                    'role': 'model',
                },
                'finish_reason': 'STOP',
            }
        ]
    }
    response = types.GenerateContentResponse._from_response(
        response=raw,
        kwargs={'config': {'thinking_config': {'include_thoughts': False}}},
    )
    assert len(response.candidates[0].content.parts) == 1
