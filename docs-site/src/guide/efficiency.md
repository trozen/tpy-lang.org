# Writing efficient TPy

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

Efficient TurboPython is mostly ordinary TurboPython. There is no interpreter,
no garbage collector, and no reference counting to pay for. The rules that
keep it efficient concern how values are represented and how they move. The
constraint decorators turn those rules into compiler checks.

Hot paths are found the usual way: profile the logic under CPython, where the
same code usually runs unchanged, or time the compiled binary. The generated
C++ can also be inspected directly ([Building & running](building.md)).

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

## Let values move; copy on purpose

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
`list[Float64]` is one contiguous block of machine floats, not boxed
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

## Constrain the hot path

The markers above make efficient code possible; the constraint decorators
make it checked. Two are enforced today; `@noalloc` is declared but not yet
checked.

The `@nocopy` decorator on a class forbids every implicit copy of that type.
Code that would have compiled with a copy warning becomes an error:

<!-- tpy: prelude -->
```python
from tpy import nocopy, Own, Float64

@nocopy
class Frame:                 # hot data: copying is never acceptable
    values: list[Float64]
    def __init__(self, values: Own[list[Float64]]):
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

The `@readonly` decorator on a method promises the object is not mutated, and
the compiler enforces the promise ([Ownership](ownership.md) covers the
parameter form, `readonly[T]`):

```python
from tpy import readonly, Own, Float64

class Reading:
    sensor: str
    values: list[Float64]
    def __init__(self, sensor: str, values: Own[list[Float64]]):
        self.sensor = sensor
        self.values = values

    @readonly
    def first(self) -> Float64:   # mutating self here is a compile error
        return self.values[0]
```

The `@noalloc` decorator declares that a function must not allocate.

!!! info "Limited today"
    The compiler accepts `@noalloc` but does not enforce the no-allocation
    check yet. [Compatibility](../compatibility.md) tracks it.

One more tool exists at this level: `@error_return(E)`, the explicit form of
the rewrite that makes `raise StopIteration` free
([Control flow](control-flow.md)). It is rarely written by hand; iterators
get it automatically.

## The checklist

| On a hot path | The tool |
|---|---|
| Arithmetic | fixed-width types; convert `int` once, at the boundary |
| A store that warns about a copy | restructure to a move, construct in place, or take `Own[T]` |
| A copy that is genuinely needed | `copy()` -- the copy is deep |
| Reading without mutating | plain parameters (read-only is inferred); slices and `StrView` for text |
| A type that must never be copied | `@nocopy` on the class |
| A method that must not mutate | `@readonly` |
| An exception on the hot path | usually return `T \| None` instead of raising; `@error_return` exists |

Everything here follows from one model. A type fixes an object's
representation, and each object has a single owner, which is what makes copies
avoidable. Parallelism -- threads without a GIL -- is deferred to
[Beyond the core](beyond.md). [Building & running](building.md) covers running
a script, inspecting the generated C++, and producing a standalone binary.
