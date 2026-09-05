# tests/migrate/test_codemod.py
import os
import pathlib

import pytest

from google.genai._migrate.codemod import transform_source

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"
LEGACY_DIR = FIXTURES_DIR / "legacy"
EXPECTED_DIR = FIXTURES_DIR / "expected"


def get_legacy_files():
    return sorted(LEGACY_DIR.glob("*.py"))


@pytest.fixture
def update_expected():
    """Return True if UPDATE_EXPECTED=1 environment variable is set."""
    return os.environ.get("UPDATE_EXPECTED") == "1"


@pytest.mark.parametrize("legacy_file", get_legacy_files(), ids=lambda f: f.stem)
def test_migration(legacy_file, update_expected):
    """Test that migrating legacy code produces expected output."""
    legacy_src = legacy_file.read_text()
    expected_file = EXPECTED_DIR / legacy_file.name
    expected_src = expected_file.read_text()

    actual_src = transform_source(legacy_src)

    if update_expected:
        expected_file.write_text(actual_src)
        pytest.skip(f"Updated expected file: {expected_file}")
    else:
        assert actual_src == expected_src, (
            f"Migration output does not match expected for {legacy_file.name}\n"
            f"--- Actual ---\n{actual_src}\n"
            f"--- Expected ---\n{expected_src}"
        )


@pytest.mark.parametrize(
    "expected_file", sorted(EXPECTED_DIR.glob("*.py")), ids=lambda f: f.stem
)
def test_idempotent(expected_file):
    """Test that running transform_source on already-migrated code is a no-op."""
    src = expected_file.read_text()
    actual_src = transform_source(src)
    assert actual_src == src, (
        f"Codemod is not idempotent for {expected_file.name}\n"
        f"--- First pass ---\n{actual_src}\n"
        f"--- Original ---\n{src}"
    )
