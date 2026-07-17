# Data modeling

TurboPython programs model data with the same building blocks as Python.
Classes describe records with behavior, containers hold collections, tuples
group a fixed set of values, and unions describe a value that is one of several
alternatives. All are written as in Python, and the largest departure is that
method calls bind at compile time.

## Classes

Fields are declared as annotations and form a fixed set. Methods are written as
in Python, and `self` is a borrowed parameter
([Functions and API boundaries](functions.md) covers borrowing). Dunder methods
work too -- `__str__` drives `print` and f-strings, and `__eq__` drives `==`.
Class-level field defaults, `@property`, and `@staticmethod` all work.

The `Reading` example from the earlier pages, extended to a full class:

<!-- tpy: prelude -->
```python
from tpy import Own, Int32

class Reading:
    sensor: str
    values: list[float]

    def __init__(self, sensor: str, values: Own[list[float]]):
        self.sensor = sensor
        self.values = values

    def add(self, v: float) -> None:
        self.values.append(v)

    def mean(self) -> float:
        return sum(self.values) / len(self.values)

    @property
    def count(self) -> Int32:
        return len(self.values)

    def __str__(self) -> str:
        return f"Reading({self.sensor}, n={len(self.values)})"
```

<!-- tpy: cont run -->
```python
def main():
    r = Reading("boiler-3", [20.5, 21.0])
    r.add(21.7)
    print(r)                  # __str__: Reading(boiler-3, n=3)
    print(r.count, r.mean())  # 3 21.066...

main()
```

## Inheritance and dispatch

Inheritance works, but overriding does not dispatch dynamically. A call
through a base-typed reference calls the base method, and the compiler warns
about every override that would behave differently under CPython:

```python
class Animal:
    name: str
    def __init__(self, name: str):
        self.name = name
    def sound(self) -> str:
        return "..."

class Dog(Animal):
    def __init__(self, name: str):
        super().__init__(name)
    def sound(self) -> str:   # warning: hides Animal.sound (bound statically)
        return "woof"
```

```
warning: Method 'Dog.sound' hides 'Animal.sound' -- any 'Animal' reference
will call 'Animal.sound', not 'Dog.sound' (differs from Python's dynamic
dispatch); make 'Animal' a @dynamic protocol for runtime dispatch
```

!!! warning "Differs from CPython"
    In CPython, calling `sound()` on a `Dog` held in an `Animal`-typed
    variable runs `Dog.sound` -- dispatch is dynamic. In TurboPython the call
    binds at compile time to `Animal.sound`. The compiler flags every such
    override with the `hides ... differs from Python's dynamic dispatch`
    warning shown above. The fix is a `@dynamic` protocol, which restores
    runtime dispatch where a design needs it ([Beyond the core](beyond.md)).

In TurboPython, polymorphism is usually modeled without inheritance: a
protocol when several types share behavior, a union when a value is one of a
fixed set of alternatives. In both, the data stays on the concrete classes;
the protocol or union carries only the choice.

## Protocols

A protocol is a named interface -- a set of method signatures with no bodies.
Any class whose methods match satisfies the protocol automatically, with no
inheritance and no registration. Conformance is checked at compile time:

<!-- tpy: run -->
```python
from typing import Protocol

class Measurable(Protocol):
    def size(self) -> int: ...

class Batch:
    n: int
    def __init__(self, n: int):
        self.n = n
    def size(self) -> int:
        return self.n

def total(m: Measurable) -> int:
    return m.size()

def main():
    print(total(Batch(5)))   # 5

main()
```

By default a protocol is resolved statically. Each call site is compiled
against the concrete type it receives, at no runtime cost. A protocol marked
`@dynamic` (from `tpy`) instead dispatches through a vtable, so a single
reference can hold different implementers chosen at runtime, the way
inheritance does in Python. [Beyond the core](beyond.md) covers `@dynamic`
protocols.

## Containers

`list`, `dict`, and `set` work as in Python and nest freely. A dict keeps
insertion order, as in Python. A container owns its elements
([Ownership and references](ownership.md)).

<!-- tpy: run -->
```python
def main():
    by_sensor: dict[str, list[float]] = {}
    by_sensor["boiler-3"] = [20.5, 21.0]
    by_sensor["boiler-7"] = [19.0]
    if "boiler-3" in by_sensor:
        by_sensor["boiler-3"].append(21.7)
    for name in by_sensor:            # insertion order, as in Python
        print(name, len(by_sensor[name]))
    seen: set[str] = set()
    seen.add("boiler-3")
    seen.add("boiler-3")
    print(len(seen))                  # 1

main()
```

