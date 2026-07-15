# expect: error Unknown decorator
from tpy import Int32
from typing import Callable

def twice(f: Callable[[Int32], Int32]) -> Callable[[Int32], Int32]:
    def wrapper(x: Int32) -> Int32:
        return f(f(x))
    return wrapper

@twice
def inc(x: Int32) -> Int32:
    return x + 1

def main():
    print(inc(5))

main()
