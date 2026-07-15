# expect: ok
from typing import Iterator

def evens(limit: int) -> Iterator[int]:
    n = 0
    while n < limit:
        yield n
        n += 2

def main():
    squares = [x * x for x in range(5)]
    by_name = {f"k{i}": i for i in range(3)}
    total = sum(squares)
    print(f"total={total}")
    print(squares)
    print(sorted(by_name.items()))
    print(list(evens(8)))
    with open("/tmp/tpy_everyday.txt", "w") as fh:
        fh.write("ok")
    print("file written")

main()
