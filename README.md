# tpy-lang.org

The marketing / landing site for **TurboPython**, served at
[tpy-lang.org](https://tpy-lang.org) via GitHub Pages. Static, no backend, no
build framework -- a single self-contained `index.html` plus generated example
data.

> **Status:** work in progress, not yet advertised. The full single-page layout
> is in shape (nav, "early development" banner, hero with the example switcher,
> install, the "vs Python" / ownership section, footer). Links to pages that
> don't exist yet (Docs, the guide, a compatibility page) are placeholders that
> pop a "coming soon" toast (class `soon` in `index.html`).

## Files

The served site lives in `docs/` (what GitHub Pages publishes); the example
sources and the generator sit at the repo root, outside the served folder.

| Path | What |
|------|------|
| `docs/` | **The served site** -- GitHub Pages publishes this folder. |
| `docs/index.html` | The landing page -- inline CSS + JS, no dependencies. Loads `examples.js` via `<script src>`. |
| `docs/examples.js` | **Generated** into `docs/` by `build_examples.py`. A `const EXAMPLES = [...]` array (per example: `label`, `file`, raw `src`, highlighted `code`). Do not edit by hand. |
| `docs/docs/` | **Generated** docs site -- the `mkdocs build` output, served at `tpy-lang.org/docs/`. Do not edit by hand. |
| `docs/CNAME` | The custom domain (`tpy-lang.org`). |
| `examples/*.py` | Source: the example programs (the code shown on the landing page). |
| `build_examples.py` | Reads `examples/`, highlights them, writes `docs/examples.js`. Pure stdlib -- no `tpy` needed to regenerate. |
| `verify_examples.py` | Compiles each example with `tpy` (runs the deterministic ones), failing on any that don't. Requires the toolchain; checks against the **published** `tpy`. |
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

Each example on the site is a **real TurboPython program** under `examples/`.
The dropdown order and display order come from the `ORDER` list in
`build_examples.py`.

Workflow when adding/editing an example:

1. Edit (or add) the `.py` under `examples/`.
2. **Verify it compiles with tpy** (this is the bar -- examples must be real).
   With the toolchain installed (`pip install tpy-lang`), check them all at once:
   `python3 verify_examples.py` (compiles each; runs the deterministic ones;
   fails on any that don't). Or check one by hand:
   - runnable ones: `diff <(python3 <f>.py) <(tpy <f>.py)` (CPython parity) or just `tpy <f>.py`.
   - tpy-only / network ones (ownership, requests): `tpy -b <f>.py` (compile + link).
3. Regenerate the data: `python3 build_examples.py`.
4. If you added a file, add it to `ORDER` in `build_examples.py`.

Conventions:
- **Keep lines <= ~57 chars.** The code window is ~61 chars wide; longer lines
  scroll horizontally (ugly). `verify_examples.py` enforces the 61-char window
  (fails any example that exceeds it); aim for <=57 for a margin.
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
settings). Pushing to the default branch publishes. HTTPS is provisioned by
GitHub (Let's Encrypt).

DNS for the apex domain points at GitHub Pages (A/AAAA records at the registrar).

## Open threads

- **Placeholder links:** the nav "Docs", the hero "Read the guide" button, and
  the banner "See what works" link carry class `soon` and pop a "coming soon"
  toast. Replace each with a real destination as those pages get written.
- **"no GIL" claim:** the hero advertises "no GIL for multithreading"; threading
  isn't shipped yet. Meant to hold by launch -- soften the wording if it slips.
- **`http.server`:** no server module yet, so the async example builds HTTP on
  raw asyncio streams.
- **Playground:** deferred (would need client-side compile -- Pyodide + in-browser
  C++ -> WASM; big project, not near-term).
- **CI self-verify:** a workflow could `pip install tpy-lang`, run
  `verify_examples.py` (confirm every example still compiles) and
  `build_examples.py` (regenerate `examples.js`) before deploy.
