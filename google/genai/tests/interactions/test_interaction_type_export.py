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

"""Tests for Interaction export typing/runtime consistency (#2732)."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from ...interactions import Interaction
from ..._gaos.types.interactions.interaction import (
    Interaction as InteractionResource,
)
from ..._gaos.types.triggers.triggercreateparams import (
    Interaction as TriggerInteractionAlias,
)


def test_interactions_module_exports_resource_class_at_runtime():
    assert Interaction is InteractionResource
    assert Interaction is not TriggerInteractionAlias
    assert isinstance(Interaction, type)


def test_interactions_module_supports_isinstance_with_resource():
    class _Dummy:
        id = 'x'

    # Resource class is a real type usable with isinstance.
    assert not isinstance(_Dummy(), Interaction)


def test_trigger_interaction_alias_still_importable_from_triggers():
    from ..._gaos.types.triggers import Interaction as TriggersInteraction

    assert TriggersInteraction is TriggerInteractionAlias


def test_interactions_module_does_not_expose_trigger_interaction_param():
    import google.genai.interactions as interactions_mod

    assert getattr(interactions_mod, 'InteractionParam', None) is None
    assert interactions_mod.Interaction.__name__ == 'Interaction'
    assert interactions_mod.Interaction.__module__.endswith(
        'types.interactions.interaction'
    )


@pytest.mark.skipif(
    subprocess.run(
        [sys.executable, '-m', 'mypy', '--version'],
        capture_output=True,
        check=False,
    ).returncode
    != 0,
    reason='mypy is not installed',
)
def test_mypy_resolves_interaction_to_resource_class(tmp_path: Path):
    """Regression for #2732: mypy must not treat Interaction as TypeAliasType."""
    sample = tmp_path / 'check_interaction_export.py'
    sample.write_text(
        textwrap.dedent(
            '''\
            from google.genai.interactions import Interaction


            def check(x: object) -> None:
                if isinstance(x, Interaction):
                    print(x.id)
            '''
        ),
        encoding='utf-8',
    )

    repo_root = Path(__file__).resolve().parents[4]
    env = os.environ.copy()
    existing = env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = (
        str(repo_root) + (os.pathsep + existing if existing else '')
    )

    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'mypy',
            '--strict',
            '--follow-imports=silent',
            str(sample),
        ],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=env,
    )
    combined = (result.stdout or '') + (result.stderr or '')
    assert 'TypeAliasType' not in combined, combined
    assert result.returncode == 0, (
        'mypy failed to treat google.genai.interactions.Interaction as the '
        f'resource class.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}'
    )
