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


"""Tests t_bytes methods in the _transformers module."""

import os

import PIL.Image
import pytest

from ... import _transformers as t
from ... import types


def test_blob_dict():
  blob = t.t_blob({'data': bytes([0, 0, 0, 0, 0, 0]), 'mime_type': 'audio/pcm'}
  )
  assert blob.data == bytes([0, 0, 0, 0, 0, 0])
  assert blob.mime_type == 'audio/pcm'


def test_blob():
  blob = t.t_blob(types.Blob(data=bytes([0, 0, 0, 0, 0, 0]), mime_type='audio/pcm')
  )
  assert blob.data == bytes([0, 0, 0, 0, 0, 0])
  assert blob.mime_type == 'audio/pcm'


def test_image(image_jpeg):
  blob = t.t_blob(image_jpeg)
  assert blob.data[6:10] == b'JFIF'
  assert blob.mime_type == 'image/jpeg'

