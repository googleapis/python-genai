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


import pathlib
import pytest
from ... import _transformers as t
from ... import types
from .. import pytest_helper


test_table: list[pytest_helper.TestTableItem] = []

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='t.t_file_name',
    test_table=test_table,
)

pytest_plugins = ('pytest_asyncio',)


def test_name_transform_name(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    for file in client.files.list():
      if file.download_uri is not None:
        break
    else:
      raise ValueError('No files found with a `download_uri`.')

    file_id = file.name.split('/')[-1]
    video = types.Video(uri=file.download_uri)
    generated_video = types.GeneratedVideo(video=video)
    for f in [
        file,
        file_id,
        file.name,
        file.uri,
        file.download_uri,
        video,
        generated_video,
    ]:
      name = t.t_file_name(f)
      assert name == file_id


def test_basic_download(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    for file in client.files.list():
      if file.download_uri is not None:
        break
    else:
      raise ValueError('No files found with a `download_uri`.')

    content = client.files.download(file=file)
    assert content[4:8] == b'ftyp'


@pytest.mark.asyncio
async def test_basic_download_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    async for file in await client.aio.files.list():
      if file.download_uri is not None:
        break
    else:
      raise ValueError('No files found with a `download_uri`.')

    content = await client.aio.files.download(file=file)
    assert content[4:8] == b'ftyp'
