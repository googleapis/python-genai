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
def client(use_vertex):
  if use_vertex:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, project='test-project', location='test-location'
    )
  else:
    yield google_genai_client_module.Client(
        vertexai=use_vertex, api_key='test-api-key'
    )


@pytest.mark.parametrize('use_vertex', [True, False])
def test_build_schema_for_list_of_pydantic_schema(client):
  """Tests _build_schema() when list[pydantic.BaseModel] is provided to response_schema."""

  list_schema = _transformers.t_schema(client, CountryInfo).model_dump()

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


@pytest.mark.parametrize('use_vertex', [True, False])
def test_build_schema_for_list_of_nested_pydantic_schema(client):
  """Tests _build_schema() when list[pydantic.BaseModel] is provided to response_schema and the pydantic.BaseModel has nested pydantic fields."""
  list_schema = _transformers.t_schema(
      client, CountryInfoWithCurrency
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


@pytest.mark.parametrize('use_vertex', [True, False])
def test_t_schema_for_pydantic_schema(client):
  """Tests t_schema when pydantic.BaseModel is passed to response_schema."""
  transformed_schema = _transformers.t_schema(client, CountryInfo)
  assert isinstance(transformed_schema, types.Schema)
  for schema_property in transformed_schema.properties:
    assert schema_property in country_info_fields
    assert isinstance(
        transformed_schema.properties[schema_property], types.Schema
    )


@pytest.mark.parametrize('use_vertex', [True, False])
def test_t_schema_for_list_of_pydantic_schema(client):
  """Tests t_schema when list[pydantic.BaseModel] is passed to response_schema."""
  transformed_schema = _transformers.t_schema(client, list[CountryInfo])
  assert isinstance(transformed_schema, types.Schema)
  assert isinstance(transformed_schema.items, types.Schema)

  for schema_property in transformed_schema.items.properties:
    assert schema_property in country_info_fields
    assert isinstance(
        transformed_schema.items.properties[schema_property], types.Schema
    )


@pytest.mark.parametrize('use_vertex', [True, False])
def test_t_schema_for_null_fields(client):
  """Tests t_schema when null fields are present."""
  transformed_schema = _transformers.t_schema(client, CountryInfoWithNullFields)
  assert isinstance(transformed_schema, types.Schema)
  assert transformed_schema.properties['population'].nullable


#@pytest.mark.parametrize('use_vertex', [True, False])
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
def test_schema_with_default_value(client):

  transformed_schema = _transformers.t_schema(
      client._api_client, CountryInfoWithDefaultValue
  )
  expected_schema = types.Schema(
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
      property_ordering=['name', 'population'],
  )

  assert transformed_schema == expected_schema


@pytest.mark.parametrize('use_vertex', [True, False])
def test_schema_with_any_of(client):
  transformed_schema = _transformers.t_schema(client, CountryInfoWithAnyOf)
  expected_schema = types.Schema(
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
      property_ordering=['name', 'restaurants_per_capita'],
  )

  assert transformed_schema == expected_schema


@pytest.mark.parametrize('use_vertex', [True, False])
def test_complex_dict_schema_with_anyof_is_unchanged(client):
  """When a dict schema is passed to process_schema, the only change should be camel-casing anyOf."""
  if client.vertexai:
    dict_schema = {
        'type': 'OBJECT',
        'title': 'Fruit Basket',
        'description': 'A structured representation of a fruit basket',
        'required': ['fruit'],
        'properties': {
            'fruit': {
                'type': 'ARRAY',
                'description': 'An ordered list of the fruit in the basket',
                'items': {
                    'description': 'A piece of fruit',
                    'anyOf': [
                        {
                            'title': 'Apple',
                            'description': 'Describes an apple',
                            'type': 'OBJECT',
                            'properties': {
                                'type': {
                                    'type': 'STRING',
                                    'description': "Always 'apple'",
                                },
                                'color': {
                                    'type': 'STRING',
                                    'description': (
                                        "The color of the apple (e.g., 'red')"
                                    ),
                                },
                            },
                            'propertyOrdering': ['type', 'color'],
                            'required': ['type', 'color'],
                        },
                        {
                            'title': 'Orange',
                            'description': 'Describes an orange',
                            'type': 'OBJECT',
                            'properties': {
                                'type': {
                                    'type': 'STRING',
                                    'description': "Always 'orange'",
                                },
                                'size': {
                                    'type': 'STRING',
                                    'description': (
                                        'The size of the orange (e.g.,'
                                        " 'medium')"
                                    ),
                                },
                            },
                            'propertyOrdering': ['type', 'size'],
                            'required': ['type', 'size'],
                        },
                    ],
                },
            }
        },
    }

    schema_before = copy.deepcopy(dict_schema)
    _transformers.process_schema(dict_schema, client)

    assert schema_before == dict_schema


@pytest.mark.parametrize('use_vertex', [True, False])
def test_process_schema_converts_const_to_enum(client):
  """The 'const' field should be converted to a singleton 'enum'."""
  schema = {
      'type': 'STRING',
      'const': 'FOO',
  }
  expected_schema = {
      'type': 'STRING',
      'enum': ['FOO'],
  }

  _transformers.process_schema(schema, client)

  assert schema == expected_schema


@pytest.mark.parametrize('use_vertex', [True, False])
def test_process_schema_forbids_non_string_const(client):
  """The 'const' field only works for strings."""
  schema = {
      'type': 'INTEGER',
      'const': 123,
  }

  with pytest.raises(ValueError, match='.*Literal values must be strings.*'):
    _transformers.process_schema(schema, client)


@pytest.mark.parametrize(
    'use_vertex,order_properties',
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_process_schema_order_properties_propagates_into_defs(
    client, order_properties
):
  """The `order_properties` setting should apply to '$defs'."""
  schema = {
      '$ref': '#/$defs/Foo',
      '$defs': {
          'Foo': {
              'type': 'OBJECT',
              'properties': {
                  'foo': {'type': 'STRING'},
                  'bar': {'type': 'STRING'},
              },
          },
      },
  }
  schema_without_property_ordering = {
      'type': 'OBJECT',
      'properties': {
          'foo': {'type': 'STRING'},
          'bar': {'type': 'STRING'},
      },
  }
  schema_with_property_ordering = {
      'type': 'OBJECT',
      'properties': {
          'foo': {'type': 'STRING'},
          'bar': {'type': 'STRING'},
      },
      'property_ordering': ['foo', 'bar'],
  }

  _transformers.process_schema(
      schema, client, order_properties=order_properties
  )

  if order_properties:
    assert schema == schema_with_property_ordering
  else:
    assert schema == schema_without_property_ordering


@pytest.mark.parametrize(
    'use_vertex,order_properties',
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_process_schema_order_properties_propagates_into_items(
    client, order_properties
):
  """The `order_properties` setting should apply to 'items'."""
  schema = {
      'type': 'ARRAY',
      'items': {
          'type': 'OBJECT',
          'properties': {
              'foo': {'type': 'STRING'},
              'bar': {'type': 'STRING'},
          },
      },
  }
  schema_without_property_ordering = copy.deepcopy(schema)
  schema_with_property_ordering = {
      'type': 'ARRAY',
      'items': {
          'type': 'OBJECT',
          'properties': {
              'foo': {'type': 'STRING'},
              'bar': {'type': 'STRING'},
          },
          'property_ordering': ['foo', 'bar'],
      },
  }

  _transformers.process_schema(
      schema, client, order_properties=order_properties
  )

  if order_properties:
    assert schema == schema_with_property_ordering
  else:
    assert schema == schema_without_property_ordering


@pytest.mark.parametrize(
    'use_vertex,order_properties',
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_process_schema_order_properties_propagates_into_prefix_items(
    client, order_properties
):
  """The `order_properties` setting should apply to 'prefixItems'."""
  schema = {
      'type': 'ARRAY',
      'prefixItems': [
          {
              'type': 'OBJECT',
              'properties': {
                  'foo': {'type': 'STRING'},
                  'bar': {'type': 'STRING'},
              },
          },
      ],
  }
  schema_without_property_ordering = copy.deepcopy(schema)
  schema_with_property_ordering = {
      'type': 'ARRAY',
      'prefixItems': [
          {
              'type': 'OBJECT',
              'properties': {
                  'foo': {'type': 'STRING'},
                  'bar': {'type': 'STRING'},
              },
              'property_ordering': ['foo', 'bar'],
          },
      ],
  }

  _transformers.process_schema(
      schema, client, order_properties=order_properties
  )

  if order_properties:
    assert schema == schema_with_property_ordering
  else:
    assert schema == schema_without_property_ordering


@pytest.mark.parametrize(
    'use_vertex,order_properties',
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_process_schema_order_properties_propagates_into_properties(
    client, order_properties
):
  """The `order_properties` setting should apply to 'properties'."""
  schema = {
      'type': 'OBJECT',
      'properties': {
          'xyz': {
              'type': 'OBJECT',
              'properties': {
                  'foo': {'type': 'STRING'},
                  'bar': {'type': 'STRING'},
              },
          },
          'abc': {'type': 'STRING'},
      },
  }
  schema_without_property_ordering = copy.deepcopy(schema)
  schema_with_property_ordering = {
      'type': 'OBJECT',
      'properties': {
          'xyz': {
              'type': 'OBJECT',
              'properties': {
                  'foo': {'type': 'STRING'},
                  'bar': {'type': 'STRING'},
              },
              'property_ordering': ['foo', 'bar'],
          },
          'abc': {'type': 'STRING'},
      },
      'property_ordering': ['xyz', 'abc'],
  }

  _transformers.process_schema(
      schema, client, order_properties=order_properties
  )

  if order_properties:
    assert schema == schema_with_property_ordering
  else:
    assert schema == schema_without_property_ordering


@pytest.mark.parametrize(
    'use_vertex,order_properties',
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_process_schema_order_properties_propagates_into_additional_properties(
    client, order_properties
):
  """The `order_properties` setting should apply to 'additionalProperties'."""
  schema = {
      'type': 'OBJECT',
      'additionalProperties': {
          'type': 'OBJECT',
          'properties': {
              'foo': {'type': 'STRING'},
              'bar': {'type': 'STRING'},
          },
      },
  }
  schema_without_property_ordering = copy.deepcopy(schema)
  schema_with_property_ordering = {
      'type': 'OBJECT',
      'additionalProperties': {
          'type': 'OBJECT',
          'properties': {
              'foo': {'type': 'STRING'},
              'bar': {'type': 'STRING'},
          },
          'property_ordering': ['foo', 'bar'],
      },
  }

  if client.vertexai:
    _transformers.process_schema(
        schema, client, order_properties=order_properties
    )

    if order_properties:
      assert schema == schema_with_property_ordering
    else:
      assert schema == schema_without_property_ordering
  else:
    with pytest.raises(ValueError) as e:
      _transformers.process_schema(
          schema, client, order_properties=order_properties
      )
    assert 'additionalProperties is not supported in the Gemini API.' in str(e)


@pytest.mark.parametrize(
    'use_vertex,order_properties',
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_process_schema_order_properties_propagates_into_any_of(
    client, order_properties
):
  """The `order_properties` setting should apply to 'anyOf'."""
  schema = {
      'anyOf': [
          {
              'type': 'OBJECT',
              'properties': {
                  'foo': {'type': 'STRING'},
                  'bar': {'type': 'STRING'},
              },
          },
          {'type': 'STRING'},
      ]
  }
  schema_without_property_ordering = copy.deepcopy(schema)
  schema_with_property_ordering = {
      'anyOf': [
          {
              'type': 'OBJECT',
              'properties': {
                  'foo': {'type': 'STRING'},
                  'bar': {'type': 'STRING'},
              },
              'property_ordering': ['foo', 'bar'],
          },
          {'type': 'STRING'},
      ]
  }

  _transformers.process_schema(
      schema, client, order_properties=order_properties
  )

  if order_properties:
    assert schema == schema_with_property_ordering
  else:
    assert schema == schema_without_property_ordering


@pytest.mark.parametrize('use_vertex', [True, False])
def test_t_schema_does_not_change_property_ordering_if_set(client):
  """Tests t_schema doesn't overwrite the property_ordering field if already set."""

  schema = CountryInfo.model_json_schema()
  custom_property_ordering = ['code', 'symbol', 'name']
  schema['property_ordering'] = custom_property_ordering.copy()

  transformed_schema = _transformers.t_schema(client, schema)
  assert transformed_schema.property_ordering == custom_property_ordering


@pytest.mark.parametrize('use_vertex', [True, False])
def test_t_schema_sets_property_ordering_for_json_schema(client):
  """Tests t_schema sets the property_ordering field for json schemas."""

  schema = CountryInfo.model_json_schema()

  transformed_schema = _transformers.t_schema(client, schema)
  assert transformed_schema.property_ordering == [
      'name',
      'population',
      'capital',
      'continent',
      'gdp',
      'official_language',
      'total_area_sq_mi',
  ]


@pytest.mark.parametrize('use_vertex', [True, False])
def test_t_schema_sets_property_ordering_for_schema_type(client):
  """Tests t_schema sets the property_ordering field for Schema types."""

  schema = types.Schema(
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

  transformed_schema = _transformers.t_schema(client, schema)
  assert transformed_schema.property_ordering == ['name', 'population']
