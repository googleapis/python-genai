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

import unittest
from unittest.mock import MagicMock, patch

from sentencepiece import sentencepiece_model_pb2

from ... import local_tokenizer
from ... import types

_FC_CONTENT = types.Content(
    role='model',
    parts=[types.Part(function_call=types.FunctionCall(
        name='get_weather', args={'location': 'Boston'}))],
)
_USER_CONTENT = types.Content(role='user', parts=[types.Part(text='thanks')])
# accumulator yields: 'get_weather', 'location', 'Boston', 'thanks'
_EXPECTED_ROLES = ['model', 'model', 'model', 'user']


class TestSentencePieceBranch(unittest.TestCase):

  def setUp(self):
    patch('genai._local_tokenizer_loader.load_model_proto').start()
    m = patch('genai._local_tokenizer_loader.get_sentencepiece').start()
    self.addCleanup(patch.stopall)
    self.mock_tokenizer = MagicMock()
    m.return_value = self.mock_tokenizer
    self.tokenizer = local_tokenizer.LocalTokenizer(model_name='gemini-2.5-flash')
    self.tokenizer._model_proto = sentencepiece_model_pb2.ModelProto(
        pieces=[sentencepiece_model_pb2.ModelProto.SentencePiece(piece='x')] * 10)

  def test_roles_align_with_texts(self):
    def proto(i):
      p = MagicMock(); p.pieces = [MagicMock(id=1, piece=f't{i}')]; return p
    self.mock_tokenizer.EncodeAsImmutableProto.side_effect = (
        lambda texts: [proto(i) for i in range(len(texts))])
    r = self.tokenizer.compute_tokens([_FC_CONTENT, _USER_CONTENT])
    self.assertEqual([t.role for t in r.tokens_info], _EXPECTED_ROLES)


class TestHuggingFaceBranch(unittest.TestCase):

  def setUp(self):
    m = patch('genai._local_tokenizer_loader.get_huggingface_tokenizer').start()
    self.addCleanup(patch.stopall)
    self.mock_tokenizer = MagicMock()
    m.return_value = self.mock_tokenizer
    self.tokenizer = local_tokenizer.LocalTokenizer(model_name='gemini-3.5-flash')

  def test_roles_align_with_texts(self):
    self.mock_tokenizer.encode.side_effect = (
        lambda texts: [[i] for i in range(len(texts))])
    self.mock_tokenizer.convert_ids_to_tokens.side_effect = lambda ids: ['tok']
    r = self.tokenizer.compute_tokens([_FC_CONTENT, _USER_CONTENT])
    self.assertEqual([t.role for t in r.tokens_info], _EXPECTED_ROLES)


if __name__ == '__main__':
  unittest.main()
