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

"""Tests for content_stream.py."""

from collections.abc import AsyncIterator, Iterable
from typing import TypeVar

import pytest

from ... import content_stream
from ... import types

T = TypeVar('T')


async def _to_async_iter(iterable: Iterable[T]) -> AsyncIterator[T]:
  for item in iterable:
    yield item


async def _parts_to_list(
    parts_iter: AsyncIterator[types.Part],
) -> list[types.Part]:
  return [part async for part in parts_iter]


@pytest.mark.asyncio
async def test_init_with_static_content_obj():
  stream = content_stream.ContentStream(content=types.UserContent('hello'))
  assert await stream.text() == 'hello'


@pytest.mark.asyncio
async def test_init_with_static_content_list():
  stream = content_stream.ContentStream(content=['hello', ' world'])
  assert await stream.text() == 'hello world'


@pytest.mark.asyncio
async def test_init_with_content_iterable():
  content = [types.UserContent('hello'), ' world']
  stream = content_stream.ContentStream(content=_to_async_iter(content))
  assert await stream.text() == 'hello world'


@pytest.mark.asyncio
async def test_init_with_content_iterator():
  content = [types.UserContent('hello'), ' world']
  stream = content_stream.ContentStream(
      content_iterator=_to_async_iter(content)
  )
  assert await stream.text() == 'hello world'

  # Attempting to read the content a second time should fail.
  with pytest.raises(RuntimeError):
    await stream.text()


@pytest.mark.asyncio
async def test_init_with_parts_iterable():
  parts_list = [types.Part(text='hello'), types.Part(text=' world')]
  stream = content_stream.ContentStream(parts=_to_async_iter(parts_list))
  assert await stream.text() == 'hello world'


@pytest.mark.asyncio
async def test_init_with_parts_iterator():
  parts_list = [types.Part(text='hello'), types.Part(text=' world')]
  stream = content_stream.ContentStream(
      parts_iterator=_to_async_iter(parts_list)
  )
  assert await stream.text() == 'hello world'

  # Attempting to read the content a second time should fail.
  with pytest.raises(RuntimeError):
    await stream.text()


def test_init_with_multiple_fail():
  with pytest.raises(ValueError):
    content_stream.ContentStream(content=[], parts=[])
  with pytest.raises(ValueError):
    content_stream.ContentStream(
        content_iterator=_to_async_iter([]), parts_iterator=_to_async_iter([])
    )


@pytest.mark.asyncio
async def test_text_with_inline_data():
  stream = content_stream.ContentStream(
      content=types.Part.from_bytes(mime_type='text/plain', data=b'hello')
  )
  assert await stream.text() == 'hello'


@pytest.mark.asyncio
async def test_text_with_non_text_part_fail():
  stream = content_stream.ContentStream(
      content=types.Part.from_bytes(mime_type='image/png', data=b'123')
  )
  with pytest.raises(ValueError):
    await stream.text()


@pytest.mark.asyncio
async def test_await():
  parts = []

  async def parts_generator():
    for i in range(3):
      parts.append(i)
      yield types.Part(text=str(i))

  await content_stream.ContentStream(parts_iterator=parts_generator())
  assert parts == [0, 1, 2]
