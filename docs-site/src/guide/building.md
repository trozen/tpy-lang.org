# Building & running

A TurboPython program is compiled to a native binary before it runs. The `tpy`
command compiles a program and runs it, while `tpyc` compiles without running.
Both take ordinary `.py` files.

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
Built: build/release/program
$ ./build/release/program
```

The binary is named after the source file and lands in `release/`. Every
build is optimized (`-O3`) unless `--debug` is given, so the default binary is
the one to ship and to measure. The `--debug` flag builds without optimization
and with debug information (`-g -O0`), which compiles faster and lands in
`debug/`:

```console
$ tpy --debug -b -o build program.py
Built: build/debug/program
```

Runtime checks such as overflow detection stay on in both variants.

The result needs no Python installation. It links only the standard system
libraries (the C++ runtime and libc), so it runs on other machines of the
same platform with compatible system libraries. Building happens on the
platform the binary targets; Linux and macOS are supported. On Windows,
builds run inside WSL and produce Linux binaries.

Adding `-x` to a `-b` build runs the result immediately after building.

## Emit and integrate C++

By default the `tpyc` command emits a C++ project and skips the native build:

```console
$ tpyc -o build program.py
```

The generated project lands directly in the output directory: `build/src/`,
`build/include/`, the bundled runtime, and `build/sources.cmake`. Omitting
`-o` writes to `__tpyc__/program.d/` next to the source instead.

Skipping the native build also makes `tpyc` the fast way to check a change. The
front end still parses, type-checks, and runs ownership analysis, so type and
ownership errors surface without waiting for the C++ compiler.

The `--dump-code` flag prints the generated C++ to stdout instead of writing a
project. It shows directly whether a loop stayed fixed-width, where a copy
happens, and what a class compiles to:

```console
$ tpyc --dump-code program.py
```

### Integrate with a CMake build

Each project carries a `sources.cmake` that defines the generated sources, the
include directories, the link libraries, and the required C++ standard. A CMake
target consumes them directly:

```cmake
include(build/sources.cmake)
add_executable(app ${TPYC_SOURCES})
target_include_directories(app PRIVATE ${TPYC_INCLUDE_DIRS})
target_link_libraries(app PRIVATE ${TPYC_LIBRARIES})
set_target_properties(app PROPERTIES CXX_STANDARD ${TPYC_CXX_STANDARD})
```

The `--no-main` flag omits the generated `main()` so the compiled code links
into an existing C++ program rather than running on its own. When `tpyc`
emits a project to an explicit `-o` directory, the runtime headers are bundled
into it, which keeps the project self-contained and safe to commit or copy to
another machine; the `--no-bundle-runtime` flag skips that copy. A native
build (`-b`) and the default `__tpyc__/` output reference the installed
runtime instead.

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
Built extension: build/release/fastmod.so
$ cp build/release/fastmod.so .
$ python3 -c "import fastmod; print(fastmod.triple(14))"
42
```

The module is imported under the `.so` name, which matches the source file.
Arguments and results convert to their Python counterparts at the boundary,
and a mismatched argument raises an ordinary `TypeError` on the Python side.
[Compatibility](../compatibility.md) tracks which boundary types are
supported.

This supports gradual migration. The application stays in CPython while the
hot module moves to TurboPython.

## Compile a multi-module program

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

## Toolchain notes

The build uses the system C++ compiler, and `--cxx` selects a different one.
C++23 support is required, so GCC 13 or newer, or Clang 19 or newer, works;
`g++ --version` reports the installed version. An auto-detected compiler that
fails the C++23 check is skipped; one named with `--cxx` is used after a
warning. The build also uses `ccache`
when available, precompiled headers (`--no-pch` turns them off), and parallel
compilation (`-j N`). Builds are cached by content, and `--rebuild` ignores
the cache and rebuilds everything, the precompiled header included.

The `zlib` and `gzip` modules link a bundled zlib by default; `--zlib system`
links the system library instead, and `--zlib none` makes importing either
module a compile error.

!!! info "Planned"
    `pyproject.toml` integration -- project-level configuration, dependencies,
    and build settings -- does not exist yet. Configuration is currently
    command-line flags only.

The remaining pages are orientation: [Beyond the core](beyond.md) and
[Coming from C++/Rust](cpp-rust.md).
