"""Fold the example programs into examples.js.

Reads each program from examples/ and emits a JS array with a display label,
the filename (for the run line), the raw source (Copy button), and
syntax-highlighted HTML. Output is not captured -- the page shows code only.
Pure stdlib; tpy is not needed to regenerate (only to verify the examples
still compile -- see README). Run from the repo root:

    python build_examples.py
"""
import io, json, keyword, tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "examples"        # input: the example programs
OUT = ROOT / "docs" / "examples.js"  # output: into the Pages-served folder
# (filename, dropdown label) -- controls order and what the selector shows.
ORDER = [
    ("mandelbrot.py", "mandelbrot"),
    ("standard_types.py", "standard types"),
    ("stdlib_demo.py", "stdlib"),
    ("classes.py", "classes"),
    ("ownership.py", "ownership"),
    ("requests_demo.py", "requests + json"),
    ("async_demo.py", "async"),
]
BUILTINS = {"print", "range", "len", "int", "float", "str", "abs", "set", "sorted"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def highlight(src):
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    out = []
    prow, pcol = 1, 0
    for i, tok in enumerate(toks):
        ttype, tstr, (srow, scol), (erow, ecol), _ = tok
        if ttype in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.INDENT, tokenize.DEDENT):
            continue
        if ttype in (tokenize.NEWLINE, tokenize.NL):
            out.append("\n"); prow, pcol = erow, 0; continue
        if srow == prow and scol > pcol:
            out.append(" " * (scol - pcol))
        elif srow > prow:
            out.append(" " * scol)
        cls = None
        if ttype == tokenize.COMMENT:
            cls = "c"
        elif ttype == tokenize.STRING:
            cls = "s"
        elif ttype == tokenize.NUMBER:
            cls = "num"
        elif ttype == tokenize.NAME:
            if keyword.iskeyword(tstr):
                cls = "k"
            else:
                nxt = toks[i + 1] if i + 1 < len(toks) else None
                if (nxt and nxt[1] == "(") or tstr in BUILTINS:
                    cls = "fn"
        text = esc(tstr)
        out.append(f'<span class="{cls}">{text}</span>' if cls else text)
        prow, pcol = erow, ecol
    return "".join(out).strip("\n")


examples = []
for filename, label in ORDER:
    src = (SRC_DIR / filename).read_text().rstrip("\n") + "\n"
    examples.append({"label": label, "file": filename, "src": src, "code": highlight(src)})

js = "const EXAMPLES = " + json.dumps(examples, separators=(",", ":")) + ";\n"
OUT.write_text(js)
print(f"wrote {OUT.relative_to(ROOT)} ({len(js)} bytes, {len(examples)} examples)")
