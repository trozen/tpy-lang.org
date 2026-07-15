# Beyond the core

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

The guide so far is the core language: the type system, ownership, data
modeling, control flow, and the build. This page is a short survey of
everything else -- what exists today, how mature it is, and where the guide
covers it. [Compatibility](../compatibility.md) is the single source of
truth for exact status.

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
`Atomic[T]` covers shared counters. The cross-thread and async-interop surface
is still partial; [Compatibility](../compatibility.md) tracks what works today.

## Generators and iterators

Generator functions, generator expressions, and hand-written iterators work.
[The map](differences.md) covers generators, and
[Control flow](control-flow.md) covers iterators (and why `StopIteration`
costs nothing). The one exception is `yield from`, which is not supported yet;
the compiler rejects it with a diagnostic.

## Protocols and dynamic dispatch

Structural protocols work and are static by default
([Data modeling](data-modeling.md)). `@dynamic` opts a protocol into runtime
dispatch -- the compiler's own suggested fix wherever an override would have
dispatched dynamically under CPython.

!!! info "Limited today"
    A protocol type cannot yet be a container element (`list[Speaker]` is
    rejected), which limits the classic heterogeneous-collection pattern.
    [Compatibility](../compatibility.md) tracks this.

## Network, processes, and the wider stdlib

An HTTP client exists in early form (`tplib.requests`), and server-side TLS
works. `subprocess` and `multiprocessing` do not exist. For a
services stack, the missing pieces are still large;
[Compatibility](../compatibility.md) is the place to check before planning a
port.

## Native interop

Two directions exist. A TurboPython module compiles into a CPython extension
(`# tpy: ext_module`, [Building](building.md)). And existing C++ binds into
TurboPython with `@native`, mapping a class or function onto a C++ type or
call -- the standard library itself is built this way. `@native` is usable
but undocumented; the API may change.

## Macros

A compile-time macro mechanism exists inside the compiler -- several built-in
decorators are implemented as compile-time macros. A user-facing macro system
is not documented or supported yet. [Compatibility](../compatibility.md)
records its status.

This closes the guide. [Getting started](../getting-started.md) and
[Compatibility](../compatibility.md) cover the practical side, and
[the map](differences.md) gives the overview again at any time.
