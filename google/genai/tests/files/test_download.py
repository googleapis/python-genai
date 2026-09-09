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


"""Test files upload method."""


import asyncio
import io
import pathlib
import time
from unittest import mock
from typing import Any
import google.auth.transport.requests
import httpx
import pytest
import requests
from ... import _transformers as t
from ... import types
from ..._api_client import BaseApiClient
from ...files import AsyncFiles, Files
from .. import pytest_helper

try:
  import aiohttp
  AIOHTTP_NOT_INSTALLED = False
except ImportError:
  AIOHTTP_NOT_INSTALLED = True


test_table: list[pytest_helper.TestTableItem] = []

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='t.t_file_name',
    test_table=test_table,
)

pytest_plugins = ('pytest_asyncio',)


def _get_downloadable_file(client: Any) -> types.File | types.Video:
  for file in client.files.list():
    if file.download_uri is not None:
      return file
  # Fallback to generating a minimal video if no downloadable files exist in the project.
  operation = client.models.generate_videos(
      model='veo-2.0-generate-001',
      prompt='A red ball',
      config=types.GenerateVideosConfig(
          person_generation='dont_allow',
          aspect_ratio='16:9',
          duration_seconds=5,
      ),
  )
  while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)
  return operation.result.generated_videos[0].video


async def _async_get_downloadable_file(
    client: Any,
) -> types.File | types.Video:
  async for file in await client.aio.files.list():
    if file.download_uri is not None:
      return file
  # Fallback to generating a minimal video if no downloadable files exist in the project.
  operation = await client.aio.models.generate_videos(
      model='veo-2.0-generate-001',
      prompt='A red ball',
      config=types.GenerateVideosConfig(
          person_generation='dont_allow',
          aspect_ratio='16:9',
          duration_seconds=5,
      ),
  )
  while not operation.done:
    await asyncio.sleep(10)
    operation = await client.aio.operations.get(operation)
  return operation.result.generated_videos[0].video


async def _mock_async_download_video(*args: Any, **kwargs: Any) -> bytes | None:
  if kwargs.get('destination') is None:
    return b'video_data'
  return None


class _AsyncMockChunkIter:

  async def iter_chunked(self, chunk_size: int | None = None):
    yield b'chunk1'
    yield b'chunk2'


class _AsyncHttpxMockChunkIter:

  async def __call__(self, chunk_size: int | None = None):
    yield b'chunk1'
    yield b'chunk2'


class _AsyncWriter:

  def __init__(self) -> None:
    self.written_chunks: list[bytes] = []

  async def write(self, data: bytes) -> None:
    self.written_chunks.append(data)