Sorting accepts Python's key functions, including lambdas:

<!-- tpy: run -->
```python
def main():
    xs: list[float] = [3.0, 1.0, 2.0]
    print(sorted(xs, key=lambda v: -v))   # [3.0, 2.0, 1.0]

main()
```

## Tuples

A tuple groups a fixed number of values, each of its own type, and behaves as
in Python. Elements are reached by a constant index or by unpacking, and tuples
compare element by element. A tuple of hashable values also works as a
dictionary key.

<!-- tpy: run -->
```python
def main():
    pair: tuple[str, float] = ("mean", 20.9)
    label, value = pair                # unpack
    print(label, value)                # mean 20.9
    print(pair[0])                     # index with a constant
    print(("a", 1) == ("a", 1))        # True -- element-wise comparison
    seen: dict[tuple[int, int], str] = {(1, 2): "cell"}
    print((1, 2) in seen)              # True -- a tuple works as a dict key

main()
```

Each element keeps the passing semantics it would have on its own. A value-type
element is copied; a reference-type element is held by reference, the same way
a standalone parameter or return of that type would be. Wrapping a value in a
tuple slot therefore does not change how it is passed: a function whose return
type goes from `Reading` to `tuple[Reading, bool]` still returns the `Reading`
by reference. [Ownership and references](ownership.md) covers the rules the
elements follow.

## Unions

A union describes a value that is exactly one of several classes, written
`A | B`. A `match` statement branches on the member a value holds and binds its
fields in the pattern:

<!-- tpy: run -->
```python
class Circle:
    radius: float
    def __init__(self, radius: float):
        self.radius = radius

class Square:
    side: float
    def __init__(self, side: float):
        self.side = side

def area(shape: Circle | Square) -> float:
    match shape:
        case Circle(radius=r):
            return 3.14159 * r * r
        case Square(side=s):
            return s * s

def main():
    print(area(Circle(1.0)))    # 3.14159
    print(area(Square(2.0)))    # 4.0

main()
```

A union used in more than one place can be named with a `type` alias, written
`type Shape = Circle | Square`, and the name then stands for the union anywhere
a type is expected.

A `match` that misses a member cannot fall through silently. With a declared
return type, every path must return, and a guarded `case` does not count as
covering its member, so the bare `case Sample():` below is required:

<!-- tpy: prelude run -->
```python
class Sample:
    value: float
    def __init__(self, value: float):
        self.value = value

class Gap:
    reason: str
    def __init__(self, reason: str):
        self.reason = reason

def describe(x: Sample | Gap) -> str:
    match x:
        case Sample(value=v) if v > 21.0:
            return "high"
        case Sample():
            return "normal"
        case Gap(reason=r):
            return f"missing: {r}"

def main():
    print(describe(Sample(21.5)))            # high
    print(describe(Sample(20.0)))            # normal
    print(describe(Gap("sensor offline")))   # missing: sensor offline

main()
```

A union stores in containers like any other value, and `case _:` is a valid
catch-all pattern:

<!-- tpy: cont run -->
```python
def main():
    stream: list[Sample | Gap] = [Sample(20.5), Gap("offline"), Sample(21.5)]
    good = 0
    for x in stream:
        match x:
            case Sample():
                good += 1
            case _:
                pass
    print(good, len(stream))   # 2 3

main()
```

For a one-off test, `isinstance(x, Sample)` is also valid on a union value.
Unions with `match` replace `isinstance` chains, and often replace a whole
inheritance hierarchy.

## Dataclasses

`@dataclass` writes the methods a plain class spells out by hand. It is a
built-in compile-time macro that generates `__init__`, `__repr__`, and `__eq__`
from the annotated fields. Passing `frozen=True` additionally makes instances
hashable, so they can serve as dict keys or set members. The decorator is
imported from `dataclasses`, as in Python.

<!-- tpy: run -->
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Cell:
    row: int
    col: int

def main():
    p = Point(1.0, 2.0)
    print(p)                        # Point(x=1.0, y=2.0)
    print(p == Point(1.0, 2.0))     # True
    grid: dict[Cell, str] = {Cell(0, 0): "origin"}
    print(grid[Cell(0, 0)])         # origin -- frozen is hashable

main()
```

How programs branch and fail -- `None` narrowing, `try`/`except`, iterators --
is the next page: [Control flow, None & errors](control-flow.md).
