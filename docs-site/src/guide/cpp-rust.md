# Coming from C++/Rust

TurboPython targets the same kind of efficient, compiled native code as C++
and Rust, but with ergonomics much closer to Python. It lets a Python
developer write efficient native software in Python's own syntax and model,
without switching to a systems language.

This page maps TurboPython's constructs to the C++ and Rust terms they
correspond to. It assumes familiarity with one of those languages; Python
readers can skip it.

In TurboPython, every object has exactly one owner. Durable storage owns what
it holds: a field owns its value, a container owns its elements, a global owns
its object. Local variables and parameters own nothing -- they refer to
objects the way names do in Python, and several of them can refer to the same
object at once.

The compiler does not restrict this aliasing the way Rust's borrow checker
does. There are no lifetime annotations, and no rule against aliasing a value
while it can still be mutated. The one thing it checks is escape: a reference
must not outlive its owner, so a function cannot return or store a reference to
something that will be freed once the call ends.

## The mapping

| TurboPython | C++ | Rust |
|---|---|---|
| `T` parameter | `const T&` / `T&` | `&T` / `&mut T` |
| `T` return | `T&` | `&T` |
| `Own[T]` parameter | `T&&` | `T` (moved) |
| `Own[T]` return | `T` | `T` (moved) |
| `readonly[T]` | `const T&` | `&T` |
| `Ptr[T]` | `T*` | `*mut T` |
| `Span[T]` | `std::span<T>` | `&mut [T]` |
| `Span[readonly[T]]` | `std::span<const T>` | `&[T]` |
| `copy()` | copy constructor | `.clone()` |
| `@nocopy` | deleted copy ctor | no `Clone` |
| `A \| B` | `std::variant` | `enum` |
| `T \| None` | `std::optional<T>` | `Option<T>` |
| `match` | tag dispatch | `match` |
| `int` | `BigInt` (arbitrary precision) | `num-bigint` |
| `Int32` / `Int64` | `int32_t` / `int64_t` | `i32` / `i64` |
| `str` | `std::string_view` / `std::string` | `Cow<str>` |
| `String` | `std::string` | `String` |
| `StrView` | `std::string_view` | `&str` |
| class | `struct` | `struct` |
| `raise` / `except` | exceptions | (no analog) |
| panic | `std::exit(1)` | `panic!` |
| `Rc` / `Arc` | `shared_ptr` / `weak_ptr` | `Rc` / `Arc` |
| `Send` | -- | `Send` |

## Behavior worth knowing

**Plain returns.** A function that returns a reference type by plain `-> T`
hands back a reference (`T&`), not a copy; the caller borrows the result. Value
types return by value. To return an owned reference-type value, annotate the
return `Own[T]`. Returning a reference-type local by plain `T` is rejected,
because that reference would dangle once the frame is gone
([Ownership](ownership.md)).

**Moves, not boxes.** `Own[T]` transfers ownership. As a parameter it lowers to
an rvalue reference (`T&&`), and the caller gives up its value; as a return it
passes the value straight out. This is Rust's by-value move -- no heap
allocation, nothing boxed.

**Implicit copies.** When a value is stored into durable storage and the source
is used again afterward, TurboPython makes a deep copy instead of a move. C++
would copy silently; Rust would reject the program. TurboPython copies, and
warns at the spot. Marking the type `@nocopy` turns that warning into an error.
When the source is not used again, the store is a move and nothing is copied
([Efficiency](efficiency.md)).

**Borrows and mutation.** Mutating a container while a reference into it is
still live is allowed, but the compiler warns (`'append' may invalidate
references`) -- the hazard C++ knows as iterator invalidation, and the one Rust
prevents outright with `&mut`.

**Const-correctness is inferred.** A parameter a function never mutates is
passed as `const T&` automatically, so the `readonly[T]` annotation is rarely
needed. This is C++ const-correctness, or Rust's split between `&` and `&mut`,
without spelling it out ([Functions](functions.md)).

**Arbitrary-precision `int`.** A bare `int` is not a machine word; it is an
arbitrary-precision integer, the kind C++ and Rust reach for a library to get.
A value that fits in 63 bits stays inline in a single word, so ordinary-sized
integers allocate nothing; only larger values move to the heap. The
fixed-width machine types are `Int32`, `Int64`, and their unsigned siblings,
which map to `int32_t`/`int64_t` and `i32`/`i64` ([Types](types.md)).

**No null dereference.** `T | None` is an explicit option type
(`std::optional<T>` / `Option<T>`). A value that might be `None` must be
narrowed before its `T` operations are allowed, and the compiler enforces
that -- there is no null pointer to forget to check
([Control flow](control-flow.md)).

**Static dispatch.** Method calls bind at compile time. A call through a
base-class reference does not dispatch virtually; it calls the static type's
method, and an override that hides a base method warns. Runtime polymorphism is
opt-in, through structural protocols (TurboPython's interfaces), not through
class inheritance ([Data modeling](data-modeling.md)).

**Deterministic destruction.** An object is destroyed when its owner releases
it, as with C++ RAII or Rust's `Drop`. `__del__` is that destructor: it runs at
a defined point, not whenever a garbage collector chooses.

**Monomorphized generics.** A generic function or class compiles once per
concrete type, like a C++ template or a Rust generic. `def first[T](xs:
list[T]) -> T` (PEP 695 syntax) produces a separate specialization for each `T`
it is used with.

**Real C++ exceptions.** `raise` and `except` compile to real C++ exceptions:
the non-throwing path costs nothing, and a `raise` unwinds the stack. The
`@error_return` decorator instead propagates errors as values, compiling to
`std::expected` -- Rust's `Result` -- for hot paths. The compiler applies it
automatically to every `__next__`, so a loop ends on `StopIteration` with no
exception-throwing cost. Panics are separate -- overflow, a failed narrowing,
and similar unrecoverable errors print a message and exit the process, like a
Rust `panic!` with no `catch_unwind` ([Control flow](control-flow.md)).

**Predictable codegen.** A class becomes a plain struct; `list[Float64]`
becomes a contiguous `std::vector<double>`; an `Own[T]` parameter becomes an
rvalue reference. `tpyc --dump-code` prints the generated C++, which shows
exactly what each construct became ([Building](building.md)).

## Threads follow Rust's model

Thread spawning takes ownership of the task and enforces `Send` at the
boundary, as Rust does. Threads do not borrow from the spawning frame, and the
join handle returns the result. There is no GIL. Sharing data across threads
goes through `Arc` -- an atomic reference count, like Rust's -- which shares
without locking and does not by itself prevent data races. `Atomic[T]` covers
counters and flags. [Compatibility](../compatibility.md) tracks the current
state of the concurrency primitives.

The thread API and a worked `spawn`/`join` example are on
[Beyond the core](beyond.md), which covers the rest of the concurrency
support.
