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
from unittest.mock import MagicMock, mock_open, patch

import sentencepiece as spm
from sentencepiece import sentencepiece_model_pb2

from ... import _local_tokenizer_loader as loader

# A minimal valid sentencepiece model proto
FAKE_MODEL_CONTENT = sentencepiece_model_pb2.ModelProto(
    pieces=[
        sentencepiece_model_pb2.ModelProto.SentencePiece(
            piece="<unk>",
            score=0,
            type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.UNKNOWN,
        ),
        sentencepiece_model_pb2.ModelProto.SentencePiece(
            piece="<s>",
            score=0,
            type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.CONTROL,
        ),
        sentencepiece_model_pb2.ModelProto.SentencePiece(
            piece="</s>",
            score=0,
            type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.CONTROL,
        ),
        sentencepiece_model_pb2.ModelProto.SentencePiece(
            piece="a",
            score=0,
            type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.NORMAL,
        ),
    ]
).SerializeToString()

GEMMA2_HASH = "61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2"


class TestGetTokenizerName(unittest.TestCase):

  def test_get_tokenizer_name_success(self):
    self.assertEqual(loader.get_tokenizer_name("gemini-2.5-pro"), "gemma3")
    self.assertEqual(
        loader.get_tokenizer_name("gemini-2.5-pro-preview-06-05"), "gemma3"
    )

  def test_get_tokenizer_name_unsupported(self):
    with self.assertRaisesRegex(
        ValueError, "Model unsupported-model is not supported"
    ):
      loader.get_tokenizer_name("unsupported-model")


@patch("genai._local_tokenizer_loader.os.rename")
@patch("genai._local_tokenizer_loader.os.makedirs")
@patch("genai._local_tokenizer_loader.os.remove")
@patch("genai._local_tokenizer_loader.open", new_callable=mock_open)
@patch("genai._local_tokenizer_loader.os.path.exists")
@patch("genai._local_tokenizer_loader.requests.get")
@patch("genai._local_tokenizer_loader.hashlib.sha256")
class TestLoaderFunctions(unittest.TestCase):

  def setUp(self):
    # Clear caches before each test
    loader.load_model_proto.cache_clear()
    loader.get_sentencepiece.cache_clear()
    # Patch tempfile.gettempdir to control cache location
    self.tempdir_patcher = patch(
        "tempfile.gettempdir", return_value="/tmp/fake_temp_dir"
    )
    self.mock_tempdir = self.tempdir_patcher.start()

  def tearDown(self):
    self.tempdir_patcher.stop()

  def _setup_get_mock(self, mock_get):
    mock_response = MagicMock()
    mock_response.content = FAKE_MODEL_CONTENT
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

  def test_load_model_proto_from_url(
      self,
      mock_sha256,
      mock_get,
      mock_exists,
      mock_open_func,
      mock_remove,
      mock_makedirs,
      mock_rename,
  ):
    mock_exists.return_value = False  # Don't use cache
    self._setup_get_mock(mock_get)
    mock_sha256.return_value.hexdigest.return_value = GEMMA2_HASH

    proto = loader.load_model_proto("gemma2")

    self.assertIsInstance(proto, sentencepiece_model_pb2.ModelProto)
    self.assertEqual(len(proto.pieces), 4)
    mock_get.assert_called_once()
    mock_makedirs.assert_called_once()
    mock_open_func.assert_called()
    mock_rename.assert_called_once()

  def test_load_model_proto_from_cache(
      self,
      mock_sha256,
      mock_get,
      mock_exists,
      mock_open_func,
      mock_remove,
      mock_makedirs,
      mock_rename,
  ):
    mock_exists.return_value = True  # Use cache
    mock_open_func.return_value.read.return_value = FAKE_MODEL_CONTENT
    mock_sha256.return_value.hexdigest.return_value = GEMMA2_HASH

    proto = loader.load_model_proto("gemma2")

    self.assertIsInstance(proto, sentencepiece_model_pb2.ModelProto)
    mock_get.assert_not_called()

  def test_load_model_proto_corrupted_cache(
      self,
      mock_sha256,
      mock_get,
      mock_exists,
      mock_open_func,
      mock_remove,
      mock_makedirs,
      mock_rename,
  ):
    mock_exists.return_value = True  # Use cache initially
    self._setup_get_mock(mock_get)
    mock_open_func.return_value.__enter__.return_value.read.return_value = (
        b"corrupted"
    )

    # First hash for corrupted cache, second for good download
    mock_sha256.side_effect = [
        MagicMock(hexdigest=MagicMock(return_value="wrong_hash")),
        MagicMock(hexdigest=MagicMock(return_value=GEMMA2_HASH)),
    ]

    proto = loader.load_model_proto("gemma2")

    self.assertIsInstance(proto, sentencepiece_model_pb2.ModelProto)
    mock_remove.assert_called_once()
    mock_get.assert_called_once()

  def test_load_model_proto_bad_hash_from_url(
      self,
      mock_sha256,
      mock_get,
      mock_exists,
      mock_open_func,
      mock_remove,
      mock_makedirs,
      mock_rename,
  ):
    mock_exists.return_value = False
    self._setup_get_mock(mock_get)
    mock_sha256.return_value.hexdigest.return_value = "wrong_hash"

    with self.assertRaisesRegex(
        ValueError, "Downloaded model file is corrupted"
    ):
      loader.load_model_proto("gemma2")

  def test_load_model_proto_unsupported(self, *args):
    with self.assertRaisesRegex(
        ValueError, "Tokenizer unsupported is not supported"
    ):
      loader.load_model_proto("unsupported")

  def test_get_sentencepiece_success(
      self,
      mock_sha256,
      mock_get,
      mock_exists,
      mock_open_func,
      mock_remove,
      mock_makedirs,
      mock_rename,
  ):
    mock_exists.return_value = False
    self._setup_get_mock(mock_get)
    mock_sha256.return_value.hexdigest.return_value = GEMMA2_HASH

    processor = loader.get_sentencepiece("gemma2")

    self.assertIsInstance(processor, spm.SentencePieceProcessor)
    mock_get.assert_called_once()

  def test_get_sentencepiece_unsupported(self, *args):
    with self.assertRaisesRegex(
        ValueError, "Tokenizer unsupported is not supported"
    ):
      loader.get_sentencepiece("unsupported")

  def test_get_sentencepiece_caching(
      self,
      mock_sha256,
      mock_get,
      mock_exists,
      mock_open_func,
      mock_remove,
      mock_makedirs,
      mock_rename,
  ):
    mock_exists.return_value = False
    self._setup_get_mock(mock_get)
    mock_sha256.return_value.hexdigest.return_value = GEMMA2_HASH

    # Call twice
    loader.get_sentencepiece("gemma2")
    loader.get_sentencepiece("gemma2")

    # Should only be loaded once due to lru_cache
    mock_get.assert_called_once()
