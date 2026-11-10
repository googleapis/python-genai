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
#

"""Tests for synchronous streaming responses."""

import io
import json
import requests

from ... import _api_client as api_client


def test_requests_sse_stream_without_charset_decodes_as_utf8() -> None:
  expected = 'café'
  payload = json.dumps({'text': expected}, ensure_ascii=False).encode('utf-8')

  resp = requests.Response()
  resp.status_code = 200
  resp.headers['Content-Type'] = 'text/event-stream'
  # Matches what requests.adapters.HTTPAdapter.build_response() sets -> 'ISO-8859-1'
  resp.encoding = requests.utils.get_encoding_from_headers(resp.headers)
  resp.raw = io.BytesIO(b'data: ' + payload + b'\n\n')

  chunk = next(api_client.HttpResponse(resp.headers, resp).segments())
  assert chunk['text'] == expected, (
      f"Expected {expected!r}, got {chunk['text']!r}"
  )


def test_requests_stream_with_none_encoding_decodes_as_utf8() -> None:
  expected = 'café'
  payload = json.dumps({'text': expected}, ensure_ascii=False).encode('utf-8')

  resp = requests.Response()
  resp.status_code = 200
  resp.encoding = None
  resp.raw = io.BytesIO(b'data: ' + payload + b'\n\n')

  chunk = next(api_client.HttpResponse(resp.headers, resp).segments())
  assert chunk['text'] == expected


def test_requests_sse_stream_multibyte_utf8_across_chunk_boundary() -> None:
  # Place a 4-byte UTF-8 sequence ("🎉") across requests' 512-byte chunk size.
  prefix = 'a' * (requests.models.ITER_CHUNK_SIZE - len('data: {"text": "') - 1)
  expected = prefix + '🎉'
  payload = json.dumps({'text': expected}, ensure_ascii=False).encode('utf-8')

  resp = requests.Response()
  resp.status_code = 200
  resp.headers['Content-Type'] = 'text/event-stream'
  resp.encoding = requests.utils.get_encoding_from_headers(resp.headers)
  resp.raw = io.BytesIO(b'data: ' + payload + b'\n\n')

  chunk = next(api_client.HttpResponse(resp.headers, resp).segments())
  assert chunk['text'] == expected


def test_requests_stream_respects_explicit_charset_header() -> None:
  expected = 'café'
  for charset in ('iso-8859-1', 'utf-16'):
    payload = json.dumps({'text': expected}, ensure_ascii=False)
    raw_line = f'data: {payload}\n\n'.encode(charset)

    resp = requests.Response()
    resp.status_code = 200
    resp.headers['Content-Type'] = f'text/event-stream; charset={charset}'
    resp.encoding = requests.utils.get_encoding_from_headers(resp.headers)
    resp.raw = io.BytesIO(raw_line)

    chunk = next(api_client.HttpResponse(resp.headers, resp).segments())
    assert chunk['text'] == expected
