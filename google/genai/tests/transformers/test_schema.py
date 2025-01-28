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


"""Tests schema processing methods in the _transformers module."""

import enum
import copy
import pydantic

from typing import Union

from ... import _transformers
from ... import types


class CurrencyInfo(pydantic.BaseModel):
  name: str
  code: str
  symbol: str


currency_info_fields = CurrencyInfo.model_fields


class CountryInfo(pydantic.BaseModel):
  name: str
  population: int
  capital: str
  continent: str
  gdp: int
  official_language: str
  total_area_sq_mi: int


country_info_fields = CountryInfo.model_fields


class CountryInfoWithCurrency(pydantic.BaseModel):
  name: str
  population: int
  capital: str
  continent: str
  gdp: int
  official_language: str
  total_area_sq_mi: int
  currency: CurrencyInfo


nested_country_info_fields = CountryInfoWithCurrency.model_fields

class CountryInfoWithNullFields(pydantic.BaseModel):
  name: str
  population: Union[int, None] = None

def test_build_schema_for_list_of_pydantic_schema():
  """Tests _build_schema() when list[pydantic.BaseModel] is provided to response_schema."""

  list_schema = _transformers.t_schema(None, CountryInfo).model_dump()

  assert isinstance(list_schema, dict)

  for field_name in list_schema['properties']:
    assert 'title' in list_schema['properties'][field_name]
    assert 'type' in list_schema['properties'][field_name]
    assert field_name in country_info_fields
    field_type_str = country_info_fields[field_name].annotation.__name__
    assert list_schema['properties'][field_name]['type'].lower().startswith(
        field_type_str.lower()
    )
    assert 'required' in list_schema
    assert list_schema['required'] == list(country_info_fields.keys())


def test_build_schema_for_list_of_nested_pydantic_schema():
  """Tests _build_schema() when list[pydantic.BaseModel] is provided to response_schema and the pydantic.BaseModel has nested pydantic fields."""
  list_schema = _transformers.t_schema(None, CountryInfoWithCurrency).model_dump()

  assert isinstance(list_schema, dict)

  for field_name in list_schema['properties']:
    assert 'title' in list_schema['properties'][field_name]
    assert 'type' in list_schema['properties'][field_name]
    assert field_name in nested_country_info_fields

  # Tested nested schema was created
  assert 'properties' in list_schema['properties']['currency']

  for field_name in list_schema['properties']['currency']['properties']:
    assert field_name in currency_info_fields


def test_t_schema_for_pydantic_schema():
  """Tests t_schema when pydantic.BaseModel is passed to response_schema."""
  transformed_schema = _transformers.t_schema(None, CountryInfo)
  assert isinstance(transformed_schema, types.Schema)
  for schema_property in transformed_schema.properties:
    assert schema_property in country_info_fields
    assert isinstance(
        transformed_schema.properties[schema_property], types.Schema
    )
    
def test_t_schema_for_int():
  """Tests t_schema when pydantic.BaseModel is passed to response_schema."""
  transformed_schema = _transformers.t_schema(None, int)
  assert types.Schema(type=types.Type.INTEGER) == transformed_schema
  
def test_t_schema_for_list_of_int():
  """Tests t_schema when pydantic.BaseModel is passed to response_schema."""
  transformed_schema = _transformers.t_schema(None, list[int])

  assert types.Schema(
      type=types.Type.ARRAY,
      items=types.Schema(type=types.Type.INTEGER)
  ) == transformed_schema
  
def test_t_schema_for_enum():
  """Tests t_schema when pydantic.BaseModel is passed to response_schema."""
  class Choices(enum.Enum):
    CHOICE_1 = 'choice_1'
    CHOICE_2 = 'choice_2'

  transformed_schema = _transformers.t_schema(None, Choices)

  assert types.Schema(
      type=types.Type.STRING,
      title="Choices",
      enum=['choice_1', 'choice_2']) == transformed_schema



def test_t_schema_for_list_of_pydantic_schema():
  """Tests t_schema when list[pydantic.BaseModel] is passed to response_schema."""
  transformed_schema = _transformers.t_schema(None, list[CountryInfo])
  assert isinstance(transformed_schema, types.Schema)
  assert isinstance(transformed_schema.items, types.Schema)

  for schema_property in transformed_schema.items.properties:
    assert schema_property in country_info_fields
    assert isinstance(
        transformed_schema.items.properties[schema_property], types.Schema
    )


def test_t_schema_for_null_fields():
  """Tests t_schema when null fields are present."""
  transformed_schema = _transformers.t_schema(None, CountryInfoWithNullFields)
  assert isinstance(transformed_schema, types.Schema)
  assert transformed_schema.properties['population'].nullable


def test_schema_with_no_null_fields_is_unchanged():
  """Tests handle_null_fields() doesn't change anything when no null fields are present."""
  test_properties = {
      'name': {'title': 'Name', 'type': 'string'},
      'total_area_sq_mi': {
          'anyOf': [{'type': 'integer'}, {'type': 'float'}],
          'default': 'null',
          'title': 'Total Area Sq Mi',
      },
  }

  for name, schema in test_properties.items():
    schema_before = copy.deepcopy(schema)
    _transformers.handle_null_fields(schema)
    assert schema_before == schema
