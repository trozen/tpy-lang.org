# Control flow, None & errors

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

Branching and looping are ordinary Python: `if`/`elif`/`else`, `for`, `while`,
`break`, `continue`, and `with` all work unchanged. This page covers the three
places where control flow meets the type system: narrowing away `None`,
exceptions, and writing an iterator.

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

## Narrowing away `None`

A value of type `T | None` cannot be used as a plain `T`; the compiler warns
and inserts a runtime check ([the map](differences.md) shows the warning). A
check on the value *narrows* it: inside the checked branch, the type is `T`
and the warning is gone. `is None` and `is not None` comparisons, truth-value
checks (`if r:`), early returns, and `assert` all narrow:

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

## Exceptions work like Python

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
re-raises the active one. Catching several types in one clause
(`except (A, B)`) is not supported today; the compiler rejects it.
[Compatibility](../compatibility.md) tracks the status.

An ordinary `raise` compiles to a C++ exception. A `try` block costs nothing
while nothing is raised; actually raising is comparatively expensive.
Exceptions are the right shape for failures, not for hot-path control flow --
which is why `__next__` gets special treatment below.

!!! warning "Silent difference from CPython"
    For a user-defined exception class, `print(e)` prints the exception
    object rather than its message, and no diagnostic flags this today.
    Built-in exceptions print the message, matching CPython. `str(e)` and
    f-string formatting (`f"failed: {e}"`) return the message on both
    runtimes, as in the example above.

Exceptions are for failures the program can handle. They are distinct from
*panics* -- integer overflow, a failed narrowing conversion -- which stop the
program and cannot be caught ([the types page](types.md) covers them).

## An iterator is two methods

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

The `raise StopIteration` costs nothing at runtime. The compiler rewrites
every `__next__` so that the end of iteration is signaled without throwing
(the `@error_return` rewrite, applied automatically;
[Writing efficient TPy](efficiency.md) covers the rare explicit form). Generator functions
(`yield`, annotated `-> Iterator[T]`) are the shorter way to write the same
thing, as shown on [the map](differences.md).

## In practice

| The situation | The tool |
|---|---|
| A value may be absent | `T \| None`; narrow once, where the `None` can appear |
| A failure the program can handle | `raise` an exception class; `try`/`except` as in Python |
| An unrecoverable violation (overflow, bad narrowing) | nothing -- a panic stops the program, by design |
| Custom iteration | `__iter__` + `__next__` + `raise StopIteration`, no runtime cost |

The next page consolidates all of this into performance guidance:
[Writing efficient TPy](efficiency.md).
