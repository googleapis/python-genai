# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
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


def test_empty_json_schema_conversion():
  """Test conversion of empty JSONSchema to Schema."""
  json_schema = types.JSONSchema()
  gemini_api_schema = types.Schema.from_json_schema(json_schema=json_schema)
  vertex_ai_schema = types.Schema.from_json_schema(
      json_schema=json_schema, api_option='VERTEX_AI'
  )

  assert gemini_api_schema == types.Schema()
  assert vertex_ai_schema == types.Schema()


def test_not_null_type_conversion():
  """Test conversion of JSONSchema.type to Schema.type"""
  json_schema_types = [
      'string',
      'number',
      'integer',
      'boolean',
      'array',
      'object',
  ]
  schema_types = [
      'STRING',
      'NUMBER',
      'INTEGER',
      'BOOLEAN',
      'ARRAY',
      'OBJECT',
  ]
  for json_schema_type, expected_type in zip(json_schema_types, schema_types):
    json_schema1 = types.JSONSchema(type=types.JSONSchemaType(json_schema_type))
    json_schema2 = types.JSONSchema(type=json_schema_type)
    gemini_api_schema1 = types.Schema.from_json_schema(json_schema=json_schema1)
    vertex_ai_schema1 = types.Schema.from_json_schema(
        json_schema=json_schema1, api_option='VERTEX_AI'
    )
    gemini_api_schema2 = types.Schema.from_json_schema(json_schema=json_schema2)
    vertex_ai_schema2 = types.Schema.from_json_schema(
        json_schema=json_schema2, api_option='VERTEX_AI'
    )

    gemini_api_not_none_field_name1 = _get_not_none_fields(gemini_api_schema1)
    vertex_api_not_none_field_name1 = _get_not_none_fields(vertex_ai_schema1)
    gemini_api_not_none_field_name2 = _get_not_none_fields(gemini_api_schema2)
    vertex_ai_not_none_field_name2 = _get_not_none_fields(vertex_ai_schema2)

    assert gemini_api_schema1.type == expected_type
    assert vertex_ai_schema1.type == expected_type
    assert gemini_api_schema2.type == expected_type
    assert vertex_ai_schema2.type == expected_type
    assert gemini_api_not_none_field_name1 == ['type']
    assert vertex_api_not_none_field_name1 == ['type']
    assert gemini_api_not_none_field_name2 == ['type']
    assert vertex_ai_not_none_field_name2 == ['type']


def test_nullable_conversion():
  """Test conversion of JSONSchema.nullable to Schema.nullable"""
  json_schema1 = types.JSONSchema(
      type=[types.JSONSchemaType('string'), types.JSONSchemaType('null')],
  )
  json_schema2 = types.JSONSchema(
      type=['string', 'null'],
  )
  gemini_api_schema1 = types.Schema.from_json_schema(json_schema=json_schema1)
  vertex_ai_schema1 = types.Schema.from_json_schema(
      json_schema=json_schema1, api_option='VERTEX_AI'
  )
  gemini_api_schema2 = types.Schema.from_json_schema(json_schema=json_schema2)
  vertex_ai_schema2 = types.Schema.from_json_schema(
      json_schema=json_schema2, api_option='VERTEX_AI'
  )
  gemini_api_not_none_field_names1 = _get_not_none_fields(gemini_api_schema1)
  vertex_ai_not_none_field_names1 = _get_not_none_fields(vertex_ai_schema1)
  gemini_api_not_none_field_names2 = _get_not_none_fields(gemini_api_schema2)
  vertex_ai_not_none_field_names2 = _get_not_none_fields(vertex_ai_schema2)

  assert gemini_api_schema1.nullable
  assert vertex_ai_schema1.nullable
  assert gemini_api_schema2.nullable
  assert vertex_ai_schema2.nullable
  assert set(gemini_api_not_none_field_names1) == set(['type', 'nullable'])
  assert set(vertex_ai_not_none_field_names1) == set(['type', 'nullable'])
  assert set(gemini_api_not_none_field_names2) == set(['type', 'nullable'])
  assert set(vertex_ai_not_none_field_names2) == set(['type', 'nullable'])


