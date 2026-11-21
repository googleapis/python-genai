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

"""Tests that generate_content rejects iterator contents with a TypeError."""

from unittest import mock

import pytest

from ... import client
from ... import models
from ... import types

pytest_plugins = ('pytest_asyncio',)

_MODEL = 'gemini-2.5-flash'


@pytest.fixture
def mock_api_client():
  api_client = mock.MagicMock(spec=client.BaseApiClient)
  api_client.api_key = 'TEST_API_KEY'
  api_client._host = lambda: 'test_host'
  api_client._http_options = {'headers': {}}
  api_client.vertexai = False
  api_client._ws_connection = None
  setattr(api_client, '_async_ws_connection', None)
  api_client.tls_connection = None
  return api_client


def _contents():
  return [
      types.UserContent(parts=[types.Part(text='a')]),
      types.UserContent(parts=[types.Part(text='b')]),
  ]


def _reversed_contents():
  return reversed(_contents())


def _generator_contents():
  return (c for c in _contents())


_ITERATOR_CASES = [
    pytest.param(_reversed_contents, 'list_reverseiterator', id='reversed'),
    pytest.param(_generator_contents, 'generator', id='generator'),
]


def _response():
  return types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  role='model', parts=[types.Part(text='hello')]
              ),
              finish_reason=types.FinishReason.STOP,
          )
      ]
  )


@pytest.mark.parametrize('make_contents, type_name', _ITERATOR_CASES)
def test_generate_content_rejects_iterator_contents(
    mock_api_client, make_contents, type_name
):
  """An iterator fails with a TypeError before any request is built."""
  with mock.patch.object(models.Models, '_generate_content') as mock_generate:
    with pytest.raises(TypeError, match=r'list\(contents\)') as exc_info:
      models.Models(mock_api_client).generate_content(
          model=_MODEL, contents=make_contents()
      )
  assert type_name in str(exc_info.value)
  mock_generate.assert_not_called()


@pytest.mark.parametrize('make_contents, type_name', _ITERATOR_CASES)
def test_generate_content_stream_rejects_iterator_contents(
    mock_api_client, make_contents, type_name
):
  """The stream raises the TypeError on its first chunk."""
  with mock.patch.object(
      models.Models, '_generate_content_stream'
  ) as mock_generate:
    stream = models.Models(mock_api_client).generate_content_stream(
        model=_MODEL, contents=make_contents()
    )
    with pytest.raises(TypeError, match=r'list\(contents\)') as exc_info:
      next(stream)
  assert type_name in str(exc_info.value)
  mock_generate.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize('make_contents, type_name', _ITERATOR_CASES)
async def test_async_generate_content_rejects_iterator_contents(
    mock_api_client, make_contents, type_name
):
  """The async method raises the TypeError when awaited."""
  with mock.patch.object(
      models.AsyncModels, '_generate_content', new_callable=mock.AsyncMock
  ) as mock_generate:
    with pytest.raises(TypeError, match=r'list\(contents\)') as exc_info:
      await models.AsyncModels(mock_api_client).generate_content(
          model=_MODEL, contents=make_contents()
      )
  assert type_name in str(exc_info.value)
  mock_generate.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize('make_contents, type_name', _ITERATOR_CASES)
async def test_async_generate_content_stream_rejects_iterator_contents(
    mock_api_client, make_contents, type_name
):
  """The async stream method raises the TypeError when awaited."""
  with mock.patch.object(
      models.AsyncModels,
      '_generate_content_stream',
      new_callable=mock.AsyncMock,
  ) as mock_generate:
    with pytest.raises(TypeError, match=r'list\(contents\)') as exc_info:
      await models.AsyncModels(mock_api_client).generate_content_stream(
          model=_MODEL, contents=make_contents()
      )
  assert type_name in str(exc_info.value)
  mock_generate.assert_not_called()


def test_generate_content_single_part_still_works(mock_api_client):
  """A single Part is not an iterator and reaches the request unchanged."""
  part = types.Part(text='hi')
  with mock.patch.object(
      models.Models, '_generate_content', return_value=_response()
  ) as mock_generate:
    response = models.Models(mock_api_client).generate_content(
        model=_MODEL, contents=part
    )
  assert response.text == 'hello'
  mock_generate.assert_called_once()
  assert mock_generate.call_args.kwargs['contents'] == part


def test_generate_content_stream_single_part_still_works(mock_api_client):
  """A single Part streams normally."""
  part = types.Part(text='hi')
  with mock.patch.object(
      models.Models,
      '_generate_content_stream',
      return_value=iter([_response()]),
  ) as mock_generate:
    chunks = list(
        models.Models(mock_api_client).generate_content_stream(
            model=_MODEL, contents=part
        )
    )
  assert [chunk.text for chunk in chunks] == ['hello']
  mock_generate.assert_called_once()
  assert mock_generate.call_args.kwargs['contents'] == part


@pytest.mark.parametrize('container', [list, tuple], ids=['list', 'tuple'])
def test_generate_content_list_and_tuple_unchanged(mock_api_client, container):
  """Lists and tuples are not iterators and reach the request unchanged."""
  contents = container(_contents())
  with mock.patch.object(
      models.Models, '_generate_content', return_value=_response()
  ) as mock_generate:
    models.Models(mock_api_client).generate_content(
        model=_MODEL, contents=contents
    )
  mock_generate.assert_called_once()
  assert mock_generate.call_args.kwargs['contents'] == contents
