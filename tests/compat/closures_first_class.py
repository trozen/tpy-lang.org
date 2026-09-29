# expect: ok
from tpy import int32
from typing import Callable

def make_adder(k: int32) -> Callable[[int32], int32]:
    def add(x: int32) -> int32:
        return x + k
    return add

def main():
    f = make_adder(10)
    print(f(5))

main()
