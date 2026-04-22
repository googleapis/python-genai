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


"""Tests tools in the _common module."""

from enum import Enum
import inspect
import logging
import textwrap
import typing
from typing import List, Optional
import warnings

import pydantic
import pytest

from ... import _common
from ... import types
from ... import errors


def test_warn_once():
  @_common.experimental_warning('Warning!')
  def func():
    pass

  with warnings.catch_warnings(record=True) as w:
    func()
    func()

  assert len(w) == 1
  assert w[0].category == errors.ExperimentalWarning

def test_warn_at_call_line():
  @_common.experimental_warning('Warning!')
  def func():
    pass

  with warnings.catch_warnings(record=True) as captured_warnings:
    call_line = inspect.currentframe().f_lineno + 1
    func()

  assert captured_warnings[0].lineno == call_line


def test_is_struct_type():
  assert _common._is_struct_type(list[dict[str, typing.Any]])
  assert _common._is_struct_type(typing.List[typing.Dict[str, typing.Any]])
  assert not _common._is_struct_type(list[dict[str, int]])
  assert not _common._is_struct_type(list[dict[int, typing.Any]])
  assert not _common._is_struct_type(list[str])
  assert not _common._is_struct_type(dict[str, typing.Any])
  assert not _common._is_struct_type(typing.List[typing.Dict[str, int]])
  assert not _common._is_struct_type(typing.List[typing.Dict[int, typing.Any]])
  assert not _common._is_struct_type(typing.List[str])
  assert not _common._is_struct_type(typing.Dict[str, typing.Any])



@pytest.mark.parametrize(
    "test_id, initial_target, update_dict, expected_target",
    [
        (
            "simple_update",
            {"a": 1, "b": 2},
            {"b": 3, "c": 4},
            {"a": 1, "b": 3, "c": 4},
        ),
        (
            "nested_update",
            {"a": 1, "b": {"x": 10, "y": 20}},
            {"b": {"y": 30, "z": 40}, "c": 3},
            {"a": 1, "b": {"x": 10, "y": 30, "z": 40}, "c": 3},
        ),
        (
            "add_new_nested_dict",
            {"a": 1},
            {"b": {"x": 10, "y": 20}},
            {"a": 1, "b": {"x": 10, "y": 20}},
        ),
        (
            "empty_target",
            {},
            {"a": 1, "b": {"x": 10}},
            {"a": 1, "b": {"x": 10}},
        ),
        (
            "empty_update",
            {"a": 1, "b": {"x": 10}},
            {},
            {"a": 1, "b": {"x": 10}},
        ),
        (
            "overwrite_non_dict_with_dict",
            {"a": 1, "b": 2},
            {"b": {"x": 10}},
            {"a": 1, "b": {"x": 10}},
        ),
        (
            "overwrite_dict_with_non_dict",
            {"a": 1, "b": {"x": 10}},
            {"b": 2},
            {"a": 1, "b": 2},
        ),
        (
            "deeper_nesting",
            {"a": {"b": {"c": 1, "d": 2}, "e": 3}},
            {"a": {"b": {"d": 4, "f": 5}, "g": 6}, "h": 7},
            {"a": {"b": {"c": 1, "d": 4, "f": 5}, "e": 3, "g": 6}, "h": 7},
        ),
        (
            "different_value_types",
            {"key1": "string_val", "key2": {"nested_int": 100}},
            {"key1": 123, "key2": {"nested_list": [1, 2, 3]}, "key3": True},
            {
                "key1": 123,
                "key2": {"nested_int": 100, "nested_list": [1, 2, 3]},
                "key3": True,
            },
        ),
        (
            "update_with_empty_nested_dict", # Existing nested dict in target should not be cleared
            {"a": {"b": 1}},
            {"a": {}},
            {"a": {"b": 1}},
        ),
        (
            "target_with_empty_nested_dict",
            {"a": {}},
            {"a": {"b": 1}},
            {"a": {"b": 1}},
        ),
        (
            "key_case_alignment_check",
            {"first_name": "John", "contact_info": {"email_address": "john@example.com"}},
            {"firstName": "Jane", "contact_info": {"email_address": "jane@example.com", "phone_number": "123"}},
            {"first_name": "Jane", "contact_info": {"email_address": "jane@example.com", "phone_number": "123"}},
        )
    ],
)
def test_recursive_dict_update(
    test_id: str, initial_target: dict, update_dict: dict, expected_target: dict
):
  _common.recursive_dict_update(initial_target, update_dict)
  assert initial_target == expected_target


