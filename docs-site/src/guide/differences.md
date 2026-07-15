# How TurboPython differs from Python

TurboPython is Python's syntax over a different execution model. A program is
type-checked, compiled to C++, and built into a native binary. Every variable
has one static type, and every object has one owner. Code that breaks a typing
or ownership rule is caught while compiling. The compiler either rejects it, or
warns and inserts a runtime check. The result runs with no interpreter, no
garbage collector, and no GIL.

Each section below states one difference briefly and links to the guide page
that covers it in full.

## The main differences

The syntax is Python's, and so is most of the semantics: loops,
comprehensions, f-strings, generators, context managers, and exceptions all
work as ordinary Python. A handful of things differ, and these are the ones
that come up earliest:

- Functions require type annotations. Parameters and return types are
  mandatory, as are class fields; locals are inferred.
- Integer literals default to `Int32`. `int` is arbitrary-precision as in
  Python, but a bare literal is deduced as fixed-width `Int32`, which can
  overflow and panic.
- Third-party packages written for regular Python cannot be imported.
  Everything imported is compiled from source with the program, so a module
  is importable only if TurboPython can compile it. Many standard-library
  modules ship with the compiler; a typical pip package does not compile.
- Durable storage owns its values. Fields and containers store their values
  inline and own them; locals and parameters alias, exactly as in Python.
  This is the one deep difference: [Ownership and references](ownership.md).

Where compiled behavior differs from CPython (the standard Python
interpreter), the compiler warns or errors wherever it can, so these
differences surface during development.

## Function signatures require annotations

Parameter types and the return type are mandatory. The compiler relies on
them to check calls and generate typed code:

<!-- tpy: expect-error="must have type annotation" -->
```python
def double(x):           # error: 'x' has no type annotation
    return x * 2

print(double(4))
```

```
error: Parameter 'x' must have type annotation
```

Local variables are inferred; annotating them is allowed but rarely needed.
More on designing signatures: [Functions and API boundaries](functions.md).

## The `int` type is exact; fixed-width is fast

Like Python, TurboPython's `int` is arbitrary-precision. It is always correct
and never the fastest choice. The fixed-width types (`Int8` through `Int64`,
unsigned variants, `Float32`/`Float64`) are fixed-size machine numbers. An
unannotated integer literal infers as `Int32`:

<!-- tpy: run -->
```python
def main():
    n: int = 2 ** 100    # int is arbitrary-precision
    print(n + 1)
    k = 5                # an unannotated literal is Int32
    print(k * k)         # 25

main()
```

Fixed-width arithmetic does not wrap silently. Overflow stops the program with
a panic: `TurboPython panic: Int32 overflow in addition`. A panic is not an
exception; it cannot be caught.

Fixed-width types are for computation, and `int` is for genuinely unbounded
arithmetic. The details, including literal inference and conversions:
[Types, inference and values](types.md).

## Third-party packages cannot be imported

Importing a package written for regular Python fails to compile:

<!-- tpy: expect-error="Module 'numpy' not found" -->
```python
import numpy            # error: no such module
```

```
error: Module 'numpy' not found
```

TurboPython compiles the program and everything it imports, so a module is
available only if it compiles as TurboPython. This is by design, not a
temporary gap.

!!! info "Limited today"
    A subset of the standard library is bundled.
    [Compatibility](../compatibility.md) tracks which modules work.

## Classes have a fixed set of fields

Fields are declared as annotations on the class. There is no `__dict__`, so an
attribute that was never declared cannot be added later:

<!-- tpy: prelude -->
```python
class Point:
    x: int
    def __init__(self, x: int):
        self.x = x
```

<!-- tpy: cont expect-error="has no field" -->
```python
def main():
    p = Point(1)
    p.label = "origin"   # error: 'label' is not a declared field

main()
```

```
error: Record 'Point' has no field 'label'
```

In exchange, objects are fixed-size and field access is a direct load, not a
dictionary lookup. Classes, collections, and `match`:
[Data modeling](data-modeling.md).

## The type includes `None`

A value that may be `None` has a union type, `T | None`, and the compiler
tracks it. Using it as a plain `T` without a check is flagged:

