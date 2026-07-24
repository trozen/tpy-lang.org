# Getting started

TurboPython installs from PyPI and compiles ordinary `.py` files to native
binaries. This page covers installation, a first program, and a ten-minute
tour of the language. [The guide](guide/differences.md) teaches the language
in depth.

## Install

TurboPython runs on Linux and macOS and needs Python 3.12 or newer. On Windows,
the recommended setup is
[WSL](https://learn.microsoft.com/windows/wsl/install){ target="_blank" rel="noopener" };
inside a WSL distribution, everything on this page works as on Linux.

TurboPython is distributed on PyPI as `tpy-lang` and can be installed with
[uv](https://docs.astral.sh/uv/getting-started/installation/){ target="_blank" rel="noopener" }
or pip:

=== "uv"

    ```console
    $ uv tool install tpy-lang
    ```

    `uv tool install` makes the `tpy` and `tpyc` commands available globally.

=== "pip"

    ```console
    $ pip install tpy-lang
    ```

    This installs the `tpy` and `tpyc` commands into the active environment.

Compilation needs a C++23 compiler: g++ 13 or newer, or clang++ 19 or newer.
An installed system compiler is detected automatically, and its C++23 support
is checked before the build; an unsupported compiler is rejected upfront with
the version floors and a suggested fix, rather than failing partway through. If
no suitable compiler is present, the `[bundled]` extra installs a C++ compiler
(zig)
together with the package and needs no other setup:

=== "uv"

    ```console
    $ uv tool install "tpy-lang[bundled]"
    ```

=== "pip"

    ```console
    $ pip install "tpy-lang[bundled]"
    ```

To confirm the installation:

```console
$ tpy --version
```

### Updating

`uv tool install` pins the version it first fetched; a later release installs
over it explicitly:

=== "uv"

    ```console
    $ uv tool upgrade tpy-lang
    ```

=== "pip"

    ```console
    $ pip install --upgrade tpy-lang
    ```

## Hello

<!-- tpy: run -->
```python
def main():
    print("hello from tpy")

main()
```

```console
$ tpy hello.py
hello from tpy
```

A `main()` function is only a convention; top-level statements work as
well. The first run compiles the runtime and is slow -- a few minutes
at most, with progress shown. Later runs reuse compiled C++ from earlier
builds and take seconds.

The package installs two commands: `tpy` compiles and runs a program in one
step, and `tpyc` compiles without running. Running `tpy` with no arguments
opens a REPL, and `tpy -c 'print(2 + 3)'` evaluates a single line.
[Building & running](guide/building.md) covers everything else the toolchain
can produce, including standalone binaries and CPython extensions.

## Ten minutes of TurboPython

Three short examples: a typed function, a class, and the one place where
TurboPython deeply differs from Python.

A TurboPython function is a Python function with a fully annotated signature.
The annotated signature is what the compiler works from; inside the function,
types are inferred. The example below is also valid Python and runs unchanged
under CPython:

<!-- tpy: run -->
```python
def fib(n: int) -> int:
    a: int = 0
    b: int = 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    print(fib(10))     # 55
    print(fib(100))    # 354224848179261915075

main()
```

The annotations are ordinary Python types. Annotated as `int`, `a` and `b`
are Python integers with arbitrary precision, which is how `fib(100)` returns
its exact 21-digit result. Without the annotations, the literals `0` and `1`
would infer `Int32`, the fast machine type, and the addition would overflow.
[Types](guide/types.md) explains the inference rules and the fixed-width
types such as `Int32` and `Int64`.

Classes follow the same pattern. Fields are declared with annotations, and
methods are ordinary Python. There is no `__dict__`: an instance has exactly
the fields its class declares, so the compiler knows the memory layout of
every object:

<!-- tpy: run -->
```python
class Sensor:
    name: str
    limit: float
    def __init__(self, name: str, limit: float):
        self.name = name
        self.limit = limit
    def check(self, v: float) -> bool:
        return v <= self.limit

def main():
    s = Sensor("boiler-3", 21.5)
    print(s.check(20.5), s.check(22.0))   # True False

main()
```

The last example is the one deep difference. In Python, a list stores
references: when a program appends an object and later modifies it, the list
shows the modification. In TurboPython, a list owns its elements. Appending
an object that is still in use afterwards therefore stores a copy, and the
compiler reports it:

<!-- tpy: run -->
```python
class Reading:
    sensor: str
    def __init__(self, sensor: str):
        self.sensor = sensor

def main():
    log: list[Reading] = []
    r = Reading("boiler-3")
    log.append(r)            # r is used below, so the list gets a copy
    r.sensor = "renamed"
    print(log[0].sensor)     # boiler-3 -- not renamed

main()
```

```
warning: copies Reading into owned storage; use copy() to make this explicit
```

Under CPython this program would print `renamed`. That difference, and the
warning that makes it visible, is the core of the ownership model. A copy is
not the only possible outcome either: when the appended object is not used
again, it is moved into the list instead of copied.
[Ownership and references](guide/ownership.md) teaches the whole model.

## Coding with an AI agent

TurboPython source is valid Python, so coding agents such as Claude Code,
Cursor, and Copilot work without a plugin. What they miss is where
TurboPython departs from Python: the ownership model, the fixed-width types,
and the parts of the standard library that are not yet available. The
`tpy --install-agent-docs` command writes that knowledge into a project.

```console
$ tpy --install-agent-docs docs
```

The command writes four reference files into the given directory:

- `TPY_FOR_AGENTS.md` -- a short Python-to-TurboPython bootstrap covering the
  delta from Python, the ownership rules, and the idiomatic patterns.
- `TPY_LANGUAGE_FEATURES.md` -- the full language reference. Only the sections
  marked **Working** are usable today.
- `TPY_STDLIB_ROADMAP.md` -- the standard library coverage, listing what is
  available and what is still missing.
- `TPY_API_REFERENCE.md` -- the exact callable API surface, with signatures
  and methods.

The API reference is generated from the installed package, so it matches
exactly what the current version can call. Re-running the command after an
upgrade refreshes all four files.

The command also prints a short snippet. Adding that snippet to the project's
`AGENTS.md` or `CLAUDE.md` points the agent at the four files so it reads them
before writing TurboPython code.

## Where next

- [How TurboPython differs from Python](guide/differences.md) -- a one-page
  map of the differences from Python.
- [Ownership and references](guide/ownership.md) -- the model behind the
  warning above.
- [Compatibility](compatibility.md) -- a precise list of what works today.
