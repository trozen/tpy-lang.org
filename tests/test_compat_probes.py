"""Verify the Compatibility page's claims against the pinned compiler.

Every row of docs-site/src/compatibility.md is backed by a probe:

- Feature rows: one program each under tests/compat/. The first line is a
  directive:
      # expect: ok                      compiles cleanly (tpyc)
      # expect: error <substring>       tpyc must fail, message must match
      # expect: build-error             tpyc -b must fail (front end passes,
                                        the C++ build does not)
- Stdlib rows: import probes generated from the two module lists below,
  which mirror the page's "bundled" table and "notable absences" list.

Bumping vendor/tpy -> re-running this file -> updating the page's stamp is
part of the release ritual (see tests/README.md).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from docsnippets import _invoke, resolve_compiler_dir

COMPAT_DIR = Path(__file__).parent / "compat"
_COMPILER_DIR = resolve_compiler_dir()

PROBES = sorted(COMPAT_DIR.glob("*.py"))

# Mirrors the stdlib table on docs-site/src/compatibility.md.
STDLIB_BUNDLED = [
    "argparse", "asyncio", "base64", "bisect", "collections", "csv",
    "dataclasses", "datetime", "enum", "errno", "functools", "hashlib",
    "heapq", "http", "io", "itertools", "json", "math", "os", "random",
    "re", "signal", "socket", "ssl", "struct", "sys", "time", "typing",
    "urllib", "zoneinfo",
]
STDLIB_ABSENT = [
    "abc", "contextlib", "copy", "glob", "logging", "multiprocessing",
    "pathlib", "pickle", "secrets", "shutil", "sqlite3", "string",
    "subprocess", "tempfile", "textwrap", "threading", "unittest", "uuid",
]


@pytest.mark.parametrize("probe", PROBES, ids=[p.stem for p in PROBES])
def test_feature_probe(probe: Path, tmp_path: Path) -> None:
    first = probe.read_text().splitlines()[0]
    m = re.match(r"#\s*expect:\s*(ok|error|build-error)\s*(.*)", first)
    assert m, f"{probe.name}: first line must be an '# expect:' directive"
    kind, pattern = m.group(1), m.group(2).strip()
    args = ["-o", str(tmp_path / "out"), str(probe)]
    if kind == "build-error":
        args = ["-b", *args]
    r = _invoke(_COMPILER_DIR, "tpyc", args)
    combined = r.stdout + r.stderr
    if kind == "ok":
        assert r.returncode == 0, (
            f"{probe.name}: expected to compile cleanly\n{combined}"
        )
    else:
        assert r.returncode != 0, (
            f"{probe.name}: expected a failure, but it succeeded"
        )
        if pattern:
            assert pattern in combined, (
                f"{probe.name}: diagnostics did not contain {pattern!r}\n"
                f"{combined}"
            )


@pytest.mark.parametrize("module", STDLIB_BUNDLED)
def test_stdlib_bundled(module: str, tmp_path: Path) -> None:
    src = tmp_path / "probe.py"
    src.write_text(f"import {module}\n")
    r = _invoke(_COMPILER_DIR, "tpyc", ["-o", str(tmp_path / "out"), str(src)])
    assert r.returncode == 0, (
        f"'import {module}' failed but the page lists it as bundled:\n"
        f"{r.stdout}{r.stderr}"
    )


@pytest.mark.parametrize("module", STDLIB_ABSENT)
def test_stdlib_absent(module: str, tmp_path: Path) -> None:
    src = tmp_path / "probe.py"
    src.write_text(f"import {module}\n")
    r = _invoke(_COMPILER_DIR, "tpyc", ["-o", str(tmp_path / "out"), str(src)])
    assert r.returncode != 0, (
        f"'import {module}' succeeded but the page lists it as absent -- "
        f"update docs-site/src/compatibility.md"
    )
