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


import logging
import pydantic

from ... import types


def _get_not_none_fields(model: pydantic.BaseModel) -> list[str]:
  """Returns field names in a Pydantic model whose values are not None."""
  return [
      field for field, value in model.model_dump().items() if value is not None
  ]


def test_empty_schema_conversion():
    """Test conversion of empty Schema to JSONSchema."""
    schema = types.Schema()
    json_schema = schema.json_schema
    not_none_field_names = _get_not_none_fields(json_schema)

    assert json_schema == types.JSONSchema()
    assert not_none_field_names == []


def test_not_null_type_conversion():
  """Test conversion of Schema.type to JSONSchema.type."""
  schema_types = [
      'OBJECT',
      'ARRAY',
      'STRING',
      'NUMBER',
      'BOOLEAN',
      'INTEGER',
  ]
  json_schema_types = [
      'object',
      'array',
      'string',
      'number',
      'boolean',
      'integer',
  ]
  for schema_type, expected_type in zip(schema_types, json_schema_types):
    schema = types.Schema(type=schema_type)
    json_schema = schema.json_schema
    not_none_field_names = _get_not_none_fields(json_schema)
    assert json_schema.type == types.JSONSchemaType(expected_type)
    assert not_none_field_names == ['type']


def test_unspecified_type_conversion():
  """Test conversion of Schema.type to JSONSchema.type."""
  schema = types.Schema(type='TYPE_UNSPECIFIED')
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.type is None
  assert not_none_field_names == []


def test_nullable_conversion():
  """Test conversion of Schema.nullable to JSONSchema.type."""
  schema = types.Schema(type='STRING', nullable=True)
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert set(json_schema.type) == set([
      types.JSONSchemaType('null'),
      types.JSONSchemaType('string')
  ])
  assert not_none_field_names == ['type']


