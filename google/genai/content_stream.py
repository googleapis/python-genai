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

"""Utilities for working with streams of genai.Part content."""

from collections.abc import AsyncIterable, AsyncIterator
from typing import Any, Callable, Generator, Generic, Optional, TypeVar, Union

from . import _transformers
from . import types


class ContentStream:
  """A syntax sugar mixin for streams of Content / Parts.

  Adapts whatever producer has to whatever consumer needs. Producer initializes
  ContentStream with an AsyncIterable or Collection of Content, Part or
  ContentListUnionDict. The consumer can iterate over the content in the stream
  or use accessor like .text() and reduce it to the given modality.

  Models and agents need to work with multimodal streaming content. Consuming
  such streams without ContentStream may look like:

    text = ''
    async for response in client.generate_content_stream(...)
      for content in response.candidates[0]:
        for part in content.parts:
          if not part.text:
            raise ValueError('Non text part received')
          text += part.text

  Many consumers would benefit from more constrained interfaces, such as "just
  return a string". But producers have to provide a generic interface to satisfy
  all clients. It works another way too: if consumer can deal with streaming
  multimodal content, it should be able to ingest unary text-only inputs.

  Whether ContentStream can be iterated over only once (like generator) or
  multiple times (like a list) depends on the specific implementation.
  It is strongly advised to allow reading content multiple times as this allows
  consumers to retry failures and tee response to multiple consumers. If the
  ContentStream is backed by a generator attempt to get content again (through
  any method) will raise a RuntimeError.

  Producers may chose to subclass ContentStream and provide additional methods.
  """

  def __init__(
      self,
      *,
      content: Union[
          types.ContentListUnionDict,
          AsyncIterable[types.ContentListUnionDict],
          None,
      ] = None,
      content_iterator: Optional[
          AsyncIterator[types.ContentListUnionDict]
      ] = None,
      parts: Optional[AsyncIterable[types.Part]] = None,
      parts_iterator: Optional[AsyncIterator[types.Part]] = None,
  ):
    """Initializes the stream.

    Only one of content_stream, parts_stream or content can be set.

    Args:
      content: Constructs the stream from a static content object or
        AsyncIterable of objects convertible to Content. It must allow iterating
        over it multiple times.
      content_iterator:  Same as `content`, but can be iterated only once.
        ContentStream will raise a RuntimeError on consecutive attempts. Use it
        if underlying iterable discards the content as soon as it is consumed.
      parts: An optimized version for the case when producer already yields Part
        objects.
      parts_iterator: Same as `parts`, but can be iterated only once.
        ContentStream will raise a RuntimeError on consecutive attempts. Use it
        if underlying iterable discards the content as soon as it is consumed.
    """
    if (
        sum(
            x is not None
            for x in [content, content_iterator, parts, parts_iterator]
        )
        > 1
    ):
      raise ValueError(
          'At most one of content, content_iterator, parts, parts_iterator can '
          'be provided.'
      )

    if content_iterator:
      content = _StreamOnce(content_iterator)
    if content:
      if isinstance(content, AsyncIterable):
        parts = _StreamContentIterable(content)
      else:
        # We have a static content object, use optimized implementation for it.
        parts = _StreamContent(content)

    if parts_iterator:
      parts = _StreamOnce(parts_iterator)

    if parts:
      self.parts: Callable[[], AsyncIterator[types.Part]] = parts.__aiter__  # type: ignore[method-assign]

  def parts(self) -> AsyncIterator[types.Part]:
    """Returns an iterator that yields all genai.Parts from the stream.

    Consecutive calls to this method return independent iterators that start
    from the beginning of the stream. If the stream can only be iterated once,
    a RuntimeError will be risen on the second attempt.
    """
    # This method is overriden in the __init__ depending on the source type and
    # is defined here to provide a good docstring.

    # Subclasses of ContentStream may also override this method directly.
    # Subclasses may also provide methods that return views of the original
    # ContentStream e.g. `.last_turn(self) -> ContentStream`
    raise NotImplementedError('ContentStream.parts is not implemented.')

  async def text(self) -> str:
    """Returns the stream contents as string.

    Returns:
      The text of the part.

    Raises:
      ValueError the underlying content contans non-text parts.
    """
    text_parts = []
    async for part in self.parts():
      if part.text is not None:
        text_parts.append(part.text)
      elif (
          part.inline_data is not None
          and part.inline_data.mime_type is not None
          and part.inline_data.mime_type.startswith('text/')
      ):
        if part.inline_data.data is None:
          raise ValueError('Invalid inline_data with None data encountered.')
        text_parts.append(part.inline_data.data.decode('utf-8'))
      else:
        raise ValueError(f'Part is not text: {part}')
    return ''.join(text_parts)

  async def content(self) -> list[types.Content]:
    """Returns all the contents of the stream as a list.

    Any consecutive Content objects with matching roles will be merged in-to one
    Content object. This way even if the producer streams its output (which it
    has to do in separate Content objects), the consumer can rely on "each item
    is a turn". Though note that in live bidirectional setups the notion of turn
    may be fuzzy or not defined.
    """
    # TODO(kibergus): To implement this we need part.part_metadata change to
    # reach production to represent roles in parts.
    raise NotImplementedError('CotentStream.content is not implemented yet.')

  def __await__(self) -> Generator[Any, None, None]:
    """Awaits until the stream is finished.

    Useful if we are not interested in the content itself, but in the side
    effect of the code that produces it.

    Returns:
      An awaitable that completes when the stream is finished.
    """

    async def await_parts() -> None:
      async for _ in self.parts():
        pass

    return await_parts().__await__()

  # More methods will be added here on as-needed basis. Candidates are:
  # async def get_dataclass(self, json_dataclass: type[T]) -> T:
  #   Interprets contents of the stream as JSON from which the json_dataclass
  #   can be instantiated. Works with models constrained with
  #   `response_schema=json_dataclass`. Also can be used to pass structured data
  #   between agents.
  #
  # async def pil_image(self) -> PIL.Image.Image:
  #   For gen-media models. Asserts that the output is a single image and
  #   returns it as PIL image.


class _StreamContent(AsyncIterable[types.Part]):
  """An AsyncIterable that yields all parts from a static Content."""

  def __init__(self, content: types.ContentListUnionDict):
    self._content: list[types.Content] = _transformers.t_contents(content)

  def __aiter__(self) -> AsyncIterator[types.Part]:
    async def yield_content() -> AsyncIterator[types.Part]:
      for content in self._content:
        if content.parts:
          for part in content.parts:
            yield part

    return yield_content()


class _StreamContentIterable(AsyncIterable[types.Part]):
  """An AsyncIterable that yields all parts from a stream of Content."""

  def __init__(self, content: AsyncIterable[types.ContentListUnionDict]):
    self._content = content

  def __aiter__(self) -> AsyncIterator[types.Part]:
    async def yield_content() -> AsyncIterator[types.Part]:
      async for content in self._content:
        contents = _transformers.t_contents(content)
        for content in contents:
          if content.parts:
            for part in content.parts:
              yield part

    return yield_content()


T = TypeVar('T')


class _StreamOnce(Generic[T]):
  """An AsyncIterable that can be iterated over only once."""

  def __init__(self, stream: AsyncIterator[T]):
    self._stream = stream
    self._exhausted = False

  def __aiter__(self) -> AsyncIterator[T]:
    if self._exhausted:
      raise RuntimeError(
          'This ContentStream is backed by an generator and can only be'
          ' iterated over once.'
      )
    self._exhausted = True
    return self._stream
