# Docs scope -- TurboPython 0.5.0

The plan of record for the `tpy-lang.org/docs/` documentation, agreed for the
upcoming 0.5.0 release. This file is the durable reference; keep it in sync if
the plan changes.

## Mission

A **soft-launch** documentation set: complete on the core language, honest about
gaps. A motivated early adopter can self-serve without prior context beyond
Python. Not a marketing funnel -- accuracy and a teachable model over polish.

## Audience and goal

The reader is a developer who **knows Python well and needs real performance**
-- a compiled native binary, not a rewrite in another language. They do not
necessarily know C++ or Rust.

Success: after reading, the reader

1. understands TurboPython's **core model** (static types + an ownership model),
   as a *model*, not as a list of differences, and
2. can **write efficient code** -- picking fixed-width ints, avoiding accidental
   copies and allocations, and reaching for the constraint decorators on hot
   paths.

A short "coming from C++/Rust" orientation lets systems readers map their mental
model across; Python readers can skip it.

## Voice

Plain, clear English for a **proficient non-native reader**. Short sentences,
concrete words, no idioms or ornate phrasing. Not dumbed-down -- assume a
competent programmer -- but never needlessly complex.

Register, calibrated during the 2026-07-13 review (Home, Getting started, and
the Guide index are the exemplars):

- **Connected explanatory prose**, written the way a human writes a language
  guide. No bolded aphorism lead-ins ("**Functions carry types.**"), no
  telegraphic fragments ("Two commands exist:", "Three snippets: X, Y, Z."),
  no punchy cliches ("one import away"), no X-decides-Y aphorism chains.
