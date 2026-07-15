# Data modeling

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

Programs model data with three tools. Classes describe records with behavior.
Containers hold collections of them. Unions describe a value that is exactly
one of several alternatives. All three are written as in Python. The largest
departure from Python is that method calls bind at compile time.

## Classes are records with methods

Fields are declared as annotations and form a fixed set
([the map](differences.md) shows the diagnostic for an undeclared field).
Methods are ordinary Python methods; `self` is a borrowed parameter, as
[the functions page](functions.md) explains. Dunder methods are ordinary
methods too: `__str__` drives `print` and f-strings, `__eq__` drives `==`.
Class-level field defaults, `@property`, and `@staticmethod` work, and
`@dataclass` generates the constructor as in Python.

The `Reading` example from the earlier pages, extended to a full class:

<!-- tpy: prelude -->
```python
from tpy import Own, Float64, Int32

class Reading:
    sensor: str
    values: list[Float64]

    def __init__(self, sensor: str, values: Own[list[Float64]]):
        self.sensor = sensor
        self.values = values

    def add(self, v: Float64) -> None:
        self.values.append(v)

    def mean(self) -> Float64:
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

A property getter receives `self` read-only.

!!! info "Limited today"
    `mean` stays an ordinary method here: `sum` cannot yet accept a read-only
    list, so it cannot be called from a property.
    [Compatibility](../compatibility.md) tracks this gap.

## Method calls bind at compile time

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

## Protocols are structural

A protocol declares a shape. Any class with matching methods satisfies it --
no inheritance, no registration:

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

The match between class and protocol is checked at compile time.

## Containers hold the records

`list`, `dict`, `set`, and `tuple` work as in Python and nest freely. A dict
keeps insertion order, as in Python. A container owns its elements
([Ownership and references](ownership.md)).

<!-- tpy: run -->
```python
from tpy import Float64

def main():
    by_sensor: dict[str, list[Float64]] = {}
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
    pair: tuple[str, Float64] = ("mean", 20.9)
    label, value = pair               # tuples unpack as usual
    print(label, value)

main()
```

Sorting accepts Python's key functions, including lambdas:

<!-- tpy: run -->
```python
from tpy import Float64

def main():
    xs: list[Float64] = [3.0, 1.0, 2.0]
    print(sorted(xs, key=lambda v: -v))   # [3.0, 2.0, 1.0]

main()
```

## Unions model the alternatives

A union's members are ordinary classes; a fieldless member needs no
`__init__` at all. For plain absence, `T | None` is enough
([the types page](types.md)); a marker class is the better member when the
alternative means something of its own, or will grow fields later.

A `match` statement branches on the union, binds fields in the pattern, and
takes guards. A `match` that misses a member cannot fall through silently.
With a declared return type, every path must return, and a guarded `case` does
not count as covering its member. The bare `case Sample():` below is therefore
required.

<!-- tpy: prelude run -->
```python
from tpy import Float64

class Sample:
    value: Float64
    def __init__(self, value: Float64):
        self.value = value

class Gap:
    pass

def describe(x: Sample | Gap) -> str:
    match x:
        case Sample(value=v) if v > 21.0:
            return "high"
        case Sample():
            return "normal"
        case Gap():
            return "missing"

def main():
    print(describe(Sample(21.5)))   # high
    print(describe(Sample(20.0)))   # normal
    print(describe(Gap()))          # missing

main()
```

A union stores in containers like any other value, and `case _:` is a valid
catch-all pattern:

<!-- tpy: cont run -->
```python
def main():
    stream: list[Sample | Gap] = [Sample(20.5), Gap(), Sample(21.5)]
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

A single check also works, since `isinstance(x, Sample)` is valid on a union value.
Unions with `match` replace `isinstance` chains, and often replace a whole
inheritance hierarchy.

## In practice

| The data is... | Model it as |
|---|---|
| A record with behavior | a class |
| One of a fixed set of alternatives | a union, branched on with `match` |
| Shared behavior across unrelated types | a protocol |
| A collection of records | a container -- it owns its elements |

How programs branch and fail -- `None` narrowing, `try`/`except`, iterators --
is the next page: [Control flow, None & errors](control-flow.md).
