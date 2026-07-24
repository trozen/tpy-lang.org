# Compatibility

This page records what works today, hand-curated for a Python developer
evaluating TurboPython. It is not an exhaustive API list; it names the common
surface and the gaps that matter in practice. Each entry carries a status:

- **Works** -- the common API is present; only edge cases are missing.
- **Partial** -- a useful subset works; the notable gaps are listed.
- **Not yet** -- not usable today.

## Language & syntax

### Works

| Feature | Note |
|---|---|
| Functions: defaults, keyword arguments, annotated `*args` | [Functions](guide/functions.md) |
| First-class functions, closures, lambdas | `Fn[...]` (zero-cost) and `Callable[...]` (type-erased); nested `def` with `nonlocal` |
| Classes: declared fields, methods, `@property`, `@staticmethod`, class-level defaults | [Data modeling](guide/data-modeling.md) |
| `@dataclass` | generates the constructor |
| Dunder methods: `__str__`, `__eq__`, `__hash__`, `__del__` | `__del__` runs deterministically when the owner frees the object |
| Operator overloading | `__add__` and friends; fresh results return `Own[T]` |
| Objects as set elements and dict keys | with `__eq__` + `__hash__` |
| Inheritance with `super()`, including multiple inheritance | dispatch is static -- the compiler warns on every hiding override |
| Structural protocols | static; `@dynamic` for runtime dispatch |
| Unions `A \| B` + `match` | guards, `case _`, `isinstance`; every path must return |
| Generators and generator expressions | `-> Iterator[T]` annotation required |
| Hand-written iterators | `StopIteration` compiled away, no throw cost |
| Comprehensions (list, dict, set) | |
| Context managers | custom `__enter__` / `__exit__` |
| Exceptions | hierarchies, base-class catch, `except (A, B)`, bare re-raise, `finally` |
| `assert` | narrows optionals; kept in `-O` builds |
| `bytes` literals | |
| User generics | PEP 695 (`def f[T](...)` / `class C[T]`); compiled once per concrete type |
| Enums | `Enum` / `IntEnum`, `auto()`, `.name` / `.value`, iteration, value/name lookup, `match` |
| Top-level code | works; `main()` is only a convention |
| Module globals | reference types are assigned once at module scope, by design |

### Partial