def test_nullable_in_union_like_type_conversion():
  """Test conversion of JSONSchema.nullable to Schema.nullable"""
  json_schema1 = types.JSONSchema(
      type=[
          types.JSONSchemaType('string'),
          types.JSONSchemaType('null'),
          types.JSONSchemaType('object'),
          types.JSONSchemaType('number'),
          types.JSONSchemaType('array'),
          types.JSONSchemaType('boolean'),
          types.JSONSchemaType('integer'),
      ],
  )
  gemini_api_schema1 = types.Schema.from_json_schema(json_schema=json_schema1)
  vertex_ai_schema1 = types.Schema.from_json_schema(
      json_schema=json_schema1, api_option='VERTEX_AI'
  )
  gemini_api_not_none_field_names1 = _get_not_none_fields(gemini_api_schema1)
  vertex_ai_not_none_field_names1 = _get_not_none_fields(vertex_ai_schema1)
  json_schema2 = types.JSONSchema(
      type=[
          'string',
          'null',
          'object',
          'number',
          'array',
          'boolean',
          'integer',
      ]
  )
  gemini_api_schema2 = types.Schema.from_json_schema(json_schema=json_schema2)
  vertex_ai_schema2 = types.Schema.from_json_schema(
      json_schema=json_schema2, api_option='VERTEX_AI'
  )
  expected_schema = types.Schema(
      nullable=True,
      any_of=[
          types.Schema(type='STRING'),
          types.Schema(type='OBJECT'),
          types.Schema(type='NUMBER'),
          types.Schema(type='ARRAY'),
          types.Schema(type='BOOLEAN'),
          types.Schema(type='INTEGER'),
      ],
  )

  assert gemini_api_schema1 == expected_schema
  assert vertex_ai_schema1 == expected_schema
  assert gemini_api_schema2 == expected_schema
  assert vertex_ai_schema2 == expected_schema


def test_union_like_type_conversion_suite1():
  """Test conversion of JSONSchema.type to Schema.any_of"""
  json_schema = types.JSONSchema(
      type=[
          types.JSONSchemaType('string'),
          types.JSONSchemaType('object'),
          types.JSONSchemaType('null'),
      ],
      description='description',
      default='default',
      max_length=10,
      min_length=5,
      enum=['value1', 'value2'],
      format='format',
      pattern='pattern',
      title='title',
      min_properties=1,
      max_properties=2,
      required=['field1', 'field2'],
      properties={
          'field1': types.JSONSchema(type='string'),
          'field2': types.JSONSchema(type='integer'),
      },
  )
  actual_gemini_api_schema = types.Schema.from_json_schema(
      json_schema=json_schema
  )
  actual_vertex_ai_schema = types.Schema.from_json_schema(
      json_schema=json_schema, api_option='VERTEX_AI'
  )
  expected_schema = types.Schema(
      nullable=True,
      any_of=[
          types.Schema(
              type='STRING',
              description='description',
              max_length=10,
              min_length=5,
              enum=['value1', 'value2'],
              format='format',
              pattern='pattern',
              title='title',
          ),
          types.Schema(
              type='OBJECT',
              properties={
                  'field1': types.Schema(type='STRING'),
                  'field2': types.Schema(type='INTEGER'),
              },
              required=['field1', 'field2'],
              min_properties=1,
              max_properties=2,
              title='title',
              description='description',
          ),
      ],
  )

  assert actual_gemini_api_schema == expected_schema
  assert actual_vertex_ai_schema == expected_schema


def test_union_like_type_conversion_suite2():
  """Test conversion of JSONSchema.type to Schema.any_of"""
  json_schema = types.JSONSchema(
      type=[
          types.JSONSchemaType('integer'),
          types.JSONSchemaType('array'),
      ],
      description='description',
      items=types.JSONSchema(type='integer', maximum=2, minimum=1),
      min_items=1,
      max_items=2,
      title='title',
      enum=['1', '2'],
      maximum=2,
      minimum=1,
  )
  actual_gemini_api_schema = types.Schema.from_json_schema(
      json_schema=json_schema
  )
  actual_vertex_ai_schema = types.Schema.from_json_schema(
      json_schema=json_schema, api_option='VERTEX_AI'
  )
  expected_schema = types.Schema(
      any_of=[
          types.Schema(
              type='INTEGER',
              description='description',
              maximum=2,
              minimum=1,
              enum=['1', '2'],
              title='title',
          ),
          types.Schema(
              type='ARRAY',
              items=types.Schema(type='INTEGER', maximum=2, minimum=1),
              min_items=1,
              max_items=2,
              title='title',
              description='description',
          ),
      ],
  )

  assert actual_gemini_api_schema == expected_schema
  assert actual_vertex_ai_schema == expected_schema


