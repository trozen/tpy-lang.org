# Guide

This guide describes how TurboPython differs from Python and how to write
idiomatic code. It assumes familiarity with Python; the goal is to cover the
delta, not to re-teach the language.

## What TurboPython is

TurboPython is a Python-to-C++ compiler. Source files are ordinary Python and
typically also run under CPython unchanged, but compile to a native binary. The
compiler type-checks statically: missing or incorrect types are compile errors,
not runtime failures.

Most code is written exactly as in Python. The TurboPython-specific additions
(`Own`, `Ptr`, `readonly`) appear only where the semantics genuinely require
them, which in practice is rare.

## The Python-to-TurboPython delta

The differences that actually come up when writing code:

- **Function signatures require annotations.** Parameter types and the return
  type are mandatory; local variables are inferred.
- **Class fields are declared as typed attributes.** There is no `__dict__`;
  attributes not listed as annotations cannot be added at runtime.
- **`int` is arbitrary-precision.** It is correct but not the fastest choice;
  use a fixed-width type (`Int32`, `Int64`, ...) for machine-integer
  performance.
- **An unannotated integer literal defaults to `Int32`.** Plain `x = 5` infers
  as `Int32`, not arbitrary precision (configurable per project).
- **`None` is narrowed before use.** An optional value must be checked
  (`if x is None` / `if x is not None`) before it is used as non-optional.
- **Unions `A | B` are tagged variants,** matched with `match`/`case`.
- **Ownership is explicit at a few boundaries** — see below.

Everything else — loops, comprehensions, f-strings, dicts, sets, tuples,
decorators, generators, `match`/`case`, context managers, `async`/`await` —
works as in Python.

## Types at a glance

Import what is needed from `tpy`; `from tpy import *` is fine for small files.

| Category | Types |
|----------|-------|
| Numeric | `int`, `Int8`/`Int16`/`Int32`/`Int64`, `UInt8`…`UInt64`, `float`/`Float64`, `Float32`, `bool` |
| Text | `str`, `StrView`, `String`, `Char` |
| Collections | `list[T]`, `dict[K, V]`, `set[T]`, `tuple[...]`, `Array[T, N]`, `Span[T]` |
| Bytes | `bytes`, `bytearray`, `BytesView` |
| Optional / union | `Optional[T]` / `T | None`, `A | B` |
| Ownership markers | `Own[T]`, `Ptr[T]`, `readonly[T]` |

Prefer fixed-width integers for performance and reserve `int` for genuinely
arbitrary-precision arithmetic. Prefer plain literals over explicit
constructors (`x = 5`, not `x = Int32(5)`) — inference handles the common case.

## Ownership

This is the one area where the semantics differ from CPython in an important
way. Read it once; most code afterwards stays plain and the ownership markers
stay out of the way.

In CPython every variable is a reference to a heap object, freed automatically
by reference counting. TurboPython keeps that behaviour for **locals and
parameters** — `y = x` and `f(x)` alias the same object, as in Python — but
differs for **persistent storage**: fields, list/dict/set elements, and globals
*own* their values rather than sharing a reference. Value types (`Int32`,
`bool`, `float`, `str`, `Char`, ...) are unaffected — they copy silently and
never need `Own`.

### Plain `T` is the default

- **Parameters** — `def f(x: Record) -> ...` is passed by reference;
  non-mutating parameters become const references automatically.
- **Locals** — `y = x` aliases the same object.
- **Returning a reference to caller-owned data** (e.g. an element of a list
  parameter) — plain `T`.
- **Value types** — always plain; never wrap `Int32` or `str` in `Own`.

### When `Own[T]` is needed

**Returning a newly created object.** A factory hands ownership to the caller:

```python
def make_point(x: Int32, y: Int32) -> Own[Point]:
    return Point(x, y)
```

The same applies element-wise inside a returned tuple: `-> tuple[str, Point]`
is rejected because the `Point` looks like a return-by-reference; spell it
`-> tuple[str, Own[Point]]`.

**A parameter that consumes its argument** — typically when storing it into a
long-lived container:

```python
def adopt(self, dog: Own[Dog]) -> None:
    self.kennel.append(dog)
```

If the caller's variable is unused after the call, the compiler moves it
automatically. If it is used afterwards, the compiler copies and warns (see
below).

**Fields, container elements, and globals** own their values — this is the
default, so the field type is written plain (`kennel: list[Dog]`), not
`list[Own[Dog]]`. Ownership is implied by the storage.

### Copies and `copy()`

A list stores objects, not references, so appending copies where CPython would
share. When the source is still used afterwards, the compiler makes that copy
explicit rather than silent:

```python
from tpy import copy

xs.append(copy(item))   # acknowledged copy; both runtimes now match
```

The warning fires only where an implicit copy would change behaviour relative
to CPython. Three ways to resolve it, in order of preference:

1. **Restructure** so the source is dead afterwards — the value moves
   automatically, no copy.
2. **Construct in place** — `xs.append(Point(1, 2))` never warns.
3. **Wrap with `copy(...)`** when both the original and a copy are genuinely
   needed.

## Writing idiomatic TurboPython

- Annotate function signatures; let the compiler infer locals. Annotate a local
  only when inference would pick the wrong type.
- Prefer plain literals (`1`, `"hello"`, `{1, 2}`) over explicit constructors.
- Put logic inside functions, not at module top level — top-level code uses a
  different codegen path. Keep the top level to imports, constants, and a single
  `main()` call.
- Use `match`/`case` for unions and enums.
- Narrow `Optional[T]` explicitly before non-optional use.
- Prefer protocols over inheritance — they are structural and need no class
  hierarchy.
- Read the copy warnings rather than suppressing them; each flags a real
  CPython/TurboPython divergence.
