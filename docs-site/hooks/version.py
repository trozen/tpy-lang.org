"""Expose the TurboPython version the docs describe, for the header block.

Both values come from the pinned `vendor/tpy` submodule rather than being kept
by hand in mkdocs.yml, so they always name the compiler the snippets are
verified against and cannot drift when the pin moves. Together they reproduce
what `tpy --version` prints. See tests/README.md for the bump ritual.
"""

import pathlib
import re
import subprocess

_TPY = pathlib.Path(__file__).parents[2] / "vendor" / "tpy"
_INIT = _TPY / "tpyc" / "__init__.py"

_HINT = "run `git submodule update --init vendor/tpy`"


def _describe():
    """The commit half of `tpy --version`, via the command tpyc itself runs."""
    try:
        done = subprocess.run(
            ["git", "describe", "--always", "--dirty"],
            cwd=str(_TPY), capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def on_config(config):
    try:
        source = _INIT.read_text()
    except OSError as exc:
        raise SystemExit(f"docs build: cannot read {_INIT} ({exc}) -- {_HINT}")

    match = re.search(r'^__version__ = "([^"]+)"', source, re.MULTILINE)
    if not match:
        raise SystemExit(f"docs build: no __version__ found in {_INIT} -- {_HINT}")

    version = match.group(1)
    release = re.sub(r"\.dev\d+$", "", version)
    config.extra["tpy_version"] = version
    config.extra["tpy_release"] = release
    config.extra["tpy_prerelease"] = version != release
    # Absent outside a git checkout; the header omits the line rather than fails.
    commit = _describe()
    config.extra["tpy_commit"] = commit
    # The footer is the only spot Material shows at every width without an
    # override, so it carries the version for phones -- the header block it
    # lives in otherwise (md-header__source) is display:none below 60em. Hence
    # the full sentence: on a phone this stands alone, with no header block
    # beside it and, once released, no banner above it either.
    # Raw HTML: mkdocs builds its Jinja env without autoescape, and copyright
    # is rendered unescaped -- the span lets the version keep the footer's
    # regular tone while the prose around it recedes (see extra.css).
    named = f'<span class="tpy-version">TurboPython {version}</span>'
    described = f"{named} ({commit})" if commit else named
    config.copyright = f"These docs describe {described}."
    return config