def test_array_type_conversion():
  """Test conversion of JSONSchema.items to Schema.items"""
  json_schema = types.JSONSchema(
      type=types.JSONSchemaType('array'),
      items=types.JSONSchema(
          type='object',
          properties={
              'field1': types.JSONSchema(type='string'),
              'field2': types.JSONSchema(type='integer'),
          },
          required=['field1', 'field2'],
          min_properties=1,
          max_properties=2,
          title='title',
          description='description',
      ),
  )
  gemini_api_schema = types.Schema.from_json_schema(json_schema=json_schema)
  vertex_ai_schema = types.Schema.from_json_schema(
      json_schema=json_schema, api_option='VERTEX_AI'
  )
  expected_schema = types.Schema(
      type='ARRAY',
      items=types.Schema(
          type='OBJECT',
          properties={
              'field1': types.Schema(type='STRING'),
              'field2': types.Schema(type='INTEGER'),
          },
          required=['field1', 'field2'],
          min_properties=1,
          max_properties=2,
          title='title',
          description='description',
      ),
  )

  assert gemini_api_schema == expected_schema
  assert vertex_ai_schema == expected_schema


def test_complex_object_type_conversion():
  """Test conversion of JSONSchema.properties to Schema.properties"""
  json_schema = types.JSONSchema(
      type=types.JSONSchemaType('object'),
      properties={
          'field1': types.JSONSchema(
              type=['string', 'array', 'null'],
              description='description1',
              max_length=20,
              min_length=15,
              enum=['value1', 'value2'],
              format='format',
              pattern='pattern',
              title='title1',
              items=types.JSONSchema(type='integer', maximum=2, minimum=1),
              min_items=1,
              max_items=2,
          ),
          'field2': types.JSONSchema(type='integer'),
      },
      required=['field1', 'field2'],
      min_properties=1,
      max_properties=2,
      title='title',
      description='description',
  )
  gemini_api_schema = types.Schema.from_json_schema(json_schema=json_schema)
  vertex_ai_schema = types.Schema.from_json_schema(
      json_schema=json_schema, api_option='VERTEX_AI'
  )
  expected_schema = types.Schema(
      type='OBJECT',
      properties={
          'field1': types.Schema(
              nullable=True,
              any_of=[
                  types.Schema(
                      type='STRING',
                      description='description1',
                      max_length=20,
                      min_length=15,
                      enum=['value1', 'value2'],
                      format='format',
                      pattern='pattern',
                      title='title1',
                  ),
                  types.Schema(
                      type='ARRAY',
                      items=types.Schema(type='INTEGER', maximum=2, minimum=1),
                      min_items=1,
                      max_items=2,
                      title='title1',
                      description='description1',
                  ),
              ],
          ),
          'field2': types.Schema(type='INTEGER'),
      },
      required=['field1', 'field2'],
      min_properties=1,
      max_properties=2,
      title='title',
      description='description',
  )

  assert gemini_api_schema == expected_schema
  assert vertex_ai_schema == expected_schema


def test_from_json_schema_logs_only_once(caplog):
  """Test that the info message is logged only once across multiple from_json_schema calls."""
  from ... import types as types_module

  types_module._from_json_schema_warning_logged = False

  caplog.set_level(logging.INFO, logger='google_genai.types')

  json_schema1 = types_module.JSONSchema(type='string')
  schema1 = types_module.Schema.from_json_schema(json_schema=json_schema1)

  assert len(caplog.records) == 1
  assert 'Json Schema is now supported natively' in caplog.text
  assert 'response_json_schema' in caplog.text

  json_schema2 = types_module.JSONSchema(type='number')
  schema2 = types_module.Schema.from_json_schema(json_schema=json_schema2)

  assert len(caplog.records) == 1

  json_schema3 = types_module.JSONSchema(type='object')
  schema3 = types_module.Schema.from_json_schema(json_schema=json_schema3)

  assert len(caplog.records) == 1

  assert schema1.type == types_module.Type('STRING')
  assert schema2.type == types_module.Type('NUMBER')
  assert schema3.type == types.Type('OBJECT')

  types_module._from_json_schema_warning_logged = False
