# Types, inference and values

Every value in TurboPython has one static type, fixed at compile time. That
type sets how the value is represented -- how many bytes it takes, where those
bytes live, and what operations on it cost. Choosing types is the main
performance decision a TurboPython program makes. This page covers the numeric
types, what the compiler infers, the string types, and the value/reference
split.

Annotations appear at function boundaries; nearly everything else is inferred.

## Numbers

The `int` type is Python's integer. It has arbitrary precision and never
overflows. Small values are stored inline; a value allocates on the heap only
once it grows past what fits inline. The fixed-width types are fixed-size
machine numbers: `Int8`, `Int16`, `Int32`, `Int64`, the unsigned `UInt8`
through `UInt64`, and `Float32`. `Float64` is an alias for `float`. `bool` and
`Char` complete the set.

Literals infer a concrete type. A plain integer literal is `Int32`, a decimal
literal is `float`:

<!-- tpy: run -->
```python
def main():
    n = 5            # Int32
    x = 1.5          # float
    flag = True      # bool
    name = "boiler"  # str
    print(n, x, flag, name)

main()
```

A literal that does not fit `Int32` falls back to `int`, and the compiler says
so:

```python
def main():
    big = 5_000_000_000   # warning: outside Int32 range, inferring int
    print(big)

main()
```

```
warning: Integer literal 5000000000 is outside default Int32 range;
inferring int (BigInt).
```

!!! note "Default integer type"
    Unannotated integer literals currently infer `Int32`. This default can be
    changed per compilation with the `--default-int` flag, and may itself
    change in a future version.

Arithmetic keeps Python's meaning. Division with `/` is true division and
returns a float, including on fixed-width operands. Division with `//` floors.
An `int` value is exact at any size:

<!-- tpy: run -->
```python
def main():
    print(7 / 2)      # 3.5
    print(7 // 2)     # 3
    n: int = 2 ** 100
    print(n + 1)      # exact

main()
```

## Mixing fixed-width types

Two different fixed widths cannot be combined in one expression. The compiler
rejects the expression rather than converting one side:

<!-- tpy: expect-error="Invalid operand types" -->
```python
from tpy import Int32, Int64

def main():
    a: Int32 = 5
    b: Int64 = 10
    print(a + b)         # error: Int32 and Int64 cannot mix

main()
```

```
error: Invalid operand types for '+': Int32 and Int64
```

!!! note
    This strictness is not final. A future version may allow some mixed-width
    expressions, where the widening is unambiguous, to improve ergonomics.

Conversions are written explicitly, in either direction, including to and from
`int`. Mixing an integer with a float needs no conversion; as in Python, the
result is a float:

<!-- tpy: run -->
```python
from tpy import Int32, Int64

def main():
    b: Int64 = 10
    a = Int32(b)             # explicit narrowing
    n = int(a)               # fixed-width to int
    print(a, Int64(a), n, Int32(n))
    print(a + 0.5)           # int-float mix gives a float: 10.5

main()
```

A conversion checks its range at runtime. `Int32(n)` with a value outside the
`Int32` range does not truncate; it panics:
`TurboPython panic: Int32 overflow: value out of range`.

Mixing a fixed-width type with `int` promotes silently. The expression
`Int32 + int` compiles, and the result is `int`. One `int` in a hot loop turns
fixed-width arithmetic into big-integer arithmetic. A stray `int` usually comes
from a literal past the `Int32` range or a value built with `int()`.
[Writing efficient TPy](efficiency.md) returns to this.

<!-- tpy: run -->
```python
from tpy import Int32

def main():
    a: Int32 = 5
    n: int = 100
    c = a + n        # c is int -- the Int32 side is promoted
    print(c)

main()
```

Overflow panics rather than wrapping. Fixed-width arithmetic that exceeds the
type's range stops the program, in optimized builds too. A panic is not an
exception: `try`/`except` cannot catch it. Where the range of a value is not
certain, a wider type or `int` is the right choice.

```python
from tpy import Int32

def main():
    k: Int32 = 2147483647
    print(k + 1)          # panics: Int32 overflow

main()
```

```
TurboPython panic: Int32 overflow in addition
```

