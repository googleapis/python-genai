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

import warnings
import inspect
import logging
import typing

import pytest

from ... import _common
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
