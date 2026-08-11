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

"""Guards the set of modules that ``import google.genai`` loads.

Import cost is invisible. An import accidentally added at module scope still
works, it only makes every program that touches the SDK start more slowly, so
nothing fails and nobody notices. These tests run the import in a fresh
interpreter and compare what it loaded against a checked-in allowlist.
"""

from __future__ import annotations

import functools
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from typing import Iterable

import pytest

_OPT_IN_ENV_VAR = 'GOOGLE_GENAI_IMPORT_TESTS'

_UPDATE_ENV_VAR = 'GOOGLE_GENAI_UPDATE_IMPORT_ALLOWLIST'

# The allowlist describes the published package layout, so these only run where
# that layout is what is on the path: the import workflow, or a developer who
# opts in from a source checkout. Asking for the allowlist to be regenerated is
# itself opting in, so that does not need both variables.
pytestmark = pytest.mark.skipif(
    os.getenv('GITHUB_ACTIONS') != 'true'
    and os.getenv(_OPT_IN_ENV_VAR) != '1'
    and not os.getenv(_UPDATE_ENV_VAR),
    reason=(
        'Checks the published package layout. Runs on GitHub Actions, or set'
        f' {_OPT_IN_ENV_VAR}=1.'
    ),
)

_ALLOWLIST_PATH = pathlib.Path(__file__).with_name('allowed_imports.txt')

_UPDATE_COMMAND = (
    f'{_UPDATE_ENV_VAR}=1 pytest'
    ' google/genai/tests/imports/test_imported_modules.py'
)

# Packages that importing the SDK must never pull in, whether or not they are
# installed. Each is reachable only from a feature the caller has to ask for:
# the MCP integration, and the local tokenizer. Naming them here, rather than
# relying on their absence from the allowlist, keeps the reason visible and
# gives a failure message that says what went wrong.
_MUST_NOT_LOAD = (
    'mcp',
    'sentencepiece',
    'torch',
    'transformers',
)

# Generated subtrees are pinned by their root only. There are hundreds of them
# and their individual names are not a contract.
_COLLAPSED = ('google.genai._gaos',)

# Names that cannot be pinned because they are not stable across machines or
# builds. The standard library's build configuration carries the platform
# triple, and mypyc-compiled and cython-compiled wheels ship helper modules
# named after a build hash.
_UNPINNABLE_PREFIXES = ('_sysconfigdata_', '_cython_')
_UNPINNABLE_SUFFIXES = ('__mypyc',)

_SNAPSHOT_SOURCE = """
import json
import sys

before = frozenset(sys.modules)
import google.genai  # noqa: F401
json.dump(sorted(frozenset(sys.modules) - before), sys.stdout)
"""