- **One fact per sentence.** Split any sentence that needs a colon and two
  clauses to land. Drop facts the reader does not need yet ("float compiles
  to a machine double" in minute one).
- **No author-facing meta.** No verification/process claims ("verified
  against a pinned build"), no docs-machinery self-reference ("the guide's
  recurring example", "these docs carry a callout"), no roadmap promises
  ("will grow"), no trust adjectives ("honest", "real diagnostics").
  Status pages carry a one-line "Status as of <version>, <date>." stamp.
- **First examples are idiomatic Python** with plain types (`float`, `int`);
  extension types (`Int32`, `Float64`) appear only where they are the point.
  Remember the literal-inference rule: bare `0`/`1` infer `Int32`, so
  examples that rely on arbitrary precision annotate their locals.
- **uv and pip are equals** in install instructions, presented as content
  tabs.
- **No leading bare code span.** A heading or a first sentence does not open
  with a backticked token; lead with a plain word ("The `int` type is exact",
  not "`int` is exact").
- **Precise, never overclaimed.** "Major", not "all"; state a limit as
  by-design when it is, rather than implying a roadmap with "yet"; check any
  count or coverage claim against the pinned `vendor/tpy` before writing it.
  Gloss `CPython` on first use (the standard Python interpreter); use it for
  behavior contrasts, but say "regular Python" when the point is the package
  ecosystem.

## Where it lives

- Source: `docs-site/src/` (MkDocs Material). Build output is committed to
  `docs/docs/` (GitHub Pages serves it at `tpy-lang.org/docs/`).
- Verified against a **pinned private submodule** of the compiler
  (`vendor/tpy` -> `trozen/tpy-lang`). Snippets compile against that exact
  commit; the Compatibility page carries a "verified against 0.5.0.devN" stamp.
- Verification runs **locally via `pytest`**. No CI for now -- the maintainer
  runs the gate before publishing. Bumping the submodule -> re-verify ->
  re-stamp is the release ritual.

## Structure -- three pillars

### 1. Getting started

Install (`pip` / `uv tool`; the `[bundled]` zig extra; the C++23 note) -> run
`hello.py` -> `tpy` vs `tpyc` + the REPL -> a ~10-minute "taste" that touches a
typed function, a class, and ownership *once*, then hands off to the Guide.

### 2. Guide (10 pages)

Teaches one continuous story: Python syntax over static compiled semantics;
types decide representation and performance; durable storage owns its values;
borrowed/local access stays Pythonic; efficient code is mostly ordinary code
plus a few constraints at hot boundaries.

1. **How TPy differs from Python** -- the map. The unifying model, mandatory
   annotations, BigInt vs fixed-width ints, no `__dict__`, narrowed `None`,
   ownership in one paragraph, warnings on known CPython differences. Sets the
   "can I `pip install` my packages?" expectation early. Introduces the callout
   conventions. Does not teach everything -- gives the map.
2. **Types, inference & values** -- fixed-width ints vs BigInt default, literal
   inference, annotations, value types vs reference types, `Optional`/unions
   intro, and **strings** (`str` / `StrView` / `String`) as a concrete
   subsection with "use this when" guidance.
3. **Functions & API boundaries** -- signatures require annotations; the
   boundary is where copy / alias / own / mutate / readonly become visible.
   Designing small typed APIs.
4. **Ownership, references & moves** -- the deep page. Locals and params alias
   like Python; fields, containers, and globals own; value types copy silently;
   reference types do not silently deep-copy. `Own[T]`, `Ptr[T]`, `readonly[T]`.
   Foreshadows the performance consequences.
5. **Data modeling** -- classes (typed fields, constructors, methods),
   collections (list/dict/set/tuple as containers), and `match` on tagged
   unions.
6. **Control flow, None & errors** -- how programs branch and fail: `None` and
   union narrowing, `try`/`except` (works like Python), and the reassurance that
   writing your own iterator is just `__next__` + `raise StopIteration` (runs
   under CPython; compiles with no exception-throwing cost, automatically).
7. **Writing efficient TPy** -- the capstone. Consolidates, introduces nothing
   new: choose fixed-width ints, avoid accidental BigInt, avoid copies and
   allocations, use views, `@noalloc` / `@nocopy` / `@readonly`, design hot
   functions with clear ownership. Reads as a checklist + synthesis.
8. **Building & running** -- task-oriented and concise: run a script, inspect
   generated C++, compile-only, standalone binary, CPython extension, the REPL.
   `pyproject` support noted as Planned.
9. **Coming from C++/Rust** -- standalone, skimmable, linked from relevant
   pages. Main message: TPy ownership is not Rust borrow-checking and not raw
   C++; it is Python-like local aliasing with owned durable storage.
10. **Beyond the core** -- an honest pointer page: async, generators, protocols,
    macros, native interop. Thin links, not a second compatibility matrix.

### 3. Compatibility

Two parts, hand-curated for users (not a copy of the internal tracker):
language features (works / partial / not-yet) and a stdlib table (module ->
status -> one-line note), at module-level granularity. Carries the "verified
against 0.5.0.devN" stamp.

## Authoring conventions

- **Per-concept rhythm:** Python version -> TPy version -> Why
  (representation / ownership / performance) -> Efficient version -> Pitfall
  (CPython difference or warning).
- **Durable rules**, taught early and reinforced throughout: annotations define
  compiled boundaries; BigInt is Pythonic, fixed-width is fast; locals and
  params alias naturally; durable storage owns what it contains; views and
  readonly references avoid copies; hot code gets `@noalloc` / `@nocopy` /
  `@readonly`.
- **North star:** teach a *model*, not a list of differences.
- **Recurring example:** thread one neutral, boundary-rich type through Types ->
  Functions -> Ownership -> Efficiency, so the reader watches the same object
  cross boundaries.
- **Weighting:** `readonly` and the *explicit* `@error_return` decorator are
  mention-only. `readonly` is mostly inferred (non-mutating params become const
  references automatically). `@error_return(StopIteration)` is auto-added to
  every `__next__`, so iterator authors never type it; the explicit decorator is
  a niche hot-path tool -> a brief pointer on the efficiency page.
- **Every section links out.** On the map and guide pages, a section that
  summarizes a topic ends with a link to the page that covers it in full; no
  section dead-ends. Transient gaps are not enumerated in prose (they age) --
  point to Compatibility instead.

## Callout conventions

- `Planned` -- does not exist yet, on the roadmap (e.g. `pyproject` support).
- `Limited today` -- partially works; states the current boundary. **Links to
  Compatibility** rather than restating status (single source of truth).
- `Coming from C++/Rust` -- systems-reader asides.
- `Differs from CPython` -- behavior differs and **the compiler warns/errors**;
  names the diagnostic.
- `Silent difference from CPython` -- differs with **no diagnostic today**;
  flagged loudly (doubles as an honest-gap marker).

## Snippet correctness

Non-trivial code blocks are written inline in the markdown and verified by
`tests/` (see `tests/README.md`). A block is controlled by an optional
`<!-- tpy: TAGS -->` HTML-comment directive on the line above the fence, so the
fence itself stays a clean ```` ```python ```` (MkDocs rendering untouched):

- (no directive) -- compile to C++ only (`tpyc`); must succeed. Fast; catches
  type / ownership / diagnostic errors, which is most of what the docs teach.
- `run` -- also build and run (`tpy`); must succeed. For blocks that show output.
- `expect-error` -- must fail to compile (for teaching rejections). Optionally
  `expect-error=/regex/` or `expect-error="substring"`; match a stable substring,
  never the exact diagnostic text (it changes).
- `fragment` -- wrap as the body of `def main(): ...` + `main()` before compiling.
- `skip` -- illustrative pseudo-code; not verified.

Illustrative prose fragments stay short. Doc snippets do **not** inherit the
landing-page 61-char width rule (that is specific to `examples/`).

Whenever a source line is the one that produces a compiler **error**, mark it
inline with a lowercase `# error: <short reason>` comment (mirroring the
compiler's own `error:` prefix), so the reader sees which line fails. This is
the standing rule for every `expect-error` block. Mark a **warning** the same
way (`# warning: <short reason>`) when the diagnostic is the point of the
example; skip incidental warnings. Every shown diagnostic is grounded in
visible code -- do not print an error or warning that names identifiers absent
from the snippet above it.

## Site integration

- Expand the MkDocs `nav` for the new pages.
- Replace the landing page's "coming soon" toasts (`class soon` in
  `docs/index.html`) with real links to Docs / Getting-started / Compatibility.
- Rebuild the committed `docs/docs/` output.

## Build-surface facts (audited 2026-07-05)

Work **today**, via public flags: run (`tpy foo.py`), REPL, inline snippet
(`-c`), emit C++ only (`tpyc`), **standalone native binary** (`tpy -b` /
`tpyc --build`), build-and-run (`-x`), optimized build (`-O`/`--release`),
**CPython extension `.so`** (`# tpy: ext_module` + `tpyc -b`), `--dump-code`,
toolchain knobs (`--cxx`, ccache, `--no-pch`, `-j`).

**Planned** (not in the code): `pyproject.toml` integration / project-level
config. This is the one true `Planned` callout on the Building page.

## Out of scope for 0.5.0

- Generated API reference (the `index.md` slot; deferred -- see below).
- Deep-dive advanced chapters (async / generators / protocols / macros / native
  interop / threading stay brief pointers).
- Blog / changelog / release notes.
- Versioned-docs selector (mike) and search/SEO/analytics polish.
- Landing-page copy refresh beyond wiring the links.

## Post-0.5.0 direction

Before 1.0, the docs grow a **full language reference** -- the Tutorial /
Language-Reference split familiar from Python's own docs. It is *additive* on top
of this Guide (which teaches the model and stays valuable), and partly
**generatable**: `tpy --print-types` already emits a markdown API dump of
builtins / tplib / bundled stdlib, and `index.md` already reserves a "generated
API reference (will follow)" slot. So the 0.5.0 work is the front half, not a
throwaway.

## Execution order

1. Write this `SCOPE.md`.
2. Add the pinned private submodule (`vendor/tpy`) + the `pytest` snippet-verify
   harness.
3. Draft the **Ownership** page as the tone-setting exemplar, for review.
4. Fill out the remaining pages page-by-page against that calibration.
