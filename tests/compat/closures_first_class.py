# expect: ok
from tpy import Int32
from typing import Callable

def make_adder(k: Int32) -> Callable[[Int32], Int32]:
    def add(x: Int32) -> Int32:
        return x + k
    return add

def main():
    f = make_adder(10)
    print(f(5))

main()
