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

"""Offline checks that the README examples still match the public SDK.

Running the README needs credentials and network access, so these tests only
parse its Python blocks (and the copy in docs/source/index.rst) and check, with
no API call, that every `types.X(...)` and `types.X.method(...)` call is valid
for the installed SDK: the name exists, keyword arguments are model fields, and
method calls bind to the real signature.
"""

import ast
import inspect
import pathlib
import re
import textwrap
from typing import Any, Callable
import unittest

import pydantic

from ... import types

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_MARKDOWN_PYTHON_BLOCK = re.compile(r'```python\n(.*?)```', re.DOTALL)
# An indented reStructuredText block: blank lines or lines with 4+ spaces.
_RST_PYTHON_BLOCK = re.compile(
    r'^\.\. code:: python\n\n((?:(?:[ ]{4}.*)?\n)+)', re.MULTILINE
)


def _markdown_blocks(text: str) -> list[str]:
  return _MARKDOWN_PYTHON_BLOCK.findall(text)


def _rst_blocks(text: str) -> list[str]:
  return [textwrap.dedent(b) for b in _RST_PYTHON_BLOCK.findall(text)]


def _types_path(func: ast.expr) -> tuple[str, ...]:
  """Returns ('Video', 'from_file') for `types.Video.from_file`, else ()."""
  names = []
  while isinstance(func, ast.Attribute):
    names.append(func.attr)
    func = func.value
  if isinstance(func, ast.Name) and func.id == 'types' and names:
    return tuple(reversed(names))
  return ()


def _check_call(name: str, obj: Any, node: ast.Call) -> list[str]:
  if inspect.isclass(obj) and issubclass(obj, pydantic.BaseModel):
    fields = set(obj.model_fields)
    fields.update(f.alias for f in obj.model_fields.values() if f.alias)
    return [
        f'{name}() has no field {kw.arg!r}'
        for kw in node.keywords
        if kw.arg not in fields
    ]
  if not callable(obj):
    return []
  try:
    signature = inspect.signature(obj)
  except (TypeError, ValueError):
    return []
  try:
    signature.bind(
        *[None] * len(node.args), **{kw.arg: None for kw in node.keywords}
    )
  except TypeError as e:
    return [f'{name}(): {e}']
  return []


def _find_problems(source: str) -> tuple[int, list[str]]:
  """Returns (number of calls checked, problems found) for one code block."""
  try:
    tree = ast.parse(source)
  except SyntaxError:
    return 0, []  # Fragments such as a bare list of contents cannot be parsed.
  checked = 0
  problems = []
  for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
      continue
    if any(isinstance(a, ast.Starred) for a in node.args) or any(
        kw.arg is None for kw in node.keywords
    ):
      continue
    path = _types_path(node.func)
    if not path:
      continue
    name = '.'.join(('types',) + path)
    obj: Any = types
    for attribute in path:
      obj = getattr(obj, attribute, None)
      if obj is None:
        problems.append(f'{name} does not exist')
        break
    else:
      checked += 1
      problems.extend(_check_call(name, obj, node))
  return checked, problems


class ReadmeExamplesTest(unittest.TestCase):

  def _assert_examples_match_sdk(
      self, relative_path: str, extract: Callable[[str], list[str]]
  ) -> None:
    path = _REPO_ROOT / relative_path
    if not path.is_file():
      self.skipTest(f'{relative_path} is not part of this checkout.')
    checked = 0
    problems = []
    for block in extract(path.read_text(encoding='utf-8')):
      block_checked, block_problems = _find_problems(block)
      checked += block_checked
      problems.extend(block_problems)
    self.assertGreater(checked, 0, f'No examples found in {relative_path}.')
    self.assertEqual(problems, [], f'Stale examples in {relative_path}.')

  def test_readme_examples_match_sdk(self):
    self._assert_examples_match_sdk('README.md', _markdown_blocks)

  def test_docs_index_examples_match_sdk(self):
    self._assert_examples_match_sdk('docs/source/index.rst', _rst_blocks)

  def test_accepts_valid_calls(self):
    source = (
        'types.Video.from_file(location="a.mp4")\n'
        'types.Part.from_text(text="hi")\n'
        'types.GenerateContentConfig(temperature=0.1)\n'
    )
    self.assertEqual(_find_problems(source), (3, []))

  def test_flags_positional_argument_to_keyword_only_classmethod(self):
    _, problems = _find_problems('types.Video.from_file("a.mp4")')
    self.assertEqual(len(problems), 1)
    self.assertIn('types.Video.from_file', problems[0])

  def test_flags_unknown_model_field(self):
    _, problems = _find_problems('types.GenerateContentConfig(no_such_field=1)')
    self.assertEqual(
        problems, ["types.GenerateContentConfig() has no field 'no_such_field'"]
    )

  def test_flags_unknown_type(self):
    _, problems = _find_problems('types.NoSuchType(x=1)')
    self.assertEqual(problems, ['types.NoSuchType does not exist'])

  def test_skips_fragments_that_do_not_parse(self):
    self.assertEqual(_find_problems('[\n  types.Part(text="a"),\n'), (0, []))

  def test_extracts_rst_code_blocks(self):
    text = (
        'Title\n=====\n\n.. code:: python\n\n    x = types.Part()\n\n'
        '    y = 1\n\nNot code.\n'
    )
    self.assertEqual(_rst_blocks(text), ['x = types.Part()\n\ny = 1\n\n'])


if __name__ == '__main__':
  unittest.main()
