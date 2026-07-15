"""Refuse to run at all without a compiler to run against.

Every test here compiles something. With no checkout the suite has nothing to
verify, and skipping would report success having compiled nothing -- the one
outcome worse than a red run, since the whole point is that the site never
shows code that does not compile.

Erroring in pytest_configure gives one clear message instead of a wall of
failures from tests that cannot do their job. See tests/README.md for how to
provide a checkout.
"""
from __future__ import annotations

import pytest

from docsnippets import resolve_compiler_dir


def pytest_configure(config):
    if resolve_compiler_dir() is None:
        raise pytest.UsageError(
            "no TurboPython checkout found -- init the vendor/tpy submodule "
            "(`git submodule update --init vendor/tpy`), set $TPY_DIR, or "
            "place a sibling ../tpy-poc. See tests/README.md."
        )
