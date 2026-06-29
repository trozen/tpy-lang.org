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
- **Examples must be real.** Run `python3 verify_examples.py` before relying on
  or showing an example. It compiles each against the `tpy` on PATH -- the
  **published** package (`pip install tpy-lang`), which is what a visitor gets,
  not a dev build. (Known gap: the site uses some features ahead of the
  published release -- e.g. the `requests` example needs a post-0.4.0 tpy. Don't
  advertise examples a `pip`-installed user can't run.)
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

## Placeholder links

- Links to pages that don't exist yet carry class `soon` and pop a "coming soon"
  toast (see the inline script). Use that pattern -- never leave a dead `#` link
  that does nothing on click.

## Commits

- No LLM/tool-generated references in messages. Concise subject; wrap the body at
  ~72 columns.
