"""Tests t_bytes methods in the _transformers module."""

import base64

from ... import _base_transformers as t

_RAW_BYTES = (
    b'\xfb\xf6\x9bq\xd7\x9f\x82\x18\xa3\x92Y\xa7\xa2\x9a\xab\xb2\xdb\xaf\xc3\x1c\xb3\x00\x10\x83\x10Q\x87'
    b' \x92\x8b0\xd3\x8fA\x14\x93QU\x97a\x9d5\xdb~9\xeb\xbf='
)


def test_t_bytes():
  assert t.t_bytes(_RAW_BYTES) == base64.b64encode(_RAW_BYTES).decode('ascii')
  assert t.t_bytes('string') == 'string'