<!-- tpy: cont -->
```python
def get_x(p: Point | None) -> int:
    return p.x           # warning: p may be None here
```

```
warning: Potential None access on optional value; generated code adds
runtime null check. Use 'if x is not None' or 'assert x is not None' to
prove safety and remove this warning.
```

The generated code stays safe (a runtime check is inserted), and the warning
names the fix, which is to narrow the value before using it.

<!-- tpy: cont run -->
```python
def get_x(p: Point | None) -> int:
    if p is None:
        return 0
    return p.x           # p is Point here -- no warning

def main():
    print(get_x(Point(3)))   # 3
    print(get_x(None))       # 0

main()
```

Narrowing `None` in full: [Control flow, None & errors](control-flow.md).

## Unions are real types; `match` branches on them

In CPython, `A | B` is only a type hint. Here it is a real representation. The
value carries a small marker, the *tag*, that records which member it currently
holds. `match` compiles to a branch on that tag rather than a chain of
`isinstance` checks. A missing `case` cannot fall through silently: with a
declared return type, the compiler rejects a `match` that can reach the end of
the function without returning.

<!-- tpy: run -->
```python
import math

class Circle:
    r: float
    def __init__(self, r: float):
        self.r = r

class Square:
    a: float
    def __init__(self, a: float):
        self.a = a

def area(s: Circle | Square) -> float:
    match s:
        case Circle(r=r):
            return math.pi * r * r
        case Square(a=a):
            return a * a

def main():
    print(area(Square(3.0)))   # 9.0

main()
```

Unions and `match` in full: [Data modeling](data-modeling.md).

## Method calls bind at compile time

In CPython, method calls dispatch dynamically: an override runs whenever the
object is a subclass instance. In TurboPython a call binds at compile time to
the declared type, and the compiler warns on every override that would behave
differently:

```python
class Animal:
    def sound(self) -> str:
        return "..."

class Dog(Animal):
    def sound(self) -> str:      # warning: hides Animal.sound
        return "woof"
```

```
warning: Method 'Dog.sound' hides 'Animal.sound' -- any 'Animal' reference
will call 'Animal.sound', not 'Dog.sound' (differs from Python's dynamic
dispatch); make 'Animal' a @dynamic protocol for runtime dispatch
```

Polymorphism is usually modeled with structural protocols or unions instead;
[Data modeling](data-modeling.md) shows both.

## Durable storage owns its values

Ownership is the one deep difference from CPython. In CPython, every variable,
field, and list element is a reference, and a garbage collector frees objects.
In TurboPython, locals and parameters still alias like Python, but a field or a
container element *owns* its value. Storing an object that is still in use elsewhere makes a copy, and
the compiler warns about every such copy. There is no garbage collector and no
reference counting by default; lifetimes are decided at compile time.

[Ownership and references](ownership.md) covers the model fully.

## Most of Python works unchanged

Those are the major differences. Ordinary code compiles and runs as it would
in Python:

<!-- tpy: run -->
```python
from typing import Iterator

def evens(limit: int) -> Iterator[int]:
    n = 0
    while n < limit:
        yield n
        n += 2

def main():
    squares = [x * x for x in range(5)]
    by_name = {f"k{i}": i for i in range(3)}
    print(f"total={sum(squares)}")     # total=30
    print(sorted(by_name.items()))
    print(list(evens(8)))              # [0, 2, 4, 6]
    with open("/tmp/note.txt", "w") as fh:
        fh.write("ok")
    print("file written")

main()
```

`try`/`except` also works as in Python; error handling has its own page,
[Control flow, None & errors](control-flow.md). Some conveniences are still
missing, and [Compatibility](../compatibility.md) tracks the gaps.

## How these docs flag differences

Five callouts appear throughout the guide, in fixed meanings:

- **Planned** -- does not exist yet; on the roadmap.
- **Limited today** -- partially works; states the current boundary and links
  to Compatibility.
- **Differs from CPython** -- behavior differs and the compiler warns or
  errors; the callout names the diagnostic.
- **Silent difference from CPython** -- behavior differs with no diagnostic
  today; the callout flags it prominently.
- **Coming from C++/Rust** -- asides for systems programmers. Python readers
  can skip them.

The guide continues with [Types, inference and values](types.md).