@pytest.mark.parametrize(
    "test_id, initial_target, update_dict, expected_target, expect_warning, expected_log_message_part",
    [
        (
            "type_match_int",
            {"a": 1},
            {"a": 2},
            {"a": 2},
            False,
            "",
        ),
        (
            "type_match_dict",
            {"a": {"b": 1}},
            {"a": {"b": 2}},
            {"a": {"b": 2}},
            False,
            "",
        ),
        (
            "type_mismatch_int_to_str",
            {"a": 1},
            {"a": "hello"},
            {"a": "hello"},
            True,
            "Type mismatch for key 'a'. Existing type: <class 'int'>, new type: <class 'str'>. Overwriting.",
        ),
        (
            "type_mismatch_dict_to_int",
            {"a": {"b": 1}},
            {"a": 100},
            {"a": 100},
            True,
            "Type mismatch for key 'a'. Existing type: <class 'dict'>, new type: <class 'int'>. Overwriting.",
        ),
        (
            "type_mismatch_int_to_dict",
            {"a": 100},
            {"a": {"b": 1}},
            {"a": {"b": 1}},
            True,
            "Type mismatch for key 'a'. Existing type: <class 'int'>, new type: <class 'dict'>. Overwriting.",
        ),
        ("add_new_key", {"a": 1}, {"b": "new"}, {"a": 1, "b": "new"}, False, ""),
    ],
)
def test_recursive_dict_update_type_warnings(test_id, initial_target, update_dict, expected_target, expect_warning, expected_log_message_part, caplog):
    _common.recursive_dict_update(initial_target, update_dict)
    assert initial_target == expected_target
    if expect_warning:
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert expected_log_message_part in caplog.records[0].message
    else:
        for record in caplog.records:
            if record.levelname == "WARNING" and expected_log_message_part in record.message:
                 pytest.fail(f"Unexpected warning logged for {test_id}: {record.message}")


@pytest.mark.parametrize(
    "test_id, target_dict, update_dict, expected_aligned_dict",
    [
        (
            "simple_snake_to_camel",
            {"first_name": "John", "last_name": "Doe"},
            {"firstName": "Jane", "lastName": "Doe"},
            {"first_name": "Jane", "last_name": "Doe"},
        ),
        (
            "simple_camel_to_snake",
            {"firstName": "John", "lastName": "Doe"},
            {"first_name": "Jane", "last_name": "Doe"},
            {"firstName": "Jane", "lastName": "Doe"},
        ),
        (
            "nested_dict_alignment",
            {"user_info": {"contact_details": {"email_address": ""}}},
            {"userInfo": {"contactDetails": {"emailAddress": "test@example.com"}}},
            {"user_info": {"contact_details": {"email_address": "test@example.com"}}},
        ),
        (
            "list_of_dicts_alignment",
            {"users_list": [{"user_id": 0, "user_name": ""}]},
            {"usersList": [{"userId": 1, "userName": "Alice"}]},
            {"users_list": [{"userId": 1, "userName": "Alice"}]},
        ),
        (
            "list_of_dicts_alignment_mixed_case_in_update",
            {"users_list": [{"user_id": 0, "user_name": ""}]},
            {"usersList": [{"user_id": 1, "UserName": "Alice"}]},
            {"users_list": [{"user_id": 1, "UserName": "Alice"}]},
        ),
        (
            "list_of_dicts_different_lengths_update_longer",
            {"items_data": [{"item_id": 0}]},
            {"itemsData": [{"itemId": 1}, {"item_id": 2, "itemName": "Extra"}]},
            {"items_data": [{"itemId": 1}, {"item_id": 2, "itemName": "Extra"}]},
        ),
        (
            "list_of_dicts_different_lengths_target_longer",
            {"items_data": [{"item_id": 0, "item_name": ""}, {"item_id": 1}]},
            {"itemsData": [{"itemId": 10}]},
            {"items_data": [{"itemId": 10}]},
        ),
        (
            "no_matching_keys_preserves_update_case",
            {"key_one": 1},
            {"KEY_TWO": 2, "keyThree": 3},
            {"KEY_TWO": 2, "keyThree": 3},
        ),
        (
            "mixed_match_and_no_match",
            {"first_name": "John", "age_years": 30},
            {"firstName": "Jane", "AGE_YEARS": 28, "occupation_title": "Engineer"},
            {"first_name": "Jane", "age_years": 28, "occupation_title": "Engineer"},
        ),
        (
            "empty_target_dict",
            {},
            {"new_key": "new_value", "anotherKey": "anotherValue"},
            {"new_key": "new_value", "anotherKey": "anotherValue"},
        ),
        (
            "empty_update_dict",
            {"existing_key": "value"},
            {},
            {},
        ),
        (
            "target_has_non_dict_value_for_nested_key",
            {"config_settings": 123},
            {"configSettings": {"themeName": "dark"}},
            {"config_settings": {"themeName": "dark"}}, # Overwrites as per recursive_dict_update logic
        ),
        (
            "update_has_non_dict_value_for_nested_key",
            {"config_settings": {"theme_name": "light"}},
            {"configSettings": "dark_theme_string"},
            {"config_settings": "dark_theme_string"}, # Overwrites
        ),
         (
            "deeply_nested_with_lists",
            {"level_one": {"list_items": [{"item_name": "", "item_value": 0}]}},
            {"levelOne": {"listItems": [{"itemName": "Test", "itemValue": 100}, {"itemName": "Test2", "itemValue": 200}]}},
            {"level_one": {"list_items": [{"itemName": "Test", "itemValue": 100}, {"itemName": "Test2", "itemValue": 200}]}},
        ),
    ],
)
def test_align_key_case(
    test_id: str, target_dict: dict, update_dict: dict, expected_aligned_dict: dict
):
  aligned_dict = _common.align_key_case(target_dict, update_dict)
  assert aligned_dict == expected_aligned_dict, f"Test failed for: {test_id}"



