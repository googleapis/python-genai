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


"""Tests for upload MIME type resolution (issue #744)."""


import pytest

from ... import _extra_utils


# PNG file signature followed by some bytes, used to exercise the binary path.
_PNG_HEADER = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'


def _write(tmp_path, name, data):
  path = tmp_path / name
  path.write_bytes(data)
  return str(path)


@pytest.mark.parametrize(
    'guessed',
    [
        'application/cu-seeme',  # .cu  (the case reported in #744)
        'text/x-python',  # .py
        'text/vnd.trolltech.linguist',  # .ts
        None,  # unknown extension
    ],
)
def test_textual_file_with_unsupported_guess_falls_back_to_text_plain(
    tmp_path, monkeypatch, guessed
):
  path = _write(tmp_path, 'source.bin', b'int main() { return 0; }\n')
  monkeypatch.setattr(
      _extra_utils.mimetypes, 'guess_type', lambda *a, **k: (guessed, None)
  )

  assert _extra_utils._resolve_upload_mime_type(path) == 'text/plain'


def test_standard_text_type_is_preserved(tmp_path, monkeypatch):
  path = _write(tmp_path, 'doc.md', b'# title\n')
  monkeypatch.setattr(
      _extra_utils.mimetypes, 'guess_type', lambda *a, **k: ('text/markdown', None)
  )

  assert _extra_utils._resolve_upload_mime_type(path) == 'text/markdown'


def test_text_compatible_application_type_is_preserved(tmp_path, monkeypatch):
  path = _write(tmp_path, 'data.json', b'{"a": 1}\n')
  monkeypatch.setattr(
      _extra_utils.mimetypes, 'guess_type', lambda *a, **k: ('application/json', None)
  )

  assert _extra_utils._resolve_upload_mime_type(path) == 'application/json'


def test_binary_file_keeps_guessed_type(tmp_path, monkeypatch):
  path = _write(tmp_path, 'image.png', _PNG_HEADER)
  monkeypatch.setattr(
      _extra_utils.mimetypes, 'guess_type', lambda *a, **k: ('image/png', None)
  )

  assert _extra_utils._resolve_upload_mime_type(path) == 'image/png'


def test_binary_file_with_unknown_guess_is_left_unset(tmp_path, monkeypatch):
  # A binary file whose type cannot be guessed must NOT be coerced to text.
  path = _write(tmp_path, 'blob.bin', _PNG_HEADER + b'\x00\x01\x02')
  monkeypatch.setattr(
      _extra_utils.mimetypes, 'guess_type', lambda *a, **k: (None, None)
  )

  assert _extra_utils._resolve_upload_mime_type(path) is None


def test_prepare_resumable_upload_uses_text_plain_for_unsupported_text(
    tmp_path, monkeypatch
):
  path = _write(tmp_path, 'kernel.cu', b'__global__ void k() {}\n')
  monkeypatch.setattr(
      _extra_utils.mimetypes,
      'guess_type',
      lambda *a, **k: ('application/cu-seeme', None),
  )

  http_options, size_bytes, mime_type = _extra_utils.prepare_resumable_upload(
      path
  )

  assert mime_type == 'text/plain'
  assert size_bytes > 0
  assert (
      http_options.headers['X-Goog-Upload-Header-Content-Type'] == 'text/plain'
  )


def test_user_provided_mime_type_takes_precedence(tmp_path, monkeypatch):
  path = _write(tmp_path, 'kernel.cu', b'__global__ void k() {}\n')
  # Should never be consulted when the user passes mime_type explicitly.
  monkeypatch.setattr(
      _extra_utils.mimetypes,
      'guess_type',
      lambda *a, **k: pytest.fail('guess_type should not be called'),
  )

  _, _, mime_type = _extra_utils.prepare_resumable_upload(
      path, user_mime_type='text/x-cuda'
  )

  assert mime_type == 'text/x-cuda'