!!! note "Overflow behavior"
    Fixed-width overflow currently panics and stops the program. This is not
    yet configurable; a future version may offer other behavior, such as
    wrapping or a catchable exception.

## Strings

The default string type is `str`. It matches Python's string for methods,
comparison, and iteration, apart from two differences worth knowing. Indexing yields a `Char` rather than a length-one string, though
a `Char` still compares against a string literal and converts to `str` freely.
A plain-range slice such as `s[0:5]` is a view of the original bytes and does
not copy, while a stepped slice, `s[i:j:k]`, returns an owned copy.

<!-- tpy: run -->
```python
from tpy import Char

def main():
    s = "hello world"
    c: Char = s[0]       # a single character
    if c == "h":         # a Char compares to a str literal
        print("first is h")
    head = s[0:5]        # a slice is a view -- no copy
    print(head, s.upper())

main()
```

Formatted string literals (f-strings) work as in Python. They interpolate
values into a string and apply the usual format specifiers:

<!-- tpy: run -->
```python
def main():
    name = "boiler-3"
    temp = 21.5
    print(f"{name}: {temp:.1f} C")   # boiler-3: 21.5 C

main()
```

Underneath, the compiler represents a `str` as owned bytes or as a view of
another string's bytes, whichever is provably safe, so the copy often never
happens. Either way a `str` behaves as an independent value. Two more string
types exist for when performance or ownership matters:

- `String`: an owned, growable string. It holds its own bytes and grows in
  place, which makes it the type for building up text such as accumulated
  output. A `String` passes wherever a `str` is expected.
- `StrView`: a string that is always a non-owning view and never copies. In a
  signature it states that no copy happens at that boundary; as a value it
  refers to part of a larger string without copying it.

<!-- tpy: run -->
```python
from tpy import String

def main():
    out = String("sensor=")
    out += "boiler-3"
    out += ";ok"
    print(out, len(out))

main()
```

<!-- tpy: run -->
```python
from tpy import StrView

def main():
    s = "hello world"
    v = StrView(s)       # always a view of s
    tail = v[6:]         # slicing a view is free
    print(v, tail)

main()
```

## Value types and reference types

The numeric types, `bool`, `Char`, `str`, and tuples of these are **value
types**. A value lives directly in its variable and is copied on assignment, so
an assigned or stored value is independent of the original. Class instances and
containers are **reference types**. Locals and parameters alias them, and
durable storage owns them. Durable storage was introduced on [the
map](differences.md); [Ownership and references](ownership.md) covers the full
model and its observable consequences.

A small `Reading` type combines one value-type field and one owned container:

<!-- tpy: prelude -->
```python
from tpy import Own

class Reading:
    sensor: str
    values: list[float]
    def __init__(self, sensor: str, values: Own[list[float]]):
        self.sensor = sensor
        self.values = values
```

The `sensor` field is a value type and copies freely. The `values` field is a
container that the `Reading` owns, and the `Own[...]` parameter takes the
caller's list -- the caller gives the list up instead of keeping a shared
reference. [Ownership and references](ownership.md) explains this *move*.

<!-- tpy: cont run -->
```python
def mean(r: Reading) -> float:
    return sum(r.values) / len(r.values)

def main():
    r = Reading("boiler-3", [20.5, 21.0, 21.7])
    print(r.sensor, mean(r))

main()
```

Containers themselves -- lists, dicts, sets, and how they model data -- are
the subject of [Data modeling](data-modeling.md).

## Optional values

A value that may be absent is a union with `None`, written `T | None`. The
compiler tracks which member the value currently holds and warns where a
possible `None` is used as a plain `T`. A check such as `is not None` narrows
the value back to a plain `T`:

<!-- tpy: run -->
```python
def first_over(values: list[int], limit: int) -> int | None:
    for v in values:
        if v > limit:
            return v
    return None

def main():
    hit = first_over([1, 5, 9], 4)
    if hit is not None:
        print("first over 4:", hit)   # hit is int here
    else:
        print("none over 4")

main()
```

General union types `A | B` and the `match` that branches on them are covered
in [Data modeling](data-modeling.md).

The next page follows these types across function boundaries:
[Functions and API boundaries](functions.md).
