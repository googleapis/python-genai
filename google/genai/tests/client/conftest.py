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

"""Shared fixtures for client tests."""

import pytest

from ... import _api_client as api_client


@pytest.fixture(autouse=True)
def reset_has_aiohttp():
  # Some client tests override the module-level `has_aiohttp` flag; restore it
  # so the override does not leak into later tests on the same pytest worker.
  original = api_client.has_aiohttp
  yield
  api_client.has_aiohttp = original