class SimpleModel(_common.BaseModel):
  name: str
  value: int
  is_active: bool = True
  none_field: Optional[str] = None


class Chain(_common.BaseModel):
  id: int
  child: Optional["Chain"] = None


Chain.model_rebuild()


class Tree(_common.BaseModel):
  id: int
  children: List["Tree"] = pydantic.Field(default_factory=list)


Tree.model_rebuild()


class ReprFalseModel(_common.BaseModel):
  visible: str
  hidden: str = pydantic.Field("secret", repr=False)


class NonPydantic:

  def __repr__(self):
    return "NonPydantic(\n  attr='value'\n)"


class MyEnum(Enum):
  ONE = 1
  TWO = 2


class EmptyModel(_common.BaseModel):
  pass


def test_repr_simple_model_defaults_and_no_none():
  obj = SimpleModel(name="Test Name", value=123)
  expected = textwrap.dedent("""
    SimpleModel(
      is_active=True,
      name='Test Name',
      value=123
    )
    """).strip()
  assert repr(obj) == expected


def test_repr_empty_model():
  obj = EmptyModel()
  expected = "EmptyModel()"
  assert repr(obj) == expected


def test_repr_nested_model():
  obj = Chain(id=1, child=Chain(id=2))
  expected = textwrap.dedent("""
    Chain(
      child=Chain(
        id=2
      ),
      id=1
    )
    """).strip()
  assert repr(obj) == expected


def test_repr_circular_model():
  obj1 = Chain(id=1)
  obj2 = Chain(id=2)
  obj1.child = obj2
  obj2.child = obj1  # Circular reference
  expected = textwrap.dedent("""
    Chain(
      child=Chain(
        child=<... Circular reference ...>,
        id=2
      ),
      id=1
    )
    """).strip()

  assert repr(obj1) == expected


def test_repr_circular_list():
  my_list = [1, 2]
  my_list.append(my_list)
  expected = textwrap.dedent("""
    [
      1,
      2,
      <... Circular reference ...>,
    ]
    """).strip()
  assert _common._pretty_repr(my_list) == expected


def test_repr_circular_dict():
  my_dict = {"a": 1}
  my_dict["self"] = my_dict
  expected = textwrap.dedent("""
    {
      'a': 1,
      'self': <... Circular reference ...>
    }
    """).strip()
  assert _common._pretty_repr(my_dict) == expected


