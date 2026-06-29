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
| `docs/index.html` | The whole page -- inline CSS + JS, no dependencies. Loads `examples.js` via `<script src>`. |
| `docs/examples.js` | **Generated** into `docs/` by `build_examples.py`. A `const EXAMPLES = [...]` array (per example: `label`, `file`, raw `src`, highlighted `code`). Do not edit by hand. |
| `docs/CNAME` | The custom domain (`tpy-lang.org`). |
| `examples/*.py` | Source: the example programs (the code shown on the site). |
| `build_examples.py` | Reads `examples/`, highlights them, writes `docs/examples.js`. Pure stdlib -- no `tpy` needed to regenerate. |

## Examples pipeline

Each example on the site is a **real TurboPython program** under `examples/`.
The dropdown order and display order come from the `ORDER` list in
`build_examples.py`.

Workflow when adding/editing an example:

1. Edit (or add) the `.py` under `examples/`.
2. **Verify it compiles with tpy** (this is the bar -- examples must be real).
   With the toolchain installed (`pip install tpy-lang`):
   - runnable ones: `diff <(python3 <f>.py) <(tpy <f>.py)` (CPython parity) or just `tpy <f>.py`.
   - tpy-only / network ones (ownership, requests): `tpy -b <f>.py` (compile + link).
3. Regenerate the data: `python3 build_examples.py`.
4. If you added a file, add it to `ORDER` in `build_examples.py`.

Conventions:
- **Keep lines <= ~57 chars.** The code window is ~61 chars wide; longer lines
  scroll horizontally (ugly). `awk '{if(length>m)m=length}END{print m}' <f>.py`.
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
- **HTTPS in examples:** TurboPython's `requests` is HTTP-only for now, so the
  requests example hits `http://ip-api.com/json` as a stopgap.
- **`http.server`:** no server module yet, so the async example builds HTTP on
  raw asyncio streams.
- **Playground:** deferred (would need client-side compile -- Pyodide + in-browser
  C++ -> WASM; big project, not near-term).
- **CI self-verify:** a workflow could `pip install tpy-lang`, run `build_examples.py`,
  confirm every example still compiles, and regenerate `examples.js` before deploy.
