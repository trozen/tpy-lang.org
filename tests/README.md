# Docs snippet verification

`pytest` compiles every ` ```python ` / ` ```tpy ` code block under
`docs-site/src/` against the TurboPython compiler, so a broken example fails
here instead of shipping. See the module docstring in `docsnippets.py` for the
directive tags (`run`, `expect-error`, `fragment`, `skip`).

## Pointing it at a compiler

The harness looks for a compiler checkout in this order:

1. `$TPY_DIR` -- an explicit path to a TurboPython checkout.
2. `vendor/tpy` -- the pinned submodule (recommended; reproducible).
3. `../tpy-poc` -- a sibling working checkout (dev convenience).

If none is found, the run errors out rather than skipping: every test here
compiles something, so with no compiler the suite would report success having
verified nothing.

### One-time submodule setup (recommended)

The compiler lives in the private repo `trozen/tpy-lang`. Add it as a pinned
submodule (needs SSH access to the private repo):

```bash
git submodule add git@github.com:trozen/tpy-lang.git vendor/tpy
git submodule update --init vendor/tpy
```

Pin it to the release the docs target, then stage the pin:

```bash
git -C vendor/tpy checkout <commit-or-tag>
git add vendor/tpy .gitmodules
```

Bumping `vendor/tpy` to a newer commit -> re-run `pytest` -> update the
"Status as of 0.5.0.devN" stamp is the release ritual.

## Running

```bash
make test                       # all snippets (uv bootstraps pytest itself)
uv run pytest -k ownership      # one page
TPY_DIR=/path/to/tpy uv run pytest
```

Snippets compile fast by default (front-end only, `tpyc`). Blocks marked
`<!-- tpy: run -->` also build and run, which is slower.

`tests/compat/` holds the probe programs behind every row of the
Compatibility page (`docs-site/src/compatibility.md`); `test_compat_probes.py`
compiles each one and import-checks the stdlib tables. Re-running it and
updating the page's "Status as of" stamp is part of the vendor-bump
ritual above.
