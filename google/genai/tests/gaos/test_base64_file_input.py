# Copyright 2026 Google LLC
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
"""Inline binary `data` input tests for the Interactions content models.

`ImageContent`, `DocumentContent`, `AudioContent` and `VideoContent` accept
inline `data` as raw bytes (like `google.genai.types.Blob`), a pre-encoded
base64 `str`, a path, or a binary stream. Non-`str` input is base64-encoded
into an ASCII string before the request is sent.
"""

from __future__ import annotations

import base64
import io
import pathlib
from typing import Any

import pydantic
import pytest

# Import the generated types through `_gaos` rather than the public
# `interactions`/`_interactions` modules: `run_tests.sh --private` rewrites
# `_gaos` imports to `_gaos_private`, so the classes match the client under test.
from ..._gaos.types import base64fileinput
from ..._gaos.types import interactions
from . import conftest

_MODEL = "gemini-3-flash-preview"

# Non-UTF-8 bytes whose standard base64 encoding contains `+` and `/`.
_RAW = b"\x00\xfb\xff\xfe\x89PNG\r\n\x1a\n"
_ENCODED = base64.b64encode(_RAW).decode("ascii")

_CONTENT_CASES = [
    pytest.param(interactions.ImageContent, "image/png", id="image"),
    pytest.param(interactions.DocumentContent, "application/pdf", id="document"),
    pytest.param(interactions.AudioContent, "audio/wav", id="audio"),
    pytest.param(interactions.VideoContent, "video/mp4", id="video"),
]

_BYTES_LIKE_CASES = [
    pytest.param(_RAW, id="bytes"),
    pytest.param(bytearray(_RAW), id="bytearray"),
    pytest.param(memoryview(_RAW), id="memoryview"),
]

_INTERACTION_BODY = {
    "id": "v1_base64_input",
    "model": _MODEL,
    "status": "completed",
    "created": "2026-11-10T12:00:00Z",
    "updated": "2026-11-10T12:00:00Z",
    "steps": [{
        "type": "model_output",
        "content": [{"type": "text", "text": "Looks good."}],
    }],
}


@pytest.mark.parametrize("data", _BYTES_LIKE_CASES)
@pytest.mark.parametrize("content_cls, mime_type", _CONTENT_CASES)
def test_bytes_like_data_is_base64_encoded(
    content_cls: type[pydantic.BaseModel], mime_type: str, data: Any
):
  content = content_cls(data=data, mime_type=mime_type)

  assert isinstance(content.data, str)
  assert content.data == _ENCODED
  assert content.data.isascii()
  assert base64.b64decode(content.data) == _RAW
  assert content.model_dump(mode="json")["data"] == _ENCODED


@pytest.mark.parametrize("content_cls, mime_type", _CONTENT_CASES)
def test_bytes_data_from_dict_is_base64_encoded(
    content_cls: type[pydantic.BaseModel], mime_type: str
):
  content_type = content_cls.model_fields["type"].default
  content = content_cls.model_validate(
      {"type": content_type, "data": _RAW, "mime_type": mime_type}
  )

  assert content.data == _ENCODED


def test_str_data_is_treated_as_pre_encoded_base64():
  content = interactions.ImageContent(data=_ENCODED, mime_type="image/png")

  assert content.data == _ENCODED


def test_base64_looking_bytes_are_encoded_not_passed_through():
  # Bytes are always raw content, even when they look like base64 text.
  content = interactions.ImageContent(data=b"YWJj", mime_type="image/png")

  assert content.data == "WVdKag=="


def test_empty_bytes_are_encoded_to_empty_string():
  content = interactions.DocumentContent(data=b"", mime_type="application/pdf")

  assert content.data == ""


def test_path_data_is_read_and_encoded(tmp_path: pathlib.Path):
  path = tmp_path / "image.png"
  path.write_bytes(_RAW)

  content = interactions.ImageContent(data=path, mime_type="image/png")

  assert content.data == _ENCODED


def test_stream_data_is_encoded_and_position_restored():
  stream = io.BytesIO(_RAW)

  content = interactions.AudioContent(data=stream, mime_type="audio/wav")

  assert content.data == _ENCODED
  assert stream.tell() == 0


def test_non_byte_memoryview_is_rejected():
  ints = memoryview(bytearray(8)).cast("i")

  with pytest.raises(pydantic.ValidationError, match="memoryview of bytes"):
    interactions.ImageContent(data=ints, mime_type="image/png")


def test_encode_base64_file_input_helper():
  encode = base64fileinput.encode_base64_file_input

  assert encode(_RAW) == _ENCODED
  assert encode(bytearray(_RAW)) == _ENCODED
  assert encode(memoryview(_RAW)) == _ENCODED
  # Strided (non-contiguous) memoryviews are copied before encoding.
  assert encode(memoryview(b"a-b-c-")[::2]) == base64.b64encode(b"abc").decode(
      "ascii"
  )
  assert encode(_ENCODED) == _ENCODED
  assert encode(None) is None


def test_create_sends_inline_bytes_as_base64(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.default_response = _INTERACTION_BODY

  mock_gaos_server.client.interactions.create(
      model=_MODEL,
      input=[
          interactions.ImageContent(data=_RAW, mime_type="image/png"),
          {
              "type": "document",
              "data": bytearray(_RAW),
              "mime_type": "application/pdf",
          },
          {"type": "text", "text": "Describe these files."},
      ],
  )

  (body,) = mock_gaos_server.captured_bodies
  assert body["input"] == [
      {"type": "image", "data": _ENCODED, "mime_type": "image/png"},
      {"type": "document", "data": _ENCODED, "mime_type": "application/pdf"},
      {"type": "text", "text": "Describe these files."},
  ]


@pytest.mark.asyncio
async def test_async_create_sends_inline_bytes_as_base64(
    mock_gaos_server: conftest.MockGaosServer,
):
  mock_gaos_server.default_response = _INTERACTION_BODY

  await mock_gaos_server.client.aio.interactions.create(
      model=_MODEL,
      input=[{"type": "audio", "data": _RAW, "mime_type": "audio/wav"}],
  )

  (body,) = mock_gaos_server.captured_bodies
  # A single-content input list may be sent wrapped in a `user_input` step.
  (sent,) = body["input"]
  if sent["type"] == "user_input":
    (sent,) = sent["content"]
  assert sent == {"type": "audio", "data": _ENCODED, "mime_type": "audio/wav"}
