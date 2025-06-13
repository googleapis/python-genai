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


def test_repr_simple_model():
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
        id=2
        child=<... Circular reference ...>
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
      <... Circular reference ...>
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
  assert len(_common._pretty_repr(b_data, max_len=90)) < 100
  assert repr(b_data) == _common._pretty_repr(b_data, max_len=200)


def test_repr_max_depth():
  nested = [[[[[["deep"]]]]]]
  assert "<... Max depth ...>" in _common._pretty_repr(nested, depth=3)


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
        9
      ],
      'set': {
        1,
        2,
        3
      },
      'tuple': (
        4,
        5,
        6
      )
    }
    """).strip()
  assert _common._pretty_repr(obj) == expected


def test_repr_empty_collections():
  assert _common._pretty_repr([]) == "[]"
  assert _common._pretty_repr({}) == "{}"
  assert (
      _common._pretty_repr(set()) == "set()"
  )  # Note: Special case for empty set
  assert _common._pretty_repr(tuple()) == "()"
  # Fixed in the code to produce {} for empty sets in collections
  assert (
      _common._pretty_repr({"empty_set": set()}) ==
      textwrap.dedent("""
        {
          'empty_set': {}
        }
      """).strip()
  )


def test_repr_strings():
  s1 = "line one\\nline two"
  exp1 = "'line one\\nline two'"  # Stays as a single line repr
  assert _common._pretty_repr(s1) == exp1

  s2 = 'line one\\nline two with """ inside'
  exp2 = '"""line one\\nline two with \\"\\"\\" inside"""'
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
                )
              ],
              role='model'
            ),
            finish_reason=<FinishReason.STOP: 'STOP'>,
            index=0
          )
        ],
        model_version='models/gemini-2.5-flash-preview-05-20',
        usage_metadata=GenerateContentResponseUsageMetadata(
          candidates_token_count=1086,
          prompt_token_count=7,
          prompt_tokens_details=[
            ModalityTokenCount(
              modality=<MediaModality.TEXT: 'TEXT'>,
              token_count=7
            )
          ],
          thoughts_token_count=860,
          total_token_count=1953
        )
      )
  """).strip()
  assert repr(obj) == expected