def test_repr_max_items():
  lst = list(range(10))
  dct = {i: i for i in range(10)}
  st = set(range(10))
  tpl = tuple(range(10))

  assert (
      "<... 5 more items ...>" in
      _common._pretty_repr(lst, max_items=5)
  )
  assert (
      "<dict len=10>" in _common._pretty_repr(dct, max_items=5))
  assert (
      "<... 5 more items ...>" in _common._pretty_repr(st, max_items=5)
  )
  assert (
      "<... 5 more items ...>" in _common._pretty_repr(tpl, max_items=5)
  )


def test_repr_max_len_bytes():
  b_data = b"a" * 100
  assert len(_common._pretty_repr(b_data, max_len=90)) == 90 + 3
  assert repr(b_data) == _common._pretty_repr(b_data, max_len=200)


def test_repr_max_depth_dict():
  nested = {'a': {'a': {'a': {'a': 'a', 'b': 'b'}}}}
  assert "{<... 2 items at Max depth ...>}" in _common._pretty_repr(nested, depth=3)


def test_repr_max_depth_list():
  nested = [[[["d", "e", "e", "p"]]]]
  assert "[<... 4 items at Max depth ...>]" in _common._pretty_repr(nested, depth=3)


def test_repr_collections():
  obj = {
      "set": {3, 1, 2},
      "tuple": (4, 5, 6),
      "dict": {"b": 2, "a": 1},
      "list": [7, 8, 9],
  }
  expected = textwrap.dedent("""
    {
      'dict': {
        'a': 1,
        'b': 2
      },
      'list': [
        7,
        8,
        9,
      ],
      'set': {
        1,
        2,
        3,
      },
      'tuple': (
        4,
        5,
        6,
      )
    }
    """).strip()
  assert _common._pretty_repr(obj) == expected


def test_tuple_collections():
  obj = {
      "tuple0": (),
      "tuple1": (1,),
      "tuple2": (1, 2),
  }
  expected = textwrap.dedent("""
    {
      'tuple0': (),
      'tuple1': (
        1,
      ),
      'tuple2': (
        1,
        2,
      )
    }
    """).strip()
  assert _common._pretty_repr(obj) == expected


def test_repr_empty_collections():
  assert _common._pretty_repr([]) == "[]"
  assert _common._pretty_repr({}) == "{}"
  assert (
      _common._pretty_repr(set()) == "set()"
  )
  assert _common._pretty_repr(tuple()) == "()"
  assert (
      _common._pretty_repr({"empty_set": set()}) ==
      textwrap.dedent("""
        {
          'empty_set': set()
        }
      """).strip()
  )


def test_repr_strings():
  s1 = "line one"
  exp1 = "'line one'"
  assert _common._pretty_repr(s1) == exp1

  s2 = 'line one\nline two with """ inside'
  exp2 = '"""line one\nline two with \\"\\"\\" inside"""'
  assert _common._pretty_repr(s2) == exp2

  s3 = 'A string with """ inside'
  exp3 = '\'A string with """ inside\''
  assert _common._pretty_repr(s3) == exp3


def test_repr_repr_false():
  obj = ReprFalseModel(visible="show", hidden="hide")
  result = repr(obj)
  assert "visible='show'" in result
  assert "hidden" not in result
  expected = textwrap.dedent("""
    ReprFalseModel(
      visible='show'
    )
    """).strip()
  assert result == expected


def test_repr_none_fields():
  obj = SimpleModel(name="Only Name", value=0, none_field=None)
  result = repr(obj)
  assert "none_field" not in result
  expected = textwrap.dedent("""
    SimpleModel(
      is_active=True,
      name='Only Name',
      value=0
    )
    """).strip()
  assert result == expected


def test_repr_other_types():
  np = NonPydantic()
  en = MyEnum.TWO
  obj = {"np": np, "en": en}
  expected = textwrap.dedent("""
    {
      'en': <MyEnum.TWO: 2>,
      'np': NonPydantic(
          attr='value'
        )
    }
    """).strip()
  assert _common._pretty_repr(obj) == expected


def test_repr_indent_delta():
  obj = SimpleModel(name="Indent Test", value=1)
  expected = textwrap.dedent("""
    SimpleModel(
        is_active=True,
        name='Indent Test',
        value=1
    )
    """).strip()
  assert _common._pretty_repr(obj, indent_delta=4) == expected


