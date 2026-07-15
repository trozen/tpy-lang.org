"""Extract and verify code snippets from the docs source.

Every ```python (or ```tpy) fenced block under docs-site/src/ is compiled
against the pinned TurboPython compiler, so a copy-pasted example that does not
compile fails the gate instead of shipping.

A block is controlled by an optional HTML-comment directive on the line just
above the opening fence, so the fence itself stays clean and MkDocs rendering is
untouched:

    <!-- tpy: run -->
    ```python
    print("hello")
    ```

Directive tags (space-separated after `tpy:`):

    (none)              compile to C++ only (tpyc); must succeed. Fast -- catches
                        type / ownership / diagnostic errors, which is most of
                        what the docs teach.
    run                 also build and run (tpy); must succeed. Use where the
                        page shows program output.
    expect-error        tpyc must FAIL. Optionally `expect-error=/regex/` or
                        `expect-error="substring"` to pin the message -- match a
                        stable substring, never the whole diagnostic (it changes).
    fragment            the block is not a whole program; wrap it as the body of
                        `def main(): ...` + a `main()` call before compiling.
    prelude             shared code (imports / classes / a demo) shown once and
                        reused: prepended to every later `cont` block in the same
                        file. Compiled on its own; combine with `run` to also run
                        it.
    cont                prepend this file's preludes so far before compiling or
                        running -- lets a focused snippet build on shared setup
                        without repeating it. A function the block redefines
                        (typically `main`) replaces the prelude's, so a prelude
                        can end with a runnable demo without colliding with
                        later blocks.
    skip                do not verify (illustrative pseudo-code).

The compiler is located, in order: $TPY_DIR, then the `vendor/tpy` submodule,
then a sibling `../tpy-poc` checkout. See tests/README.md.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "docs-site" / "src"

_VERIFIED_LANGS = {"python", "py", "tpy"}
_DIRECTIVE_RE = re.compile(r"<!--\s*tpy:\s*(?P<tags>.*?)\s*-->")
_FENCE_RE = re.compile(r"^(?P<indent>\s*)(?P<ticks>`{3,}|~{3,})(?P<info>.*)$")


@dataclass
class Snippet:
    path: Path
    line: int  # 1-based line of the opening fence
    lang: str
    code: str
    skip: bool = False
    run: bool = False
    fragment: bool = False
    prelude: bool = False
    cont: bool = False
    expect_error: bool = False
    error_pattern: str | None = None  # regex source, or None for "any error"
    preamble: str = ""  # shared prelude code prepended before compiling

    @property
    def ident(self) -> str:
        rel = self.path.relative_to(REPO_ROOT)
        return f"{rel}:{self.line}"


def _parse_directive(tags_text: str) -> dict:
    """Parse the tag list from a `<!-- tpy: ... -->` directive."""
    out: dict = {}
    # expect-error may carry =/regex/ or ="text"; split those off first.
    for m in re.finditer(r'expect-error(?:=(?:/(?P<rx>.*?)/|"(?P<sub>.*?)"))?', tags_text):
        out["expect_error"] = True
        if m.group("rx") is not None:
            out["error_pattern"] = m.group("rx")
        elif m.group("sub") is not None:
            out["error_pattern"] = re.escape(m.group("sub"))
    tags_text = re.sub(r'expect-error(?:=(?:/.*?/|".*?"))?', "", tags_text)
    for tok in tags_text.split():
        if tok in ("run", "fragment", "skip", "prelude", "cont"):
            out[tok] = True
    return out


def extract_snippets(md_text: str, path: Path) -> list[Snippet]:
    """Return every verifiable fenced block in one markdown document."""
    snippets: list[Snippet] = []
    preamble_parts: list[str] = []  # prelude code accumulated in document order
    lines = md_text.splitlines()
    pending: dict = {}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        dm = _DIRECTIVE_RE.search(line)
        if dm and line.strip().startswith("<!--"):
            pending = _parse_directive(dm.group("tags"))
            i += 1
            continue
        fm = _FENCE_RE.match(line)
        if fm and fm.group("info").strip():
            lang = fm.group("info").strip().split()[0].lstrip("{").rstrip("}").lstrip(".")
            ticks = fm.group("ticks")
            indent = fm.group("indent")
            body: list[str] = []
            j = i + 1
            while j < n:
                cm = _FENCE_RE.match(lines[j])
                if cm and cm.group("ticks")[0] == ticks[0] and \
                        len(cm.group("ticks")) >= len(ticks) and \
                        not cm.group("info").strip():
                    break
                body.append(lines[j])
                j += 1
            if lang in _VERIFIED_LANGS:
                # Strip the fence's own indentation from the body.
                code = "\n".join(
                    ln[len(indent):] if ln.startswith(indent) else ln for ln in body
                )
                is_prelude = pending.get("prelude", False)
                is_cont = pending.get("cont", False)
                snippets.append(Snippet(
                    path=path, line=i + 1, lang=lang, code=code,
                    skip=pending.get("skip", False),
                    run=pending.get("run", False),
                    fragment=pending.get("fragment", False),
                    prelude=is_prelude,
                    cont=is_cont,
                    expect_error=pending.get("expect_error", False),
                    error_pattern=pending.get("error_pattern"),
                    # a later prelude may build on an earlier one, so preludes
                    # see the accumulated preamble too (their own code excluded).
                    preamble=("\n\n".join(preamble_parts)
                              if (is_cont or is_prelude) else ""),
                ))
                if is_prelude:
                    preamble_parts.append(code)
            pending = {}
            i = j + 1
            continue
        if line.strip():
            pending = {}  # a directive only binds to the fence right below it
        i += 1
    return snippets


def iter_all_snippets(src_dir: Path = SRC_DIR) -> list[Snippet]:
    out: list[Snippet] = []
    for md in sorted(src_dir.rglob("*.md")):
        out.extend(extract_snippets(md.read_text(), md))
    return out


def resolve_compiler_dir() -> Path | None:
    """Locate a TurboPython checkout to compile against, or None."""
    env = os.environ.get("TPY_DIR")
    if env:
        p = Path(env).expanduser().resolve()
        return p if (p / "pyproject.toml").exists() else None
    for cand in (REPO_ROOT / "vendor" / "tpy", REPO_ROOT.parent / "tpy-poc"):
        if (cand / "pyproject.toml").exists():
            return cand
    return None


def _strip_redefined(preamble: str, body: str) -> str:
    """Drop top-level functions (and calls to them) that `body` redefines.

    tpyc's front end tolerates a duplicate `def main()`, but the generated C++
    does not -- so a prelude's demo must give way to the block's own version.
    Comments are lost in the round-trip; the composed source is only compiled,
    never shown.
    """
    try:
        pre = ast.parse(preamble)
        redefined = {n.name for n in ast.parse(body).body
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    except SyntaxError:
        return preamble
    if not redefined:
        return preamble
    kept = [
        node for node in pre.body
        if not (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name in redefined)
        and not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                 and isinstance(node.value.func, ast.Name)
                 and node.value.func.id in redefined)
    ]
    return ast.unparse(ast.Module(body=kept, type_ignores=[]))


def _wrap_fragment(code: str) -> str:
    body = "\n".join(("    " + ln) if ln.strip() else ln for ln in code.splitlines())
    return f"def main():\n{body}\n\nmain()\n"


def _invoke(compiler_dir: Path, tool: str, args: list[str]) -> subprocess.CompletedProcess:
    cmd = ["uv", "run", "--project", str(compiler_dir), tool, *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600)


def verify(snippet: Snippet, compiler_dir: Path) -> None:
    """Compile (and maybe run) one snippet; raise AssertionError on mismatch."""
    if snippet.skip:
        return
    body = _wrap_fragment(snippet.code) if snippet.fragment else snippet.code
    preamble = _strip_redefined(snippet.preamble, body) if snippet.preamble else ""
    source = f"{preamble}\n\n{body}" if preamble else body
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        src = tmp / "main.py"
        src.write_text(source)
        out = tmp / "out"

        if snippet.expect_error:
            r = _invoke(compiler_dir, "tpyc", ["-o", str(out), str(src)])
            combined = r.stdout + r.stderr
            assert r.returncode != 0, (
                f"{snippet.ident}: expected a compile error, but it compiled.\n"
                f"--- snippet ---\n{source}"
            )
            if snippet.error_pattern:
                assert re.search(snippet.error_pattern, combined), (
                    f"{snippet.ident}: error did not match /{snippet.error_pattern}/.\n"
                    f"--- diagnostics ---\n{combined}"
                )
            return

        tool, args = ("tpy", ["-o", str(out), str(src)]) if snippet.run \
            else ("tpyc", ["-o", str(out), str(src)])
        r = _invoke(compiler_dir, tool, args)
        assert r.returncode == 0, (
            f"{snippet.ident}: expected to {'run' if snippet.run else 'compile'} "
            f"cleanly, but {tool} failed (exit {r.returncode}).\n"
            f"--- snippet ---\n{source}\n--- diagnostics ---\n{r.stdout}{r.stderr}"
        )
