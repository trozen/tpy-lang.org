# expect: ok
from tpy import int32

class Countdown:
    n: int32
    def __init__(self, n: int32):
        self.n = n
    def __iter__(self) -> "Countdown":
        return self
    def __next__(self) -> int32:
        if self.n == 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

def main():
    for i in Countdown(3):
        print(i)

main()
