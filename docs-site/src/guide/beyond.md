# Beyond the core

The guide so far is the core language: the type system, ownership, data
modeling, control flow, and the build. This page is a short survey of
everything else -- what exists today and how mature it is.
[Compatibility](../compatibility.md) is the single source of truth for exact
status.

## Async

Coroutines (`async def`), `await`, tasks, and `asyncio`-style entry points
compile and run:

<!-- tpy: run -->
```python
import asyncio

async def fetch(n: int) -> int:
    await asyncio.sleep(0.01)
    return n

async def amain() -> None:
    t = asyncio.create_task(fetch(40))
    u = asyncio.create_task(fetch(2))
    print(await t + await u)   # 42

asyncio.run(amain())
```

!!! info "Limited today"
    The executor is single-threaded. `asyncio.run`, `create_task`, `sleep`,
    and awaiting results work; `gather` works with an explicit type argument
    (`gather[int](...)`) and returns a list. Timeouts, streams, and the wider
    `asyncio` surface are not covered yet.
    [Compatibility](../compatibility.md) tracks the exact boundary.

## Threads

There is no GIL, and no `threading` module either. Threads are TurboPython's
own API, modeled on Rust's threads. The `spawn` function takes an owned task
and returns a handle to join. It checks at compile time that the task is safe
to send across threads (`Send`):

<!-- tpy: run -->
```python
from tpy.thread import spawn
from tpy import Int32

class Job:
    n: Int32
    def __init__(self, n: Int32):
        self.n = n
    def run(self) -> Int32:
        return self.n * 2

def main():
    h = spawn(Job(21))
    print(h.join())        # 42

main()
```

Cross-thread sharing goes through `Arc` ([Ownership](ownership.md)), and
`Atomic[T]` covers shared counters. `Mutex[T]` and `RwLock[T]` guard shared
mutable state, and `Condvar` blocks until a condition holds -- Rust's
`std::sync` primitives, from `tpy.sync`. The cross-thread and async-interop
surface is still partial; [Compatibility](../compatibility.md) tracks what
works today.

## Generators and iterators

Generator functions, generator expressions, and hand-written iterators work.
The one exception is `yield from`, which is not supported yet; the compiler
rejects it with a diagnostic.

## First-class functions

Functions are values. A function can be passed by name, a `lambda` bound
wherever a callable is expected, and a nested `def` can close over the
enclosing frame's locals -- `nonlocal` makes a captured local mutable.

Two callable types mark the trade-off. `Fn[[A], R]` is a zero-cost callback
for a parameter, inlined like a C++ template with no allocation or
indirection. `Callable[[A], R]` is a type-erased callable -- a
`std::function` -- that can also live in a field, a return, or a container,
where the concrete function is not known until runtime. A `lambda` infers its
parameter types from the type the context expects.

## Protocols and dynamic dispatch

Structural protocols work and are static by default
([Data modeling](data-modeling.md)). `@dynamic` opts a protocol into runtime
dispatch -- the compiler's own suggested fix wherever an override would have
dispatched dynamically under CPython.

!!! info "Limited today"
    A protocol type cannot yet be a container element (`list[Speaker]` is
    rejected), which limits the classic heterogeneous-collection pattern.
    [Compatibility](../compatibility.md) tracks this.

## Enums

`enum.Enum` and `IntEnum` work, with `auto()` values, `.name` and `.value`,
identity and equality comparison, iteration over the members, and value or
name lookup (`Color(0)`, `Color["red"]`). A `match` can branch on enum
members, and an enum compiles to a C++ `enum class`.

## Network, processes, and the wider stdlib

An HTTP client exists in early form (`tplib.requests`), and TLS works for both
HTTPS clients and servers. `subprocess` and `multiprocessing` do not exist.
For a services stack, the missing pieces are still large;
[Compatibility](../compatibility.md) is the place to check before planning a
port.

## Native interop

Native interop runs in two directions. A TurboPython module compiles into a
CPython extension (`# tpy: ext_module`, [Building](building.md)). Existing C++
binds into TurboPython with `@native`, mapping a class or function onto a C++
type or call -- the standard library itself is built this way. `@native` is
usable but undocumented; the API may change.

## Macros

A compile-time macro mechanism exists inside the compiler -- several built-in
decorators are implemented as compile-time macros. A user-facing macro system
is not documented or supported yet. [Compatibility](../compatibility.md)
records its status.

This closes the core guide. For readers coming from a systems language,
[Coming from C++/Rust](cpp-rust.md) maps the language onto C++ and Rust terms.
[Getting started](../getting-started.md) and
[Compatibility](../compatibility.md) cover the practical side, and
[the map](differences.md) gives the overview again at any time.
