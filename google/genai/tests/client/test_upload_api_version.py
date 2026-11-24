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

"""Tests that Gemini API uploads use the client's API version."""

import io
import json
from typing import Any, Optional
from unittest import mock

import pytest

from ... import _api_client
from ... import _replay_api_client
from ... import Client
from ... import types

_BASE_URL = 'https://generativelanguage.googleapis.com'
_STORE_NAME = 'fileSearchStores/my-store'
_UPLOAD_URL = 'https://generativelanguage.googleapis.com/upload/session'


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.delenv('GOOGLE_GENAI_API_VERSION', raising=False)
  monkeypatch.delenv('GOOGLE_GENAI_USE_VERTEXAI', raising=False)
  monkeypatch.delenv('GOOGLE_GEMINI_BASE_URL', raising=False)


def _make_client(**http_options: Any) -> Client:
  return Client(
      api_key='test-key',
      vertexai=False,
      http_options=types.HttpOptions(**http_options) if http_options else None,
  )


def _start_response() -> _api_client.HttpResponse:
  return _api_client.HttpResponse(
      headers={'x-goog-upload-url': _UPLOAD_URL}, response_stream=['{}']
  )


def _upload_response(body: dict[str, Any]) -> _api_client.HttpResponse:
  return _api_client.HttpResponse(
      headers={}, response_stream=[json.dumps(body)]
  )


_FILE_BODY = {'file': {'name': 'files/abc'}}
_OPERATION_BODY = {'name': f'{_STORE_NAME}/upload/operations/op'}


class _Recorder:
  """Records the URLs of the requests that start an upload."""

  def __init__(self, client: Client, upload_body: dict[str, Any]):
    self.urls: list[str] = []
    api_client = client._api_client

    def fake_request(http_request, http_options=None, stream=False):
      del http_options, stream
      self.urls.append(http_request.url)
      return _start_response()

    async def fake_async_request(http_request, http_options=None, stream=False):
      del http_options, stream
      self.urls.append(http_request.url)
      return _start_response()

    def fake_upload_file(*args, **kwargs):
      del args, kwargs
      return _upload_response(upload_body)

    async def fake_async_upload_file(*args, **kwargs):
      del args, kwargs
      return _upload_response(upload_body)

    self._patches = [
        mock.patch.object(api_client, '_request', side_effect=fake_request),
        mock.patch.object(
            api_client, '_async_request', side_effect=fake_async_request
        ),
        mock.patch.object(
            api_client, 'upload_file', side_effect=fake_upload_file
        ),
        mock.patch.object(
            api_client, 'async_upload_file', side_effect=fake_async_upload_file
        ),
    ]

  def __enter__(self) -> '_Recorder':
    for p in self._patches:
      p.start()
    return self

  def __exit__(self, *exc: Any) -> None:
    for p in self._patches:
      p.stop()


def _files_upload(
    client: Client, http_options: Optional[types.HttpOptions] = None
) -> str:
  with _Recorder(client, _FILE_BODY) as recorder:
    client.files.upload(
        file=io.BytesIO(b'data'),
        config=types.UploadFileConfig(
            mime_type='text/plain', http_options=http_options
        ),
    )
  assert len(recorder.urls) == 1
  return recorder.urls[0]


def _upload_to_store(
    client: Client, http_options: Optional[types.HttpOptions] = None
) -> str:
  with _Recorder(client, _OPERATION_BODY) as recorder:
    client.file_search_stores.upload_to_file_search_store(
        file_search_store_name=_STORE_NAME,
        file=io.BytesIO(b'data'),
        config=types.UploadToFileSearchStoreConfig(
            mime_type='text/plain', http_options=http_options
        ),
    )
  assert len(recorder.urls) == 1
  return recorder.urls[0]


@pytest.mark.parametrize(
    'path, api_version, expected',
    [
        ('upload/{api_version}/files', 'v1', 'upload/v1/files'),
        ('upload/{api_version}/files', 'v1alpha', 'upload/v1alpha/files'),
        ('upload/{api_version}/files', 'v1beta', 'upload/v1beta/files'),
        ('upload/{api_version}/files', '', 'upload/files'),
        ('upload/{api_version}/files', None, 'upload/files'),
        (
            'upload/{api_version}/fileSearchStores/s:uploadToFileSearchStore',
            'v1',
            'upload/v1/fileSearchStores/s:uploadToFileSearchStore',
        ),
        (
            'upload/{api_version}/files?alt=json',
            'v1alpha',
            'upload/v1alpha/files?alt=json',
        ),
    ],
)
def test_resolve_api_version_in_path(
    path: str, api_version: Optional[str], expected: str
) -> None:
  assert _api_client._resolve_api_version_in_path(path, api_version) == expected


def test_files_upload_uses_default_api_version() -> None:
  assert _files_upload(_make_client()) == (
      f'{_BASE_URL}/upload/{_api_client.GOOGLE_AI_API_DEFAULT_VERSION}/files'
  )


def test_upload_to_file_search_store_uses_default_api_version() -> None:
  assert _upload_to_store(_make_client()) == (
      f'{_BASE_URL}/upload/{_api_client.GOOGLE_AI_API_DEFAULT_VERSION}/'
      f'{_STORE_NAME}:uploadToFileSearchStore'
  )


