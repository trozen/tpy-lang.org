# Coming from C++/Rust

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

This page maps TurboPython onto C++ and Rust vocabulary. It is for readers
who know those languages; Python readers can skip it.

TurboPython is not Rust borrow-checking and not raw C++. Storage is single-owner, as in Rust: fields, container elements, and
globals own their values. Access is Python-like aliasing: locals and
parameters are unchecked references, freely copied and freely aliased, as in
C++. The compiler checks *escape*, not aliasing. A reference cannot be returned or
stored beyond its owner's lifetime. A move is only taken when no live alias
remains; otherwise the store falls back to a deep copy and a warning. Mutating
a container while an element borrow is live draws a warning
(`'append' may invalidate references`). There is no
aliasing-XOR-mutation rule to satisfy, and no lifetime annotations anywhere.

## The mapping

| TurboPython | C++ | Rust |
|---|---|---|
| plain `T` parameter | `T&` (or `const T&`, inferred) | `&T`/`&mut T`, unchecked |
| plain `T` return | `T&` | `&T` |
| `Own[T]` | `T&&` in practice; a `unique_ptr`-style handoff | by-value `T` |
| `readonly[T]` | `const T&` | `&T` |
| `Ptr[T]` | `T*` | raw pointer |
| `copy()` | explicit copy construction | `.clone()` |
| `@nocopy` class | deleted copy constructor | a type without `Clone` |
| `A \| B` | `std::variant` | an `enum` |
| `match` on a union | a branch on the tag | `match` |
| `str` | `std::string` or `std::string_view`; the compiler decides per use | `Cow<str>`-like |
| `String` | owned `std::string` | `String` |
| `StrView` | `std::string_view` | `&str` |
| a class | a plain `struct`, stored inline in containers | a `struct` |
| `raise` / `except` | C++ exceptions | no analog: unchecked exceptions |
| a panic | `std::exit(1)` after printing `TurboPython panic: <msg>` | `panic!` without `catch_unwind` |
| `Rc` / `Arc` / `Weak` (opt-in) | like `shared_ptr` + `weak_ptr` | `Rc` / `Arc` / `Weak` |
| `Send` (thread spawn bound) | -- | `Send` |

## Surprises for C++/Rust readers

**Plain returns are reference returns.** For a reference type, `def f() -> T`
returns `T&`, not a value (value types return by value); only `Own[T]` returns
an owned reference-type value. Returning a *reference-type* local through a
plain return type is the compile error that teaches this
([Ownership](ownership.md)).

**Implicit copies exist, and they warn.** Where C++ would silently copy and
Rust would refuse to compile, TurboPython copies deeply and emits a warning
naming the spot. `@nocopy` per type turns the warning into an error
([Efficiency](efficiency.md)).

**Dispatch is static, without `virtual`.** A call through a base-typed
reference binds at compile time, with a warning on every hiding override.
Runtime dispatch is an opt-in property of structural protocols (interfaces),
not of classes ([Data modeling](data-modeling.md)).

**Destruction is deterministic.** `__del__` runs the moment the owner frees
the object -- a destructor in the RAII sense, not a garbage-collector
finalizer.

**Generics monomorphize.** `def first[T](xs: list[T]) -> T` (PEP 695 syntax)
compiles per instantiation, like a template.

**Exceptions are real C++ exceptions.** The non-throwing path is free; a
`raise` unwinds. Panics -- overflow, failed narrowing -- are unrecoverable
process exits, not exceptions ([Control flow](control-flow.md)).

**The generated code is the code to expect.** A class compiles to a plain
struct; `list[Float64]` is a contiguous `std::vector<double>`; `Own`
parameters are rvalue references. `tpyc --dump-code` shows it
([Building](building.md)).

## Threads follow Rust's model

Thread spawning takes an owned task and enforces `Send` at the boundary;
threads do not borrow, and the handle joins for the result. There is no GIL.
Cross-thread sharing goes through `Arc` ([Ownership](ownership.md)), which
shares without locking and does not enforce race freedom. `Atomic[T]` covers
counters and flags. [Compatibility](../compatibility.md) tracks the current
state of the concurrency primitives.

The thread API and a worked `spawn`/`join` example are on
[Beyond the core](beyond.md), which tracks the rest of the concurrency
support.
