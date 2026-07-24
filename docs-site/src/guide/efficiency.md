# Writing efficient TPy

Efficient TurboPython is mostly ordinary TurboPython. There is no interpreter,
no garbage collector, and no reference counting to pay for. The rules that
keep it efficient concern how values are represented and how they move. The
constraint decorators turn those rules into compiler checks.

Hot paths are found by timing the compiled binary. The generated C++ can also
be inspected directly to confirm how a value is represented
([Building & running](building.md)).

## Keep arithmetic fixed-width

The `int` type is exact and allocates as it grows; the fixed-width types are
fixed-size machine numbers ([Types](types.md)). The trap is silent promotion.
One `int` operand converts a whole expression to big-integer arithmetic. A stray `int`
usually comes from a literal past the `Int32` range or a value built with
`int()`. The fix is an explicit conversion at the boundary:

<!-- tpy: run -->
```python
from tpy import Int32

def main():
    n: int = 100            # arrives as int, e.g. from int(...)
    k = Int32(n)            # converted once, at the boundary
    total: Int32 = 0
    for i in range(3):
        total += k + i      # stays fixed-width all the way
    print(total)            # 303

main()
```

Promotion has no diagnostic today. The first check is the arithmetic itself:
any `int` operand converts the whole expression. For confirmation, the
generated C++ shows a promoted loop directly ([Building](building.md)) -- no
C++ fluency is needed to spot a big-integer type where `int32_t` was expected.

## Move instead of copying

A store into durable storage moves when it can and copies when it must, with
a warning for every copy ([Ownership](ownership.md)). The resolution order:

1. **Restructure so the store is the last use** -- the copy becomes a move.
2. **Construct in place** -- a temporary always moves.
3. **Take `Own[T]` at the boundary** -- the caller gives the object up.
4. **Accept the copy with `copy()`** -- when both the original and the stored
   value are genuinely needed. On a hot path it is the most expensive of the
   four.

The costs behind those four options explain the order. A move relocates a
small fixed-size value and copies no elements. A view -- a borrow, a
contiguous slice, a `StrView` -- costs nothing.
A deep copy allocates and copies everything the object owns; for the
`Reading` class, that is the sensor text plus the whole values buffer (a
`list[float]` is one contiguous block of machine floats, not boxed
elements). A big-integer operation can allocate. These four facts rank almost
every decision on this page.

A copy warning marks a CPython behavior difference *and* a runtime cost. On a
hot path, the resolution order above applies before `copy()` silences the
warning.

## Borrow instead of copying

Passing never copies: parameters borrow, and non-mutating parameters are
passed read-only automatically ([Functions](functions.md)). Slices of `str`
are views, not copies, and `StrView` makes the no-copy view part of a
signature ([Types](types.md)). A plain reference return gives the caller a
borrowed object with no transfer at all. None of this needs annotations; the
gain comes from the copies that are never written.

Beyond copies, allocations come from growing containers, strings, and big
integers.

## Keep dispatch static

Structural protocols and unions resolve at compile time, with no runtime
dispatch cost ([Data modeling](data-modeling.md)). The dynamic escape hatches
trade that away. A `@dynamic` protocol dispatches every method call through a
vtable, and `Any` holds a value of statically unknown type, checking or casting
it against a runtime type tag on each use. `Any` is supported but slow, and it
gives up most of the compiler's static reasoning.

Prefer a static protocol or a union where the set of types is known; reach for
`@dynamic` or `Any` only when the design genuinely needs runtime polymorphism.

## Constrain the hot path

The markers above make efficient code possible; the constraint decorators
make it checked. Two are enforced today, `@nocopy` and `@readonly`; `@noalloc`
and `@hotpath` are planned.

!!! warning "Not available yet"
    `@noalloc` (a function must not allocate) and `@hotpath` (code that must
    stay on the fast path) are accepted but not enforced today, and enforcement
    will not land in the next release. [Compatibility](../compatibility.md)
    tracks their status.

The `@nocopy` decorator on a class forbids every implicit copy of that type.
Code that would have compiled with a copy warning becomes an error:

<!-- tpy: prelude -->
```python
from tpy import nocopy, Own

@nocopy
class Frame:                 # hot data: copying is never acceptable
    values: list[float]
    def __init__(self, values: Own[list[float]]):
        self.values = values
```

<!-- tpy: cont expect-error="cannot be moved into" -->
```python
def main():
    frames: list[Frame] = []
    f = Frame([0.0, 1.0])
    frames.append(f)         # error: f used below; @nocopy forbids the copy
    print(len(f.values))

main()
```

```
error: @nocopy type 'Frame' is used after this point and cannot be moved
into 'value: Own[Frame]'. Remove later uses or restructure the code.
```

(The `value: Own[Frame]` named in the error is `append`'s own parameter.)
The error names the fix, and the move forms compile unchanged:

<!-- tpy: cont run -->
```python
def main():
    frames: list[Frame] = []
    frames.append(Frame([0.0, 1.0]))   # a temporary moves -- no copy
    print(len(frames))                 # 1

main()
```

## Read-only methods

The `@readonly` decorator on a method promises the object is not mutated, and
the compiler enforces the promise ([Ownership](ownership.md) covers the
parameter form, `readonly[T]`):

```python
from tpy import readonly, Own

class Reading:
    sensor: str
    values: list[float]
    def __init__(self, sensor: str, values: Own[list[float]]):
        self.sensor = sensor
        self.values = values

    @readonly
    def first(self) -> float:   # mutating self here is a compile error
        return self.values[0]
```

## Error returns

Exceptions are the throw-and-catch tier of a two-tier model; `@error_return` is
the explicit-propagation tier for hot paths. A function marked
`@error_return(E)` returns its error as a value instead of throwing, so raising
`E` costs nothing while the caller still writes ordinary `try`/`except`. The
error class mixes in `ReturnException`:

<!-- tpy: run -->
```python
from tpy import error_return, ReturnException

class NotFound(Exception, ReturnException):
    pass

@error_return(NotFound)
def find(items: list[int], target: int) -> int:
    for i in range(len(items)):
        if items[i] == target:
            return i
    raise NotFound

def main():
    items = [10, 20, 30]
    try:
        print(find(items, 20))     # 1
    except NotFound:
        print("not found")

main()
```

The same rewrite makes `raise StopIteration` free, so iterators get
`@error_return` automatically ([Control flow](control-flow.md)).

## The checklist

| On a hot path | The tool |
|---|---|
| Arithmetic | fixed-width types; convert `int` once, at the boundary |
| A store that warns about a copy | restructure to a move, construct in place, or take `Own[T]` |
| A copy that is genuinely needed | `copy()` -- the copy is deep |
| Reading without mutating | plain parameters (read-only is inferred); slices and `StrView` for text |
| Runtime polymorphism | static protocols or unions; `@dynamic` and `Any` add dispatch cost |
| A type that must never be copied | `@nocopy` on the class |
| A method that must not mutate | `@readonly` |
| An exception on the hot path | usually return `T \| None` instead of raising; `@error_return` exists |

Everything here follows from one model. A type fixes an object's
representation, and each object has a single owner, which is what makes copies
avoidable. Parallelism -- threads without a GIL -- is deferred to
[Beyond the core](beyond.md). [Building & running](building.md) covers running
a script, inspecting the generated C++, and producing a standalone binary.