def test_name_transform_name(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = _get_downloadable_file(client)

    file_id = (file.name or file.uri).split('/')[-1].split(':')[0]
    download_uri = getattr(file, 'download_uri', None) or getattr(
        file, 'uri', None
    )
    video = types.Video(uri=download_uri)
    generated_video = types.GeneratedVideo(video=video)
    for f in [
        file,
        file_id,
        getattr(file, 'name', file_id),
        getattr(file, 'uri', None),
        getattr(file, 'download_uri', None),
        video,
        generated_video,
    ]:
      if f is not None:
        name = t.t_file_name(f)
        assert name == file_id


def test_basic_download(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = _get_downloadable_file(client)

    content = client.files.download(file=file)
    assert content[4:8] == b'ftyp'


@pytest.mark.asyncio
async def test_basic_download_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = await _async_get_downloadable_file(client)

    content = await client.aio.files.download(file=file)
    assert content[4:8] == b'ftyp'


def test_destination_download(client, tmp_path):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = _get_downloadable_file(client)

    out_file = tmp_path / 'downloaded.mp4'
    result = client.files.download(file=file, destination=out_file)
    assert result is None
    assert out_file.exists()
    assert out_file.read_bytes()[4:8] == b'ftyp'


@pytest.mark.asyncio
async def test_async_destination_download(client, tmp_path):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = await _async_get_downloadable_file(client)

    out_file = tmp_path / 'downloaded_async.mp4'
    result = await client.aio.files.download(file=file, destination=out_file)
    assert result is None
    assert out_file.exists()
    assert out_file.read_bytes()[4:8] == b'ftyp'


def test_destination_filepath(client, tmp_path):
  if client._api_client.vertexai:
    with pytest.raises(
        ValueError, match='only supported in the Gemini Developer client'
    ):
      client.files.download(
          file='files/test_123', destination=str(tmp_path / 'out.mp4')
      )
    return

  api_client = mock.create_autospec(
      BaseApiClient, instance=True, spec_set=True
  )
  api_client.vertexai = False
  api_client.download_file.return_value = None

  files_client = Files(api_client)
  target_file = str(tmp_path / 'out.mp4')

  result = files_client.download(file='files/test_123', destination=target_file)
  assert result is None
  api_client.download_file.assert_called_once()
  assert api_client.download_file.call_args.kwargs['destination'] == target_file


def test_destination_pathlib(client, tmp_path):
  if client._api_client.vertexai:
    return

  api_client = mock.create_autospec(
      BaseApiClient, instance=True, spec_set=True
  )
  api_client.vertexai = False
  api_client.download_file.return_value = None

  files_client = Files(api_client)
  target_file = tmp_path / 'out.mp4'

  result = files_client.download(file='files/test_123', destination=target_file)
  assert result is None
  api_client.download_file.assert_called_once()
  assert api_client.download_file.call_args.kwargs['destination'] == target_file


def test_destination_bytesio(client):
  if client._api_client.vertexai:
    return

  api_client = mock.create_autospec(
      BaseApiClient, instance=True, spec_set=True
  )
  api_client.vertexai = False
  api_client.download_file.return_value = None

  files_client = Files(api_client)
  buffer = io.BytesIO()

  result = files_client.download(file='files/test_123', destination=buffer)
  assert result is None
  api_client.download_file.assert_called_once()
  assert api_client.download_file.call_args.kwargs['destination'] == buffer


def test_video_destination_behavior(client, tmp_path):
  if client._api_client.vertexai:
    return

  api_client = mock.create_autospec(
      BaseApiClient, instance=True, spec_set=True
  )
  api_client.vertexai = False

  # When destination is None, returns bytes and sets video.video_bytes
  api_client.download_file.return_value = b'video_data'
  files_client = Files(api_client)
  video = types.Video(
      uri='https://generativelanguage.googleapis.com/v1beta/files/test_video'
  )
  data = files_client.download(file=video)
  assert data == b'video_data'
  assert video.video_bytes == b'video_data'

  # When destination is provided, returns None and does not overwrite video.video_bytes
  video2 = types.Video(
      uri='https://generativelanguage.googleapis.com/v1beta/files/test_video'
  )
  api_client.download_file.return_value = None
  buf = io.BytesIO()
  data2 = files_client.download(file=video2, destination=buf)
  assert data2 is None
  assert video2.video_bytes is None

  # GeneratedVideo when destination is None sets video.video_bytes
  video3 = types.Video(
      uri='https://generativelanguage.googleapis.com/v1beta/files/test_video'
  )
  gen_video = types.GeneratedVideo(video=video3)
  api_client.download_file.return_value = b'video_data'
  data3 = files_client.download(file=gen_video)
  assert data3 == b'video_data'
  assert gen_video.video.video_bytes == b'video_data'


@pytest.mark.asyncio
async def test_async_video_destination_behavior(client):
  if client._api_client.vertexai:
    return

  api_client = mock.create_autospec(
      BaseApiClient, instance=True, spec_set=True
  )
  api_client.vertexai = False
  api_client.async_download_file = mock.AsyncMock(
      side_effect=_mock_async_download_video
  )
  files_client = AsyncFiles(api_client)
  video = types.Video(
      uri='https://generativelanguage.googleapis.com/v1beta/files/test_video'
  )
  data = await files_client.download(file=video)
  assert data == b'video_data'
  assert video.video_bytes == b'video_data'

  video2 = types.Video(
      uri='https://generativelanguage.googleapis.com/v1beta/files/test_video'
  )
  buf = io.BytesIO()
  data2 = await files_client.download(file=video2, destination=buf)
  assert data2 is None
  assert video2.video_bytes is None


@pytest.mark.asyncio
async def test_async_destination(client, tmp_path):
  if client._api_client.vertexai:
    with pytest.raises(
        ValueError, match='only supported in the Gemini Developer client'
    ):
      await client.aio.files.download(
          file='files/test_123', destination=str(tmp_path / 'out.mp4')
      )
    return

  api_client = mock.create_autospec(
      BaseApiClient, instance=True, spec_set=True
  )
  api_client.vertexai = False
  api_client.async_download_file = mock.AsyncMock(return_value=None)
  files_client = AsyncFiles(api_client)
  target_file = tmp_path / 'out.mp4'

  result = await files_client.download(
      file='files/test_123', destination=target_file
  )
  assert result is None


@pytest.mark.asyncio
async def test_async_destination_bytesio(client):
  if client._api_client.vertexai:
    return

  api_client = mock.create_autospec(
      BaseApiClient, instance=True, spec_set=True
  )
  api_client.vertexai = False
  api_client.async_download_file = mock.AsyncMock(return_value=None)
  files_client = AsyncFiles(api_client)
  buffer = io.BytesIO()

  result = await files_client.download(file='files/test_123', destination=buffer)
  assert result is None


def test_destination_invalid_type(client):
  if client._api_client.vertexai:
    return

  api_client = BaseApiClient(api_key='test_key')
  with pytest.raises(ValueError, match='Unsupported destination type'):
    api_client.download_file('files/test_123:download', destination=12345)


@pytest.mark.asyncio
async def test_async_destination_invalid_type(client):
  if client._api_client.vertexai:
    return

  api_client = BaseApiClient(api_key='test_key')
  with pytest.raises(ValueError, match='Unsupported destination type'):
    await api_client.async_download_file(
        'files/test_123:download', destination=12345
    )


@pytest.mark.asyncio
@pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason='aiohttp is not installed, skipping test.'
)
async def test_async_destination_bytesio_writes_chunks(client):
  if client._api_client.vertexai:
    return

  api_client = BaseApiClient(api_key='test_key')

  mock_response = mock.create_autospec(aiohttp.ClientResponse, instance=True)
  mock_response.status = 200
  mock_response.content = _AsyncMockChunkIter()

  mock_session = mock.create_autospec(aiohttp.ClientSession, instance=True)
  mock_session.request = mock.AsyncMock(return_value=mock_response)
  mock_session.configure_mtls_channel = mock.AsyncMock()
  mock_session._is_mtls = False

  buffer = io.BytesIO()
  with mock.patch.object(
      api_client, '_use_aiohttp', return_value=True
  ), mock.patch.object(
      api_client, '_get_aiohttp_session', return_value=mock_session
  ):
    result = await api_client.async_download_file(
        'files/test_123:download', destination=buffer
    )

  assert result is None
  assert buffer.getvalue() == b'chunk1chunk2'
  mock_response.close.assert_called_once()


def test_authorized_session_destination_closes_response(client):
  if client._api_client.vertexai:
    return

  api_client = BaseApiClient(api_key='test_key')
  mock_response = mock.create_autospec(requests.Response, instance=True)
  mock_response.status_code = 200
  mock_response.iter_content.return_value = [b'chunk1', b'chunk2']

  mock_auth_session = mock.create_autospec(
      google.auth.transport.requests.AuthorizedSession, instance=True
  )
  mock_auth_session.request.return_value = mock_response
  mock_auth_session._is_mtls = False

  api_client._authorized_session = mock_auth_session
  buffer = io.BytesIO()

  with mock.patch.object(api_client, '_use_google_auth_sync', return_value=True):
    result = api_client.download_file(
        'files/test_123:download', destination=buffer
    )

  assert result is None
  assert buffer.getvalue() == b'chunk1chunk2'
  mock_response.close.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.skipif(
    AIOHTTP_NOT_INSTALLED, reason='aiohttp is not installed, skipping test.'
)
async def test_async_destination_awaitable_writer(client):
  if client._api_client.vertexai:
    return

  api_client = BaseApiClient(api_key='test_key')

  mock_response = mock.create_autospec(aiohttp.ClientResponse, instance=True)
  mock_response.status = 200
  mock_response.content = _AsyncMockChunkIter()

  mock_session = mock.create_autospec(aiohttp.ClientSession, instance=True)
  mock_session.request = mock.AsyncMock(return_value=mock_response)
  mock_session.configure_mtls_channel = mock.AsyncMock()
  mock_session._is_mtls = False

  async_writer = _AsyncWriter()
  with mock.patch.object(
      api_client, '_use_aiohttp', return_value=True
  ), mock.patch.object(
      api_client, '_get_aiohttp_session', return_value=mock_session
  ):
    result = await api_client.async_download_file(
        'files/test_123:download', destination=async_writer
    )

  assert result is None
  assert async_writer.written_chunks == [b'chunk1', b'chunk2']
  mock_response.close.assert_called_once()


@pytest.mark.asyncio
async def test_async_httpx_destination_bytesio_writes_chunks(client):
  if client._api_client.vertexai:
    return

  api_client = BaseApiClient(api_key='test_key')

  mock_response = mock.create_autospec(httpx.Response, instance=True)
  mock_response.status_code = 200
  mock_response.aiter_bytes = _AsyncHttpxMockChunkIter()
  mock_response.aclose = mock.AsyncMock()

  buffer = io.BytesIO()
  with mock.patch.object(
      api_client, '_use_aiohttp', return_value=False
  ), mock.patch.object(
      api_client._async_httpx_client, 'send', mock.AsyncMock(return_value=mock_response)
  ):
    result = await api_client.async_download_file(
        'files/test_123:download', destination=buffer
    )

  assert result is None
  assert buffer.getvalue() == b'chunk1chunk2'
  mock_response.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_httpx_destination_awaitable_writer(client):
  if client._api_client.vertexai:
    return

  api_client = BaseApiClient(api_key='test_key')

  mock_response = mock.create_autospec(httpx.Response, instance=True)
  mock_response.status_code = 200
  mock_response.aiter_bytes = _AsyncHttpxMockChunkIter()
  mock_response.aclose = mock.AsyncMock()

  async_writer = _AsyncWriter()
  with mock.patch.object(
      api_client, '_use_aiohttp', return_value=False
  ), mock.patch.object(
      api_client._async_httpx_client, 'send', mock.AsyncMock(return_value=mock_response)
  ):
    result = await api_client.async_download_file(
        'files/test_123:download', destination=async_writer
    )

  assert result is None
  assert async_writer.written_chunks == [b'chunk1', b'chunk2']
  mock_response.aclose.assert_awaited_once()



