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

"""Tests for invoking AFC functions defined under PEP 563 annotations."""

# !Please DO NOT combine the test in this file with other tests. This file is
# used to test the future annotation, which is the first line of import.
from __future__ import annotations

import typing
from typing import Annotated, Optional

import pydantic
import pytest

from ... import _extra_utils
from ... import errors
from ... import types

if typing.TYPE_CHECKING:
  from ...client import Client


class Location(pydantic.BaseModel):
  city: str


def _response_with_call(name: str, args: dict[str, object]):
  return types.GenerateContentResponse(
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          function_call=types.FunctionCall(name=name, args=args)
                      )
                  ]
              )
          )
      ]
  )


def test_invoke_builtin_primitive_types():
  """String annotations of builtin types resolve before the type check."""

  def get_weather(city: str, days: int = 3) -> str:
    return f'sunny in {city} for {days} days'

  result = _extra_utils.invoke_function_from_dict_args(
      {'city': 'Paris', 'days': 2}, get_weather
  )

  assert result == 'sunny in Paris for 2 days'


def test_get_function_response_parts_runs_tool():
  """The tool runs and its result, not a TypeError, goes to the model."""

  def get_weather(city: str) -> str:
    return f'sunny in {city}'

  parts = _extra_utils.get_function_response_parts(
      _response_with_call('get_weather', {'city': 'Paris'}),
      {'get_weather': get_weather},
  )

  assert parts[0].function_response.response == {'result': 'sunny in Paris'}


def test_invoke_pydantic_model_and_containers():
  """Pydantic models, lists of them and Optional resolve from strings."""

  def find(
      location: Location,
      locations: list[Location],
      days: Optional[int] = None,
  ) -> list[object]:
    return [location, locations, days]

  location, locations, days = _extra_utils.invoke_function_from_dict_args(
      {
          'location': {'city': 'Paris'},
          'locations': [{'city': 'Rome'}, {'city': 'Oslo'}],
          'days': 2,
      },
      find,
  )

  assert location == Location(city='Paris')
  assert locations == [Location(city='Rome'), Location(city='Oslo')]
  assert days == 2


def test_invoke_annotated_parameter():
  """An Annotated string annotation checks the value against its base type."""

  def forecast(days: Annotated[int, pydantic.Field(ge=1, le=7)] = 3) -> int:
    return days

  assert _extra_utils.invoke_function_from_dict_args({'days': 2}, forecast) == 2


def test_invoke_incompatible_value_raises():
  """A mismatched value raises the same error as with eager annotations."""

  def get_weather(city: str) -> str:
    return city

  with pytest.raises(
      errors.UnknownFunctionCallArgumentError, match='not compatible'
  ):
    _extra_utils.invoke_function_from_dict_args({'city': 1}, get_weather)


def test_invoke_unresolvable_hints_falls_back_to_raw_annotations():
  """A TYPE_CHECKING-only name does not raise NameError from the lookup."""

  def forecast(days: int = 3, client: Optional[Client] = None) -> int:
    del client
    return days

  assert _extra_utils.invoke_function_from_dict_args({}, forecast) == 3


@pytest.mark.asyncio
async def test_get_function_response_parts_async_runs_tool():
  """The async path runs a coroutine tool defined under PEP 563."""

  async def get_weather(city: str) -> str:
    return f'sunny in {city}'

  parts = await _extra_utils.get_function_response_parts_async(
      _response_with_call('get_weather', {'city': 'Paris'}),
      {'get_weather': get_weather},
  )

  assert parts[0].function_response.response == {'result': 'sunny in Paris'}