def test_repr_complex_object():
  obj = types.GenerateContentResponse(
      automatic_function_calling_history=[],
      candidates=[
          types.Candidate(
              content=types.Content(
                  parts=[
                      types.Part(
                          text="""There isn't a single "best" LLM, as the ideal choice highly depends on your specific needs, use case, budget, and priorities. The field is evolving incredibly fast, with new models and improvements being released constantly.

However, we can talk about the **leading contenders** and what they are generally known for:..."""
                      )
                  ],
                  role="model"
              ),
              finish_reason=types.FinishReason.STOP,
              index=0
          )
      ],
      model_version='models/gemini-2.5-flash-preview-05-20',
      usage_metadata=types.GenerateContentResponseUsageMetadata(
          candidates_token_count=1086,
          prompt_token_count=7,
          prompt_tokens_details=[
              types.ModalityTokenCount(
                  modality=types.MediaModality.TEXT,
                  token_count=7
              )
          ],
          thoughts_token_count=860,
          total_token_count=1953
      )
  )

  expected = textwrap.dedent("""
      GenerateContentResponse(
        automatic_function_calling_history=[],
        candidates=[
          Candidate(
            content=Content(
              parts=[
                Part(
                  text=\"\"\"There isn't a single "best" LLM, as the ideal choice highly depends on your specific needs, use case, budget, and priorities. The field is evolving incredibly fast, with new models and improvements being released constantly.

      However, we can talk about the **leading contenders** and what they are generally known for:...\"\"\"
                ),
              ],
              role='model'
            ),
            finish_reason=<FinishReason.STOP: 'STOP'>,
            index=0
          ),
        ],
        model_version='models/gemini-2.5-flash-preview-05-20',
        usage_metadata=GenerateContentResponseUsageMetadata(
          candidates_token_count=1086,
          prompt_token_count=7,
          prompt_tokens_details=[
            ModalityTokenCount(
              modality=<MediaModality.TEXT: 'TEXT'>,
              token_count=7
            ),
          ],
          thoughts_token_count=860,
          total_token_count=1953
        )
      )
  """).strip()
  assert repr(obj) == expected


def test_move_value_by_path():
  """Test move_value_by_path function with array wildcard notation."""
  data = {
      "requests": [
          {
              "request": {
                  "content": {
                      "parts": [
                          {
                              "text": "1"
                          }
                      ]
                  }
              },
              "outputDimensionality": 64
          },
          {
              "request": {
                  "content": {
                      "parts": [
                          {
                              "text": "2"
                          }
                      ]
                  }
              },
              "outputDimensionality": 64
          },
          {
              "request": {
                  "content": {
                      "parts": [
                          {
                              "text": "3"
                          }
                      ]
                  }
              },
              "outputDimensionality": 64
          }
      ]
  }

  paths = {'requests[].*': 'requests[].request.*'}
  _common.move_value_by_path(data, paths)

  expected = {
      "requests": [
          {
              "request": {
                  "content": {
                      "parts": [
                          {
                              "text": "1"
                          }
                      ]
                  },
                  "outputDimensionality": 64
              }
          },
          {
              "request": {
                  "content": {
                      "parts": [
                          {
                              "text": "2"
                          }
                      ]
                  },
                  "outputDimensionality": 64
              }
          },
          {
              "request": {
                  "content": {
                      "parts": [
                          {
                              "text": "3"
                          }
                      ]
                  },
                  "outputDimensionality": 64
              }
          }
      ]
  }

  assert data == expected


def test_check_field_type_mismatches_no_warning_for_correct_types(caplog):
  """Test that no warning is logged when types match."""

  class ModelA(_common.BaseModel):
    value: int

  class TestModel(_common.BaseModel):
    model_a: ModelA

  # Should not warn - dict will be converted to ModelA by Pydantic
  data = {"model_a": {"value": 123}}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    result = TestModel.model_validate(data)

  assert result.model_a.value == 123
  assert len(caplog.records) == 0


