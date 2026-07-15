# expect: ok
from tpy.thread import spawn
from tpy import Int32

class Job:
    n: Int32
    def __init__(self, n: Int32):
        self.n = n
    def run(self) -> Int32:
        return self.n * 2

def main():
    h = spawn(Job(21))
    print(h.join())

main()
