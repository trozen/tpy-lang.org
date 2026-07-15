"""Compile every docs code snippet against the pinned TurboPython compiler.

Run with:  pytest    (from the repo root)

Errors out if no compiler checkout is found (see tests/conftest.py) -- see
tests/README.md for how to point it at the `vendor/tpy` submodule (or a
sibling `../tpy-poc`).
"""
from __future__ import annotations

import pytest

from docsnippets import iter_all_snippets, resolve_compiler_dir, verify

_COMPILER_DIR = resolve_compiler_dir()
_SNIPPETS = iter_all_snippets()


@pytest.mark.parametrize("snippet", _SNIPPETS, ids=[s.ident for s in _SNIPPETS])
def test_snippet_compiles(snippet):
    if snippet.skip:
        pytest.skip("marked `skip`")
    verify(snippet, _COMPILER_DIR)


def test_found_some_snippets():
    # Guard against the extractor silently matching nothing (e.g. a fence-format
    # change) -- an empty corpus would make every run vacuously green.
    assert _SNIPPETS, "no verifiable code snippets found under docs-site/src/"
