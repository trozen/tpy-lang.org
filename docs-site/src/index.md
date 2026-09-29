# TurboPython documentation

TurboPython is a programming language and a compiler based on Python. It
keeps Python's familiar syntax and adds a few extensions that let a program
be statically compiled into a fast native binary. These docs cover how to
write TurboPython and what works today.

- **[Getting started](getting-started.md)** -- installation, a first program,
  and a ten-minute tour of the language.
- **[Guide](guide/index.md)** -- what changes coming from Python, the
  ownership model, and idiomatic patterns.
- **[Compatibility](compatibility.md)** -- a precise list of what works today.

A generated API reference will follow.

!!! note "Early development"
    The core language compiles and runs real programs, but some ordinary Python
    constructs are still rejected, the standard library is a subset, and known
    bugs can produce wrong results silently. [Compatibility](compatibility.md)
    records what works; the [landing page](https://tpy-lang.org/) has runnable
    examples.
