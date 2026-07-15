# Functions and API boundaries

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

A function signature in TurboPython is a compiled contract. The compiler
checks every call against it and generates code from it. A signature also
decides representation at every call, and it is where the ownership model
becomes visible. A call either copies the argument, mutates it, or keeps it.
This page covers what a signature promises and how
to design small, clear APIs. The examples use the `Reading` class
from the [Types page](types.md).

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

## A signature is a contract

Parameter and return types are mandatory; the compiler rejects an unannotated
signature ([the map](differences.md) shows the diagnostic). Default values,
keyword arguments, and annotated `*args` work as in Python:

<!-- tpy: run -->
```python
from tpy import Float64, Int32

def scale(x: Float64, factor: Float64 = 2.0) -> Float64:
    return x * factor

def total(*xs: Int32) -> Int32:
    t: Int32 = 0
    for x in xs:
        t += x
    return t

def main():
    print(scale(3.0))               # 6.0
    print(scale(3.0, factor=0.5))   # 1.5
    print(total(1, 2, 3))           # 6

main()
```

Keyword-argument collection is restricted. A plain `**kwargs: T` is rejected,
and the typed form (`Unpack[TypedDict]`) is required.

## Passing borrows

Passing a reference-type object never copies it. The parameter *borrows* the
caller's object -- in Python terms, it aliases it: it becomes another name for
the same object. A mutation made inside the function is therefore visible to
the caller. ([Ownership and references](ownership.md), the next page, defines
borrowing in full.)

<!-- tpy: cont run -->
```python
def add_value(r: Reading, v: Float64) -> None:
    r.values.append(v)

def main():
    r = Reading("boiler-3", [20.5])
    add_value(r, 21.0)
    print(len(r.values), r.values[1])   # 2 21.0

main()
```

When a function does not mutate a parameter, the object is passed read-only,
still without copying. No annotation is needed. The compiler reads the
function body and sees that the parameter is never mutated.

Methods follow the same rules. `self` is a borrowed parameter. Mutation
through it is visible to the caller, and the read-only check works the same
way. Classes have their own page: [Data modeling](data-modeling.md).

Value types (`Int32`, `float`, `str`, ...) are passed as copies. Reassigning
the parameter changes the copy, never the caller's variable -- observably the
same as Python:

<!-- tpy: run -->
```python
from tpy import Int32

def bump(x: Int32) -> Int32:
    x += 1        # changes the local copy only
    return x

def main():
    n: Int32 = 5
    m = bump(n)
    print(n, m)   # 5 6

main()
```

## Returning: a reference or a fresh object

For reference types, a plain return type returns a *reference*. That is the
right shape when the object outlives the function -- an element of a caller's
list, a field of a parameter. A freshly built object needs `Own[...]`: the
caller takes ownership. (Value types are returned by copy, as always.)

<!-- tpy: prelude -->
```python
def first(items: list[Reading]) -> Reading:
    return items[0]          # a reference into the caller's list

def load(sensor: str) -> Own[Reading]:
    return Reading(sensor, [20.5, 21.0])   # ownership moves to the caller
```

Returning a local by plain reference is a compile error;
[Ownership and references](ownership.md) shows the diagnostic and the rule.

## Taking ownership at the boundary

An `Own[T]` parameter declares that the function keeps the object -- typically
to store it. `Reading`'s own constructor does this with its list:
`values: Own[list[Float64]]` moves the caller's list into the field.

At the call site the caller writes nothing extra. An `Own` return is used like
any other object, and passing to an `Own` parameter at the argument's last use
hands the object over with no copy:

<!-- tpy: cont run -->
```python
def archive(store: list[Reading], r: Own[Reading]) -> None:
    store.append(r)          # the function keeps the object

def main():
    store: list[Reading] = []
    r = load("boiler-3")     # r is used like any other Reading
    print(r.sensor)          # boiler-3
    archive(store, r)        # last use of r -- handed over, no copy
    print(len(store))        # 1

main()
```

A caller that keeps using the argument afterwards should pass `copy(...)`;
otherwise the compiler makes the copy anyway and warns about it. The mechanics
are on [the ownership page](ownership.md).

## Absent results are unions

A function that may find nothing returns `T | None`, and the caller narrows
before use, as shown on [the map](differences.md):

<!-- tpy: cont run -->
```python
def find(items: list[Reading], sensor: str) -> Reading | None:
    for r in items:
        if r.sensor == sensor:
            return r
    return None

def main():
    items: list[Reading] = [Reading("a", [1.0]), Reading("b", [2.0])]
    hit = find(items, "b")
    if hit is not None:
        print(hit.sensor)            # b
    print(find(items, "zz") is None) # True

main()
```

## Designing a small API

A signature tells the caller what happens to the argument. Five shapes cover
almost every function:

| The function... | Signature shape |
|---|---|
| reads data | `def mean(r: Reading) -> Float64` -- borrowed; the compiler verifies read-only |
| modifies in place | `def add_value(r: Reading, v: Float64) -> None` -- borrowed, mutated |
| creates an object | `def load(sensor: str) -> Own[Reading]` -- ownership to the caller |
| keeps its argument | `def archive(r: Own[Reading]) -> None` -- ownership from the caller |
| may find nothing | `def find(...) -> Reading \| None` -- composes with the shapes above |

The everyday case is a plain `T` parameter and a plain `T` or value-type
return. `Own[...]` appears exactly where an object crosses into or out of
long-lived storage. Ownership itself is the next page:
[Ownership and references](ownership.md).
