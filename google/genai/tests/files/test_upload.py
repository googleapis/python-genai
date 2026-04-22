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


import io
import pathlib
import pytest
from ... import types
from ... import errors
from .. import pytest_helper

# Upload method is not pydantic.
test_table: list[pytest_helper.TestTableItem] = []
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method='files.upload',
    test_table=test_table,
)


def test_image_png_upload(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/google.png')
    assert file.name.startswith('files/')

def test_image_png_upload_with_path(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    p = pathlib.Path('tests/data/google.png')
    file = client.files.upload(
        file=p,
        config=types.UploadFileConfig(display_name='test_image_png_path'),
    )
    assert file.name.startswith('files/')

def test_image_png_upload_with_bytesio(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    with open('tests/data/google.png', 'rb') as f:
      with io.BytesIO(f.read()) as buffer:
        file = client.files.upload(
            file=buffer,
            config=types.UploadFileConfig(mime_type='image/png'),
        )

        assert file.name.startswith('files/')

def test_image_png_upload_with_fd(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    with open('tests/data/google.png', 'rb') as f:
      file = client.files.upload(
          file=f,
          config=types.UploadFileConfig(mime_type='image/png'),
      )

    assert file.name.startswith('files/')

def test_image_png_upload_with_config(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/google.png',
        config=types.UploadFileConfig(display_name='test_image_png'),
    )
    assert file.name.startswith('files/')


def test_image_png_upload_with_config_dict(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/google.png', config={'display_name': 'test_image_png'}
    )
    assert file.name.startswith('files/')


def test_image_jpg_upload(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/google.jpg')
    assert file.name.startswith('files/')


def test_image_jpg_upload_with_config(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/google.jpg',
        config=types.UploadFileConfig(display_name='test_image_jpg'),
    )
    assert file.name.startswith('files/')


def test_image_jpg_upload_with_config_dict(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/google.jpg', config={'display_name': 'test_image_jpg'}
    )
    assert file.name.startswith('files/')


def test_application_pdf_file_upload(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/story.pdf')
    assert file.name.startswith('files/')


def test_application_pdf_upload_with_config(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/story.pdf',
        config=types.UploadFileConfig(display_name='test_application_pdf'),
    )
    assert file.name.startswith('files/')


def test_application_pdf_upload_with_config_dict(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/story.pdf',
        config={'display_name': 'test_application_pdf'},
    )
    assert file.name.startswith('files/')


def test_video_mp4_file_upload(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(file='tests/data/animal.mp4')
    assert file.name.startswith('files/')


def test_video_mp4_upload_with_config(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/animal.mp4',
        config=types.UploadFileConfig(display_name='test_video_mp4'),
    )
    assert file.name.startswith('files/')


def test_video_mp4_upload_with_config_dict(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/animal.mp4', config={'display_name': 'test_video_mp4'}
    )
    assert file.name.startswith('files/')


def test_audio_m4a_file_upload(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/pixel.m4a',
        config=types.UploadFileConfig(mime_type='audio/mp4'),
    )
    assert file.name.startswith('files/')


def test_audio_m4a_upload_with_config(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/pixel.m4a',
        config=types.UploadFileConfig(
            display_name='test_audio_m4a', mime_type='audio/mp4'
        ),
    )
    assert file.name.startswith('files/')


def test_audio_m4a_upload_with_config_dict(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = client.files.upload(
        file='tests/data/pixel.m4a',
        config={'display_name': 'test_audio_m4a', 'mime_type': 'audio/mp4'},
    )
    assert file.name.startswith('files/')


def test_bad_mime_type(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    with pytest.raises(errors.APIError, match="Unsupported MIME"):
      file = client.files.upload(
          file=io.BytesIO(b'test'),
          config={'mime_type': 'bad/mime_type'},
      )


@pytest.mark.asyncio
async def test_image_upload_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = await client.aio.files.upload(file='tests/data/google.png')
    assert file.name.startswith('files/')


@pytest.mark.asyncio
async def test_image_upload_with_config_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = await client.aio.files.upload(
        file='tests/data/google.png',
        config=types.UploadFileConfig(display_name='test_image'),
    )
    assert file.name.startswith('files/')


@pytest.mark.asyncio
async def test_image_upload_with_config_dict_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    file = await client.aio.files.upload(
        file='tests/data/google.png',
        config={
            'display_name': 'test_image',
            'http_options': {'timeout': '8000'},
        },
    )
    assert file.name.startswith('files/')


@pytest.mark.asyncio
async def test_image_upload_with_bytesio_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    with open('tests/data/google.png', 'rb') as f:
      buffer = io.BytesIO(f.read())
    file = await client.aio.files.upload(
        file=buffer,
        config=types.UploadFileConfig(
            mime_type='image/png'),
    )
    assert file.name.startswith('files/')


@pytest.mark.asyncio
async def test_unknown_path_upload_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    try:
      await client.aio.files.upload(file='unknown_path')
    except FileNotFoundError as e:
      assert 'is not a valid file path' in str(e)

@pytest.mark.asyncio
async def test_bad_mime_type_async(client):
  with pytest_helper.exception_if_vertex(client, ValueError):
    with pytest.raises(errors.APIError, match="Unsupported MIME"):
      file = await client.aio.files.upload(
          file=io.BytesIO(b'test'),
          config={'mime_type': 'bad/mime_type'},
      )
