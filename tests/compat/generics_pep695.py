# expect: ok
from tpy import Float64

def first_of[T](xs: list[T]) -> T:
    return xs[0]

def main():
    print(first_of([1.5, 2.5]))
    print(first_of(["a", "b"]))

main()
