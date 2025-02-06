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

import copy
from typing import Union

import pydantic
import pytest

from ... import _transformers
from ... import client as google_genai_client_module
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


class CountryInfoWithDefaultValue(pydantic.BaseModel):
  name: str
  population: int = 0


class CountryInfoWithAnyOf(pydantic.BaseModel):
  name: str
  restaurants_per_capita: Union[int, float]


@pytest.fixture
@pytest.mark.parametrize('use_vertex', [True, False])
def client(use_vertex):
  if use_vertex:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, project='test-project', location='test-location'
    )
  else:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, api_key='test-api-key'
    )


def test_build_schema_for_list_of_pydantic_schema():
  """Tests _build_schema() when list[pydantic.BaseModel] is provided to response_schema."""

  list_schema = _transformers.t_schema(None, CountryInfo).model_dump()

  assert isinstance(list_schema, dict)

  for field_name in list_schema['properties']:
    assert 'title' in list_schema['properties'][field_name]
    assert 'type' in list_schema['properties'][field_name]
    assert field_name in country_info_fields
    field_type_str = country_info_fields[field_name].annotation.__name__
    assert (
        list_schema['properties'][field_name]['type']
        .lower()
        .startswith(field_type_str.lower())
    )
    assert 'required' in list_schema
    assert list_schema['required'] == list(country_info_fields.keys())


def test_build_schema_for_list_of_nested_pydantic_schema():
  """Tests _build_schema() when list[pydantic.BaseModel] is provided to response_schema and the pydantic.BaseModel has nested pydantic fields."""
  list_schema = _transformers.t_schema(
      None, CountryInfoWithCurrency
  ).model_dump()

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

  for _, schema in test_properties.items():
    schema_before = copy.deepcopy(schema)
    _transformers.handle_null_fields(schema)
    assert schema_before == schema


@pytest.mark.parametrize('use_vertex', [True, False])
def test_schema_with_default_value_raises_for_mldev(client):

  if not client.vertexai:
    with pytest.raises(ValueError) as e:
      _transformers.t_schema(client._api_client, CountryInfoWithDefaultValue)
    assert 'Default value is not supported' in str(e)
  else:
    transformed_schema_vertex = _transformers.t_schema(
        client._api_client, CountryInfoWithDefaultValue
    )
    expected_schema_vertex = types.Schema(
        properties={
            'name': types.Schema(
                type='STRING',
                title='Name',
            ),
            'population': types.Schema(
                type='INTEGER',
                default=0,
                title='Population',
            ),
        },
        type='OBJECT',
        required=['name'],
        title='CountryInfoWithDefaultValue',
    )

    assert transformed_schema_vertex == expected_schema_vertex


@pytest.mark.parametrize('use_vertex', [True, False])
def test_schema_with_any_of_raises_for_mldev(client):
  if not client.vertexai:
    with pytest.raises(ValueError) as e:
      _transformers.t_schema(client._api_client, CountryInfoWithAnyOf)
    assert 'AnyOf is not supported' in str(e)
  else:
    transformed_schema_vertex = _transformers.t_schema(
        client._api_client, CountryInfoWithAnyOf
    )
    expected_schema_vertex = types.Schema(
        properties={
            'name': types.Schema(
                type='STRING',
                title='Name',
            ),
            'restaurants_per_capita': types.Schema(
                any_of=[
                    types.Schema(type='INTEGER'),
                    types.Schema(type='NUMBER'),
                ],
                title='Restaurants Per Capita',
            ),
        },
        type='OBJECT',
        required=['name', 'restaurants_per_capita'],
        title='CountryInfoWithAnyOf',
    )

    assert transformed_schema_vertex == expected_schema_vertex
