# Building & running

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

The `tpy` command compiles a program and runs it. The `tpyc` command compiles
without running. Both take ordinary `.py` files.

## Run a program

```console
$ tpy program.py
```

The program is type-checked, compiled to C++, built, and run. The first build
compiles the runtime and is slow; later builds reuse compiled C++ from
earlier builds and take seconds.

## Run the REPL and one-liners

Running `tpy` with no arguments starts an interactive REPL (`-i`/`--repl`
forces it). One-liners run with `-c`:

```console
$ tpy -c 'print(2 + 3)'
5
```

## Build a standalone binary

```console
$ tpy -b -o build program.py
Built: build/debug/program
$ ./build/debug/program
```

The binary is named after the source file and lands in `debug/` by default.
That build is unoptimized and meant for development. The build to ship and to
measure is `-O` (or
`--release`):

```console
$ tpy -O -b -o build program.py
Built: build/release/program
```

The result needs no Python installation. It links only the standard system
libraries (the C++ runtime and libc), so it runs on any Linux with the same
or newer system libraries. Building happens on the platform the binary
targets. Binaries are small. A trivial release build is about 250 KB.

## Check without building; read the C++

The `tpyc` command runs the front end only -- parsing, type checking,
ownership analysis, C++ generation -- and skips the native build. It is the
fast way to check a change:

```console
$ tpyc -o build program.py
```

The output directory receives the generated C++ project. `--dump-code` prints
the generated C++ instead, which shows directly whether a loop stayed
fixed-width, where a copy happens, and what a class compiles to:

```console
$ tpyc --dump-code program.py
```

Adding `-x` to a `-b` build runs the result immediately after building.

## Build a CPython extension

A module marked `# tpy: ext_module` compiles into a regular CPython extension.
Functions marked `@export` become the module's public API:

```python
# tpy: ext_module
from tpy.extern import export

@export
def triple(x: int) -> int:
    return x * 3
```

```console
$ tpyc -b -o build fastmod.py
Built extension: build/debug/fastmod.so
$ cp build/debug/fastmod.so .
$ python3 -c "import fastmod; print(fastmod.triple(14))"
42
```

The module is imported under the `.so` name, which matches the source file.
Arguments and results convert to their Python counterparts at the boundary,
and a mismatched argument raises an ordinary `TypeError` on the Python side.
[Compatibility](../compatibility.md) tracks which boundary types are
supported.

This supports gradual migration: the application stays in CPython while the
hot module moves to TurboPython.

## A project is a directory of modules

There is no project file yet ([Planned](#toolchain-notes), below). A program
is its entry file plus everything it imports. Local modules and packages next
to the entry file resolve as in Python, and all of it is compiled together:

```
app.py          # the entry file:  tpy app.py
helpers.py      # import helpers
pkg/
    __init__.py
    scale.py    # from pkg.scale import to_f
```

Module-level constants are declared `Final`. The compiler suggests it for an
ALL_CAPS name whose type `Final` can wrap:

```python
from typing import Final
from tpy import Float64

FACTOR: Final[Float64] = 1.8
```

## Toolchain notes

The build uses the system C++ compiler, and `--cxx` selects a different one.
C++23 support is required, so GCC 13 or newer, or Clang 19 or newer, works;
`g++ --version` reports the installed version. The build also uses `ccache`
when available, precompiled headers (`--no-pch` turns them off), and parallel
compilation (`-j N`).

!!! info "Planned"
    `pyproject.toml` integration -- project-level configuration, dependencies,
    and build settings -- does not exist yet. Configuration is currently
    command-line flags only.

The remaining pages are orientation: [Coming from C++/Rust](cpp-rust.md) and
[Beyond the core](beyond.md).
