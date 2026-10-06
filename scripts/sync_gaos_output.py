"""Syncs generated Speakeasy Python output to target _gaos directory and rewrites imports."""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import textwrap

PYTHON_LICENSE_HEADER = textwrap.dedent("""\
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
    # pyformat: disable
    # pylint: skip-file
    """)

_PY_ABSOLUTE_IMPORT_RE = re.compile(
    r"(?P<pre>(?:from|import)\s+)(?P<pkg>google\.genai(?:\.\w+)*)(?P<rest>\b)"
)


def _absolute_to_relative(
    match: re.Match[str], file_pkg: tuple[str, ...]
) -> str:
  pre = match.group("pre")
  pkg = match.group("pkg")
  rest = match.group("rest")

  sub = pkg[len("google.genai") :]
  if sub.startswith("."):
    sub = sub[1:]

  target_pkg = tuple(sub.split(".")) if sub else ()

  k = 0
  min_len = min(len(file_pkg), len(target_pkg))
  while k < min_len and file_pkg[k] == target_pkg[k]:
    k += 1

  up = len(file_pkg) - k
  down = target_pkg[k:]

  if up == 0:
    dots = "."
  else:
    dots = "." * (up + 1)

  if down:
    relative_module = dots + ".".join(down)
  else:
    relative_module = dots

  return f"{pre}{relative_module}{rest}"


def _apply_httpx2_fallback(output_dir: pathlib.Path) -> None:
  """Rewrites httpx imports to fall back to httpx2 (matching common.bara.sky)."""
  for py_file in sorted(output_dir.rglob("*.py")):
    text = py_file.read_text(encoding="utf-8")
    rewritten = text.replace(
        "\nimport httpx\n",
        "\ntry:\n    import httpx\nexcept ImportError:\n    import httpx2 as"
        " httpx\n",
    )
    rel_posix = py_file.relative_to(output_dir).as_posix()
    if rel_posix == "utils/headers.py":
      rewritten = rewritten.replace(
          "\nfrom httpx import Headers\n",
          "\ntry:\n    from httpx import Headers\nexcept ImportError:\n    from"
          " httpx2 import Headers\n",
      )
    elif rel_posix == "utils/values.py":
      rewritten = rewritten.replace(
          "\nfrom httpx import Response\n",
          "\ntry:\n    from httpx import Response\nexcept ImportError:\n   "
          " from httpx2 import Response\n",
      )
    if rewritten != text:
      py_file.write_text(rewritten, encoding="utf-8")


def sync_and_rewrite(
    input_dir: pathlib.Path,
    output_dir: pathlib.Path,
    httpx2_fallback: bool = False,
) -> None:
  if not input_dir.is_dir():
    raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

  output_dir.mkdir(parents=True, exist_ok=True)

  # Clear existing python and typed files in target, preserving hand-crafted files
  preserved_paths = {"google_genai.py", "live_interactions.py", "lib", "_hooks"}
  for p in output_dir.glob("**/*"):
    if p.is_file() and p.suffix in {".py", ".typed"}:
      rel_parts = p.relative_to(output_dir).parts
      if rel_parts[0] in preserved_paths:
        continue
      p.unlink()

  # Clean empty directories
  for p in sorted(output_dir.glob("**/*"), reverse=True):
    if p.is_dir() and not any(p.iterdir()):
      p.rmdir()

  # Copy all files from input_dir to output_dir
  for src_file in input_dir.rglob("*"):
    if not src_file.is_file():
      continue

    rel_path = src_file.relative_to(input_dir)
    dest_file = output_dir / rel_path
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    if src_file.suffix == ".py":
      content = src_file.read_text(encoding="utf-8")
      if not content.startswith("# Copyright"):
        content = PYTHON_LICENSE_HEADER + "\n" + content
      dest_file.write_text(content, encoding="utf-8")
    else:
      shutil.copy2(src_file, dest_file)

  # Rewrite absolute imports to relative
  rewritten_count = 0
  for py_file in sorted(output_dir.rglob("*.py")):
    rel = py_file.relative_to(output_dir)
    file_pkg = rel.parent.parts

    text = py_file.read_text(encoding="utf-8")
    rewritten = _PY_ABSOLUTE_IMPORT_RE.sub(
        lambda m, pkg=file_pkg: _absolute_to_relative(m, pkg), text
    )
    if rewritten != text:
      py_file.write_text(rewritten, encoding="utf-8")
      rewritten_count += 1

  if httpx2_fallback:
    _apply_httpx2_fallback(output_dir)

  print(
      f"Synced {len(list(output_dir.rglob('*.py')))} Python files"
      f" ({rewritten_count} imports rewritten)."
  )


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--input-dir",
      type=pathlib.Path,
      required=True,
      help="Input directory from generator",
  )
  parser.add_argument(
      "--output-dir",
      type=pathlib.Path,
      required=True,
      help="Target _gaos directory",
  )
  parser.add_argument(
      "--httpx2-fallback",
      action="store_true",
      help="Rewrite httpx imports to fall back to httpx2 (for GitHub repos).",
  )
  args = parser.parse_args()

  sync_and_rewrite(
      args.input_dir, args.output_dir, httpx2_fallback=args.httpx2_fallback
  )


if __name__ == "__main__":
  main()
