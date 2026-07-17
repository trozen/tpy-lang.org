# Control flow, None & errors

Branching, looping, and iteration in TurboPython are ordinary Python. This page
starts with the everyday constructs, comprehensions, and pattern matching, then
turns to the parts that carry TurboPython-specific rules: narrowing away
`None`, exceptions and panics, and writing iterators and generators.

## Loops and conditionals

`if`/`elif`/`else`, `for`, `while`, `break`, `continue`, and `range` behave as
in Python:

<!-- tpy: run -->
```python
def main():
    total = 0
    for i in range(10):
        if i == 5:
            break            # stop at 5
        if i % 2 == 1:
            continue         # skip odds
        total += i
    print(total)             # 0 + 2 + 4 = 6

    n = 20
    while n > 1:
        n //= 2
    print(n)                 # 1

main()
```

A conditional expression such as `"odd" if n % 2 == 1 else "even"` works as in
Python. Context managers work as well: `with` drives both built-in resources
such as open files and any class that defines `__enter__` and `__exit__`.

## Comprehensions

List, set, and dict comprehensions and generator expressions all work as in
Python:

<!-- tpy: run -->
```python
def main():
    squares = [x * x for x in range(5)]
    evens = {x for x in range(10) if x % 2 == 0}
    index = {x: x * x for x in range(4)}
    total = sum(x * x for x in range(5))    # generator expression
    print(squares)           # [0, 1, 4, 9, 16]
    print(len(evens))        # 5
    print(index[3])          # 9
    print(total)             # 30

main()
```

## Pattern matching

`match` branches on the shape of a value, an alternative to a chain of
`if`/`elif`. It handles primitive values with literal and OR patterns and an
optional guard, and a final `case _` catches the rest:

<!-- tpy: run -->
```python
def classify(n: int) -> str:
    match n:
        case 0:
            return "zero"
        case 1 | 2 | 3:          # OR pattern
            return "small"
        case _ if n < 0:         # guard
            return "negative"
        case _:                  # wildcard
            return "anything else"

def main():
    print(classify(0))     # zero
    print(classify(2))     # small
    print(classify(-5))    # negative
    print(classify(99))    # anything else

main()
```

`match` also destructures classes, binding the fields a pattern names
(`case Circle(radius=r)`), and branches on the members of a union, where the
compiler checks that every member is covered. [Data modeling](data-modeling.md)
shows both forms. A pattern can bind the whole value with `as`, as in
`case Circle() as c`.

Sequence, tuple, and mapping patterns (`case [a, b]`, `case {"k": v}`) are not
available yet.

## Narrowing away `None`

A value of type `T | None` cannot be used as a plain `T`; the compiler warns
and inserts a runtime check. A check on the value *narrows* it, so inside the
checked branch the type is `T` and the warning is gone. `is None` and
`is not None` comparisons, truth-value checks (`if r:`), early returns, and
`assert` all narrow:

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

<!-- tpy: cont run -->
```python
def label(r: Reading | None) -> str:
    if r is None:
        return "no reading"
    return r.sensor              # r is Reading here

def sensor_of(r: Reading | None) -> str:
    assert r is not None         # narrows too
    return r.sensor

def main():
    print(label(None))                             # no reading
    print(label(Reading("boiler-3", [20.5])))      # boiler-3
    print(sensor_of(Reading("boiler-7", [19.0])))  # boiler-7

main()
```

The rule is to narrow once, close to where the `None` can appear, and to pass
plain `T` onward. Functions that take `T | None` make every caller
repeat the check.

A failed `assert` raises an `AssertionError`, catchable like any exception;
uncaught, it stops the program. Optimized builds keep asserts -- there is no
CPython `-O` stripping.

## Exceptions

`raise`, `try`/`except`/`finally`, exception classes, and `except ... as e`
all behave as in Python. An exception class is an ordinary class deriving from
`Exception`:

<!-- tpy: run -->
```python
class ParseError(Exception):
    pass

def parse(text: str) -> int:
    if len(text) == 0:
        raise ParseError("empty input")
    return int(text)

def main():
    try:
        print(parse("42"))       # 42
    finally:
        print("always runs")
    try:
        parse("")
    except ParseError as e:
        print("bad:", str(e))    # bad: empty input

main()
```

`except` on a base class catches derived exceptions, and a bare `raise`
re-raises the active one.

A `try` block costs nothing while nothing is raised; actually raising is
comparatively expensive. Exceptions are the right shape for failures, not for
hot-path control flow -- which is why `__next__` gets special treatment below.

!!! warning "Silent difference from CPython"
    For a user-defined exception class, `print(e)` prints the exception
    object rather than its message, and no diagnostic flags this today.
    Built-in exceptions print the message, matching CPython. `str(e)` and
    f-string formatting (`f"failed: {e}"`) return the message on both
    runtimes, as in the example above.

Exceptions are for failures the program can handle. They are distinct from
*panics* -- integer overflow, a failed narrowing conversion -- which stop the
program and cannot be caught ([the types page](types.md) covers them).

## Iterators

A custom iterator is written exactly as in Python: `__iter__` returns the
iterator, `__next__` returns the next value or raises `StopIteration`. The
same class runs unchanged under CPython:

<!-- tpy: run -->
```python
from tpy import Int32

class Countdown:
    n: Int32
    def __init__(self, n: Int32):
        self.n = n
    def __iter__(self) -> "Countdown":
        return self
    def __next__(self) -> Int32:
        if self.n == 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

def main():
    for i in Countdown(3):
        print(i)                 # 3 2 1

main()
```

The `raise StopIteration` costs nothing at runtime; ending iteration is
signaled without actually throwing. [Writing efficient TPy](efficiency.md)
covers the `@error_return` mechanism behind this and its explicit form.

## Generators

A generator function uses `yield` and is annotated `-> Iterator[T]`. It is the
concise form of the iterator above, with no explicit `__next__`:

<!-- tpy: run -->
```python
from typing import Iterator

def squares(n: int) -> Iterator[int]:
    for i in range(n):
        yield i * i

def main():
    for s in squares(4):
        print(s)             # 0 1 4 9

main()
```

The next page consolidates all of this into performance guidance:
[Writing efficient TPy](efficiency.md).
