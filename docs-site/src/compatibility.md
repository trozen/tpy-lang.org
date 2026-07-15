# Compatibility

!!! warning "Review pending"
    This page has not yet been reviewed by the maintainer.

This page tracks what works today -- exactly for language features, at
module level for the standard library.

**Status as of TurboPython 0.5.0.dev0, 2026-07-08.**

## Language features

### Works

| Feature | Note |
|---|---|
| Functions: defaults, keyword arguments, annotated `*args` | [Functions](guide/functions.md) |
| First-class functions and closures | functions return functions; `Callable[...]` types |
| Lambdas | e.g. as `sorted` keys |
| Classes: declared fields, methods, `@property`, `@staticmethod`, class-level defaults | [Data modeling](guide/data-modeling.md) |
| `@dataclass` | generates the constructor |
| Dunder methods: `__str__`, `__eq__`, `__hash__`, `__del__` | `__del__` runs deterministically when the owner frees the object |
| Operator overloading | `__add__` and friends; fresh results return `Own[T]`, per the normal rule |
| Objects as set elements and dict keys | with `__eq__` + `__hash__` |
| Inheritance with `super()`, including multiple inheritance | dispatch is static -- differs from CPython; the compiler warns on every hiding override |
| Structural protocols | static; `@dynamic` for runtime dispatch |
| Unions `A \| B` + `match` | guards, `case _`, `isinstance`; every path must return |
| Generators and generator expressions | `-> Iterator[T]` annotation required |
| Hand-written iterators | `StopIteration` compiled away, no throw cost |
| Comprehensions (list, dict, set) | |
| Context managers | custom `__enter__`/`__exit__` work |
| Exceptions | hierarchies, base-class catch, bare re-raise, `finally` |
| `assert` | narrows optionals; kept in `-O` builds (no CPython `-O` stripping) |
| `bytes` literals | |
| User generics | PEP 695 syntax (`def f[T](...)`); compiled once per concrete type |
| Top-level code | works; `main()` is only a convention |
| Module globals | reference types are assigned once at module scope, by design |
| Threads | `tpy.thread.spawn`/`join`, `Send` checked at spawn; no GIL |
| Shared ownership | `Rc`, thread-safe `Arc`, `Weak` |
| CPython extensions | `# tpy: ext_module` + `@export` |

### Partial

| Feature | Current boundary |
|---|---|
| `asyncio` | single-threaded executor; `run`, `create_task`, `sleep`, and plain `await` work ([Beyond the core](guide/beyond.md) has the details) |
| `**kwargs` | only the typed form (`Unpack[TypedDict]`); plain `**kwargs: T` is rejected |
| f-strings | scalars format; a list or dict cannot be formatted directly |
| `except` clauses | one exception type per clause; `except (A, B)` is rejected |
| `print(e)` on exceptions | prints the object, not the message; `str(e)` and f-strings return the message |
| Union elements in containers | matching on elements of `list[A \| B]` works; passing an element to a union-typed *parameter* fails in the C++ build today |
| Protocol types in containers | `list[SomeProtocol]` is rejected |
| `sorted` | elements must be `Comparable`; tuples containing lists are rejected |
| `sum` | cannot yet accept a read-only list, so it cannot be called where data is read-only (e.g. inside a `@property`) |
| Fixed-width `*args` | `Int32` varargs work; `Float64` varargs reject augmented assignment in the loop body |

### Not yet

| Feature | Status |
|---|---|
| Third-party packages (`pip install` imports) | modules must be written in or ported to TurboPython |
| User-defined decorators | `@my_decorator` on a function is rejected (`Unknown decorator`) |
| `yield from` | rejected with a clear message |
| `@noalloc` enforcement | the decorator parses; the no-allocation check is not implemented |
| `pyproject.toml` integration | planned; configuration is command-line flags |
| Race detection through `Arc` | the compiler does not yet detect data races through `Arc` clones; `Atomic[T]` covers counters, and a `Mutex` type does not exist |
| User-facing macros | the mechanism exists internally only |
| `@native` C++ binding documentation | usable but undocumented; the API may change |

## Standard library

A bundled subset ships with the compiler. Statuses: **bundled** -- the module
imports against the pinned build and covers a useful subset of the CPython
API, not the whole surface; **bundled, partial** -- large known gaps, listed
where the guide covers the module; **bundled, early** -- new code, expect
movement.

| Module | Status | Note |
|---|---|---|
| `math` | bundled | constants and common functions |
| `json` | bundled | encode/decode |
| `re` | bundled | pattern matching |
| `datetime`, `time`, `zoneinfo` | bundled | dates, times, time zones |
| `os`, `io`, `sys` | bundled | files, paths, environment basics |
| `collections`, `itertools`, `functools` | bundled | core helpers |
| `bisect`, `heapq` | bundled | sorted-list and heap algorithms |
| `dataclasses`, `enum`, `typing` | bundled | |
| `argparse` | bundled | command-line parsing |
| `csv`, `base64`, `struct`, `hashlib` | bundled | data formats and hashing |
| `random` | bundled | |
| `asyncio` | bundled, partial | see the language table above |
| `socket`, `ssl`, `http`, `urllib` | bundled, early | server-side TLS since 0.5.0.dev |
| `errno`, `signal` | bundled | process signals and error codes |
| `tplib.requests` | bundled, early | HTTP client, TurboPython-native |

Notable absences: `pathlib`,
`logging`, `subprocess`, `threading` (TurboPython has
[its own threads](guide/beyond.md)), `multiprocessing`, `pickle`, `sqlite3`,
`unittest`, `contextlib`, `copy` (TurboPython has its own
[`copy()`](guide/ownership.md)), `abc`, `string`, `textwrap`, `glob`,
`shutil`, `tempfile`, `uuid`, `secrets`.