def test_check_field_type_mismatches_warns_on_pydantic_type_mismatch(caplog):
  """Test that warning is logged when Pydantic model types mismatch."""

  class ModelA(_common.BaseModel):
    value: int

  class ModelB(_common.BaseModel):
    value: str

  class TestModel(_common.BaseModel):
    model_field: ModelA

  # Create an instance of ModelB (wrong type)
  model_b_instance = ModelB(value="test")

  # Pass the wrong Pydantic model instance
  data = {"model_field": model_b_instance}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    TestModel._check_field_type_mismatches(data)

  assert len(caplog.records) == 1
  assert "Type mismatch in TestModel.model_field" in caplog.records[0].message
  assert "expected ModelA, got ModelB" in caplog.records[0].message


def test_check_field_type_mismatches_no_warning_for_none_values(caplog):
  """Test that no warning is logged for None values."""

  class ModelA(_common.BaseModel):
    value: int

  class TestModel(_common.BaseModel):
    model_field: Optional[ModelA] = None

  data = {"model_field": None}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    result = TestModel.model_validate(data)

  assert result.model_field is None
  assert len(caplog.records) == 0


def test_check_field_type_mismatches_no_warning_for_missing_fields(caplog):
  """Test that no warning is logged for missing fields."""

  class ModelA(_common.BaseModel):
    value: int

  class TestModel(_common.BaseModel):
    model_field: Optional[ModelA] = None

  data = {}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    result = TestModel.model_validate(data)

  assert result.model_field is None
  assert len(caplog.records) == 0


def test_check_field_type_mismatches_no_warning_for_primitive_types(caplog):
  """Test that no warning is logged for primitive type mismatches."""

  class TestModel(_common.BaseModel):
    int_field: int
    str_field: str

  # Even though we're passing wrong primitive types, we should not warn
  # (Pydantic will handle validation)
  data = {"int_field": "123", "str_field": "test"}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    # This will succeed because Pydantic can coerce "123" to int
    result = TestModel.model_validate(data)

  assert result.int_field == 123
  assert result.str_field == "test"
  assert len(caplog.records) == 0


def test_check_field_type_mismatches_handles_optional_unwrapping(caplog):
  """Test that Optional types are properly unwrapped before checking."""

  class ModelA(_common.BaseModel):
    value: int

  class ModelB(_common.BaseModel):
    value: str

  class TestModel(_common.BaseModel):
    model_field: Optional[ModelA] = None

  # Pass wrong Pydantic model type
  model_b_instance = ModelB(value="test")
  data = {"model_field": model_b_instance}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    TestModel._check_field_type_mismatches(data)

  assert len(caplog.records) == 1
  assert "expected ModelA, got ModelB" in caplog.records[0].message


def test_check_field_type_mismatches_no_warning_for_correct_pydantic_instance(caplog):
  """Test that no warning is logged when correct Pydantic instance is provided."""

  class ModelA(_common.BaseModel):
    value: int

  class TestModel(_common.BaseModel):
    model_field: ModelA

  # Pass correct Pydantic model instance
  model_a_instance = ModelA(value=42)
  data = {"model_field": model_a_instance}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    result = TestModel.model_validate(data)

  assert result.model_field.value == 42
  assert len(caplog.records) == 0


def test_check_field_type_mismatches_with_multiple_fields(caplog):
  """Test checking multiple fields with mixed scenarios."""

  class ModelA(_common.BaseModel):
    value: int

  class ModelB(_common.BaseModel):
    value: str

  class TestModel(_common.BaseModel):
    field_a: ModelA
    field_b: Optional[ModelA] = None
    field_c: str

  model_b_instance = ModelB(value="wrong")
  data = {
      "field_a": model_b_instance,  # Wrong type - should warn
      "field_b": None,  # None - should not warn
      "field_c": "test",  # Primitive - should not warn
  }

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    TestModel._check_field_type_mismatches(data)

  # Should only warn about field_a
  assert len(caplog.records) == 1
  assert "field_a" in caplog.records[0].message
  assert "expected ModelA, got ModelB" in caplog.records[0].message


def test_check_field_type_mismatches_generic_type_no_error(caplog):
  """Test that validation doesn't crash on generic types like list[str]."""
  class TestModel(_common.BaseModel):
    tags: list[str]

  data = {"tags": ["a", "b"]}

  with caplog.at_level(logging.WARNING, logger="google_genai._common"):
    TestModel.model_validate(data)

  assert len(caplog.records) == 0
