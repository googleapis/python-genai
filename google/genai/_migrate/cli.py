"""CLI for google-generativeai -> google-genai migration."""

import argparse
import difflib
import sys
from pathlib import Path

from google.genai._migrate.codemod import transform_source


def collect_python_files(path: Path, include_tests: bool) -> list[Path]:
    """Collect .py files from path, optionally including test_*.py files."""
    files: list[Path] = []
    if path.is_file() and path.suffix == ".py":
        files.append(path)
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            if include_tests or not py_file.name.startswith("test_"):
                files.append(py_file)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="genai-migrate",
        description="Migrate google-generativeai code to google-genai.",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to migrate",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print unified diff to stdout, do not write files",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite files in place",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Also process test_*.py files (default: off)",
    )

    args = parser.parse_args()

    if not args.diff and not args.in_place:
        parser.error("Must specify either --diff or --in-place")

    target_path = args.path
    if not target_path.exists():
        parser.error(f"Path does not exist: {target_path}")

    files = collect_python_files(target_path, args.include_tests)
    if not files:
        print("No Python files found to process.")
        return 0

    total_files = len(files)
    changed_files = 0

    for file_path in files:
        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            continue

        new_source = transform_source(source)

        if new_source == source:
            continue

        changed_files += 1

        if args.diff:
            diff = difflib.unified_diff(
                source.splitlines(keepends=True),
                new_source.splitlines(keepends=True),
                fromfile=str(file_path),
                tofile=str(file_path),
            )
            sys.stdout.writelines(diff)
        elif args.in_place:
            try:
                file_path.write_text(new_source, encoding="utf-8")
            except Exception as e:
                print(f"Error writing {file_path}: {e}", file=sys.stderr)

    print(f"Processed {total_files} files, {changed_files} changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
