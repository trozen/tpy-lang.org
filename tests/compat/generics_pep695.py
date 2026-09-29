# expect: ok
def first_of[T](xs: list[T]) -> T:
    return xs[0]

def main():
    print(first_of([1, 2]))
    print(first_of(["a", "b"]))

main()