@functools.lru_cache(maxsize=None)
def _modules_loaded_by_import() -> frozenset[str]:
  """Returns the modules ``import google.genai`` adds to a fresh interpreter.

  A subprocess is the only honest way to measure this. The test session has
  already imported the SDK by the time any test runs, and an import cannot be
  undone: deleting entries from ``sys.modules`` leaves C extension state and
  class identities behind.
  """
  # .../google/genai/tests/imports/<this file> -> the directory holding the
  # ``google`` package. Prepending it puts the sources under test ahead of any
  # installed copy. Computed here rather than at module scope: other layouts
  # nest this file less deeply, and importing the module must not fail there.
  import_root = pathlib.Path(__file__).resolve().parents[4]
  env = dict(os.environ)
  env['PYTHONPATH'] = os.pathsep.join(
      part for part in (str(import_root), env.get('PYTHONPATH')) if part
  )
  # Run from an empty directory. The implicit ``sys.path[0]`` entry would
  # otherwise let this package's own ``types.py`` shadow the standard library.
  with tempfile.TemporaryDirectory() as empty_cwd:
    result = subprocess.run(
        [sys.executable, '-c', _SNAPSHOT_SOURCE],
        cwd=empty_cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
  if result.returncode != 0:
    pytest.fail(
        'Could not import google.genai in a fresh interpreter:\n'
        + result.stderr,
        pytrace=False,
    )
  return frozenset(json.loads(result.stdout))


def _tracked(module_names: Iterable[str]) -> frozenset[str]:
  """Reduces raw module names to the units the allowlist pins.

  Every ``google.genai`` submodule is pinned by name, because those are the
  ones this repository controls. Everything else is pinned by its top-level
  package only, because a library's internal module layout changes between
  releases and is not this repository's business. Standard library modules are
  ignored: which of them exist depends on the interpreter version, and
  importing them is close to free.

  Args:
    module_names: Raw module names, as they appear in ``sys.modules``.

  Returns:
    The names the allowlist pins, which is a much smaller set.
  """
  tracked = set()
  for name in module_names:
    parts = name.split('.')
    if parts[0] in sys.stdlib_module_names:
      continue
    if name == 'google':
      continue  # The namespace package itself, not a dependency.
    if name.startswith(_UNPINNABLE_PREFIXES) or name.endswith(
        _UNPINNABLE_SUFFIXES
    ):
      continue
    collapsed = next(
        (
            root
            for root in _COLLAPSED
            if name == root or name.startswith(root + '.')
        ),
        None,
    )
    if collapsed is not None:
      tracked.add(collapsed)
    elif name.startswith('google.genai'):
      tracked.add(name)
    elif parts[0] == 'google':
      tracked.add('.'.join(parts[:2]))
    else:
      tracked.add(parts[0])
  return frozenset(tracked)


def _read_allowlist() -> frozenset[str]:
  return frozenset(
      line.strip()
      for line in _ALLOWLIST_PATH.read_text().splitlines()
      if line.strip() and not line.startswith('#')
  )


def _write_allowlist(loaded: frozenset[str]) -> None:
  """Rewrites the allowlist from what this interpreter loaded."""
  names = set(loaded)
  if _ALLOWLIST_PATH.exists():
    # A third-party dependency can be conditional on the interpreter version,
    # so keep entries this interpreter did not happen to load. Regenerating on
    # a recent interpreter would otherwise drop the backports that older ones
    # still need. Only google.genai entries are dropped; those are the ratchet.
    names |= {
        name
        for name in _read_allowlist() - loaded
        if not name.startswith('google.genai')
    }
  header = f"""\
# Modules that `import google.genai` is allowed to load.
#
# Every google.genai submodule is listed by name, and that part has to match
# exactly. Everything else is listed by top-level package only and is a
# ceiling rather than a requirement, because some dependencies are conditional
# on the interpreter version. Standard library modules are not listed.
#
# Adding a line means importing the SDK got more expensive. Deleting lines is
# the goal.
#
# Regenerate after an intentional change:
#   {_UPDATE_COMMAND}
"""
  _ALLOWLIST_PATH.write_text(header + '\n'.join(sorted(names)) + '\n')


def test_import_does_not_load_optional_features() -> None:
  """Importing the SDK leaves the opt-in feature dependencies alone."""
  loaded = _modules_loaded_by_import()
  offenders = sorted(
      package
      for package in _MUST_NOT_LOAD
      if any(
          name == package or name.startswith(package + '.') for name in loaded
      )
  )
  if not offenders:
    return
  pytest.fail(
      '`import google.genai` now loads packages that belong to an opt-in'
      ' feature:\n'
      + '\n'.join(f'  {name}' for name in offenders)
      + '\n\nSomething in your change imports one of these while the SDK is'
      ' being imported, so everyone pays for a feature they may not use.'
      ' Move the import into the function that needs it, or behind the'
      ' module __getattr__.\n\nTo see what pulled it in:\n'
      "  python -X importtime -c 'import google.genai' 2>&1 | grep "
      f"'{offenders[0]}'",
      pytrace=False,
  )


def test_imported_modules_match_allowlist() -> None:
  """The import loads exactly the modules the allowlist permits."""
  loaded = _tracked(_modules_loaded_by_import())

  if os.environ.get(_UPDATE_ENV_VAR):
    _write_allowlist(loaded)
    pytest.skip(f'Rewrote {_ALLOWLIST_PATH.name} from this interpreter.')

  allowed = _read_allowlist()
  added = sorted(loaded - allowed)
  # Only google.genai removals are enforced. A third-party package that stops
  # being imported on one interpreter version is not a regression, but one of
  # our own modules dropping out is a win worth recording so it cannot quietly
  # come back.
  removed = sorted(
      name for name in allowed - loaded if name.startswith('google.genai')
  )

  if not added and not removed:
    return

  report = ['`import google.genai` no longer loads what the allowlist says.']
  if added:
    report += [
        '',
        f'{len(added)} module(s) are now loaded that were not before:',
        *(f'  + {name}' for name in added[:40]),
    ]
    if len(added) > 40:
      report.append(f'  ... and {len(added) - 40} more')
    report += [
        '',
        (
            'If you did not mean to make importing the SDK more expensive, find'
            ' the new module-scope import and move it into the function that'
            " needs it. `python -X importtime -c 'import google.genai'` shows"
            ' what pulled it in.'
        ),
    ]
  if removed:
    report += [
        '',
        f'{len(removed)} module(s) are no longer loaded:',
        *(f'  - {name}' for name in removed[:40]),
    ]
    if len(removed) > 40:
      report.append(f'  ... and {len(removed) - 40} more')
    report.append('')
    report.append('That is an improvement. Record it so it cannot regress.')
  report += [
      '',
      'Either way, update the allowlist and include it in your change:',
      f'  {_UPDATE_COMMAND}',
  ]
  pytest.fail('\n'.join(report), pytrace=False)
