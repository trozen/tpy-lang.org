# expect: error Unknown decorator
from tpy import int32
from typing import Callable

def twice(f: Callable[[int32], int32]) -> Callable[[int32], int32]:
    def wrapper(x: int32) -> int32:
        return f(f(x))
    return wrapper

@twice
def inc(x: int32) -> int32:
    return x + 1

def main():
    print(inc(5))

main()
