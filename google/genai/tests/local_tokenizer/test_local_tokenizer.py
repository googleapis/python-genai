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


class TestLocalTokenizer(unittest.TestCase):

  def setUp(self):
    # This setup will be used by all tests
    self.mock_load_model_proto = patch(
        'genai._local_tokenizer_loader.load_model_proto'
    ).start()
    self.mock_get_sentencepiece = patch(
        'genai._local_tokenizer_loader.get_sentencepiece'
    ).start()

    self.mock_load_model_proto.return_value = MagicMock()
    self.mock_tokenizer = MagicMock()
    self.mock_get_sentencepiece.return_value = self.mock_tokenizer

    self.tokenizer = local_tokenizer.LocalTokenizer(model_name='gemini-3-pro-preview')

  def tearDown(self):
    patch.stopall()

  def test_count_tokens_simple_string(self):
    self.mock_tokenizer.encode.return_value = [[1, 2, 3]]
    result = self.tokenizer.count_tokens('Hello world')
    self.assertEqual(result.total_tokens, 3)
    self.mock_tokenizer.encode.assert_called_once_with(['Hello world'])

  def test_count_tokens_list_of_strings(self):
    self.mock_tokenizer.encode.return_value = [[1, 2], [3]]
    result = self.tokenizer.count_tokens(['Hello', 'world'])
    self.assertEqual(result.total_tokens, 3)
    self.mock_tokenizer.encode.assert_called_once_with(['Hello', 'world'])

  def test_count_tokens_with_content_object(self):
    self.mock_tokenizer.encode.return_value = [[1, 2, 3]]
    content = types.Content(parts=[types.Part(text='Hello world')])
    result = self.tokenizer.count_tokens(content)
    self.assertEqual(result.total_tokens, 3)
    self.mock_tokenizer.encode.assert_called_once_with(['Hello world'])

  def test_count_tokens_with_chat_history(self):
    self.mock_tokenizer.encode.return_value = [[1, 2], [3, 4, 5]]
    history = [
        types.Content(role='user', parts=[types.Part(text='Hello')]),
        types.Content(role='model', parts=[types.Part(text='Hi there!')]),
    ]
    result = self.tokenizer.count_tokens(history)
    self.assertEqual(result.total_tokens, 5)
    self.mock_tokenizer.encode.assert_called_once_with(['Hello', 'Hi there!'])

  def test_count_tokens_with_tools(self):
    self.mock_tokenizer.encode.return_value = [
        [1],
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4],
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5, 6],
    ]
    tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name='get_weather',
                description='Get the weather for a location',
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        'location': types.Schema(
                            type=types.Type.STRING, description='The location'
                        )
                    },
                    required=['location'],
                ),
            )
        ]
    )
    config = types.CountTokensConfig(tools=[tool])
    result = self.tokenizer.count_tokens(
        'What is the weather in Boston?', config=config
    )
    self.assertEqual(result.total_tokens, 21)
    self.mock_tokenizer.encode.assert_called_once_with([
        'What is the weather in Boston?',
        'get_weather',
        'Get the weather for a location',
        'location',
        'location',
        'The location',
    ])

  def test_count_tokens_with_function_call(self):
    self.mock_tokenizer.encode.return_value = [[1, 2], [3], [4, 5]]
    content = types.Content(
        role='model',
        parts=[
            types.Part(
                function_call=types.FunctionCall(
                    name='get_weather', args={'location': 'Boston'}
                )
            )
        ],
    )
    result = self.tokenizer.count_tokens(content)
    self.assertEqual(result.total_tokens, 5)
    self.mock_tokenizer.encode.assert_called_once_with(
        ['get_weather', 'location', 'Boston']
    )

  def test_count_tokens_with_function_response(self):
    self.mock_tokenizer.encode.return_value = [[1, 2], [3], [4, 5]]
    content = types.Content(
        role='user',
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    name='get_weather', response={'weather': 'sunny'}
                )
            )
        ],
    )
    result = self.tokenizer.count_tokens(content)
    self.assertEqual(result.total_tokens, 5)
    self.mock_tokenizer.encode.assert_called_once_with(
        ['get_weather', 'weather', 'sunny']
    )

  def test_count_tokens_with_unsupported_content(self):
    with self.assertRaises(ValueError):
      self.tokenizer.count_tokens(
          [
              types.Content(
                  parts=[
                      types.Part(
                          inline_data=types.Blob(
                              data=b'test', mime_type='image/png'
                          )
                      )
                  ]
              )
          ]
      )

  def test_count_tokens_with_system_instruction(self):
    self.mock_tokenizer.encode.return_value = [[1, 2, 3], [4, 5]]
    config = types.CountTokensConfig(
        system_instruction=types.Content(
            parts=[types.Part(text='You are a helpful assistant.')]
        )
    )
    result = self.tokenizer.count_tokens('Hello', config=config)
    self.assertEqual(result.total_tokens, 5)
    self.mock_tokenizer.encode.assert_called_once_with(
        ['Hello', 'You are a helpful assistant.']
    )

  def test_count_tokens_with_response_schema(self):
    self.mock_tokenizer.encode.return_value = [
        [1],
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4],
        [1, 2, 3, 4, 5],
    ]
    schema = types.Schema(
        type=types.Type.OBJECT,
        format='schema_format',
        description='Recipe schema',
        enum=['schema_enum1', 'schema_enum2'],
        properties={
            'recipe_name': types.Schema(
                type=types.Type.STRING,
                description='Name of the recipe',
            )
        },
        items=types.Schema(
            type=types.Type.STRING,
            description='Item in the recipe',
        ),
        example={
            'recipe_example': types.Schema(
                type=types.Type.STRING,
                description='example in the recipe',
            )
        },
        required=['recipe_name'],
    )
    config = types.CountTokensConfig(
        generation_config=types.GenerationConfig(response_schema=schema)
    )
    result = self.tokenizer.count_tokens(
        'Generate a recipe for chocolate chip cookies.', config=config
    )
    self.assertEqual(result.total_tokens, 15)
    self.mock_tokenizer.encode.assert_called_once_with([
        'Generate a recipe for chocolate chip cookies.',
        'schema_format',
        'Recipe schema',
        'schema_enum1',
        'schema_enum2',
        'recipe_name',
        'Item in the recipe',
        'recipe_name',
        'Name of the recipe',
        'recipe_example',
    ])

  def test_count_tokens_with_unsupported_fields_logs_warning(self):
    self.mock_tokenizer.encode.return_value = [[1, 2, 3]]
    content_with_unsupported = types.Content(
        role='user',
        parts=[
            types.Part(text='hello'),
            # executable_code is not supported by _TextsAccumulator
            types.Part(
                executable_code=types.ExecutableCode(
                    language='PYTHON', code='print(1)'
                )
            ),
        ],
    )
    with self.assertLogs('google_genai.local_tokenizer', level='WARNING') as cm:
      self.tokenizer.count_tokens(content_with_unsupported)
      self.assertIn(
          'Content contains unsupported types for token counting', cm.output[0]
      )

  def test_compute_tokens_simple_string(self):
    mock_spt = MagicMock()
    mock_spt.pieces = [
        MagicMock(id=1, piece='He'),
        MagicMock(id=2, piece='llo'),
        MagicMock(id=3, piece=' world'),
    ]
    self.mock_tokenizer.EncodeAsImmutableProto.return_value = [mock_spt]
    result = self.tokenizer.compute_tokens('Hello world')
    self.assertEqual(len(result.tokens_info), 1)
    self.assertEqual(result.tokens_info[0].token_ids, [1, 2, 3])
    self.assertEqual(result.tokens_info[0].tokens, [b'He', b'llo', b' world'])
    self.assertEqual(result.tokens_info[0].role, 'user')
    self.mock_tokenizer.EncodeAsImmutableProto.assert_called_once_with(
        ['Hello world']
    )

  def test_compute_tokens_with_chat_history(self):
    mock_spt1 = MagicMock()
    mock_spt1.pieces = [MagicMock(id=1, piece='Hello')]
    mock_spt2 = MagicMock()
    mock_spt2.pieces = [
        MagicMock(id=2, piece='Hi'),
        MagicMock(id=3, piece=' there!'),
    ]
    self.mock_tokenizer.EncodeAsImmutableProto.return_value = [
        mock_spt1,
        mock_spt2,
    ]
    history = [
        types.Content(role='user', parts=[types.Part(text='Hello')]),
        types.Content(role='model', parts=[types.Part(text='Hi there!')]),
    ]
    result = self.tokenizer.compute_tokens(history)
    self.assertEqual(len(result.tokens_info), 2)
    self.assertEqual(result.tokens_info[0].token_ids, [1])
    self.assertEqual(result.tokens_info[0].tokens, [b'Hello'])
    self.assertEqual(result.tokens_info[0].role, 'user')
    self.assertEqual(result.tokens_info[1].token_ids, [2, 3])
    self.assertEqual(result.tokens_info[1].tokens, [b'Hi', b' there!'])
    self.assertEqual(result.tokens_info[1].role, 'model')
    self.mock_tokenizer.EncodeAsImmutableProto.assert_called_once_with(
        ['Hello', 'Hi there!']
    )

  def test_compute_tokens_with_byte_tokens(self):
    mock_spt = MagicMock()
    mock_spt.pieces = [
        MagicMock(id=1, piece='<0x48>'),
        MagicMock(id=2, piece='ello'),
    ]
    self.mock_tokenizer.EncodeAsImmutableProto.return_value = [mock_spt]
    self.tokenizer._model_proto = sentencepiece_model_pb2.ModelProto(
        pieces=[
            sentencepiece_model_pb2.ModelProto.SentencePiece(),
            sentencepiece_model_pb2.ModelProto.SentencePiece(
                type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.BYTE
            ),
            sentencepiece_model_pb2.ModelProto.SentencePiece(
                type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.NORMAL
            ),
        ]
    )
    result = self.tokenizer.compute_tokens('Hello')
    self.assertEqual(len(result.tokens_info), 1)
    self.assertEqual(result.tokens_info[0].token_ids, [1, 2])
    self.assertEqual(result.tokens_info[0].tokens, [b'H', b'ello'])
    self.mock_tokenizer.EncodeAsImmutableProto.assert_called_once_with(
        ['Hello']
    )


class TestParseHexByte(unittest.TestCase):

  def test_valid_hex(self):
    self.assertEqual(local_tokenizer._parse_hex_byte('<0x41>'), 65)
    self.assertEqual(local_tokenizer._parse_hex_byte('<0xFF>'), 255)
    self.assertEqual(local_tokenizer._parse_hex_byte('<0x00>'), 0)

  def test_invalid_length(self):
    with self.assertRaisesRegex(ValueError, 'Invalid byte length'):
      local_tokenizer._parse_hex_byte('<0x41')
    with self.assertRaisesRegex(ValueError, 'Invalid byte length'):
      local_tokenizer._parse_hex_byte('<0x411>')

  def test_invalid_format(self):
    with self.assertRaisesRegex(ValueError, 'Invalid byte format'):
      local_tokenizer._parse_hex_byte(' 0x41>')
    with self.assertRaisesRegex(ValueError, 'Invalid byte format'):
      local_tokenizer._parse_hex_byte('<0x41 ')

  def test_invalid_hex_value(self):
    with self.assertRaisesRegex(ValueError, 'Invalid hex value'):
      local_tokenizer._parse_hex_byte('<0xFG>')
