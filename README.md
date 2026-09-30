# tpy-lang.org

The marketing / landing site for **TurboPython**, served at
[tpy-lang.org](https://tpy-lang.org) via GitHub Pages. Static, no backend, no
build framework -- a single self-contained `index.html` plus generated example
data.

> **Status:** live at tpy-lang.org, not yet announced. The landing page links
> to the docs site (`/docs/`), the guide, and the compatibility page; no
> placeholder links remain.

## Files

The served site lives in `docs/` (what GitHub Pages publishes); the generator
sits at the repo root, outside the served folder. The example sources are not in
this repository at all -- they live in `trozen/tpy-examples`, vendored as a
submodule.

| Path | What |
|------|------|
| `docs/` | **The served site** -- GitHub Pages publishes this folder. |
| `docs/index.html` | The landing page -- inline CSS + JS, no dependencies. Loads `examples.js` via `<script src>`. |
| `docs/examples.js` | **Generated** into `docs/` by `build_examples.py`. A `const EXAMPLES = [...]` array (per example: `label`, `file`, raw `src`, highlighted `code`). Do not edit by hand. |
| `docs/docs/` | **Generated** docs site -- the `mkdocs build` output, served at `tpy-lang.org/docs/`. Do not edit by hand. |
| `docs/og.png` | **Generated** by `make og` from `og-card.html` -- the 1200x630 preview card that link unfurls (X, Slack, Discord, LinkedIn...) show for the landing page. Do not edit by hand. |
| `docs/robots.txt`, `docs/sitemap.xml` | Crawler hints for the landing page; the docs site has its own sitemap under `docs/docs/`. |
| `docs/CNAME` | The custom domain (`tpy-lang.org`). |
| `vendor/tpy-examples/` | **Submodule** (`trozen/tpy-examples`) -- the example gallery. `landing/` in it holds the programs shown on the landing page; `shedskin/` holds the larger ported programs the docs link to. |
| `build_examples.py` | Reads `vendor/tpy-examples/landing/`, highlights the programs, writes `docs/examples.js`. Pure stdlib -- no `tpy` needed to regenerate. |
| `verify_examples.py` | Compiles each example with whatever `tpy` is on PATH (runs the deterministic ones), failing on any that don't. `make check` runs it against the pinned `vendor/tpy`; the pre-announce gate in `CLAUDE.md` runs it against the published package. |
| `docs-site/` | Source for the docs site: `mkdocs.yml`, `src/` markdown, theme overrides, logo. Built with MkDocs Material into `docs/docs/`. |

## Docs site

The documentation at `tpy-lang.org/docs/` is built with **MkDocs + Material**.
Source lives in `docs-site/`; the build output is committed to `docs/docs/`
(same "commit the generated output" approach as `examples.js`). Rebuild after
editing any docs source:

```bash
cd docs-site
pip install -r requirements.txt        # first time: mkdocs-material
mkdocs serve                           # preview at http://127.0.0.1:8000
mkdocs build                           # writes ../docs/docs/  -- commit the result
```

**Rebuild before committing docs changes** -- `docs/docs/` is generated, so an
edit to `docs-site/` that isn't rebuilt leaves the served site stale.

## Examples pipeline

Each example on the site is a **real TurboPython program**, and the sources live
in the `tpy-examples` submodule under `vendor/tpy-examples/landing/`. The
dropdown order and display order come from the `ORDER` list in
`build_examples.py`, which is in this repo -- adding a file to the submodule
does not put it on the page.

Both scripts need the submodule checked out, and say so if it is missing:

```bash
git submodule update --init vendor/tpy-examples
```

Workflow when adding/editing an example:

1. Edit (or add) the `.py` under `vendor/tpy-examples/landing/`, and **commit it
   in that repository** -- it is a separate repo with its own history.
2. **Verify it compiles with tpy** (this is the bar -- examples must be real).
   `make check` compiles them all against the pinned `vendor/tpy` (runs the
   deterministic ones; fails on any that don't). Or check one by hand:
   - runnable ones: `diff <(python3 <f>.py) <(tpy <f>.py)` (CPython parity) or just `tpy <f>.py`.
   - tpy-only / network ones (ownership, requests): `tpy -b <f>.py` (compile + link).
3. Regenerate the data: `python3 build_examples.py`.
4. If you added a file, add it to `ORDER` in `build_examples.py`.
5. Commit the moved submodule pointer here, alongside the regenerated
   `docs/examples.js`. The pointer has to reference a commit that has been
   **pushed** to `tpy-examples`, or a fresh clone and the Pages build cannot
   resolve it.

Conventions:
- **Keep lines <= ~57 chars.** The code window is ~61 chars wide; longer lines
  scroll horizontally (ugly). `verify_examples.py` enforces the 61-char window
  (fails any example that exceeds it); aim for <=57 for a margin. The constraint
  is restated in `vendor/tpy-examples/landing/README.md`, since that is where
  someone editing the sources will be.
- Comments explain a concept at **showcase altitude**, not full docs -- the
  examples are a taste, the language guide is where things get taught.

## Local preview

```bash
xdg-open docs/index.html            # or: open / your browser
python3 -m http.server -d docs 8000 # -> http://localhost:8000
```

## Deployment

Served by **GitHub Pages** from the **`/docs` folder** of this repo's default
branch, at the custom domain **`tpy-lang.org`** (set via `docs/CNAME` + Pages
settings). Pushing to the default branch publishes, via
`.github/workflows/pages.yml`. HTTPS is provisioned by GitHub (Let's Encrypt).

That workflow uploads `docs/` itself rather than letting Pages build the
branch, because the default builder clones submodules and cannot fetch the
private `vendor/tpy` over SSH. It follows that **Pages must stay on
Settings > Pages > Source == "GitHub Actions"**; switching it back to
"Deploy from a branch" reinstates the failure.

DNS for the apex domain points at GitHub Pages (A/AAAA records at the registrar).

## Open threads

- **`http.server`:** no server module yet, so the async example builds HTTP on
  raw asyncio streams.
- **Playground:** deferred (would need client-side compile -- Pyodide + in-browser
  C++ -> WASM; big project, not near-term).
- **CI self-verify:** a workflow could `pip install tpy-lang`, run
  `verify_examples.py` (confirm every example still compiles) and
  `build_examples.py` (regenerate `examples.js`) before deploy.
