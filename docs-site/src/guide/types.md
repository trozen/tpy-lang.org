# Types, inference and values

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

Every value in TurboPython has one static type, fixed at compile time, and the
type decides the representation: how many bytes, where they live, what an
operation costs. Choosing types is the main performance decision a TurboPython
program makes. This page covers the numeric types, what the compiler infers,
the value/reference split, and the string types.

Annotations appear at function boundaries; nearly everything else is inferred.

## Numbers: `int` is exact, fixed-width is fast

The `int` type is Python's integer. It has arbitrary precision, never
overflows, and allocates as it grows. The fixed-width types are fixed-size machine numbers: `Int8`, `Int16`,
`Int32`, `Int64`, unsigned `UInt8` through `UInt64`, and `Float32`. `float` is
`Float64`. `bool` and `Char` complete the set.

Literals infer a concrete type. A plain integer literal is `Int32`, a decimal
literal is `Float64`:

<!-- tpy: run -->
```python
def main():
    n = 5            # Int32
    x = 1.5          # Float64 (float)
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

Arithmetic keeps Python's meaning. `/` is true division and returns a float,
also on fixed-width operands; `//` is floor division; `int` values are exact at
any size:

<!-- tpy: run -->
```python
def main():
    print(7 / 2)      # 3.5
    print(7 // 2)     # 3
    n: int = 2 ** 100
    print(n + 1)      # exact

main()
```

## Widths do not mix implicitly

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

Mixing a fixed-width type with `int` promotes silently. `Int32 + int` compiles,
and the result is `int`. One `int` in a hot loop silently converts fixed-width
arithmetic into big-integer arithmetic. A stray `int` usually comes from a
literal past the `Int32` range or a value built with `int()`.
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

## Value types and reference types

The numeric types, `bool`, `Char`, `str`, and tuples of these are **value
types**. A value lives directly in its variable and is copied on assignment.
For `str` this means an assigned or stored value is independent of the
original; when bytes are really copied is shown below, under Strings. Class
instances and containers are **reference types**. Locals and parameters alias
them, and durable storage owns them. Durable storage was introduced on [the map](differences.md); the
full model, with its observable consequences, is
[Ownership and references](ownership.md).

A small `Reading` type combines one value-type field and one owned container:

<!-- tpy: prelude -->
```python
from tpy import Own, Float64

class Reading:
    sensor: str
    values: list[Float64]
    def __init__(self, sensor: str, values: Own[list[Float64]]):
        self.sensor = sensor
        self.values = values
```

The `sensor` field is a value type and copies freely. The `values` field is a
container that the `Reading` owns, and the `Own[...]` parameter takes the
caller's list -- the caller gives the list up instead of keeping a shared
reference. [Ownership and references](ownership.md) explains this *move*.

<!-- tpy: cont run -->
```python
def mean(r: Reading) -> Float64:
    return sum(r.values) / len(r.values)

def main():
    r = Reading("boiler-3", [20.5, 21.0, 21.7])
    print(r.sensor, mean(r))

main()
```

Containers themselves -- lists, dicts, sets, and how they model data -- are
the subject of [Data modeling](data-modeling.md).

## Optional values and unions

A value that may be absent is a union with `None`: the type is `T | None`, and
the compiler tracks which member it currently holds, warning where a possible
`None` is used as a plain `T`. General unions `A | B` are tagged values that
`match` branches on. Both were shown on [the map](differences.md);
[Data modeling](data-modeling.md) covers them fully.

## Strings: `str`, `String`, `StrView`

The `str` type is the default. It works like Python's string for methods, comparison,
and iteration, with two differences worth knowing. Indexing yields a `Char`,
not a length-one string; a `Char` still compares against a string literal and
converts to `str` freely. A plain-range slice does not copy: `s[0:5]` is a view
of the original bytes. A stepped slice, `s[i:j:k]`, returns an owned copy.

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

The `String` type is the owned string. It holds its own bytes and grows in
place, which makes it the type for accumulating output. A `String` passes wherever a `str`
is expected:

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

A plain `str` always behaves as an independent value. Underneath, the
compiler picks the representation per use -- owned bytes, or a view of another
string's bytes where that is provably safe -- so the copy often never happens.
`StrView` removes the choice: it always refers and never copies. In a
signature it states "no copy here". As a value it refers to part of a larger
string without copying it:

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

The default is `str`; a `String` builds up or owns text explicitly, and a
`StrView` makes a no-copy view part of a signature.

## Choosing a type

| Data | Type |
|---|---|
| Counters, indices, hot arithmetic | `Int32`; `Int64` when values can exceed two billion |
| Genuinely unbounded integers | `int` |
| Real numbers | `float` (`Float32` halves the memory of large arrays) |
| Text, by default | `str` |
| Text built up piece by piece | `String` |
| Text at a boundary, no copies | `StrView` |
| A single character | `Char` |
| Binary data | `bytes` |
| A value that may be absent | `T \| None` |

The next page follows these types across function boundaries:
[Functions and API boundaries](functions.md).
