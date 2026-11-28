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


"""Tests for Pager and AsyncPager iteration."""

import asyncio
import re

from unittest import mock

import pytest

from ... import pagers


def make_response(files, next_page_token):
  response = mock.MagicMock()
  response.files = files
  response.next_page_token = next_page_token
  response.sdk_http_response = None
  return response


# page_token -> (files, next_page_token). The middle page is empty but still
# has a next_page_token, which list APIs may return (AIP-158).
PAGES = {
    None: (['files/a'], 'token-1'),
    'token-1': ([], 'token-2'),
    'token-2': (['files/b'], None),
}


def fake_request(config):
  token = config.get('page_token') if isinstance(config, dict) else config.page_token
  files, next_token = PAGES[token]
  return make_response(files, next_token)


async def fake_async_request(config):
  return fake_request(config)


def test_pager_iterates_past_empty_page():
  first_files, first_token = PAGES[None]
  pager = pagers.Pager(
      'files', fake_request, make_response(first_files, first_token), None
  )

  assert [f for f in pager] == ['files/a', 'files/b']


def test_pager_stops_after_last_empty_page():
  pages = {
      None: (['files/a'], 'token-1'),
      'token-1': ([], None),
  }

  def request(config):
    token = config.get('page_token') if isinstance(config, dict) else config.page_token
    files, next_token = pages[token]
    return make_response(files, next_token)

  first_files, first_token = pages[None]
  pager = pagers.Pager(
      'files', request, make_response(first_files, first_token), None
  )

  assert [f for f in pager] == ['files/a']


def test_async_pager_iterates_past_empty_page():
  async def collect():
    first_files, first_token = PAGES[None]
    pager = pagers.AsyncPager(
        'files', fake_async_request, make_response(first_files, first_token), None
    )
    return [f async for f in pager]

  assert asyncio.run(collect()) == ['files/a', 'files/b']
