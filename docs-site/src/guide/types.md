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
machine numbers: `int8`, `int16`, `int32`, `int64`, the unsigned `uint8`
through `uint64`, and `float32`. `float64` is an alias for `float`. `bool` and
`char` complete the set.

The lowercase names are machine representations, spelled like Python's own
`int`, `float`, and `bool`. Capitalized names such as `String`, `StrView`,
`BigInt`, `Span`, and `Own` are abstractions built over them.

Literals infer a concrete type. A plain integer literal is `int32`, a decimal
literal is `float`:

<!-- tpy: run -->
```python
def main():
    n = 5            # int32
    x = 1.5          # float
    flag = True      # bool
    name = "boiler"  # str
    print(n, x, flag, name)

main()
```

A literal that does not fit `int32` falls back to `int`, and the compiler says
so:

```python
def main():
    big = 5_000_000_000   # warning: outside int32 range, inferring int
    print(big)

main()
```

```
warning: Integer literal 5000000000 is outside default int32 range;
inferring int (BigInt).
```

!!! note "Default integer type"
    Unannotated integer literals currently infer `int32`. This default can be
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

An operator whose operands have different fixed widths converts the narrower
operand to the wider type, and the result has the wider type. A conversion
exists where no value can be lost: to a wider type of the same signedness, or
from an unsigned type into a strictly wider signed one (`uint16` into
`int32`). The operation is the wider type's, so its overflow check applies
at that width:

<!-- tpy: run -->
```python
from tpy import int32, int64

def main():
    a: int32 = 5
    b: int64 = 9_000_000_000
    print(a + b)         # int64: 9000000005

main()
```

A pair with no such direction, such as `int32` with `uint32`, has no common
fixed-width type, and the compiler rejects the expression rather than
choosing one:

<!-- tpy: expect-error="Invalid operand types" -->
```python
from tpy import int32, uint32

def main():
    a: int32 = 5
    b: uint32 = 10
    print(a + b)         # error: neither type holds the other

main()
```

```
error: Invalid operand types for '+': int32 and uint32
```

Arithmetic on 8- and 16-bit operands computes in the default integer type, as
CPython's unbounded integers would: two `uint8` values of 200 and 100 add to
300, an `int32`. Bitwise operators (`&`, `|`, `^`, `>>`) keep the narrow
type.

A fixed-width slot accepts any integer. A value that widens into the slot is
stored as it is; any other value -- a wider or differently signed fixed
width, or an `int` -- passes a runtime range check that raises
`OverflowError` when it does not fit. The rule holds at every slot:
assignment, argument, return, field, and container element. The type's
constructor, as in `int32(b)`, spells the same checked conversion explicitly.
An integer literal that does not fit the slot is rejected at compile time.
Mixing an integer with a float needs no conversion; as in Python, the result
is a float:

<!-- tpy: run -->
```python
from tpy import int32, int64

def main():
    b: int64 = 10
    a: int32 = b             # checked narrowing at the slot
    n = int(a)               # fixed-width to int
    print(a, int32(b), n, int32(n))
    print(a + 0.5)           # int-float mix gives a float: 10.5

main()
```

A variable does not change between the two, though. Rebinding an integer
local with a float, or growing it with `*=` by a float, is a compile error
rather than a silent widening, and the error names the fix: write the literal
as a float, or annotate the variable as `float`. A list literal or a
conditional expression that mixes the two is rejected the same way; a slot
declared `float` still accepts an integer, as in Python.

<!-- tpy: expect-error="is bound to int" -->
```python
def main():
    x = 14
    x *= 1.3         # error: x is bound to int, and *= makes it float
    print(x)

main()
```

```
error: 'x' is bound to int at line 2 and '*=' makes it float here, and
CPython keeps each value's own type; write 14.0 instead of 14, or annotate
x: float
```

A conversion checks its range at runtime. `int32(n)` with a value outside the
`int32` range does not truncate; it raises
`OverflowError: int32 overflow: value out of range`.

Mixing a fixed-width type with `int` promotes silently. The expression
`int32 + int` compiles, and the result is `int`. One `int` in a hot loop turns
fixed-width arithmetic into big-integer arithmetic. A stray `int` usually comes
from a literal past the `int32` range or a value built with `int()`.
[Writing efficient TPy](efficiency.md) returns to this.

!!! note "Promotion behavior"
    Silent promotion to `int` is the current behavior, not a settled one. A
    future version may warn on the promoting operation or reject it, so that
    the trap surfaces at compile time.

<!-- tpy: run -->
```python
from tpy import int32

def main():
    a: int32 = 5
    n: int = 100
    c = a + n        # c is int -- the int32 side is promoted
    print(c)

main()
```

Overflow raises rather than wrapping. Fixed-width arithmetic that exceeds the
type's range raises `OverflowError`, in optimized builds too, and the program
can catch it like any other exception. Where the range of a value is not
certain, a wider type or `int` is the right choice.

<!-- tpy: run -->
```python
from tpy import int32

def main():
    k: int32 = 2147483647
    try:
        print(k + 1)
    except OverflowError as e:
        print("caught:", e)  # caught: int32 overflow in addition

main()
```

Where wrapping is the intended arithmetic, as in hashing and checksums, each
fixed-width type provides it explicitly. `T.wrap(x)` converts modulo 2**bits
into the type's range instead of checking, and `T.wrap_add`, `T.wrap_sub`,
`T.wrap_mul`, `T.wrap_shl` and `T.wrap_shr` compute the wrapped result of one
operation. They are static methods rather than methods on the value, so the
same code runs under CPython, where a fixed-width value is often a plain
`int`:

<!-- tpy: run -->
```python
from tpy import int32, uint32

def fnv1a(data: bytes) -> uint32:
    h: uint32 = 2166136261
    for b in data:
        h = uint32.wrap_mul(h ^ b, 16777619)
    return h

def main():
    k: int32 = 2147483647
    print(int32.wrap_add(k, 1))    # -2147483648
    print(uint32.wrap(-1))         # 4294967295
    print(fnv1a(b"tpy"))           # 2820810480

main()
```

## Strings

The default string type is `str`. It matches Python's string for methods,
comparison, and iteration, apart from two differences worth knowing. Indexing yields a `char` rather than a length-one string, though
a `char` still compares against a string literal and converts to `str` freely.
A plain-range slice such as `s[0:5]` is a view of the original bytes and does
not copy, while a stepped slice, `s[i:j:k]`, returns an owned copy.

<!-- tpy: run -->
```python
from tpy import char

def main():
    s = "hello world"
    c: char = s[0]       # a single character
    if c == "h":         # a char compares to a str literal
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

The numeric types, `bool`, `char`, `str`, and tuples of these are **value
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