def test_files_upload_uses_client_api_version() -> None:
  client = _make_client(api_version='v1alpha')
  assert _files_upload(client) == f'{_BASE_URL}/upload/v1alpha/files'


def test_upload_to_file_search_store_uses_client_api_version() -> None:
  client = _make_client(api_version='v1alpha')
  assert _upload_to_store(client) == (
      f'{_BASE_URL}/upload/v1alpha/{_STORE_NAME}:uploadToFileSearchStore'
  )


def test_files_upload_uses_per_request_api_version() -> None:
  client = _make_client(api_version='v1beta')
  url = _files_upload(client, types.HttpOptions(api_version='v1alpha'))
  assert url == f'{_BASE_URL}/upload/v1alpha/files'


def test_upload_to_file_search_store_uses_per_request_api_version() -> None:
  client = _make_client(api_version='v1beta')
  url = _upload_to_store(client, types.HttpOptions(api_version='v1alpha'))
  assert url == (
      f'{_BASE_URL}/upload/v1alpha/{_STORE_NAME}:uploadToFileSearchStore'
  )


def test_per_request_api_version_does_not_change_client() -> None:
  client = _make_client(api_version='v1beta')
  _files_upload(client, types.HttpOptions(api_version='v1alpha'))
  assert _files_upload(client) == f'{_BASE_URL}/upload/v1beta/files'


def test_upload_uses_env_api_version(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setenv('GOOGLE_GENAI_API_VERSION', 'v1alpha')
  client = _make_client()
  assert _files_upload(client) == f'{_BASE_URL}/upload/v1alpha/files'
  assert _upload_to_store(client) == (
      f'{_BASE_URL}/upload/v1alpha/{_STORE_NAME}:uploadToFileSearchStore'
  )


def test_explicit_api_version_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setenv('GOOGLE_GENAI_API_VERSION', 'v1alpha')
  client = _make_client(api_version='v1')
  assert _files_upload(client) == f'{_BASE_URL}/upload/v1/files'


def test_upload_with_empty_api_version_has_no_version_segment() -> None:
  client = _make_client(api_version='')
  assert _files_upload(client) == f'{_BASE_URL}/upload/files'


@pytest.mark.asyncio
async def test_async_files_upload_uses_client_api_version() -> None:
  client = _make_client(api_version='v1alpha')
  with _Recorder(client, _FILE_BODY) as recorder:
    await client.aio.files.upload(
        file=io.BytesIO(b'data'),
        config=types.UploadFileConfig(mime_type='text/plain'),
    )
  assert recorder.urls == [f'{_BASE_URL}/upload/v1alpha/files']


@pytest.mark.asyncio
async def test_async_upload_to_file_search_store_uses_per_request_version() -> (
    None
):
  client = _make_client(api_version='v1beta')
  with _Recorder(client, _OPERATION_BODY) as recorder:
    await client.aio.file_search_stores.upload_to_file_search_store(
        file_search_store_name=_STORE_NAME,
        file=io.BytesIO(b'data'),
        config=types.UploadToFileSearchStoreConfig(
            mime_type='text/plain',
            http_options=types.HttpOptions(api_version='v1alpha'),
        ),
    )
  assert recorder.urls == [
      f'{_BASE_URL}/upload/v1alpha/{_STORE_NAME}:uploadToFileSearchStore'
  ]


def test_vertex_upload_paths_are_unchanged() -> None:
  client = _api_client.BaseApiClient(
      vertexai=True, project='my-project', location='us-central1'
  )
  request = client._build_request('post', 'upload/v1beta/files', {})
  assert request.url == (
      'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/'
      'my-project/locations/us-central1/upload/v1beta/files'
  )


def test_collection_scoped_base_url_omits_api_version() -> None:
  # With a COLLECTION-scoped base_url, the base_url carries the version, so
  # the `{api_version}` placeholder must not leak into the URL.
  client = _make_client(
      base_url='https://my-proxy.example.com/v1beta',
      base_url_resource_scope=types.ResourceScope.COLLECTION,
  )
  request = client._api_client._build_request(
      'post', 'upload/{api_version}/files', {}
  )
  assert request.url == 'https://my-proxy.example.com/v1beta/upload/files'


@pytest.mark.parametrize(
    'url, expected',
    [
        ('{MLDEV_URL_PREFIX}/v1beta/files', '{MLDEV_URL_PREFIX}/files'),
        ('{MLDEV_URL_PREFIX}/v1/files', '{MLDEV_URL_PREFIX}/files'),
        (
            '{MLDEV_URL_PREFIX}/v1alpha/fileSearchStores/s:upload',
            '{MLDEV_URL_PREFIX}/fileSearchStores/s:upload',
        ),
        ('{MLDEV_URL_PREFIX}/models/m', '{MLDEV_URL_PREFIX}/models/m'),
        ('{VERTEX_URL_PREFIX}/v1/files', '{VERTEX_URL_PREFIX}/v1/files'),
    ],
)
def test_replay_upload_url_ignores_api_version(url: str, expected: str) -> None:
  assert _replay_api_client._normalize_mldev_upload_url(url) == expected
