"""Verify every example program is real -- compile each with tpy, and run the
deterministic ones, failing if any doesn't.

The "examples must be real" bar lives here, not in build_examples.py (which
only highlights). Network/nondeterministic examples are compiled + linked
(`tpy -b`) but not run; the rest are compiled + run (`tpy <f>`). Requires the
toolchain (`pip install tpy-lang`). Run from the repo root:

    python3 verify_examples.py

Exits non-zero if any example fails, so it's usable as a CI / pre-deploy gate.
"""
import subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "examples"
# Hit the network / nondeterministic -- compile + link only, don't run.
NO_RUN = {"requests_demo.py", "async_demo.py"}


def check(path):
    """Compile (and run, unless network) one example. Returns (ok, detail)."""
    build_only = path.name in NO_RUN
    with tempfile.TemporaryDirectory() as out:
        # -o must precede the input file; args after it go to the program as
        # sys.argv. -b compiles + links without running; without it tpy runs.
        cmd = ["tpy", "-o", out] + (["-b"] if build_only else []) + [str(path)]
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
        except FileNotFoundError:
            sys.exit("error: `tpy` not found on PATH -- install it: pip install tpy-lang")
        except subprocess.TimeoutExpired:
            return False, "timed out"
    if r.returncode != 0:
        last = (r.stderr.strip().splitlines() or ["(no stderr)"])[-1]
        return False, last
    return True, "compiled + linked" if build_only else "compiled + ran"


def main():
    files = sorted(SRC_DIR.glob("*.py"))
    if not files:
        sys.exit(f"no examples found in {SRC_DIR}")
    failures = []
    for path in files:
        ok, detail = check(path)
        print(f"{'ok  ' if ok else 'FAIL'} {path.name:22} {detail}")
        if not ok:
            failures.append(path.name)
    print()
    if failures:
        sys.exit(f"{len(failures)} example(s) failed: {', '.join(failures)}")
    print(f"all {len(files)} examples verified")


if __name__ == "__main__":
    main()
