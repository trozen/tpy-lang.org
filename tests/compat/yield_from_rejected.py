# expect: error not yet supported
from typing import Iterator

def inner() -> Iterator[int]:
    yield 1
    yield 2

def outer() -> Iterator[int]:
    yield 0
    yield from inner()

def main():
    print(list(outer()))
    print(sum(x * x for x in range(4)))

main()