def test_property_conversion():
  """Test conversion of Schema.properties to JSONSchema.properties."""
  schema = types.Schema(
      type='OBJECT',
      properties={
          'key1': types.Schema(type='STRING'),
          'key2': types.Schema(type='NUMBER'),
      },
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.properties == {
      'key1': types.JSONSchema(type=types.JSONSchemaType('string')),
      'key2': types.JSONSchema(type=types.JSONSchemaType('number')),
  }
  assert json_schema.type == types.JSONSchemaType('object')
  assert not_none_field_names == ['type', 'properties']


def test_complex_property_conversion():
  """Test conversion of complex Schema.properties to JSONSchema.properties."""
  schema = types.Schema(
      type='OBJECT',
      properties={
          'key1': types.Schema(
              type='OBJECT',
              properties={
                  'key2': types.Schema(type='STRING'),
                  'key3': types.Schema(type='NUMBER'),
              },
          ),
          'key2': types.Schema(type='ARRAY', items=types.Schema(type='STRING')),
      },
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.properties == {
      'key1': types.JSONSchema(
          type=types.JSONSchemaType('object'),
          properties={
              'key2': types.JSONSchema(type=types.JSONSchemaType('string')),
              'key3': types.JSONSchema(type=types.JSONSchemaType('number')),
          },
      ),
      'key2': types.JSONSchema(
          type=types.JSONSchemaType('array'),
          items=types.JSONSchema(type=types.JSONSchemaType('string')),
      ),
  }
  assert json_schema.type == types.JSONSchemaType('object')
  assert not_none_field_names == ['type', 'properties']


def test_items_conversion():
  """Test conversion of Schema.items to JSONSchema.items."""
  schema = types.Schema(
      type='ARRAY',
      items=types.Schema(type='STRING'),
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.type == types.JSONSchemaType('array')
  assert json_schema.items == types.JSONSchema(
      type=types.JSONSchemaType('string')
  )
  assert not_none_field_names == ['type', 'items']


def test_complex_items_conversion():
  """Test conversion of complex Schema.items to JSONSchema.items."""
  schema = types.Schema(
      type='ARRAY',
      items=types.Schema(
          type='OBJECT',
          properties={
              'key1': types.Schema(type='STRING'),
              'key2': types.Schema(type='NUMBER'),
          },
      ),
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.type == types.JSONSchemaType('array')
  assert json_schema.items == types.JSONSchema(
      type=types.JSONSchemaType('object'),
      properties={
          'key1': types.JSONSchema(type=types.JSONSchemaType('string')),
          'key2': types.JSONSchema(type=types.JSONSchemaType('number')),
      },
  )
  assert not_none_field_names == ['type', 'items']


def test_any_of_conversion():
  """Test conversion of Schema.any_of to JSONSchema.any_of."""
  schema = types.Schema(
      type='OBJECT',
      any_of=[
          types.Schema(type='STRING'),
          types.Schema(type='NUMBER'),
      ],
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.type == types.JSONSchemaType('object')
  assert json_schema.any_of == [
      types.JSONSchema(type=types.JSONSchemaType('string')),
      types.JSONSchema(type=types.JSONSchemaType('number')),
  ]
  assert not_none_field_names == ['type', 'any_of']


def test_complex_any_of_conversion():
  """Test conversion of complex Schema.any_of to JSONSchema.any_of."""
  schema = types.Schema(
      type='OBJECT',
      any_of=[
          types.Schema(
              type='OBJECT',
              properties={
                  'key1': types.Schema(type='STRING'),
                  'key2': types.Schema(type='NUMBER'),
              },
          ),
          types.Schema(type='ARRAY', items=types.Schema(type='STRING')),
      ],
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.type == types.JSONSchemaType('object')
  assert json_schema.any_of == [
      types.JSONSchema(
          type=types.JSONSchemaType('object'),
          properties={
              'key1': types.JSONSchema(type=types.JSONSchemaType('string')),
              'key2': types.JSONSchema(type=types.JSONSchemaType('number')),
          },
      ),
      types.JSONSchema(
          type=types.JSONSchemaType('array'),
          items=types.JSONSchema(type=types.JSONSchemaType('string')),
      ),
  ]
  assert not_none_field_names == ['type', 'any_of']


def test_example_conversion():
  """Test conversion of Schema.direct to JSONSchema.direct."""
  schema = types.Schema(
      example='this is an example',
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert not_none_field_names == []


def test_property_ordering_conversion():
  """Test conversion of Schema.property_ordering to JSONSchema.property_ordering."""
  schema = types.Schema(
      property_ordering=['a', 'b'],
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert not_none_field_names == []


def test_direct_conversion():
  """Test Schema fiedls that do not need to be converted."""
  schema = types.Schema(
      pattern='^[a-z]+$',
      default=1,
      max_length=10,
      title='title',
      min_length=2,
      min_properties=3,
      max_properties=7,
      description='description',
      enum=['enum1', 'enum2'],
      format='email',
      max_items=199,
      maximum=300,
      min_items=6,
      minimum=40,
      required=['required1', 'required2'],
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.pattern == '^[a-z]+$'
  assert json_schema.default == 1
  assert json_schema.max_length == 10
  assert json_schema.title == 'title'
  assert json_schema.min_length == 2
  assert json_schema.min_properties == 3
  assert json_schema.max_properties == 7
  assert json_schema.description == 'description'
  assert json_schema.enum == ['enum1', 'enum2']
  assert json_schema.format == 'email'
  assert json_schema.max_items == 199
  assert json_schema.maximum == 300
  assert json_schema.min_items == 6
  assert json_schema.minimum == 40
  assert json_schema.required == ['required1', 'required2']
  assert not_none_field_names.sort() == [
      'pattern',
      'default',
      'max_length',
      'title',
      'min_length',
      'min_properties',
      'max_properties',
      'description',
      'enum',
      'format',
      'max_items',
      'maximum',
      'min_items',
      'minimum',
      'required',
  ].sort()


def test_complex_any_of_conversion():
  schema = types.Schema(
      type=types.Type.OBJECT,
      title='Fruit Basket',
      description='A structured representation of a fruit basket',
      properties={
          'fruit': types.Schema(
              type=types.Type.ARRAY,
              description='An ordered list of the fruit in the basket',
              items=types.Schema(
                  any_of=[
                      types.Schema(
                          title='Apple',
                          description='Describes an apple',
                          type=types.Type.OBJECT,
                          properties={
                              'type': types.Schema(
                                  type=types.Type.STRING,
                                  description='Always "apple"',
                              ),
                              'variety': types.Schema(
                                  type=types.Type.STRING,
                                  description=(
                                      'The variety of apple (e.g., "Granny'
                                      ' Smith")'
                                  ),
                              ),
                          },
                          property_ordering=['type', 'variety'],
                          required=['type', 'variety'],
                      ),
                      types.Schema(
                          title='Orange',
                          description='Describes an orange',
                          type=types.Type.OBJECT,
                          properties={
                              'type': types.Schema(
                                  type=types.Type.STRING,
                                  description='Always "orange"',
                              ),
                              'variety': types.Schema(
                                  type=types.Type.STRING,
                                  description=(
                                      'The variety of orange (e.g.,"Navel'
                                      ' orange")'
                                  ),
                              ),
                          },
                          property_ordering=['type', 'variety'],
                          required=['type', 'variety'],
                      ),
                  ],
              ),
          ),
      },
      required=['fruit'],
  )
  json_schema = schema.json_schema
  not_none_field_names = _get_not_none_fields(json_schema)

  assert json_schema.type == types.JSONSchemaType('object')
  assert json_schema.title == 'Fruit Basket'
  assert json_schema.description == 'A structured representation of a fruit basket'
  assert json_schema.properties == {
      'fruit': types.JSONSchema(
          type=types.JSONSchemaType('array'),
          description='An ordered list of the fruit in the basket',
          items=types.JSONSchema(
              any_of=[
                  types.JSONSchema(
                      title='Apple',
                      description='Describes an apple',
                      type=types.JSONSchemaType('object'),
                      properties={
                          'type': types.JSONSchema(
                              type=types.JSONSchemaType('string'),
                              description='Always "apple"',
                          ),
                          'variety': types.JSONSchema(
                              type=types.JSONSchemaType('string'),
                              description=(
                                  'The variety of apple (e.g., "Granny'
                                  ' Smith")'
                              ),
                          ),
                      },
                      required=['type', 'variety'],
                  ),
                  types.JSONSchema(
                      title='Orange',
                      description='Describes an orange',
                      type=types.JSONSchemaType('object'),
                      properties={
                          'type': types.JSONSchema(
                              type=types.JSONSchemaType('string'),
                              description='Always "orange"',
                          ),
                          'variety': types.JSONSchema(
                              type=types.JSONSchemaType('string'),
                              description=(
                                  'The variety of orange (e.g.,"Navel orange")'
                              ),
                          ),
                      },
                      required=['type', 'variety'],
                  ),
              ],
          ),
      ),
  }
  assert json_schema.required == ['fruit']
  assert not_none_field_names == [
      'type',
      'title',
      'description',
      'properties',
      'required',
  ]


def test_json_schema_logs_only_once(caplog):
  """Test that the info message is logged only once across multiple json_schema calls."""
  from ... import types as types_module

  types_module._json_schema_warning_logged = False

  caplog.set_level(logging.INFO, logger='google_genai.types')

  schema1 = types_module.Schema(type='STRING')
  json_schema1 = schema1.json_schema

  assert len(caplog.records) == 1
  assert 'Json Schema is now supported natively' in caplog.text
  assert 'response_json_schema' in caplog.text

  schema2 = types_module.Schema(type='NUMBER')
  json_schema2 = schema2.json_schema

  assert len(caplog.records) == 1

  schema3 = types_module.Schema(type='OBJECT')
  json_schema3 = schema3.json_schema

  assert len(caplog.records) == 1

  assert json_schema1.type == types_module.JSONSchemaType('string')
  assert json_schema2.type == types_module.JSONSchemaType('number')
  assert json_schema3.type == types_module.JSONSchemaType('object')

  types_module._json_schema_warning_logged = False
