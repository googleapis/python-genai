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


"""Tests t_file_name method in the _transformers module."""

from ... import _transformers as t


def test_file_name_from_https_uri():
  assert (
      t.t_file_name(
          'https://generativelanguage.googleapis.com/v1beta/files/abc123'
      )
      == 'abc123'
  )


def test_file_name_from_https_uri_with_dashes():
  # File names may contain dashes (e.g. files/123-456); the full name must
  # be extracted, not truncated at the first dash.
  assert (
      t.t_file_name(
          'https://generativelanguage.googleapis.com/v1beta/files/my-doc'
      )
      == 'my-doc'
  )
  assert (
      t.t_file_name(
          'https://generativelanguage.googleapis.com/v1beta/files/123-456'
      )
      == '123-456'
  )


def test_file_name_from_https_uri_with_download_suffix():
  # The extraction still stops at the ':' of the download suffix.
  assert (
      t.t_file_name(
          'https://generativelanguage.googleapis.com/v1beta/files/'
          'abc123:download?alt=media'
      )
      == 'abc123'
  )


def test_file_name_from_files_prefix():
  assert t.t_file_name('files/my-doc') == 'my-doc'


def test_file_name_plain():
  assert t.t_file_name('abc123') == 'abc123'
