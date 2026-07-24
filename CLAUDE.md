# CLAUDE.md

Working guidance for Claude Code in this repo. See `README.md` for build/deploy
mechanics; this file is the conventions that aren't obvious from the code.

## What this is

The TurboPython marketing / landing site, served at **tpy-lang.org** via GitHub
Pages from **`docs/`**. A single self-contained `index.html` (inline CSS + JS,
no framework, no external requests) plus generated example data. Audience:
experienced Python developers.

## Hard rules

- **Never push, and never deploy.** The user controls every push and the live
  site. Commit only when explicitly asked.
- **Never hand-edit `docs/examples.js`** -- it is generated. Edit the programs
  in `examples/` and run `python3 build_examples.py`.
- **Examples must be real.** Run `make check` before relying on or showing an
  example -- it compiles every docs snippet *and* every `examples/` program
  against the pinned `vendor/tpy`, and fails rather than skipping if that
  checkout is missing. Nothing the site shows should fail to compile.
- **Before announcing the site, re-check the examples against the published
  package.** `make check` uses the pin, which can run ahead of PyPI, so it
  cannot by itself prove a visitor can run what the landing page shows.
  `uv run --with 'tpy-lang==<version>' python verify_examples.py` runs that
  check against the published package; it must pass, or the affected examples
  must come off the page, before anyone is pointed at the site. As of 0.5.0
  this gate passes: all eight examples verify against the published release,
  `requests_demo.py` (tile 6) included. Re-run it after each release bump, and
  whenever the pin moves ahead of what is on PyPI.
- **Self-contained landing page.** No external scripts, styles, fonts, or network
  requests in `index.html` -- everything inline, no framework. (The docs site under
  `docs-site/` is the exception: it uses MkDocs Material.)
- **Never hand-edit `docs/docs/`** -- it is the `mkdocs build` output. Edit
  `docs-site/src/` and rebuild (`cd docs-site && mkdocs build`). Rebuild before
  committing docs changes, or the served site goes stale.

## Voice / copy

Applies to the **landing page** (`index.html`):

- **Declarative, third-person, professional.** No marketing fluff, no cutesy
  taglines, no hype ("blazing", "sharper rules", "the compiler flags the rest").
- **No second person.** Don't address the reader as "you"/"your" -- describe the
  language. Match the rest of the page.
- Don't over-claim: features that aren't shipped/usable yet aren't "available".
- Copy explains at showcase altitude; the docs site teaches.

The **docs site** (`docs-site/`) is currently written in the same declarative,
no-second-person voice for consistency. Whether a guide should instead use
second person ("you annotate...") is an open call for the user -- don't switch
it unprompted.

## Examples

- Real TurboPython programs under `examples/`; order/labels in `build_examples.py`'s
  `ORDER`. Each opens with a 1-2 line comment saying what it shows.
- Keep lines <= ~57 chars (the code window width; longer lines scroll).

## Docs site (`docs-site/`) conventions

- **Prose register lives in `docs-site/SCOPE.md` (Voice).** Connected
  explanatory prose; no aphorism lead-ins, telegraphic fragments, cliches, or
  author-facing meta. Follow it for every docs edit.
- **External links open in a new tab, marked manually per link** (deliberately
  no JS/plugin for this): `[uv](https://...){ target="_blank" rel="noopener" }`
  -- `attr_list` is enabled for exactly this. `extra.css` adds the open-in-new
  icon to any `a[target="_blank"]` automatically. Links within tpy-lang.org
  (e.g. docs -> landing page) stay in the same tab: no attributes.

## Placeholder links

- Links to pages that don't exist yet carry class `soon` and pop a "coming soon"
  toast (see the inline script). Use that pattern -- never leave a dead `#` link
  that does nothing on click.

## Commits

- No LLM/tool-generated references in messages. Concise subject; wrap the body at
  ~72 columns.
