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


"""Test files register method."""

import json
from unittest import mock

from google.auth import credentials
import httpx
import pytest

from ... import _api_client
from ... import Client
from ... import types
from .. import pytest_helper


class FakeCredentials(credentials.Credentials):

  def __init__(self, token="fake_token", expired=False, quota_project_id=None):
    super().__init__()
    self.token = token
    self._expired = expired
    self._quota_project_id = quota_project_id
    self.refresh_count = 0

  @property
  def expired(self):
    return self._expired

  @property
  def quota_project_id(self):
    return self._quota_project_id

  def refresh(self, request):
    self.refresh_count += 1
    self.token = "refreshed_token"
    self._expired = False


@mock.patch.object(_api_client.BaseApiClient, "_request_once", autospec=True)
def test_simple_token(mock_request):
  client = Client(api_key="dummy_key")
  captured_request = None

  def side_effect(self, http_request, stream=False):
    nonlocal captured_request
    captured_request = http_request
    return _api_client.HttpResponse(
        headers={},
        response_stream=[json.dumps({"files": [{"uri": "files/abc"}]})],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    response = client.files.register_files(
        auth=FakeCredentials(token="test_token"),
        uris=["gs://test-bucket/test-file-1.txt"],
    )

    assert len(response.files) == 1
    assert response.files[0].uri == "files/abc"
    assert captured_request.headers["authorization"] == "Bearer test_token"


@mock.patch.object(_api_client.BaseApiClient, "_request_once", autospec=True)
def test_token_refresh(mock_request):
  client = Client(api_key="dummy_key")
  captured_request = None

  def side_effect(self, http_request, stream=False):
    nonlocal captured_request
    captured_request = http_request
    return _api_client.HttpResponse(
        headers={},
        response_stream=[json.dumps({"files": [{"uri": "files/abc"}]})],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    creds = FakeCredentials(expired=True)
    response = client.files.register_files(
        auth=creds,
        uris=["gs://test-bucket/test-file-1.txt"],
    )
    assert creds.refresh_count == 1
    assert len(response.files) == 1
    assert response.files[0].uri == "files/abc"
    assert captured_request.headers["authorization"] == "Bearer refreshed_token"


@mock.patch.object(_api_client.BaseApiClient, "_request_once", autospec=True)
def test_quota_project(mock_request):
  client = Client(api_key="dummy_key")
  captured_request = None

  def side_effect(self, http_request, stream=False):
    nonlocal captured_request
    captured_request = http_request
    return _api_client.HttpResponse(
        headers={},
        response_stream=[json.dumps({"files": [{"uri": "files/abc"}]})],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    creds = FakeCredentials(quota_project_id="test_project")
    response = client.files.register_files(
        auth=creds,
        uris=["gs://test-bucket/test-file-1.txt"],
    )
    assert len(response.files) == 1
    assert response.files[0].uri == "files/abc"
    assert captured_request.headers["x-goog-user-project"] == "test_project"


@mock.patch.object(_api_client.BaseApiClient, "_request_once", autospec=True)
def test_multiple_uris(mock_request):
  client = Client(api_key="dummy_key")

  def side_effect(self, http_request, stream=False):
    return _api_client.HttpResponse(
        headers={},
        response_stream=[
            json.dumps({"files": [{"uri": "files/abc"}, {"uri": "files/def"}]})
        ],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    response = client.files.register_files(
        auth=FakeCredentials(),
        uris=[
            "gs://test-bucket/test-file-1.txt",
            "gs://test-bucket/test-file-2.txt",
        ],
    )
    assert len(response.files) == 2
    assert response.files[0].uri == "files/abc"
    assert response.files[1].uri == "files/def"


@pytest.mark.asyncio
@mock.patch.object(
    _api_client.BaseApiClient, "_async_request_once", autospec=True
)
async def test_async_single(mock_request):
  client = Client(api_key="dummy_key")

  async def side_effect(self, http_request, stream=False):
    return _api_client.HttpResponse(
        headers={},
        response_stream=[json.dumps({"files": [{"uri": "files/abc"}]})],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    response = await client.aio.files.register_files(
        auth=FakeCredentials(),
        uris=["gs://test-bucket/test-file-1.txt"],
    )

    assert len(response.files) == 1
    assert response.files[0].uri == "files/abc"


@pytest.mark.asyncio
@mock.patch.object(
    _api_client.BaseApiClient, "_async_request_once", autospec=True
)
async def test_async_token_refresh(mock_request):
  client = Client(api_key="dummy_key")
  captured_request = None

  async def side_effect(self, http_request, stream=False):
    nonlocal captured_request
    captured_request = http_request
    return _api_client.HttpResponse(
        headers={},
        response_stream=[json.dumps({"files": [{"uri": "files/abc"}]})],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    creds = FakeCredentials(expired=True)
    response = await client.aio.files.register_files(
        auth=creds,
        uris=["gs://test-bucket/test-file-1.txt"],
    )
    assert creds.refresh_count == 1
    assert len(response.files) == 1
    assert response.files[0].uri == "files/abc"
    assert captured_request.headers["authorization"] == "Bearer refreshed_token"


@pytest.mark.asyncio
@mock.patch.object(
    _api_client.BaseApiClient, "_async_request_once", autospec=True
)
async def test_async_quota_project(mock_request):
  client = Client(api_key="dummy_key")
  captured_request = None

  async def side_effect(self, http_request, stream=False):
    nonlocal captured_request
    captured_request = http_request
    return _api_client.HttpResponse(
        headers={},
        response_stream=[json.dumps({"files": [{"uri": "files/abc"}]})],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    creds = FakeCredentials(quota_project_id="test_project")
    response = await client.aio.files.register_files(
        auth=creds,
        uris=["gs://test-bucket/test-file-1.txt"],
    )
    assert len(response.files) == 1
    assert response.files[0].uri == "files/abc"
    assert captured_request.headers["x-goog-user-project"] == "test_project"


@pytest.mark.asyncio
@mock.patch.object(
    _api_client.BaseApiClient, "_async_request_once", autospec=True
)
async def test_async_multiple_uris(mock_request):
  client = Client(api_key="dummy_key")

  async def side_effect(self, http_request, stream=False):
    return _api_client.HttpResponse(
        headers={},
        response_stream=[
            json.dumps({"files": [{"uri": "files/abc"}, {"uri": "files/def"}]})
        ],
    )

  mock_request.side_effect = side_effect

  with pytest_helper.exception_if_vertex(client, ValueError):
    response = await client.aio.files.register_files(
        auth=FakeCredentials(),
        uris=[
            "gs://test-bucket/test-file-1.txt",
            "gs://test-bucket/test-file-2.txt",
        ],
    )
    assert len(response.files) == 2
    assert response.files[0].uri == "files/abc"
    assert response.files[1].uri == "files/def"
