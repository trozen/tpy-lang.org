# expect: ok
from tpy.thread import spawn
from tpy import int32

class Job:
    n: int32
    def __init__(self, n: int32):
        self.n = n
    def run(self) -> int32:
        return self.n * 2

def main():
    h = spawn(Job(21))
    print(h.join())

main()
