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

from importlib.metadata import version
import re
import typing
from typing import Any

from ... import _mcp_utils
from ... import types

_is_mcp_imported = False
if typing.TYPE_CHECKING:
  import mcp

  _is_mcp_imported = True
else:
  try:
    import mcp

    _is_mcp_imported = True
  except ImportError:
    _is_mcp_imported = False


def test_set_mcp_usage_header_from_empty_dict():
  if not _is_mcp_imported:
    return
  """Test whether the MCP usage header is set correctly from an empty dict."""
  headers = {}
  _mcp_utils.set_mcp_usage_header(headers)
  assert re.match(r'mcp_used/\d+\.\d+\.\d+', headers['x-goog-api-client'])


def test_set_mcp_usage_header_with_existing_header():
  if not _is_mcp_imported:
    return
  """Test whether the MCP usage header is set correctly from an existing header."""
  headers = {'x-goog-api-client': 'google-genai-sdk/1.0.0 gl-python/1.0.0'}
  _mcp_utils.set_mcp_usage_header(headers)
  assert re.match(
      r'google-genai-sdk/1.0.0 gl-python/1.0.0 mcp_used/\d+\.\d+\.\d+',
      headers['x-goog-api-client'],
  )


def test_set_mcp_usage_header_with_existing_mcp_header():
  if not _is_mcp_imported:
    return
  """Test whether the MCP usage header is set correctly from an existing MCP header."""
  headers = {
      'x-goog-api-client': (
          'google-genai-sdk/1.0.0 gl-python/1.0.0 mcp_used/1.0.0'
      )
  }
  _mcp_utils.set_mcp_usage_header(headers)
  assert re.match(
      r'google-genai-sdk/1.0.0 gl-python/1.0.0 mcp_used/\d+\.\d+\.\d+',
      headers['x-goog-api-client'],
  )
