# expect: ok
from tplib.arc import Arc

class Obj:
    x: int
    def __init__(self, x: int):
        self.x = x

def main():
    a = Arc.new(Obj(1))
    b = a.clone()
    b.get().x = 5
    print(a.get().x)

main()
