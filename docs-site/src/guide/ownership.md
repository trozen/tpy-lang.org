# Ownership and references

Every program stores its data in memory, and that memory must be managed: an
object is created, lives while the program uses it, and has to be released once
nothing needs it anymore. Many languages automate this lifecycle so the
programmer never sees it, usually with a garbage collector or with reference
counting, and the convenience has a runtime cost. In Python that cost is always
present: every variable is a reference to a heap object, a reference count is
updated on every assignment, and a garbage collector collects the reference
cycles.

TurboPython manages object lifecycles at compile time instead. Two distinctions
make this possible.

First, TurboPython (like C#, Java, Swift, or Rust) separates **value types**
from **reference types**. Value types are the simple data: `int` and the
fixed-width integers, `float`, `bool`, `str`, `Char`, and tuples of these. A
value lives directly in its variable and is copied on assignment -- the way
numbers already appear to behave in Python. Value types have no lifecycle to
manage; nothing on this page applies to them.

Second, every reference-type object -- a class instance, a list, a dict -- has
exactly one **owner**, known at compile time, and it lives exactly as long as
its owner:

- An object created in a function is owned by that function's **frame** and
  freed when the function returns.
- An object stored in a **container** or a **field** is owned by that storage.
  This *durable storage* (the compiler's diagnostics call it *owned storage*)
  holds its own value, not a shared reference. A module **global** also owns
  its value; a reference-type global is assigned once, at module scope, and
  cannot be reassigned later.
- **Local variables and parameters own nothing.** The frame owns what the
  call creates; the names only *borrow* -- in Python terms, they alias: two
  names can refer to the same object, exactly as in Python.

One owner with a known lifetime is what replaces the garbage collector. The
compiler frees each object at the right point, stores it inline instead of
behind a pointer, and rejects code that would keep a reference past its owner's
lifetime. All of it is decided at compile time.

Ownership is the one real shift from Python; the rest is ordinary Python with
static types. It cannot be switched off, but it rarely needs to be written
explicitly: the markers (`Own[T]`, `copy()`, `readonly[T]`) appear only where
ownership transfers: where an object is returned or stored. For designs that
genuinely need one object with several owners, an opt-in shared-ownership type
(`Rc`) exists; it is covered briefly at the end of this page.

## Locals and parameters alias, like Python

An object created in a function is owned by that function's frame, and the
frame frees it when the function returns. The local variable does not own the
object: it only refers to it. Assignment therefore never copies: `b = a`
makes `b` a second name for the same object. Passing an argument works the same
way: the parameter becomes another name for the caller's object. A change
made through one name is visible through every other.

The examples reuse the `Reading` class from the
[Types page](types.md); the `Own[...]` in its constructor is taught later on
this page.

<!-- tpy: prelude run -->
```python
from tpy import Own, copy, readonly, Float64

class Reading:
    sensor: str
    values: list[Float64]
    def __init__(self, sensor: str, values: Own[list[Float64]]):
        self.sensor = sensor
        self.values = values

def main():
    a = Reading("boiler-3", [20.5])   # owned by main's frame
    b = a                             # b refers to the same object as a
    b.sensor = "boiler-9"
    print(a.sensor)                   # boiler-9

main()
```

Neither `a` nor `b` owns anything: both are *borrows*, names that refer to an
object owned elsewhere. Reading a field, calling a method, passing the object
on to another function -- all of it happens through borrows. That is why
everyday TurboPython code looks and behaves exactly like Python, with no copies
and no annotations.

Ownership becomes visible at two points only: when an object is *returned* out
of the frame that owns it, and when it is *stored* into durable storage -- a
container or a field. The next three sections take these in turn.

## A frame owns its locals

A local variable lives in the frame of the function that creates it, and is
freed when that function returns. It therefore cannot be returned by reference
-- the reference would point at freed memory:

<!-- tpy: cont expect-error="Use Own[Reading] to return by value" -->
```python
def make() -> Reading:
    r = Reading("boiler-3", [20.5])
    return r     # error: r is a local, freed when make() returns
```

```
error: Cannot return local or temporary as reference. Object type 'Reading'
is returned by reference. Use Own[Reading] to return by value.
```

The diagnostic names a rule the page has not stated yet: a plain `Reading`
return type returns a *reference* to the object, not the object itself. That
is fine when the object outlives the function -- returning an element of a
caller's list, for example:

<!-- tpy: cont -->
```python
def first(items: list[Reading]) -> Reading:
    return items[0]   # borrowed from the caller's list
```

A local dies with the frame, so it needs the other kind of return.
`Own[Reading]` hands the object itself to the caller, and the caller's frame
becomes its owner:

<!-- tpy: cont run -->
```python
def make() -> Own[Reading]:
    r = Reading("boiler-3", [20.5])
    return r     # ownership moves to the caller

def main():
    m = make()   # the object now lives in main's frame
    print(m.sensor)   # boiler-3

main()
```

## A container owns its elements

A `list`, `dict`, or `set` stores its elements, not references to them. Most of
the time this changes nothing -- building a list looks exactly like Python:

<!-- tpy: cont run -->
```python
def main():
    items: list[Reading] = []
    for i in range(3):
        items.append(Reading("boiler", [0.5 * i]))
    print(items[2].values[0])   # 1.0

main()
```

Each `Reading` here has no other user, so it simply becomes the list's element.
Nothing is copied and nothing is shared. A store copies only when the compiler
cannot simply hand the object over, that is, when some name still refers to
the object after the store. (The exact rule is under
[Advanced: move or copy](#advanced-move-or-copy).)

Keeping a second name for the stored object is where TurboPython and CPython
diverge. The list needs its own value, so the store makes a copy, and the
compiler warns about it:

<!-- tpy: cont run -->
```python
def main():
    items: list[Reading] = []
    r = Reading("boiler-3", [20.5])
    items.append(r)          # warning: copies r into the list (still used below)
    r.sensor = "renamed"     # changes r -- NOT the stored copy
    print(items[0].sensor)   # prints boiler-3; under CPython: renamed

main()
```

```
warning: copies Reading into owned storage; use copy() to make this explicit
```

!!! warning "Differs from CPython"
    This program prints `boiler-3`. Under CPython it prints `renamed`: the
    list would hold a reference to `r`, so the rename would show through the
    list. In TurboPython the element owns its own `Reading`, and the original
    `r` is a different object from the moment of the store. The compiler flags
    every such store with the `copies ... into owned storage` warning shown
    above, so this divergence is never silent.

The warning is acknowledged with `copy()`. The copy happens either way;
`copy()` makes it intentional, visible in the code, and clears the warning. The
copy is deep: the stored element owns its own complete structure, including
everything the object itself owns.

<!-- tpy: cont run -->
```python
def main():
    items: list[Reading] = []
    r = Reading("boiler-3", [20.5])
    items.append(copy(r))    # the list holds its own copy, on purpose
    r.sensor = "renamed"
    print(items[0].sensor)   # boiler-3

main()
```

Often the copy is avoidable altogether: storing a value the program no longer
uses costs nothing. How the compiler decides is covered below, under
[Advanced: move or copy](#advanced-move-or-copy) -- everyday code can stop at
`copy()`.

## A field owns its value

A field outlives the call that sets it, so it must own its value rather than
borrow one that may disappear. The rule is the same as for a container element:
storing a borrowed value copies it. Here the borrowed value is the parameter.
The caller still owns the object, so it cannot simply be taken; the store
copies it into the field, and the compiler says so:

<!-- tpy: cont -->
```python
class Cache:
    last: Reading
    def __init__(self, r: Reading):
        self.last = r    # warning: copies r into the field
```

```
warning: copies Reading into field; use copy() to make this explicit
```

This is the same divergence from CPython as the container store above, flagged
by the same kind of warning.

For the field to *take* the caller's object instead of copying it, the
parameter is declared `Own[Reading]` -- the same marker `Reading`'s own
constructor uses to take the caller's list:

<!-- tpy: prelude -->
```python
class Cache:
    last: Reading
    def __init__(self, r: Own[Reading]):
        self.last = r    # the field takes ownership
```

An `Own` parameter moves the question to the call site. A caller that is done
with the object gives it up directly: no copy, no warning. A caller that
keeps using the object afterwards faces the same rule as the container store:
the argument must be copied, or the compiler warns:

<!-- tpy: cont run -->
```python
def main():
    r = Reading("boiler-3", [20.5])
    c = Cache(copy(r))       # r stays in use below -- pass a copy
    r.sensor = "renamed"
    print(c.last.sensor)     # boiler-3

main()
```

## In practice

Value types (`Int32`, `str`, ...) always stay plain: they copy, and ownership
does not concern them. For reference types:

| Situation | Annotation |
|---|---|
| Passing an object to a function | plain `T` -- it is borrowed |
| A local that refers to another object | plain `T` -- it borrows too |
| Returning an object owned elsewhere (a field, an element) | plain `T` -- a reference |
| Returning a freshly built object | `Own[T]` |
| A field or parameter that takes ownership | `Own[T]` |
| Storing a last-use local, or an unnamed value like `Reading(...)` | nothing -- it moves (see below) |
| Storing an object that is used again afterwards | `copy(...)` -- or restructure so it moves |
| A parameter the function does not mutate | `readonly[T]` (optional) |

Ordinary annotated Python code already follows this table; no extra decisions
are needed. The markers appear only where ownership actually transfers --
returning an object, or storing one.

## Advanced: move or copy

Everything above is enough for everyday code: plain code borrows, a store
copies when the original stays in use, and `copy()` accepts the warning. The
rest of the page covers what the compiler actually does with each store, and
the explicit borrow markers. It matters mostly for performance-sensitive code.

Every store into durable storage needs a value the storage can own. The
compiler obtains one in two ways.

**A move.** When the object was created in the current frame and the store is
its last use, no one else needs it: the object is handed over as-is. No
separate copy is made, and there is nothing to warn about:

<!-- tpy: cont run -->
```python
def main():
    items: list[Reading] = []
    r = Reading("boiler-7", [21.0])
    items.append(r)          # last use of r -- it moves into the list
    print(items[0].sensor)   # boiler-7

main()
```

Constructing the value in place is the same move in its simplest form. A
temporary -- an unnamed value like `Reading(...)` below -- has no other use by
definition, so it always moves and never warns:

<!-- tpy: cont run -->
```python
def main():
    items: list[Reading] = []
    items.append(Reading("boiler-7", [21.0]))   # a temporary always moves
    print(items[0].sensor)                      # boiler-7

main()
```

An alias counts as a use. If another name still refers to the object, the
store is not its last use, so the compiler copies and warns instead of moving.
No name is ever left pointing at a moved-away object:

<!-- tpy: cont run -->
```python
def main():
    items: list[Reading] = []
    a = Reading("boiler-3", [20.5])
    b = a                    # a second name for the object
    items.append(a)          # not a move: b still needs it -- copy, warned
    b.sensor = "renamed"
    print(items[0].sensor)   # boiler-3

main()
```

**A copy.** When a move is impossible -- the object is still referred to after
the store, or it belongs to the caller (a parameter is a borrow, and never
moves) -- the storage receives its own deep copy, and the compiler warns. The
warning marks exactly where TurboPython and CPython behave differently:
CPython would have shared the object instead. The wording varies with the
target (`into field`, `into container`, `into owned storage`), and the fix is
the same everywhere. A `copy()` written where the compiler would have moved is
flagged from the other side:

```
warning: unnecessary copy() -- 'r' is at its last use and would be moved
automatically
```

Resolving a copy warning, in order of preference:

1. **Restructure so the store is the last use** -- the copy becomes a move.
2. **Construct in place** -- a temporary always moves.
3. **Take `Own[T]` at the boundary** -- when the caller should give the object
   up, as in the `Cache` example above.
4. **Accept the copy with `copy()`** -- when both the original and the stored
   value are genuinely needed.

## Advanced: explicit borrows (`readonly[T]`, `Ptr[T]`)

These markers are rarely written. A parameter is already a borrow, never a
copy. When a function does not mutate a parameter, the compiler sees that and
treats the borrow as read-only automatically. The explicit forms exist to
state that intent in the signature.

`readonly[T]` declares a parameter the function does not mutate; mutating
through it is a compile error:

<!-- tpy: cont -->
```python
def first_value(r: readonly[Reading]) -> Float64:
    return r.values[0]
```

`Ptr[T]` is an explicit pointer, for the uncommon case one is needed (an
optional reference, or C++ interop). Ordinary code does not use it.

!!! note "Coming from C++/Rust"
    `Own[T]` is pass or return by value with move semantics -- like handing
    off a `std::unique_ptr<T>`, or Rust's by-value `T`. `readonly[T]` is
    `const T&`, and `Ptr[T]` is a raw `T*`. A plain `T` parameter -- and a
    plain `T` *return type* -- is a reference, never a copy; reference returns
    by default are the biggest single departure from C++. Storage is
    single-owner as in Rust, but borrows are unchecked C++-style references:
    the compiler rejects references that escape their owner (returns, stores)
    and falls back to a copy when a live alias blocks a move. There is no
    aliasing-XOR-mutation rule to satisfy. The full mapping:
    [Coming from C++/Rust](cpp-rust.md).

## Advanced: shared ownership (`Rc`, `Arc`)

Single ownership plus copies covers most designs, but not all of them. When one
object genuinely needs several owners -- a cache and a live user, an object
indexed by two dicts -- the standard library provides `Rc` (`from tplib import
Rc`): opt-in shared ownership with reference counting, paid only where it is
used. `Rc.new(...)` creates the shared object and `.clone()` adds an owner;
clones alias the same object, as references do in Python. `Arc`
(`from tplib.arc import Arc`) is its thread-safe sibling: the same shape with
atomic counters, for sharing across threads.

Everything else on this page is the default: one owner per object, decided at
compile time.
