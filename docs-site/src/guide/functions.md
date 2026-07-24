# Functions and API boundaries

A function signature in TurboPython is a contract the compiler enforces. Where
Python treats an annotation as a hint the runtime ignores, a TurboPython
annotation is binding. A function accepts and returns only the types its
signature allows, and a call that passes anything else does not compile. The
compiler generates the calling code from that same signature, which also fixes
how each argument is represented. That is where the ownership model becomes
visible. A call either copies its argument, mutates it, or keeps it. This page
covers what a signature promises and how to design small, clear APIs, reusing
the `Reading` class from the [Types page](types.md).

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

## Signatures must be fully typed

Parameter and return types are mandatory; the compiler rejects an unannotated
signature. Default values, keyword arguments, and annotated `*args` work as in
Python:

<!-- tpy: run -->
```python
from tpy import Int32

def scale(x: float, factor: float = 2.0) -> float:
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

## Passing borrows

Passing a reference-type object never copies it. The parameter *borrows* the
caller's object -- in Python terms, it aliases it: it becomes another name for
the same object. A mutation made inside the function is therefore visible to
the caller. ([Ownership and references](ownership.md), the next page, defines
borrowing in full.)

<!-- tpy: cont run -->
```python
def add_value(r: Reading, v: float) -> None:
    r.values.append(v)

def main():
    r = Reading("boiler-3", [20.5])
    add_value(r, 21.0)
    print(len(r.values), r.values[1])   # 2 21.0

main()
```

Methods follow the same rules. `self` is a borrowed parameter, and a mutation
through it is visible to the caller. Classes have their own page:
[Data modeling](data-modeling.md).

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

## Returning a reference or a fresh object

For reference types, a plain return type returns a *reference*. That is the
right shape when the object outlives the function -- an element of a caller's
list, a field of a parameter. A freshly built object needs `Own[...]`, which
hands ownership of the object to the caller. (Value types are returned by copy,
as always.)

<!-- tpy: prelude -->
```python
def first(items: list[Reading]) -> Reading:
    return items[0]          # a reference into the caller's list

def load(sensor: str) -> Own[Reading]:
    return Reading(sensor, [20.5, 21.0])   # ownership moves to the caller
```

Returning a local by plain reference is a compile error, covered by
[Ownership and references](ownership.md).

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

## Optional results

A function that may find nothing returns `T | None`, and the caller narrows
before use:

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

`Own[...]` appears only where an object crosses into or out of long-lived
storage; a plain `T` parameter and return cover everything else. The next page,
[Ownership and references](ownership.md), defines the model behind all of this.
