# Guide

The guide teaches the core of the language. It opens with a one-page
map of the differences from Python; the pages after it build up the model
behind them. Types are static, and the type of a value decides how it is
stored in memory. Fields, containers, and
globals own the values stored in them, while local variables and parameters
alias objects exactly as in Python. Efficient TurboPython is mostly ordinary Python code, with a few constraints
added where performance matters.

Readers new to TurboPython can start with
[Getting started](../getting-started.md), which installs the compiler and
gives a ten-minute tour of the language.

## The pages, in reading order

1. [How TurboPython differs from Python](differences.md) -- a one-page map
   of the language: the model and the main differences from Python, with the
   diagnostics the compiler prints for them.
2. [Types, inference and values](types.md) -- `int` and the fixed-width
   number types, what literals infer, value types against reference types,
   optionals, and the three string types.
3. [Functions and API boundaries](functions.md) -- what an annotated
   signature promises, how arguments and return values cross the boundary,
   and how to design a small typed API.
4. [Ownership and references](ownership.md) -- the most detailed page:
   which storage owns its values, how borrowing works, and when a store
   moves or copies.
5. [Data modeling](data-modeling.md) -- classes, protocols, containers,
   and unions with `match`, and where method dispatch differs from Python.
6. [Control flow, None & errors](control-flow.md) -- narrowing `None`
   away, exceptions and what they cost, and writing iterators.
7. [Writing efficient TPy](efficiency.md) -- the closing checklist:
   fixed-width arithmetic, deliberate copies, borrowing, and the constraint
   decorators.
8. [Building & running](building.md) -- running programs, the REPL,
   standalone binaries, the generated C++, and CPython extensions.
9. [Coming from C++/Rust](cpp-rust.md) -- how the model maps onto C++ and
   Rust concepts; Python readers can skip it.
10. [Beyond the core](beyond.md) -- the current state of async, threads,
    generators, protocols, and native interop.

[Compatibility](../compatibility.md) tracks the exact status of language
features and the standard library.
