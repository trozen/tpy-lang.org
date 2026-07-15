# expect: ok
from typing import Protocol

class Measurable(Protocol):
    def size(self) -> int: ...

class Batch:
    n: int
    def __init__(self, n: int):
        self.n = n
    def size(self) -> int:
        return self.n

def total(m: Measurable) -> int:
    return m.size()

def main():
    print(total(Batch(5)))

main()