**`async` / `await`.** The syntax works; the runtime is a growing subset --
see the `asyncio` entry under [Concurrency](#concurrency).

**Built-in functions and types.**

**Works:** the common built-ins -- `len`, `range`, `enumerate`, `zip`, `map`,
`filter`, `sorted`, `sum`, `min` / `max`, `abs`, `round`, `int` / `float` /
`str`, `list` / `dict` / `set` / `tuple`, `isinstance`, `input()`, and most
exception types. The `input` function does not accept a prompt argument.

**Not yet:** `frozenset`, `complex`, `memoryview`, `format`, `ascii`,
`callable`, `id`, runtime `type(x)`.

**`**kwargs`.** The typed form `**kwargs: Unpack[TypedDict]` works; the untyped
`**kwargs: T` form is rejected.

**f-strings.** Scalar values and format specs (`f"{x:.2f}"`) work; a `list` or
`dict` cannot be formatted directly inside the braces.

**`print(e)` on exceptions.** For built-in exceptions this prints the message,
matching CPython, and `str(e)` and f-strings return the message on both
runtimes. For a user-defined exception class, `print(e)` prints the object
rather than the message, with no diagnostic.

**Protocol and union types in containers.** Matching on the elements of a
`list[A | B]` works. `list[SomeProtocol]` is rejected, and passing a
`list[A | B]` element to a union-typed *parameter* fails in the C++ build
today.

### Not yet

| Feature | Note |
|---|---|
| User-defined decorators | `@my_decorator` on a function is rejected (`Unknown decorator`) |
| `yield from` | rejected with a clear message |
| `@noalloc` enforcement | the decorator parses; the no-allocation check is not implemented |
| `pyproject.toml` integration | planned; configuration is command-line flags today |
| User-facing macros | the compile-time macro mechanism exists internally only |
| `@native` C++ binding | usable but undocumented; the API may change |

## Standard library

A bundled subset ships with the compiler, grouped by domain below. Each library
is one entry with its status; partial ones list what works and what does not.

### Numbers & math

#### `math` -- Works { #math }

Constants (`pi`, `e`, `tau`, `inf`, `nan`) and the full CPython function set:
trig and inverse-trig, `log` / `log2` / `log10` / `exp`, `pow` / `sqrt` /
`isqrt` / `cbrt`, `floor` / `ceil` / `trunc` / `fmod` / `remainder` /
`copysign`, `gcd` / `lcm`, `factorial` / `comb` / `perm`, `fsum` / `prod` /
`dist` / `hypot`, `degrees` / `radians`, `isclose` / `isnan` / `isinf` /
`isfinite`. Signatures match CPython.

**Not yet:** a `tuple` passed as the iterable to `fsum` / `prod` / `dist`
(a tuple-iteration gap).

#### `random` -- Partial { #random }

**Works:** `Random`, `random`, `seed` (integer, or no-arg OS entropy),
`getrandbits(k)`, `randint`, `randrange`, `randbytes`, `choice`, `shuffle`,
`uniform`, `triangular`, and the distribution suite (`gauss`, `normalvariate`,
`lognormvariate`, `expovariate`, `paretovariate`, `weibullvariate`,
`gammavariate`, `betavariate`, `vonmisesvariate`). Byte-identical to CPython on
the same seed.

**Not yet:** `choices`, `sample`, `SystemRandom`, `getstate` / `setstate`,
`binomialvariate`.

#### `decimal` -- Not yet { #decimal }

A large surface; a candidate for a BigInt-based or native implementation.

#### `fractions` -- Not yet { #fractions }

#### `statistics` -- Not yet { #statistics }

### Text & data formats

#### `json` -- Partial { #json }

**Works:** `loads`, `dumps` (with `indent` / `sort_keys`), `load(fp)`,
`dump(obj, fp)`, `JSONDecodeError`, over a recursive `JsonValue` union.
Byte-compatible with CPython.

**Not yet:** the `JSONEncoder` / `JSONDecoder` classes and the remaining
`dumps` / `loads` keyword arguments (`ensure_ascii`, `separators`, `default`,
`object_hook`, `parse_float`, ...).

#### `re` -- Partial { #re }

**Works:** `compile`, `search`, `match`, `fullmatch`, `findall`, `finditer`,
`sub` (with `count`), `split`; `Pattern` and `Match` objects (`group` / `start`
/ `end` / `span`); the `IGNORECASE` / `MULTILINE` / `DOTALL` / `VERBOSE` /
`ASCII` flags; `re.error`. Backed by PCRE2 (vendored, bundled by default;
`--pcre2=` selects the backend).

**Not yet:** named-group accessors, bytes input, the compile cache.

#### `csv` -- Partial { #csv }

**Works:** `reader`, `writer`, `DictReader`, `DictWriter` over the `io`
`Readable` / `Writable` protocols; the Excel dialect; `delimiter` /
`quotechar` / `doublequote` / `skipinitialspace` / `lineterminator` kwargs;
`QUOTE_MINIMAL` writing. Byte-compatible with CPython.

**Not yet:** `Sniffer`, `Dialect` objects / `register_dialect`, the quoting
constants, `escapechar`, `DictReader` `restkey` / `restval`.

#### `base64` -- Works { #base64 }

b64 / b32 / b16 encode and decode, urlsafe and standard variants, `altchars` /
`validate` / `casefold` / `map01` kwargs, `encodebytes` / `decodebytes`;
accepts `bytes` / `bytearray` / `str` on the decoders.

**Not yet:** b85 / a85 (separate algorithms).

#### `struct` -- Partial { #struct }

**Works:** `unpack`, `calcsize`. **Not yet:** `pack` (needs a buffer builder).

#### `hashlib` -- Partial { #hashlib }

**Works:** SHA-256 (pure TurboPython). **Not yet:** MD5, SHA-1, SHA-512,
BLAKE2 / SHA-3, an optional OpenSSL backend.

#### `string` -- Not yet { #string }

#### `textwrap` -- Not yet { #textwrap }

### Collections, functional & typing

#### `collections` -- Partial { #collections }

**Works:** `Counter` (construction, `[]`, `len`, `in`, `total`,
`most_common(n)`, `update`, `subtract`).

**Not yet:** `deque`, `defaultdict`, `namedtuple`, `OrderedDict`,
`Counter.elements` and the `+ - & |` operators.

#### `itertools` -- Partial { #itertools }

**Works:** `count`, `repeat`, `cycle`, `islice(it, stop)`, `takewhile`,
`dropwhile`, `filterfalse`.

**Not yet:** `chain`, `product`, `starmap`, `accumulate`, `pairwise`,
`compress`, `tee`, `groupby`, `batched` (each blocked on a distinct compiler
gap -- variadic tuples, buffering).

#### `functools` -- Partial { #functools }

**Works:** `reduce(func, iterable[, initial])`, `total_ordering`.

**Not yet:** `lru_cache`, `partial`, `partialmethod`, `wraps`, `cmp_to_key`,
`cached_property`, `singledispatch`.

#### `bisect` -- Works { #bisect }

All four functions (`bisect_left` / `bisect_right` / `insort_left` /
`insort_right`), generic over `Comparable`.

#### `heapq` -- Works { #heapq }

All non-variadic operations plus `merge` (lazy, stable n-way).

**Not yet:** `merge` over arbitrary iterables (inputs must be `list[T]`),
`key=` / `reverse=` on `merge`.

#### `dataclasses` -- Partial { #dataclasses }

**Works:** field declarations, the generated `__init__`, `frozen` / `order`,
inheritance, `asdict` / `astuple`, `__post_init__`.

**Not yet:** `InitVar`, `replace()`, field `metadata`.

#### `enum` -- Works { #enum }

`Enum` / `IntEnum`, `auto()`, `.name` / `.value`, `==` / `is`, iteration
(`for c in Color`), value lookup (`Color(0)`), name lookup (`Color["red"]`),
`try_parse`, `match` on members, a configurable underlying type via mixin
(`(Int8, Enum)`), and `@native` binding to a C++ `enum class`.

**Not yet:** the functional API (`Enum("Color", [...])`).

#### `typing` -- Partial { #typing }

**Works:** `Protocol`, `Self`, `overload`, `override`, `Sized`, `Iterable`,
`Iterator`, `Sequence`, `Optional`, `Final`, `Callable`, `Literal`,
`TypedDict`, `Unpack`, `ClassVar`, `Any`, `cast`. Most operations on an `Any`
value require narrowing with `isinstance` or extraction with `cast` first.

**Not yet:** `Generic`, `TypeVar`, `ParamSpec`, `NewType` -- use PEP 695
syntax (`class C[T]`, `def f[T]`) for generics.

#### `copy` -- Not yet { #copy }

TurboPython has its own [`copy()`](guide/ownership.md).

### Files, OS & runtime

#### `os` -- Partial { #os }

**Works:** filesystem queries (`getcwd`, `chdir`, `listdir`, `scandir` ->
`DirEntry`, `stat` / `lstat` / `fstat` -> `stat_result`, `walk`); mutating
operations (`mkdir` / `makedirs`, `rmdir`, `remove` / `unlink`, `rename` /
`replace`, `symlink` / `readlink` / `link`, `chmod` / `chown`, `utime`,
`truncate`); low-level fd I/O (`open` / `close` / `read` / `write` / `lseek` /
`pipe` / `dup` / `dup2`, the `O_*` / `SEEK_*` constants); `access`; `urandom`;
process and system queries (`getpid` / `getppid`, the `getuid` family,
`umask`, `cpu_count`, `isatty`, `get_terminal_size`); `environ` (a snapshot
mapping) with `putenv` / `unsetenv`; module constants (`name`, `sep`, ...).
Errors carry structured `.errno` / `.strerror` / `.filename` with CPython-exact
`str(e)`.

**Not yet:** process spawning.

#### `os.path` -- Works { #os-path }

The full POSIX surface: `join` / `split` / `splitext` / `basename` /
`dirname` / `isabs` / `normpath` / `splitdrive` / `commonpath`; filesystem
queries `exists` / `lexists` / `isfile` / `isdir` / `islink` / `getsize` /
`abspath` / `realpath` / `relpath` / `getmtime` / `samefile` / `ismount` /
`expandvars` / `expanduser`. Byte-compatible with CPython's `posixpath`.

#### `io` -- Partial { #io }

**Works:** `StringIO`, `BytesIO` (read / write / `read(size)` / `readline` /
`seek` / `tell` / `truncate` / iteration / context manager); `FileIO` (raw
fd); `BufferedReader`; the `Readable` / `Writable` / `BinaryReadable` /
`BinaryWritable` protocols; `SEEK_*` and `DEFAULT_BUFFER_SIZE`.

**Not yet:** `TextIOWrapper`, the `IOBase` ABC hierarchy, `BufferedReader.peek`
/ `readinto`, encoding / newline / errors kwargs.

#### `sys` -- Partial { #sys }

**Works:** `argv`, `stdout`, `stderr`, `exit`, `maxsize`.

**Not yet:** `stdin`, `path`, `version_info`.

#### `signal` -- Partial { #signal }

**Works:** `raise_signal`, the `SIGINT` / `SIGTERM` constants.

**Not yet:** `signal.signal` handler registration.

#### `errno` -- Partial { #errno }

**Works:** the constants TurboPython's stdlib maps to `OSError` subclasses --
the network domain (`EAGAIN`, `EWOULDBLOCK`, `EINPROGRESS`, `EPIPE`,
`ECONNRESET`, `ECONNREFUSED`, `ECONNABORTED`) and the file domain (`ENOENT`,
`EEXIST`, `EACCES`, `EPERM`, `EISDIR`, `ENOTDIR`, `EBADF`, `ETIMEDOUT`), read
from the platform headers so values are host-correct. Enables
`e.errno == errno.ENOENT`.

**Not yet:** the full constant table (it grows as constants gain consumers).

#### `pathlib` -- Not yet { #pathlib }

Use `os` and `os.path`.

#### `glob` -- Not yet { #glob }

#### `shutil` -- Not yet { #shutil }

#### `tempfile` -- Not yet { #tempfile }

### Date & time

#### `datetime` -- Works { #datetime }

`timedelta`, `date`, `time`, `datetime`; fixed-offset `timezone` and
`ZoneInfo`-aware values; PEP 495 fold; `strftime` / `strptime` /
`fromisoformat`; `timestamp` / `astimezone`; `date()` / `time()` accessors;
`timedelta` float operators.

**Not yet:** an aware `time`, float constructor arguments
(`timedelta(hours=1.5)` -- use integer components).

#### `time` -- Partial { #time }

**Works:** `time`, `sleep`, `perf_counter`, `monotonic`, `time_ns` /
`perf_counter_ns` / `monotonic_ns`, `process_time`, `tzset`.

**Not yet:** `struct_time`, `strftime`, `gmtime` / `localtime`, the timezone
constants.

#### `zoneinfo` -- Works { #zoneinfo }

`ZoneInfo` (a value type with an interned zone id and per-instant DST offsets),
`available_timezones()`, `ZoneInfoNotFoundError`, `ZoneInfo.fromutc`.

**Not yet:** `from_file`, `TZPATH` / `reset_tzpath`, `no_cache` / `clear_cache`.

### Networking

#### `socket` -- Partial { #socket }

**Works:** IPv4 TCP client and server, blocking and non-blocking
(`setblocking`); `send` / `recv` / `sendall` / `shutdown`; `setsockopt_int` /
`getsockopt_int`; `getsockname` / `getpeername`; `gethostbyname`; `socketpair`;
`create_connection` / `create_server`; context-manager use; `settimeout` /
`gettimeout` (recv, send, and connect honor it; a timeout raises
`TimeoutError`); `makefile("rb")` -> `io.BufferedReader`. Errors subclass
`OSError` with structured `.errno` / `.strerror` and map to the PEP 3151
`ConnectionError` family (`BrokenPipeError` / `ConnectionResetError` /
`ConnectionRefusedError` / `ConnectionAbortedError`); `SIGPIPE` is ignored, so
writing to a hung-up peer raises rather than killing the process.

**Not yet:** IPv6 (`AF_INET6`), `AF_UNIX`, UDP (`sendto` / `recvfrom` /
`recv_into`), full `getaddrinfo`, `makefile` text or write modes,
`setdefaulttimeout`, Windows.

#### `ssl` -- Partial { #ssl }

**Works:** a verifying HTTPS client -- `create_default_context()` ->
`wrap_socket(sock, server_hostname=...)` -> `SSLSocket`, with certificate
verification and hostname checking on by default, trusting a vendored Mozilla
root bundle plus the platform CA bundle (`SSL_CERT_FILE` overrides). Server-side
TLS -- `SSLContext()` -> `load_cert_chain(cert, key)` ->
`wrap_socket(server_side=True)`. Backed by mbedTLS; `SSLError` and its
subclasses.

**Not yet:** mutual-TLS client-certificate verification, `SSL_CERT_DIR`
directory trust stores, macOS Keychain-only corporate CAs.

#### `http` -- Partial { #http }

**Works:** `HTTPStatus` (the full IntEnum -- `.value` / `.name`, value lookup,
integer comparison).

**Not yet:** `HTTPMethod`, the per-status `.phrase` / `.description` (an enum
member cannot carry extra data yet).

#### `http.client` -- Partial { #http-client }

**Works:** HTTP/1.1 over plaintext (`HTTPConnection`) and TLS
(`HTTPSConnection`, secure-default context, `context=` override, port 443):
`request` / `getresponse` / `connect` / `close`; `HTTPResponse` (`status` /
`reason` / `version` / `read` / `getheader` / `getheaders`); `HTTPException` /
`BadStatusLine` / `UnknownProtocol`. Automatic Host / Accept-Encoding /
Content-Length; body framing via Content-Length, chunked, and
connection-close; persistent keep-alive connections; `timeout=` threaded
through.

**Not yet:** low-level `putrequest` / `putheader`, string / file / iterable
request bodies, `email.message`-style headers, proxy / `set_tunnel`,
pipelining.

#### `urllib.parse` -- Partial { #urllib-parse }

**Works:** `urlsplit` / `urlparse` / `urlunsplit` / `urlunparse` / `urljoin`,
the `quote` family, `urlencode`, `parse_qsl`; byte-compatible with CPython.

**Not yet:** `parse_qs`, bytes variants, `urldefrag`; results are records, not
indexable/unpackable namedtuples.

#### `urllib.request` -- Partial { #urllib-request }

**Works:** `urlopen(url, data=None, timeout=None, context=None)` over
`http.client` (GET/POST), returning an `HTTPResponse`; `http` and `https`
schemes (https verifies out of the box); other schemes raise `URLError`.

**Not yet:** the opener/handler stack, redirects, proxies, auth handlers.

#### `tplib.requests` -- Partial { #tplib-requests }

**Works:** `get` / `post` / `put` / `patch` / `delete` / `head` / `request`,
with `params` / `headers` / `data` / `files` / `json` / `auth` / `timeout` /
`allow_redirects` / `cookies`; a `data=` body as raw `bytes` or a urlencoded
`dict`; `files=` multipart uploads; `Response` (`.status_code` / `.ok` /
`.text` / `.content` / `.json()` / `.headers` (a `CaseInsensitiveDict`) /
`.cookies` / `.url` / `.history` / `.raise_for_status()`); redirect following
(301/302/303/307/308); `stream=True` (`iter_content` / `iter_lines` / `.raw` /
`.close()`); a `Session` with default headers, connection pooling, and
persistent cookies; HTTPS verification (`verify=True | "<ca>" | False`);
exceptions rooted at `OSError` (`HTTPError` / `ConnectionError` / `Timeout` /
`TooManyRedirects`).

**Not yet:** `(connect, read)` timeout tuples, an untyped `.json()` return,
`asctime` cookie-expiry parsing.

This is a TurboPython-native client, not the PyPI `requests` package.

### Concurrency

#### Threads (`tpy.thread`) -- Works { #threads }

`spawn(task)` / `join`, with `Send` checked at spawn. There is no GIL.

#### Locks (`tpy.sync`) -- Works { #locks }

`Mutex[T]` (with a `MutexGuard` deref guard), `RwLock[T]`, and `Condvar`.

#### Atomics (`tpy.atomic`) -- Works { #atomics }

`Atomic[T]` over fixed-width integers: `load` / `store` / `exchange`,
`fetch_add` / `fetch_sub` / `fetch_and` / `fetch_or` / `fetch_xor`,
`compare_exchange`, the in-place operators, and a module-level `fence`. Each
operation takes a `MemoryOrder` that defaults to `SEQ_CST`.

#### Shared ownership -- Works { #shared-ownership }

`Rc` (non-atomic), the thread-safe `Arc`, and `Weak` for both, with an explicit
`.clone()` to share.

#### Channels (`tplib.channel`) -- Works { #channels }

A blocking multi-producer, single-consumer channel over OS threads.
`channel[T: Send](capacity)` returns a `(Sender[T], Receiver[T])` pair backed by
a fixed-capacity ring buffer. `send` and `recv` block the calling thread until
space or a value is available. Values cross the channel as `Own[T]`, moved from
sender to receiver rather than duplicated. `Sender.clone()` adds another producer; the
receiver is single-consumer and drains through `recv()` or iteration
(`for v in rx:`). The channel closes when the last `Sender` is dropped or on an
explicit `close()`, after which `recv` raises `ChannelClosed` once the buffer is
empty.

#### `asyncio` -- Partial { #asyncio }

**Works:** `run`, `sleep`, `create_task`, `Task[T]` / `Future[T]`, `Event`,
`CancelledError`; `gather(*tasks)` and `gather_list(tasks)`; `async with` /
`async for` + `StopAsyncIteration`; `wait_for` / `TimeoutError`; the sync
primitives `Lock` / `Semaphore` / `BoundedSemaphore` / `Queue`; an epoll/kqueue
reactor with `sock_recv` / `sock_sendall` / `sock_accept` / `sock_connect`;
streams (`open_connection` -> `StreamReader` / `StreamWriter`, `start_server` ->
`Server`); SIGINT graceful shutdown.

**Not yet:** the heterogeneous `gather[*Ts](*coros) -> tuple[*Ts]` form, a
multi-threaded executor, graceful SIGTERM.

#### Data-race detection through `Arc` -- Not yet { #data-race-detection }

`Arc` shares without a compile-time race check; guard shared mutation with
`Mutex` / `RwLock`, or use `Atomic`.

#### `threading` -- Not yet { #threading }

TurboPython has [its own threads](guide/beyond.md) (`tpy.thread`); the CPython
`threading` module is not ported.

#### `multiprocessing` -- Not yet { #multiprocessing }

Needs process spawning.

#### `subprocess` -- Not yet { #subprocess }

Needs process spawning.

### Development & introspection

#### `argparse` -- Partial { #argparse }

**Works:** positionals and optional flags; all seven actions and all four
`nargs` forms; `type=` (`int` / `float` / `str`, the fixed-width ints,
`Float32`, custom records via `from_arg`); `choices` / `required` / `dest` /
`help` / `metavar`; `Optional[T]` / `Optional[list[T]]` for absent flags;
list-literal defaults; bare `parse_args()` reading `sys.argv[1:]`; `--help` /
`-h` auto-generation and `add_help=False`; `prog=` / `usage=` / `epilog=`;
subparsers (flat namespace).

**Not yet:** mutually-exclusive groups, argument groups, terminal-width help
wrapping, `BooleanOptionalAction`, `parents=`, `allow_abbrev`, custom formatter
classes, `action=<callable>`.

#### `logging` -- Not yet { #logging }

#### `configparser` -- Not yet { #configparser }

#### `inspect` -- Not yet { #inspect }

Needs runtime type and function introspection.

#### `pickle` -- Not yet { #pickle }

Needs dynamic type information.

#### `unittest` -- Not yet { #unittest }

## Third-party packages

There is no `pip install` of PyPI packages. A dependency must be written in or
ported to TurboPython; regular Python packages -- pure-Python or C-extension --
do not import. TurboPython-native libraries live under `tplib` (for example
[`tplib.requests`](#tplib-requests)).
